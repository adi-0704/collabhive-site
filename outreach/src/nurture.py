"""CollabHive Outreach — bridge replies into quotes.

There was a hole in the funnel. Outreach produced a 38% reply rate and those
replies landed in data/closing_queue.json, but send_auto_quotes() only ever
read data/brand_briefs.json — the form submissions. A brand that replied
"interested" to an email therefore never received anything back automatically:
20 hot leads, 5 quotes, and every one of those quotes had an empty address.

This module closes it:

  * nurture_hot_leads -> a brand that replied gets one personal reply asking
                         for the three facts needed to build a shortlist,
                         with the brief form as the easy option.
  * chase_quotes      -> a quote that was genuinely emailed and went quiet
                         gets one follow-up, then stops.
  * clean_queue       -> drop entries that were never replies to our outreach
                         (Google alerts, autoresponders) so the funnel numbers
                         and these emails stay honest.

Every send is once-per-recipient and recorded. Stdlib only.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .common import ROOT, env, gmail_credentials, load_json, log, save_json

NURTURE_STATE = "data/nurtured.json"
QUOTE_CHASE_STATE = "data/quote_chased.json"


def _age_hours(ts: str) -> float | None:
    if not ts:
        return None
    try:
        d = datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - d).total_seconds() / 3600.0


_POOL_NAMES: dict[str, str] | None = None


def _brand_from_email(email: str, cfg: dict | None = None) -> str:
    """Brand name for the greeting.

    Prefers the real name from the seed pool — "SUGAR Cosmetics" reads like a
    human wrote it, "Sugarcosmetics" (derived from the domain) does not. Falls
    back to the domain only when the brand isn't in the pool.
    """
    global _POOL_NAMES
    domain = (email or "").partition("@")[2].lower()
    if not domain:
        return "there"

    if _POOL_NAMES is None and cfg:
        _POOL_NAMES = {}
        for b in (load_json(ROOT / cfg["brands"]["seed_file"]) or []):
            if not isinstance(b, dict):
                continue
            site = (b.get("website") or "").lower()
            site = site.replace("https://", "").replace("http://", "")
            site = site.split("/")[0].replace("www.", "")
            if site and b.get("name"):
                _POOL_NAMES[site] = b["name"]
            for addr in (b.get("emails") or []):
                d = addr.partition("@")[2].lower()
                if d and b.get("name"):
                    _POOL_NAMES.setdefault(d, b["name"])

    if _POOL_NAMES and domain in _POOL_NAMES:
        return _POOL_NAMES[domain]
    root = domain.split(".")[0]
    return root.replace("-", " ").title() if root else "there"


# ---------------------------------------------------------------- hygiene
def clean_queue(cfg: dict) -> dict:
    """Remove closing-queue entries that were never replies to our outreach.

    triage_replies now filters these at the source, but entries captured before
    that fix are still on disk, inflating the reply rate and — worse — they
    would receive the nurture email below.
    """
    from .sales import _contacted_index, _is_reply_to_us
    path = ROOT / cfg["sales"]["closing_file"]
    rows = load_json(path)
    rows = rows if isinstance(rows, list) else []
    contacted = _contacted_index(cfg)
    keep = [r for r in rows if _is_reply_to_us(r.get("email", ""), contacted)]
    removed = len(rows) - len(keep)
    if removed:
        save_json(path, keep)
        log(f"Closing queue: removed {removed} non-reply entr(ies), {len(keep)} real leads remain.")
    return {"removed": removed, "remaining": len(keep)}


# ---------------------------------------------------------------- nurture
def nurture_hot_leads(cfg: dict) -> dict:
    """Reply to brands that showed interest, asking for what a quote needs."""
    ncfg = cfg.get("nurture", {})
    if not ncfg.get("enabled", True):
        return {"sent": 0, "skipped": "disabled"}
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"sent": 0, "skipped": "no_password"}

    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    quotes = load_json(ROOT / cfg.get("quotes", {}).get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    quoted = {(q.get("email") or "").lower() for q in quotes if q.get("email")}

    state = load_json(ROOT / NURTURE_STATE)
    state = state if isinstance(state, dict) else {}

    from .growth import dnc_set
    dnc = dnc_set(cfg)

    p = cfg["profile"]
    user, password = gmail_credentials()
    sent = 0
    skipped = 0

    for lead in closing:
        email = (lead.get("email") or "").lower().strip()
        if not email or email in dnc or email in quoted or email in state:
            skipped += 1
            continue
        if lead.get("status") not in ("interested", "negotiating"):
            continue
        # Give the human a chance to reply personally first.
        age = _age_hours(lead.get("ts", ""))
        wait = float(ncfg.get("wait_hours", 24))
        if age is not None and age < wait:
            skipped += 1
            continue

        brand = _brand_from_email(email, cfg)
        subject = ncfg.get("subject", "Your creator shortlist — {brand}").format(brand=brand)
        body = _render(brand, p)
        try:
            from .automation import _send_mime
            _send_mime(cfg, user, password, email, subject, body, _html(body))
            state[email] = {"ts": datetime.now(timezone.utc).isoformat(), "brand": brand}
            save_json(ROOT / NURTURE_STATE, state)
            sent += 1
            log(f"  NURTURE -> {email} ({brand})")
        except Exception as exc:
            log(f"  NURTURE FAIL {email}: {exc}")
            skipped += 1

    return {"sent": sent, "skipped": skipped, "hot_leads": len(closing)}


def _render(brand: str, p: dict) -> str:
    return (
        f"Hi {brand} team,\n\n"
        "Thanks for coming back to us — happy to put something concrete together.\n\n"
        "To build you a shortlist I only need three things:\n\n"
        "  1. Your budget range\n"
        "  2. The city or audience you want to reach\n"
        "  3. What the campaign is for (awareness, content, or sales)\n\n"
        "Reply with those three lines and I'll send back matched creators and a\n"
        "transparent quote within a day. Creators keep 90%, there's no retainer\n"
        "and no minimum spend.\n\n"
        f"If a form is easier: {p.get('brand_brief_url', '')}\n\n"
        "Best,\n"
        f"{p.get('company', 'CollabHive')}\n"
        f"{p.get('contact_email', '')} · {p.get('phone', '')}\n"
    )


def _html(text: str) -> str:
    esc = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return ("<div style=\"font-family:Segoe UI,Roboto,Helvetica,Arial,sans-serif;"
            "font-size:15px;line-height:1.6;color:#2d2d2d;white-space:pre-wrap;\">"
            f"{esc}</div>")


# ---------------------------------------------------------------- quote chasing
def chase_quotes(cfg: dict) -> dict:
    """One follow-up on a quote that was actually emailed and went quiet."""
    qcfg = cfg.get("quotes", {})
    ncfg = cfg.get("nurture", {})
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"sent": 0, "skipped": "no_password"}

    quotes = load_json(ROOT / qcfg.get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    replied = {(c.get("email") or "").lower() for c in closing}

    state = load_json(ROOT / QUOTE_CHASE_STATE)
    state = state if isinstance(state, dict) else {}

    after_h = float(ncfg.get("quote_chase_hours", 72))
    user, password = gmail_credentials()
    p = cfg["profile"]
    sent = 0
    skipped = 0

    for q in quotes:
        email = (q.get("email") or "").lower().strip()
        # A quote with no address was only ever a draft — nothing to chase.
        if not email or email in state or q.get("draft"):
            skipped += 1
            continue
        age = _age_hours(q.get("ts", ""))
        if age is None or age < after_h:
            skipped += 1
            continue

        brand = q.get("brand") or _brand_from_email(email, cfg)
        subject = "Re: Your CollabHive campaign proposal — %s" % brand
        body = (
            f"Hi {brand} team,\n\n"
            "Just circling back on the shortlist and quote we sent over.\n\n"
            "Happy to adjust the number of creators or the posts per creator to\n"
            "fit a different budget — the proposal was a starting point, not a\n"
            "fixed package.\n\n"
            "Would a quick call be easier? Either way, no pressure.\n\n"
            "Best,\n"
            f"{p.get('company', 'CollabHive')}\n"
            f"{p.get('contact_email', '')} · {p.get('phone', '')}\n"
        )
        try:
            from .automation import _send_mime
            _send_mime(cfg, user, password, email, subject, body, _html(body))
            state[email] = {"ts": datetime.now(timezone.utc).isoformat()}
            save_json(ROOT / QUOTE_CHASE_STATE, state)
            sent += 1
            log(f"  QUOTE CHASE -> {email} ({brand})")
        except Exception as exc:
            log(f"  QUOTE CHASE FAIL {email}: {exc}")
            skipped += 1

    return {"sent": sent, "skipped": skipped, "quotes": len(quotes),
            "already_replied": len(replied)}


def run_nurture(cfg: dict) -> dict:
    """Entrypoint for `python src/run.py nurture`."""
    cleaned = clean_queue(cfg)
    nurtured = nurture_hot_leads(cfg)
    chased = chase_quotes(cfg)
    return {"cleaned": cleaned, "nurtured": nurtured, "chased": chased}
