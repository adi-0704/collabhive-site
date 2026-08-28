"""CollabHive Outreach — delivery verification.

Checks the Gmail account (via IMAP, using the same app password as sending)
to confirm outreach emails actually landed and to detect bounces / rejections.
This closes the loop so we never assume a send succeeded when it did not.

Checks performed:
  1. SENT CONFIRMATION: count outreach emails found in the Sent folder whose
     recipients match our recorded sends (sent_log in state.json).
  2. TRANSIT: for each recorded send, is there a matching "Sent" message?
  3. BOUNCES: scan the Inbox for Delivery Status Notifications / Mailer-Daemon
     / "Undelivered Mail" and extract the failed addresses.

Outputs a delivery_health dict that the dashboard shows, and writes
outreach/data/delivery_health.json.

To be effective, the Gmail account must have "Sent" + "Inbox" accessible via
IMAP (default). Uses stdlib imaplib only.
"""
from __future__ import annotations

import imaplib
import re
from datetime import datetime, timedelta, timezone

from .common import ROOT, env, load_config, load_json, log, save_json

SUBJECT_HINT = "creator network"  # part of our outreach subject line
DSN_SNIPPET_MARKERS = (
    "delivery status notification", "undelivered mail", "mail delivery subsystem",
    "address not found", "mailbox unavailable", "recipient address rejected",
    "did not reach the following recipient", "could not be delivered", "550",
    "returned mail", "message rejected", "spam", "permanently failed",
)
DSN_SENDER_MARKERS = ("mailer-daemon", "mail delivery subsystem", "postmaster")


def _connect(cfg: dict, user: str, password: str):
    conn = imaplib.IMAP4_SSL(cfg["sales"].get("imap_host", "imap.gmail.com"),
                             cfg["sales"].get("imap_port", 993), timeout=30)
    conn.login(user, password)
    return conn


def _search_ents(conn, mailbox: str, since: datetime):
    """Return a list of (from_email, to_addresses, subject, snippet)."""
    # Gmail folder names with brackets ([Gmail]/Sent Mail) must be quoted.
    quoted = mailbox if mailbox.startswith('"') else '"%s"' % mailbox
    try:
        conn.select(quoted)
    except Exception:
        return []
    since_str = since.strftime("%d-%b-%Y")
    try:
        status, data = conn.search(None, f'(SINCE "{since_str}")')
    except Exception:
        return []
    ids = data[0].split() if data and data[0] else []
    out = []
    import email as email_lib
    from email.header import decode_header, make_header
    for num in ids[-500:]:
        try:
            s, d = conn.fetch(num, "(RFC822)")
            msg = email_lib.message_from_bytes(d[0][1])
            frm = _dec(msg.get("from", ""))
            to = _dec(msg.get("to", ""))
            subj = _dec(msg.get("subject", ""))
            snippet = _body_snippet(msg)
            out.append({"from": frm, "to": to, "subject": subj, "snippet": snippet})
        except Exception:
            continue
    return out


def _dec(v):
    from email.header import decode_header, make_header
    try:
        return str(make_header(decode_header(v or "")))
    except Exception:
        return v or ""


def _body_snippet(msg) -> str:
    body = ""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    body = payload.decode("utf-8", "ignore") if payload else ""
                    break
        else:
            payload = msg.get_payload(decode=True)
            body = payload.decode("utf-8", "ignore") if payload else ""
    except Exception:
        body = ""
    return " ".join(body.split())[:500]


def _emails(text: str) -> list[str]:
    return [e.lower() for e in re.findall(r"[\w.\-+]+@[\w.\-]+\.\w+", text or "")]


def verify_delivery(cfg: dict) -> dict:
    user = cfg["smtp"]["username"]
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        return {"ok": False, "reason": "no_password", "note": "Set OUTREACH_EMAIL_PASS to enable IMAP verification."}

    lookback_hours = cfg.get("verification", {}).get("lookback_hours", 96)
    since = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    # Load recorded sends.
    state_file = ROOT / cfg["brands"]["state_file"]
    state = load_json(state_file)
    state = state if isinstance(state, dict) else {}
    recorded = state.get("sent_log", [])
    recorded_emails = [ (e.get("email") or "").lower() for e in recorded ]
    recorded_emails = [e for e in recorded_emails if e]
    unique_recorded = list(dict.fromkeys(recorded_emails))

    sent_confirmed = []
    sent_unconfirmed = []
    bounces = []

    try:
        conn = _connect(cfg, user, password)
    except Exception as exc:
        log(f"IMAP connect failed for verification: {exc}")
        return {"ok": False, "reason": "imap_fail", "error": str(exc)}

    try:
        # 1) Scan Sent folder for our outreach messages.
        sent_msgs = _search_ents(conn, "[Gmail]/Sent Mail", since)
        sent_to = []
        for m in sent_msgs:
            if SUBJECT_HINT.lower() in m["subject"].lower():
                sent_to.extend(_emails(m["to"]))
                sent_to.extend(_emails(m["snippet"]))
        sent_set = set(sent_to)

        # Classify each recorded send.
        for addr in unique_recorded:
            if addr in sent_set:
                sent_confirmed.append(addr)
            else:
                sent_unconfirmed.append(addr)

        # 2) Scan Inbox for bounces/DSNs.
        inbox_msgs = _search_ents(conn, "INBOX", since)
        for m in inbox_msgs:
            subject = (m["subject"] or "").lower()
            from_lower = (m["from"] or "").lower()
            lookup = subject + " " + (m["snippet"] or "").lower()
            is_dsn = any(mk in from_lower for mk in DSN_SENDER_MARKERS) or \
                     "delivery status" in subject or "undelivered" in subject or \
                     any(mk in lookup for mk in DSN_SNIPPET_MARKERS)
            if is_dsn:
                emails = _emails(m["snippet"])
                bounces.extend({"email": e, "subject": m["subject"], "snippet": m["snippet"][:200]}
                               for e in emails if e and e != user.lower())
    finally:
        try:
            conn.logout()
        except Exception:
            pass

    bounce_emails = list({b["email"] for b in bounces if b["email"]})
    bounced_set = set(bounce_emails)

    # Health metrics.
    total_sends = len(unique_recorded)
    confirmed = len(sent_confirmed)
    deliv_rate = round(confirmed / total_sends * 100, 1) if total_sends else 0.0
    bounced = [a for a in bounced_set if a in set(unique_recorded)]
    missing = [a for a in sent_unconfirmed if a not in bounced_set]

    health = {
        "ok": True,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "lookback_hours": lookback_hours,
        "recorded_sends": total_sends,
        "confirmed_in_sent": confirmed,
        "unconfirmed": len(sent_unconfirmed),
        "delivery_rate_pct": deliv_rate,
        "bounces": len(bounced_set),
        "bounce_emails": bounced[:20],
        "unconfirmed_emails": missing[:20],
        "flagged": (deliv_rate < 60 and total_sends >= 5),
    }
    save_json(ROOT / cfg.get("verification", {}).get("health_file", "data/delivery_health.json"), health)

    # Persist bounced emails into state so they are never re-sent.
    if bounced_set:
        _mark_bounces(state, bounced_set, state_file)
        log(f"Marked {len(bounced_set)} bounced email(s) as do-not-send.")

    log(f"Delivery verity: confirmed={confirmed}/{total_sends}, delivery_rate={deliv_rate}%, "
        f"bounces={len(bounced_set)}, unconfirmed={len(missing)}")
    if health["flagged"]:
        log("WARNING: delivery rate low — possible bounces or send issues. Review before sending more.")
    return health


def _mark_bounces(state: dict, bounced: set, state_file) -> None:
    if not isinstance(state, dict):
        state = {}
    state.setdefault("bounced_emails", [])
    for e in bounced:
        if e not in state["bounced_emails"]:
            state["bounced_emails"].append(e)
    save_json(state_file, state)
