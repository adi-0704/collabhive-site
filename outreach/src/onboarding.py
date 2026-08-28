"""CollabHive Outreach — onboarding & funnel module.

Fully automatic (no human input). Boosts application conversion for BOTH
influencers and brands:
  * record_event                 -> funnel events (form_view / submit / approve / brief)
  * funnel_analytics             -> derive funnel + drop-off rates per stage
  * instant_value_emails         -> right after a creator/brand submits, email them
                                   something valuable (profile link / quote preview)
  * remarket_openers             -> nudge anyone who opened the form but never submitted
  * social_proof                 -> counts for "creators joined", "campaigns ran", etc.
  * referral_stats / track_referral -> share-link referral attribution

Stdlib only. Persists to outreach/data/.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from .common import ROOT, env, gmail_credentials, load_config, load_json, log, save_json

from . import sales as sales_mod


# ---------- events ----------
def _events_file(cfg):
    return ROOT / cfg["onboarding"]["events_file"]


def record_event(cfg: dict, kind: str, email: str = "", referrer: str = "",
                 source: str = "site", extra: dict | None = None) -> dict:
    """Append a funnel event. kind in form_view|submit|approve|brief|quote_sent."""
    path = _events_file(cfg)
    events = load_json(path)
    events = events if isinstance(events, list) else []
    events.append({
        "kind": kind,
        "email": (email or "").lower(),
        "referrer": (referrer or "").lower(),
        "source": source,
        "ts": datetime.now(timezone.utc).isoformat(),
        **(extra or {}),
    })
    if isinstance(events, list):
        save_json(path, events[-4000:])
    return {"recorded": 1, "kind": kind, "total": len(events) if isinstance(events, list) else 0}


def seed_events_from_data(cfg: dict) -> dict:
    """Derive funnel events from existing pools so analytics isn't empty.

    Creators in the pool -> creator_registered; briefs (incl. the brand form
    sheet) -> brand_submit/brief. Idempotent: only adds kinds/emails not seen.
    """
    path = _events_file(cfg)
    events = load_json(path)
    events = events if isinstance(events, list) else []
    seen = set()
    for e in events:
        seen.add("%s:%s" % (e.get("kind"), (e.get("email") or "").lower()))

    added = 0
    # Creators -> creator_registered
    for c in sales_mod.load_creators(cfg):
        key = "creator_registered:%s" % (c.get("email") or "").lower()
        if key not in seen:
            events.append({"kind": "creator_registered", "email": (c.get("email") or "").lower(),
                           "referrer": "", "source": "seed", "ts": datetime.now(timezone.utc).isoformat()})
            seen.add(key); added += 1
    # Briefs -> brand_submit
    for b in sales_mod.load_briefs(cfg):
        key = "brand_submit:%s" % (b.get("email") or "").lower()
        if key not in seen:
            events.append({"kind": "brand_submit", "email": (b.get("email") or "").lower(),
                           "referrer": "", "source": "seed", "ts": datetime.now(timezone.utc).isoformat()})
            seen.add(key); added += 1
    if added:
        save_json(path, events[-4000:])
    return {"added": added, "total": len(events)}


def load_events(cfg: dict) -> list[dict]:
    events = load_json(_events_file(cfg))
    return events if isinstance(events, list) else []


# ---------- funnel analytics ----------
def funnel_analytics(cfg: dict) -> dict:
    events = load_events(cfg)
    by_kind = {}
    for e in events:
        by_kind[e.get("kind", "?")] = by_kind.get(e.get("kind", "?"), 0) + 1

    form_views = by_kind.get("form_view", 0)
    creator_subs = by_kind.get("creator_submit", 0)
    brand_subs = by_kind.get("brand_submit", 0)
    approves = by_kind.get("approve", 0)
    briefs = by_kind.get("brief", 0)
    quotes = by_kind.get("quote_sent", 0)

    def rate(num, den):
        return round(num / den * 100, 1) if den else 0.0

    creator_count = by_kind.get("creator_registered", 0) or creator_subs
    brand_count = by_kind.get("brand_registered", 0) or brand_subs

    return {
        "form_views": form_views,
        "creator_submissions": creator_subs,
        "brand_submissions": brand_subs,
        "creators_approved": approves,
        "brand_briefs": briefs,
        "quotes_sent": quotes,
        "creator_conversion_pct": rate(creator_subs, form_views) if form_views else 0.0,
        "brand_conversion_pct": rate(brand_subs, form_views) if form_views else 0.0,
        "approve_rate_pct": rate(approves, creator_subs) if creator_subs else 0.0,
        "brief_rate_pct": rate(briefs, brand_subs) if brand_subs else 0.0,
        "events_last_24h": sum(1 for e in events if _age_hours(e.get("ts", "")) <= 24),
    }


def _age_hours(ts: str) -> float:
    try:
        t = datetime.fromisoformat(ts)
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 3600
    except (ValueError, TypeError):
        return 1e9


# ---------- instant value emails ----------
def instant_value_emails(cfg: dict) -> dict:
    ob = cfg.get("onboarding", {})
    if not ob.get("instant_email_on_signup", True):
        return {"sent": 0, "skipped": "disabled"}
    from .verify import _emails  # noqa: F401
    from . import automation as auto_mod

    # Look at recent submissions we haven't yet welcomed.
    events = load_events(cfg)
    sent_file = ROOT / "data" / "instant_sent.json"
    sent = load_json(sent_file)
    sent = sent if isinstance(sent, list) else []
    sent_keys = set(sent)

    user, password = gmail_credentials()
    if not password:
        return {"sent": 0, "skipped": "no_password"}

    sent_count = 0
    for e in events:
        kind = e.get("kind")
        email = (e.get("email") or "").lower()
        if not email:
            continue
        key = "%s:%s" % (kind, email)
        if key in sent_keys:
            continue
        if kind == "creator_submit":
            subject = "CollabHive — your creator profile is ready"
            body = ("Hi!\n\nGreat news — you're on the CollabHive creator network. "
                    "Your profile card is live and brands can now discover you.\n\n"
                    "Book your profile link: %s\n\n"
                    "Tip: keep your best posts pinned to get matched faster.\n\n- CollabHive Team" % cfg["profile"]["site_url"])
            ok = _safe_send(cfg, user, password, email, subject, body)
        elif kind == "brand_submit":
            subject = "CollabHive — we're matching creators for you"
            body = ("Hi!\n\nThanks for your brief. Here's a sample of what a campaign "
                    "quote looks like so you know what to expect.\n\n"
                    "Budget estimate: from ₹{budget:,} total (creators keep 90%, "
                    "10% commission).\n\n"
                    "Our team will send your exact shortlist + quote shortly. "
                    "Just hit reply to speed it up.\n\n- CollabHive Team").format(budget=ob.get("quote_preview_min_budget", 10000))
            ok = _safe_send(cfg, user, password, email, subject, body)
        else:
            continue
        if ok:
            sent.append(key)
            save_json(sent_file, sent)
            sent_count += 1
            log(f"  INSTANT -> {email} [{kind}]")
    return {"sent": sent_count}


def _safe_send(cfg, user, password, to, subject, body):
    try:
        auto_mod._send_mime(cfg, user, password, to, subject, body, body)
        return True
    except Exception as exc:
        log(f"  instant send fail {to}: {exc}")
        return False


# ---------- remarketing ----------
def remarket_openers(cfg: dict) -> dict:
    ob = cfg.get("onboarding", {})
    from .verify import _emails  # noqa: F401

    events = load_events(cfg)
    # People who VIEWED the form but never submitted.
    viewed = {}
    for e in events:
        email = (e.get("email") or "").lower()
        if not email:
            continue
        if e.get("kind") == "form_view":
            viewed[email] = e
        else:
            viewed.pop(email, None)  # submitted -> don't remarket

    # Only those who haven't submitted anything and wait long enough.
    remarket_file = ROOT / ob.get("remarket_file", "data/remarket.json")
    done = load_json(remarket_file)
    done = done if isinstance(done, list) else []
    done_set = set(done)

    after_hours = ob.get("remarket_after_hours", 24)
    once = ob.get("remarket_once_per_email", True)
    user, password = gmail_credentials()
    if not password:
        return {"sent": 0, "skipped": "no_password"}

    sent_count = 0
    for email, e in viewed.items():
        if email in done_set and once:
            continue
        if _age_hours(e.get("ts", "")) < after_hours:
            continue
        subject = "CollabHive — one quick step to finish"
        body = ("Hi!\n\nYou started joining CollabHive but didn't finish. It only "
                "takes 2 minutes and there are no fees.\n\nApply now: %s\n\n- "
                "CollabHive Team" % cfg["profile"]["apply_url"])
        if _safe_send(cfg, user, password, email, subject, body):
            done.append(email)
            save_json(remarket_file, done)
            done_set.add(email)
            sent_count += 1
            log(f"  REMARKET -> {email}")
    return {"sent": sent_count, "candidates": len(viewed)}


# ---------- social proof ----------
def social_proof(cfg: dict) -> dict:
    events = load_events(cfg)
    by_kind = {}
    for e in events:
        by_kind[e.get("kind", "?")] = by_kind.get(e.get("kind", "?"), 0) + 1
    ttl = cfg.get("onboarding", {}).get("social_proof_ttl_hours", 120)
    # "Active creators" = creator_submit in the window.
    ttl_cut = datetime.now(timezone.utc) - timedelta(hours=ttl)
    creators_recent = 0
    campaigns_recent = 0
    for e in events:
        try:
            t = datetime.fromisoformat(e.get("ts", ""))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            if t < ttl_cut:
                continue
        except (ValueError, TypeError):
            continue
        if e.get("kind") in ("creator_submit", "approve"):
            creators_recent += 1
        if e.get("kind") in ("brief", "quote_sent"):
            campaigns_recent += 1
    proof = {
        "creators_joined": creators_recent,
        "campaigns_run": campaigns_recent,
        "alltime_creators": by_kind.get("creator_submit", 0) + by_kind.get("creator_registered", 0),
        "alltime_briefs": by_kind.get("brief", 0) + by_kind.get("brand_submit", 0),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    save_json(ROOT / "data" / "social_proof.json", proof)
    return proof


# ---------- referrals ----------
def track_referral(cfg: dict, handle_or_email: str) -> dict:
    ref_file = ROOT / cfg["onboarding"]["referral_file"]
    refs = load_json(ref_file)
    refs = refs if isinstance(refs, list) else []
    refs.append({"creator": (handle_or_email or "").lower(),
                 "ts": datetime.now(timezone.utc).isoformat()})
    save_json(ref_file, refs)
    return {"tracked": 1, "total": len(refs)}


def referral_stats(cfg: dict) -> dict:
    ref_file = ROOT / cfg["onboarding"]["referral_file"]
    refs = load_json(ref_file)
    refs = refs if isinstance(refs, list) else []
    by_creator = {}
    for r in refs:
        c = r.get("creator", "?")
        by_creator[c] = by_creator.get(c, 0) + 1
    top = sorted(by_creator.items(), key=lambda kv: kv[1], reverse=True)[:10]
    return {"total_referrals": len(refs), "creators_referring": len(by_creator),
            "top": [{"creator": k, "signups": v} for k, v in top]}


# ---------- A/B landing CTA ----------
def assign_cta_variant(cfg: dict, visitor_key: str = "") -> dict:
    """Deterministically assign a CTA label to a visitor (hash of key + day)."""
    ab = cfg["onboarding"].get("ab_cta", {})
    variants = ab.get("variants", ["Start a Campaign", "Get a Free Quote"])
    if not variants:
        return {"variant": ""}
    seed = sum(ord(c) for c in (visitor_key or "")) + int(datetime.now().strftime("%d"))
    return {"variant": variants[seed % len(variants)], "variants": variants}


def record_cta_click(cfg: dict, variant: str, referrer: str = "") -> dict:
    """Record a CTA click -> submit pair so we can score conversion per variant."""
    ab = cfg["onboarding"].get("ab_cta", {})
    record_on = ab.get("record_on", "cta_click")
    kind = "cta_click"
    res = record_event(cfg, kind, "", referrer=referrer, extra={"variant": variant})
    return res


def cta_winner(cfg: dict) -> dict:
    """Score each CTA variant: clicks vs resulting submissions (conversion)."""
    events = load_events(cfg)
    by_variant = {}
    for e in events:
        v = (e.get("extra") or {}).get("variant") or e.get("variant")
        if not v:
            continue
        d = by_variant.setdefault(v, {"clicks": 0, "submits": 0})
        if e.get("kind") == "cta_click":
            d["clicks"] += 1
        elif e.get("kind") in ("creator_submit", "brand_submit", "brief"):
            d["submits"] += 1
    rows = []
    for v, d in by_variant.items():
        conv = round(d["submits"] / d["clicks"] * 100, 1) if d["clicks"] else 0.0
        rows.append({"variant": v, "clicks": d["clicks"], "submits": d["submits"], "conversion_pct": conv})
    rows.sort(key=lambda r: r["conversion_pct"], reverse=True)
    winner = rows[0]["variant"] if rows and rows[0]["clicks"] > 0 else ""
    cfg_ab = cfg["onboarding"].get("ab_cta", {})
    save_json(ROOT / cfg_ab.get("winner_file", "data/cta_winner.json"),
              {"winner": winner, "rows": rows, "generated_at": datetime.now(timezone.utc).isoformat()})
    return {"winner": winner, "rows": rows}


# ---------- WhatsApp handoff ----------
def whatsapp_handoff(cfg: dict, phone: str = "", brand: str = "", kind: str = "brief") -> dict:
    """Respond to a brief/hot-lead on WhatsApp.

    Returns a wa.me deep link (works now). If a Meta Cloud API token is set,
    it attempts to AUTO-SEND the message too; otherwise the deep link is the
    handoff (brand taps -> pre-filled message opens, you take it from there).
    """
    wa = cfg["onboarding"].get("whatsapp", {})
    if not wa.get("enabled", True):
        return {"handoff": "disabled"}
    link_num = wa.get("link_number", "918178022572")
    if kind == "hot_lead":
        text = ("Thanks for your interest in CollabHive! We've noted your interest. "
                "Let's lock in your campaign: reply with your preferred creators and "
                "timeline, and we'll send a quote right away.")
    else:
        text = ("Thanks for submitting your CollabHive brief! We're matching your "
                "campaign to creators now. Reply here with your WhatsApp number and "
                "we'll send the shortlist + quote.")
    url = "https://wa.me/%s?text=%s" % (link_num, _urlencode(text))

    sent = None
    if wa.get("token") and wa.get("auto_send"):
        sent = _wa_auto_send(cfg, wa, phone, text)
    return {"deep_link": url, "message": text, "auto_sent": sent}


def _urlencode(text: str) -> str:
    import urllib.parse
    return urllib.parse.quote(text)


def _wa_auto_send(cfg, wa, phone, text):
    """Send via Meta Cloud API if configured. Requires phone_id + token (human setup)."""
    import urllib.request
    import json as _json
    if not phone or not wa.get("token") or not wa.get("phone_id"):
        return None
    url = "https://graph.facebook.com/v19.0/%s/messages" % wa["phone_id"]
    payload = _json.dumps({
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template" if wa.get("template") else "text",
        "text": {"body": text},
    }).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": "Bearer %s" % wa["token"],
        "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as exc:
        log(f"WA auto-send failed: {exc}")
        return False
