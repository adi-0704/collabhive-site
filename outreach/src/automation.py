"""CollabHive Outreach — sales-closing & digest automations.

Fully automatic (no human input):
  * send_auto_quotes -> for each matched brief with a known contact, email the
                        brand a shortlist + quote (sum of creator rates + commission).
  * send_weekly_digest -> email the owner a recap of sends/sales/reach metrics.
  * score_briefs -> enrich briefs with a priority score (budget, intent, recency)
                    so hot leads surface first.

Uses the same Gmail SMTP + template pattern as mailer. Stdlib only.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .common import ROOT, env, gmail_credentials, load_config, load_json, log, save_json

from . import sales as sales_mod
from .mailer import warmup_delay


# ---------- helpers ----------
def _render_tpl(path_name: str, ctx: dict, subject_tpl: str = "") -> tuple[str, str, str]:
    from pathlib import Path
    tdir = ROOT / "templates"
    subject = (subject_tpl or "Your CollabHive proposal").format(**ctx)
    txt_file = tdir / f"{path_name}.txt"
    html_file = tdir / f"{path_name}.html"
    txt = txt_file.read_text(encoding="utf-8") if txt_file.exists() else ""
    html = html_file.read_text(encoding="utf-8") if html_file.exists() else txt
    try:
        body_txt = txt.format(**ctx)
    except (KeyError, IndexError, ValueError):
        body_txt = txt
    try:
        body_html = html.format(**ctx)
    except (KeyError, IndexError, ValueError):
        body_html = html
    return subject, body_txt, body_html


def _creator_lines(creators: list[dict], html: bool) -> str:
    if html:
        return "".join(
            f"<p style='margin:4px 0;font-size:13px;'>{_e(c.get('name'))} "
            f"({_e(c.get('handle'))}) &middot; {_e(c.get('niche'))} &middot; "
            f"{c.get('followers') or 0:,} followers &middot; ₹{c.get('rate') or 0:,}</p>"
            for c in creators
        )
    return "\n".join(
        f"  • {c.get('name')} ({c.get('handle')}) — {c.get('niche')}, "
        f"{c.get('followers') or 0} followers, ₹{c.get('rate') or 0}/post"
        for c in creators
    )


def _e(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- auto-quote emails ----------
def send_auto_quotes(cfg: dict) -> dict:
    qcfg = cfg.get("quotes", {})
    if not qcfg.get("enabled", True):
        return {"quoted": 0, "skipped": "disabled"}
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"quoted": 0, "skipped": "no_password"}

    import smtplib
    import ssl

    from .verify import _emails  # reuse email extraction

    # Shortlist from matching.
    short_file = ROOT / cfg["sales"]["shortlist_file"]
    short = load_json(short_file)
    short = short if isinstance(short, dict) else {}
    shortlist = short.get("shortlist", []) if isinstance(short, dict) else []

    # Already-sent quotes (dedupe).
    sent_file = ROOT / qcfg.get("created_file", "data/quotes_sent.json")
    sent = load_json(sent_file)
    sent = sent if isinstance(sent, list) else []
    sent_keys = {(s.get("brand") or "").lower(): s for s in sent}

    briefs = sales_mod.load_briefs(cfg)
    creators = sales_mod.load_creators(cfg)
    by_brand = {}  # brand -> list of matched creator objects
    for item in shortlist:
        by_brand[(item.get("brand") or "").lower()] = item.get("matches", [])

    default_posts = qcfg.get("default_posts", 2)
    commission_pct = cfg["sales"].get("commission_pct", 10)
    p = cfg["profile"]
    user, password = gmail_credentials()
    if not password:
        return {"quoted": 0, "skipped": "no_password"}

    quoted = []
    skipped = 0
    for brief in briefs:
        brand_key = (brief.get("brand") or "").lower()
        if not brand_key:
            skipped += 1
            continue
        if brand_key in sent_keys:
            continue
        contact_email = (brief.get("email") or "").strip()
        # Matched creators -> resolve full objects.
        matches = by_brand.get(brand_key, [])
        if not matches:
            skipped += 1
            continue
        matched_objs = []
        for mt in matches:
            handle = (mt.get("handle") or "").lower()
            src = next((c for c in creators if (c.get("handle") or "").lower() == handle), None)
            matched_objs.append(mt if not src else {**src, "handle": src.get("handle") or mt.get("handle")})
        if not matched_objs:
            skipped += 1
            continue
        # Quote math.
        posts = _to_int(brief.get("posts")) or default_posts
        payout = sum(_to_int(c.get("rate")) for c in matched_objs)
        commission = round(payout * commission_pct / 100, 2)
        total = round(payout + commission, 2)

        ctx = {
            "name": (brief.get("contact") or brief.get("brand") or "there"),
            "brand": brief.get("brand", ""),
            "goal": brief.get("goal", ""),
            "niche": brief.get("niche", ""),
            "city": brief.get("city", ""),
            "budget": brief.get("budget", ""),
            "n": len(matched_objs),
            "creator_list": _creator_lines(matched_objs, False),
            "creator_list_html": _creator_lines(matched_objs, True),
            "payout": "{:,}".format(payout),
            "commission": "{:,}".format(commission),
            "pct": commission_pct,
            "total": "{:,}".format(total),
            "contact_email": p["contact_email"],
            "phone": p["phone"],
        }
        subj_tpl = "Your CollabHive campaign proposal — {brand}"

        if qcfg.get("send_email", True) and contact_email:
            try:
                subject, body_txt, body_html = _render_tpl("quote", ctx, subj_tpl)
                _send_mime(cfg, user, password, contact_email, subject, body_txt, body_html)
                quoted.append({"brand": brief.get("brand"), "email": contact_email,
                               "total": total, "ts": datetime.now(timezone.utc).isoformat()})
                log(f"  QUOTE SENT -> {contact_email} ({brief.get('brand')}) ₹{total}")
            except Exception as exc:
                log(f"  QUOTE FAIL {contact_email}: {exc}")
                skipped += 1
        else:
            quoted.append({"brand": brief.get("brand"), "email": contact_email, "total": total,
                           "ts": datetime.now(timezone.utc).isoformat(), "draft": True})
            log(f"  QUOTE DRAFT (no email) -> {brief.get('brand')} ₹{total}")

        # Mark as processed even if no contact (avoid re-processing).
        sent.append({"brand": brief.get("brand"), "email": contact_email,
                     "total": total, "ts": datetime.now(timezone.utc).isoformat(),
                     "status": "sent" if contact_email else "no_contact"})

    save_json(sent_file, sent)
    return {"shortlisted": len(shortlist), "quoted": len(quoted), "skipped": skipped}


def _send_mime(cfg, user, password, to, subject, body_txt, body_html):
    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    smtp_cfg = cfg["smtp"]
    from_addr = smtp_cfg["username"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_cfg['from_name']} <{from_addr}>"
    msg["To"] = to
    msg.attach(MIMEText(body_txt, "plain", _charset="utf-8"))
    msg.attach(MIMEText(body_html, "html", _charset="utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP(smtp_cfg["host"], smtp_cfg["port"], timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ctx)
        smtp.ehlo()
        smtp.login(user, password)
        smtp.sendmail(from_addr, [to], msg.as_string())


# ---------- lead scoring ----------
def score_briefs(cfg: dict) -> list[dict]:
    """Annotate briefs with a priority score. Returns sorted list."""
    briefs = sales_mod.load_briefs(cfg)
    scored = []
    for b in briefs:
        budget = _to_int(b.get("budget"))
        s = 0.0
        if budget:
            s += min(1.0, budget / 50000) * 0.4
        goal = (b.get("goal") or "").lower()
        if any(k in goal for k in ("sell", "convert", "launch", "sales", "footfall")):
            s += 0.3
        if (b.get("email") or "").strip():
            s += 0.2
        if (b.get("contact") or "").strip():
            s += 0.1
        b = dict(b)
        b["priority"] = round(s, 3)
        b["tier"] = "hot" if s >= 0.6 else ("warm" if s >= 0.4 else "cold")
        scored.append(b)
    scored.sort(key=lambda x: x["priority"], reverse=True)
    save_json(ROOT / "data" / "briefs_scored.json", scored)
    return scored


def _to_int(v):
    import re
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = re.sub(r"[^\d]", "", str(v))
    return int(s) if s else 0


# ---------- follow-up sequence ----------
def send_followups(cfg: dict) -> dict:
    """Send polite follow-ups to brands we contacted but haven't replied to.

    Logic:
      * only follow up emails that were SENT >= enabled_after_days ago
      * max_followups per brand
      * wait_between_days between each follow-up
      * optionally skip brands that replied (only_if_no_reply -> check closing queue)
    """
    fcfg = cfg.get("followup", {})
    if not fcfg.get("enabled", True):
        return {"sent": 0, "skipped": "disabled"}
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"sent": 0, "skipped": "no_password"}

    state_file = ROOT / cfg["brands"]["state_file"]
    state = load_json(state_file)
    state = state if isinstance(state, dict) else {}
    sent_log = state.get("sent_log", [])

    # Do not follow up brands that replied (closing queue) if configured.
    replied = set()
    if fcfg.get("only_if_no_reply", True):
        closing = load_json(ROOT / cfg["sales"]["closing_file"])
        closing = closing if isinstance(closing, list) else []
        replied = {c.get("email", "").lower() for c in closing if c.get("email")}

    # Track per-email follow-up count + last sent time.
    fu_file = ROOT / fcfg.get("state_file", "data/followups.json")
    fu_state = load_json(fu_file)
    fu_state = fu_state if isinstance(fu_state, dict) else {}

    # Skip anyone on the Do-Not-Contact registry.
    from .growth import dnc_set
    dnc = dnc_set(cfg)

    now = datetime.now(timezone.utc)
    after_days = fcfg.get("enabled_after_days", 3)
    max_fu = fcfg.get("max_followups", 2)
    wait_days = fcfg.get("wait_between_days", 4)
    company = cfg["profile"]["company"]
    contact_email = cfg["profile"]["contact_email"]
    phone = cfg["profile"]["phone"]
    site_url = cfg["profile"]["site_url"]

    sent = 0
    skipped = 0
    for entry in sent_log:
        email = (entry.get("email") or "").lower()
        if not email or email in replied:
            continue
        if email in dnc:
            continue
        try:
            ts = datetime.fromisoformat(entry.get("ts", ""))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            ts = None
        if ts is None:
            continue

        fu = fu_state.get(email, {})
        count = fu.get("count", 0)
        last_ts = _parse_ts(fu.get("last_sent", ""))

        # Eligibility: enough time since the ORIGINAL send, and within follow-up limit.
        days_since = (now - ts).total_seconds() / 86400 if ts else 0
        if days_since < after_days:
            skipped += 1
            continue
        if count >= max_fu:
            continue

        # Space out follow-ups.
        if last_ts:
            days_since_last = (now - last_ts).total_seconds() / 86400
            if days_since_last < wait_days:
                skipped += 1
                continue

        name = entry.get("name") or "there"
        brand = name
        ctx = {
            "name": name.split()[0] if name else "there",
            "brand": brand,
            "company": company,
            "site_url": site_url,
            "contact_email": contact_email,
            "phone": phone,
        }
        subj_tpl = fcfg.get("subject_prefix", "Re: ") + "A creator network for {brand}"
        try:
            subject, body_txt, body_html = _render_tpl("followup", ctx, subj_tpl)
            _send_mime(cfg, cfg["smtp"]["username"], password, email, subject, body_txt, body_html)
            fu_state[email] = {"count": count + 1, "last_sent": now.isoformat(), "name": name}
            save_json(fu_file, fu_state)
            sent += 1
            log(f"  FOLLOWUP {count + 1} -> {email} ({name})")
        except Exception as exc:
            log(f"  FOLLOWUP FAIL {email}: {exc}")
            skipped += 1

    return {"sent": sent, "skipped": skipped, "replied_skipped": len(replied)}


def _parse_ts(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


# ---------- hot-lead alert ----------
def alert_hot_leads(cfg: dict) -> dict:
    """Email the owner when a hot lead (interested/negotiating) lands, throttled."""
    acfg = cfg.get("alerts", {})
    if not acfg.get("enabled", True) or not acfg.get("on_hot_lead", True):
        return {"alerted": 0, "skipped": "disabled"}
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"alerted": 0, "skipped": "no_password"}
    to = acfg.get("to_email", cfg["profile"]["contact_email"])

    # Throttle: only alert once per cooldown window.
    last_file = ROOT / acfg.get("last_sent_file", "data/alert_last.json")
    last = load_json(last_file)
    last = last if isinstance(last, dict) else {}
    cooldown = acfg.get("cooldown_minutes", 120)
    if last.get("ts"):
        try:
            prev = datetime.fromisoformat(last["ts"])
            if (datetime.now(timezone.utc) - prev).total_seconds() < cooldown * 60:
                return {"alerted": 0, "skipped": "cooldown"}
        except (ValueError, TypeError):
            pass

    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    hot = [c for c in closing if c.get("status") in ("interested", "negotiating")]
    # Only new ones since the last alert.
    if last.get("seen") and isinstance(last["seen"], list):
        seen = set(last["seen"])
        hot = [c for c in hot if (c.get("email") or "").lower() not in seen]
    if not hot:
        return {"alerted": 0, "skipped": "no_new_hot"}

    lines = ["You have %d hot lead(s) ready to close:" % len(hot), ""]
    for c in hot:
        lines.append("• %s — [%s] — %s" % (c.get("email"), c.get("status"), (c.get("snippet") or "")[:120]))
    body = "\n".join(lines)
    subject = "CollabHive: %d hot lead(s) ready" % len(hot)
    try:
        _send_mime(cfg, cfg["smtp"]["username"], password, to, subject, body, body)
        save_json(last_file, {"ts": datetime.now(timezone.utc).isoformat(),
                              "seen": [c.get("email") for c in closing]})
        log(f"Hot-lead alert sent to {to} ({len(hot)} leads)")
        return {"alerted": len(hot), "to": to}
    except Exception as exc:
        log(f"Alert FAIL: {exc}")
        return {"alerted": 0, "error": str(exc)}


# ---------- weekly digest ----------
def send_weekly_digest(cfg: dict) -> dict:
    dcfg = cfg.get("digest", {})
    if not dcfg.get("enabled", True):
        return {"sent": 0, "skipped": "disabled"}
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"sent": 0, "skipped": "no_password"}
    to = dcfg.get("to_email", cfg["profile"]["contact_email"])

    # Only send once per 7 days.
    last_file = ROOT / dcfg.get("last_sent_file", "data/digest_last.json")
    last = load_json(last_file)
    if isinstance(last, dict) and last.get("ts"):
        try:
            prev = datetime.fromisoformat(last["ts"])
            age_h = (datetime.now(timezone.utc) - prev).total_seconds() / 3600
            if age_h < (24 * 7):
                return {"sent": 0, "skipped": "recent"}
        except (ValueError, TypeError):
            pass

    rep = _build_digest_metrics(cfg)
    ctx = {
        "date": datetime.now().strftime("%d %b %Y"),
        "owner": "Team",
        "days": dcfg.get("days", 7),
        "sent_total": rep["sent_total"],
        "delivery_rate": rep["delivery_rate"],
        "bounces": rep["bounces"],
        "unique_brands": rep["unique_brands"],
        "closing": rep["closing"],
        "interested": rep["interested"],
        "negotiating": rep["negotiating"],
        "declined": rep["declined"],
        "matched_briefs": rep["matched_briefs"],
        "quotes_sent": rep["quotes_sent"],
        "creator_pool": rep["creator_pool"],
        "seo_pages": rep["seo_pages"],
        "actions": rep["actions"],
    }
    from .common import gmail_credentials as gc
    user, password = gc()
    try:
        # Digest is a plain-text only email (no HTML template exists).
        from pathlib import Path
        tdir = ROOT / "templates"
        txt = (tdir / "digest.txt").read_text(encoding="utf-8")
        body_txt = txt.format(**ctx)
        subject_tpl = "CollabHive Weekly Report — {date}"
        try:
            subject = subject_tpl.format(**ctx)
        except (KeyError, IndexError, ValueError):
            subject = subject_tpl
        _send_mime(cfg, user, password, to, subject, body_txt, body_txt)
        save_json(last_file, {"ts": datetime.now(timezone.utc).isoformat(), "to": to})
        log(f"Digest sent to {to}")
        return {"sent": 1, "to": to}
    except Exception as exc:
        log(f"Digest FAIL: {exc}")
        return {"sent": 0, "error": str(exc)}


def _build_digest_metrics(cfg: dict) -> dict:
    from .verify import verify_delivery  # noqa: F401
    state_file = ROOT / cfg["brands"]["state_file"]
    state = load_json(state_file)
    state = state if isinstance(state, dict) else {}
    sent_log = state.get("sent_log", [])
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    by_status = {}
    for c in closing:
        s = c.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    short = load_json(ROOT / cfg["sales"]["shortlist_file"])
    short = short if isinstance(short, dict) else {}
    shortlist = short.get("shortlist", []) if isinstance(short, dict) else []
    quotes = load_json(ROOT / cfg.get("quotes", {}).get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    seed = load_json(ROOT / cfg["sales"]["creator_pool_file"])
    seed = seed if isinstance(seed, list) else []
    health = load_json(ROOT / cfg.get("verification", {}).get("health_file", "data/delivery_health.json"))
    health = health if isinstance(health, dict) else {}
    seo = ROOT / cfg.get("seo", {}).get("output_dir", "../seo-pages")
    seo_pages = len(list(seo.glob("*.html"))) if seo.exists() else 0

    actions = "✅ All systems running. Keep sending daily and close hot leads."
    if health.get("flagged"):
        actions = "⚠ Delivery rate is low — review bounces before sending more."

    return {
        "sent_total": len(sent_log),
        "delivery_rate": health.get("delivery_rate_pct", 0),
        "bounces": health.get("bounces", 0),
        "unique_brands": len(state.get("emailed_emails", [])),
        "closing": len(closing),
        "interested": by_status.get("interested", 0),
        "negotiating": by_status.get("negotiating", 0),
        "declined": by_status.get("declined", 0),
        "matched_briefs": len(shortlist),
        "quotes_sent": len(quotes),
        "creator_pool": len(seed),
        "seo_pages": seo_pages,
        "actions": actions,
    }
