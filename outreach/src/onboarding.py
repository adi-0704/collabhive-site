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
