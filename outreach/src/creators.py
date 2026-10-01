"""CollabHive - email campaigns to the creator side of the marketplace.

Two campaigns, both aimed at the same thing: more creators on the platform.

    activate  -> to a creator who applied and is now live on the site. Confirms
                 they are published, asks for the rate and content details we
                 need to match them to a brief.
    refer     -> asks a live creator to pass the application form to creators
                 they know. This is the growth engine: an application form
                 shared by a creator who is already on the platform converts
                 far better than any cold approach, and it is the only creator
                 acquisition channel that does not involve scraping anyone.

Who may be emailed
------------------
ONLY creators who submitted the application form themselves and were published
to the site. That is the consent boundary and it is enforced in code, not by
convention: `real_creators()` cross-checks every address in creators_pool.json
against published_creators.json and drops anything that does not match.

This matters because the pool is seeded with 22 synthetic demo creators whose
addresses are literally handle@gmail.com. Mailing those would bounce 22 times
in one run and damage the sending reputation the brand outreach depends on.
Nothing here will ever send to an address that is not a real applicant.

    python src/run.py creators            # send the next batch
    python src/run.py creators --dry-run  # show who would be mailed
"""
from __future__ import annotations

import ssl
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from .common import ROOT, gmail_credentials, load_json, log, save_json
from .emailcheck import validate
from .protect import jitter

STATE_FILE = "data/creator_campaign.json"
TEMPLATE_DIR = ROOT / "templates"


# ------------------------------------------------------------------ audience
def real_creators(cfg: dict) -> list[dict]:
    """Creators who submitted the application form themselves.

    The application sheet is the primary source, not creators_pool.json. Three
    reasons, in order of importance:

      1. Consent. Everyone on the sheet typed their own address into our form.
         That is the boundary, and reading the sheet makes it structural rather
         than something a later edit could quietly widen.
      2. It works in CI. creators_pool.json is gitignored (it holds creator
         emails and phone numbers), so in GitHub Actions it does not exist —
         reading it there would have silently mailed nobody, forever, while
         reporting success.
      3. The sheet carries their content links, which the local pool drops.

    The local pool is only a fallback for offline development, and then only
    where a handle is confirmed against the published list — that pool is
    seeded with synthetic handle@gmail.com demo creators which must never be
    mailed.
    """
    out, seen = [], set()

    def _add(c: dict) -> None:
        email = (c.get("email") or "").strip().lower()
        handle = (c.get("handle") or "").lower().lstrip("@")
        if not email or email in seen:
            return
        ok, why = validate(email, None, check_mx=False)
        if not ok:
            log(f"  skip {handle or email}: {why}")
            return
        seen.add(email)
        out.append({**c, "email": email, "handle": handle})

    try:
        from .publication import pull_applicants
        applicants = pull_applicants(cfg) or []
    except Exception as exc:
        log(f"  applicant sheet unavailable: {str(exc)[:80]}")
        applicants = []

    for c in applicants:
        _add(c)
    if out:
        return out

    # Offline fallback. Only creators already published to the site, which is
    # the one signal that separates a real applicant from seeded demo data.
    log("  applicant sheet empty - falling back to the published local pool")
    pool = load_json(ROOT / cfg["sales"]["creator_pool_file"])
    pool = pool if isinstance(pool, list) else []
    pub = load_json(ROOT / cfg["publish"]["published_file"])
    pub = pub if isinstance(pub, dict) else {}
    published = {(c.get("handle") or "").lower().lstrip("@")
                 for c in pub.get("creators", []) if c.get("handle")}
    if not published:
        log("  no published creators either - refusing to email anyone")
        return []
    for c in pool:
        if (c.get("handle") or "").lower().lstrip("@") in published:
            _add(c)
    return out


# ----------------------------------------------------------------- templates
def _load(name: str) -> tuple[str, str]:
    txt = (TEMPLATE_DIR / f"{name}.txt").read_text(encoding="utf-8")
    html_path = TEMPLATE_DIR / f"{name}.html"
    html = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    return txt, html


def _render(txt: str, html: str, creator: dict, cfg: dict) -> tuple[str, str]:
    p = cfg["profile"]
    name = (creator.get("name") or "").strip()
    first = name.split()[0] if name else "there"
    ctx = {
        "name": first,
        "handle": "@" + creator.get("handle", ""),
        "niche": creator.get("niche", "") or "your niche",
        "city": creator.get("city", "") or "",
        "company": p["company"],
        "site_url": p["site_url"],
        "apply_url": p["apply_url"],
        "contact_email": p["contact_email"],
        "bonus_pct": cfg.get("onboarding", {}).get("referral_bonus_pct", 5),
    }
    def _fmt(t: str) -> str:
        try:
            return t.format(**ctx)
        except (KeyError, IndexError, ValueError):
            return t
    return _fmt(txt), _fmt(html)


# ------------------------------------------------------------------- sending
def _subject(kind: str, creator: dict, cfg: dict) -> str:
    if kind == "refer":
        return "Know a creator who should be on this?"
    return "You're live on CollabHive"


def run_campaign(cfg: dict, kind: str = "activate", limit: int = 0,
                 dry_run: bool = False) -> dict:
    """Send one batch. Never mails the same creator the same campaign twice."""
    if kind not in ("activate", "refer"):
        return {"ok": False, "reason": "unknown_campaign", "kind": kind}

    state = load_json(ROOT / STATE_FILE)
    state = state if isinstance(state, dict) else {}
    done = set(state.get(kind, []))

    audience = real_creators(cfg)

    if kind == "activate":
        # This email states "your profile is live", so it may only go to
        # creators who ARE live. The applicant sheet includes people whose
        # profile has not been published yet; telling them otherwise is simply
        # a false claim in outbound mail.
        pub = load_json(ROOT / cfg["publish"]["published_file"])
        pub = pub if isinstance(pub, dict) else {}
        live = {(c.get("handle") or "").lower().lstrip("@")
                for c in pub.get("creators", []) if c.get("handle")}
        before = len(audience)
        audience = [c for c in audience if c.get("handle") in live]
        if before != len(audience):
            log(f"  {before - len(audience)} applicant(s) not published yet - "
                f"they get the activation mail once they are live")

    if kind == "refer":
        # Only ask for referrals from creators we have already spoken to.
        # Both campaigns otherwise select the same first N creators and land in
        # the same inbox minutes apart on day one, which reads as a blast.
        # Gating on the activation list also produces a natural stagger: a
        # creator activated today becomes referral-eligible on a later run.
        activated = set(state.get("activate", []))
        audience = [c for c in audience if c["email"] in activated]

    pending = [c for c in audience if c["email"] not in done]

    # The creator list is small and finite, so a modest batch keeps the sending
    # pattern human and stays well inside the Gmail account's daily headroom
    # that brand outreach also draws on.
    cap = limit or int(cfg.get("creators", {}).get("daily_limit", 12))

    # The cap is per DAY, not per run. A manual re-run (or a retry) otherwise
    # sends another full batch within the hour from the same Gmail account that
    # brand outreach depends on — the limit has to survive being invoked twice.
    today = datetime.now(timezone.utc).date().isoformat()
    sent_today = int((state.get("sent_by_day", {}) or {}).get(today, 0))
    room = max(0, cap - sent_today)
    if room < cap:
        log(f"  {sent_today} already sent today - {room} slot(s) left of {cap}")
    batch = pending[:room]

    log(f"creator campaign '{kind}': {len(audience)} eligible, "
        f"{len(done)} already sent, {len(batch)} in this batch")
    if not batch:
        return {"ok": True, "kind": kind, "sent": 0, "eligible": len(audience),
                "already": len(done), "sent_today": sent_today,
                "note": "nothing pending or daily cap reached"}

    txt_tpl, html_tpl = _load(f"creator_{kind}")

    if dry_run:
        for c in batch:
            log(f"  DRY  {c['email']:<34} {c['handle']:<22} {c.get('niche','')}")
        return {"ok": True, "kind": kind, "sent": 0, "would_send": len(batch),
                "dry_run": True}

    user, password = gmail_credentials()
    if not password:
        log("  OUTREACH_EMAIL_PASS not set - nothing sent")
        return {"ok": False, "reason": "no_password", "kind": kind}

    ctx = ssl.create_default_context()
    import smtplib
    sent = failed = 0
    try:
        smtp = smtplib.SMTP(cfg["smtp"]["host"], cfg["smtp"]["port"], timeout=30)
        smtp.ehlo(); smtp.starttls(context=ctx); smtp.ehlo()
        smtp.login(user, password)
    except Exception as exc:
        log(f"  SMTP connect failed: {exc}")
        return {"ok": False, "reason": "smtp_fail", "error": str(exc)[:120]}

    try:
        for c in batch:
            body_txt, body_html = _render(txt_tpl, html_tpl, c, cfg)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = _subject(kind, c, cfg)
            msg["From"] = f"{cfg['smtp'].get('from_name', 'CollabHive')} <{user}>"
            msg["To"] = c["email"]
            msg.attach(MIMEText(body_txt, "plain", "utf-8"))
            if body_html.strip():
                msg.attach(MIMEText(body_html, "html", "utf-8"))
            try:
                smtp.sendmail(user, [c["email"]], msg.as_string())
                sent += 1
                done.add(c["email"])
                log(f"  sent {kind} -> {c['handle']}")
            except Exception as exc:
                failed += 1
                log(f"  FAILED {c['handle']}: {str(exc)[:90]}")
                if failed >= 5:
                    log("  too many failures - stopping")
                    break
            # Same spacing discipline as brand outreach: a burst of identical
            # messages from one Gmail account is what gets a sender throttled.
            time.sleep(jitter(float(cfg.get("creators", {})
                                    .get("gap_seconds", 20))))
    finally:
        try:
            smtp.quit()
        except Exception:
            pass

    state[kind] = sorted(done)
    by_day = state.get("sent_by_day") or {}
    by_day[today] = int(by_day.get(today, 0)) + sent
    # Keep a fortnight; this is a rate-limit ledger, not an archive.
    state["sent_by_day"] = {d: n for d, n in sorted(by_day.items())[-14:]}
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_json(ROOT / STATE_FILE, state)
    log(f"  done. sent={sent} failed={failed}")
    return {"ok": True, "kind": kind, "sent": sent, "failed": failed,
            "eligible": len(audience), "remaining": len(pending) - sent}
