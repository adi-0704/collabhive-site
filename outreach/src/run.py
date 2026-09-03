"""CollabHive Outreach — daily automation entrypoint.

Modes (run from the outreach/ directory or as a module):
  * daily   -> refresh brand emails, pick today's batch, send emails, write state.
               This is what the scheduled GitHub Action runs.
  * enrich  -> refresh emails for seed brands (web extraction), no sending.
  * report  -> write data/report.json (dashboard data), no sending.

Usage:
  python outreach/src/run.py daily
  python outreach/src/run.py enrich
  python outreach/src/run.py report
  python outreach/src/run.py all          # enrich + daily + report
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import brands as brands_mod  # noqa: E402
from src.common import ROOT, env, load_config, load_json, log, save_json  # noqa: E402

def gather_report(cfg: dict) -> dict:
    """Builds the dashboard report from current state + seed pool."""
    from collections import Counter
    from datetime import datetime, timezone

    state_file = ROOT / cfg["brands"]["state_file"]
    seed_file = ROOT / cfg["brands"]["seed_file"]

    state = {}
    if state_file.exists():
        from src.common import load_json
        _s = load_json(state_file)
        if isinstance(_s, dict):
            state = _s
    pool = brands_mod.load_seed_pool(cfg)
    sent_log = state.get("sent_log", [])

    by_niche = Counter(entry.get("niche", "Other") for entry in sent_log)
    by_city = Counter(entry.get("city", "Other") for entry in sent_log)
    total_sent = len(sent_log)
    unique_emails = len(state.get("emailed_emails", []))
    brands_with_email = sum(1 for b in pool if b.get("email") or b.get("emails"))
    brands_total = len(pool)

    # Per-niche progress: how many in each niche have been emailed.
    pool_by_niche = Counter((b.get("niche") or "Other") for b in pool)

    # Today's sends (last 24h).
    now = datetime.now(timezone.utc)
    recency = []
    for entry in sent_log:
        try:
            ts = datetime.fromisoformat(entry.get("ts", ""))
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            recency.append(ts)
        except (ValueError, TypeError):
            recency.append(None)
    sent_today = sum(1 for ts in recency if ts and (now - ts).total_seconds() <= 86400)
    sent_week = sum(1 for ts in recency if ts and (now - ts).total_seconds() <= 7 * 86400)

    report = {
        "generated_at": now.isoformat(),
        "profile": cfg["profile"],
        "summary": {
            "total_sent": total_sent,
            "unique_brands_emailed": unique_emails,
            "brands_in_pool": brands_total,
            "brands_with_email": brands_with_email,
            "remaining_candidates": max(brands_with_email - unique_emails, 0),
            "sent_today": sent_today,
            "sent_week": sent_week,
            "day_streak": sum(1 for ts in recency if ts and (now - ts).total_seconds() <= 7 * 86400),
            "daily_budget": cfg.get("smtp", {}).get("daily_limit", 18),
        },
        "by_niche": dict(by_niche),
        "by_city": dict(by_city),
        "pool_by_niche": dict(pool_by_niche),
        "recent_sends": sent_log[-20:][::-1],
        "sales": _gather_sales(cfg),
        "verification": _gather_verification(cfg),
        "pipeline_dataset": _gather_pipeline(cfg),
        "onboarding": _gather_onboarding(cfg),
        "publish": _gather_publish(cfg),
        "buffer": _gather_buffer(cfg),
        "dnc_count": _gather_dnc(cfg),
        "last_run": state.get("last_run", ""),
    }
    return report


def _gather_buffer(cfg: dict) -> dict:
    from src.common import load_json
    drafts = load_json(ROOT / cfg["social"]["drafts_file"])
    drafts = drafts if isinstance(drafts, list) else []
    queued = sum(1 for d in drafts if d.get("buffered"))
    needs_media = sum(1 for d in drafts if d.get("buffer_status") == "needs_media")
    return {
        "queued_count": queued,
        "needs_media_count": needs_media,
        "has_drafts": len(drafts),
        "statuses": {s: sum(1 for d in drafts if d.get("buffer_status") == s)
                     for s in set(d.get("buffer_status") for d in drafts if d.get("buffer_status"))},
    }


def _gather_publish(cfg: dict) -> dict:
    from src.common import load_json
    pub = load_json(ROOT / cfg["publish"]["published_file"])
    pub = pub if isinstance(pub, dict) else {}
    drafts = load_json(ROOT / cfg["social"]["drafts_file"])
    drafts = drafts if isinstance(drafts, list) else []
    return {
        "published_count": pub.get("count", 0),
        "creators": pub.get("creators", [])[:20],
        "drafts": [{"handle": d.get("handle"), "name": d.get("name"), "niche": d.get("niche")}
                   for d in drafts],
        "drafts_count": len(drafts),
    }


def _gather_onboarding(cfg: dict) -> dict:
    from src import onboarding as ob_mod
    try:
        funnel = ob_mod.funnel_analytics(cfg)
    except Exception:
        funnel = {}
    try:
        proof = ob_mod.social_proof(cfg)
    except Exception:
        proof = {}
    try:
        refs = ob_mod.referral_stats(cfg)
    except Exception:
        refs = {}
    try:
        cta = ob_mod.cta_winner(cfg)
    except Exception:
        cta = {}
    return {"funnel": funnel, "proof": proof, "referrals": refs, "cta_winner": cta}


def _gather_pipeline(cfg: dict) -> dict:
    from src.common import load_json
    rows = load_json(ROOT / cfg.get("pipeline", {}).get("state_file", "data/pipeline.json"))
    rows = rows if isinstance(rows, list) else []
    counts = {}
    for r in rows:
        s = r.get("stage", "brief")
        counts[s] = counts.get(s, 0) + 1
    return {"counts": counts, "rows": rows[:20]}


def _gather_dnc(cfg: dict) -> int:
    from src.common import load_json
    dnc = load_json(ROOT / cfg.get("dnc", {}).get("state_file", "data/dnc.json"))
    return len(dnc) if isinstance(dnc, list) else 0


def _gather_verification(cfg: dict) -> dict:
    from src.common import load_json
    health = load_json(ROOT / cfg.get("verification", {}).get("health_file", "data/delivery_health.json"))
    return health if isinstance(health, dict) else {}


def _gather_sales(cfg: dict) -> dict:
    """Read closing queue + shortlist for the dashboard."""
    from src.common import load_json
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    short = load_json(ROOT / cfg["sales"]["shortlist_file"])
    short = short if isinstance(short, dict) else {}
    shortlist = short.get("shortlist", []) if isinstance(short, dict) else []
    scored = load_json(ROOT / "data" / "briefs_scored.json")
    scored = scored if isinstance(scored, list) else []
    quotes = load_json(ROOT / cfg.get("quotes", {}).get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    by_status = {}
    for c in closing:
        s = c.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    tier_count = {"hot": 0, "warm": 0, "cold": 0}
    for b in scored:
        tier_count[b.get("tier", "cold")] = tier_count.get(b.get("tier", "cold"), 0) + 1
    return {
        "closing_count": len(closing),
        "closing_by_status": by_status,
        "recent_closing": closing[-10:][::-1],
        "shortlist": [(s.get("brand"), s.get("niche"), [m.get("handle") for m in s.get("matches", [])][:5])
                      for s in shortlist],
        "shortlist_count": len(shortlist),
        "hot_briefs": tier_count.get("hot", 0),
        "briefs_by_tier": tier_count,
        "quotes_sent": len(quotes),
        "recent_quotes": quotes[-8:][::-1],
        "lead_tiers": [(b.get("brand"), b.get("tier"), b.get("priority")) for b in scored[:10]],
        "replied_count": len(closing),
        "reply_rate_pct": _reply_rate(cfg),
    }


def _reply_rate(cfg: dict) -> float:
    """Reply rate = replies / sends (from state), as a percentage."""
    from src.common import load_json
    state = load_json(ROOT / cfg["brands"]["state_file"])
    state = state if isinstance(state, dict) else {}
    sent = len(state.get("emailed_emails", []))
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    replied = len(closing)
    if not sent:
        return 0.0
    return round(replied / sent * 100, 1)


def cmd_enrich(cfg: dict) -> None:
    res = brands_mod.refresh_brand_emails(cfg)
    log(f"Enrich done: {res}")


def cmd_daily(cfg: dict) -> None:
    from datetime import datetime, timezone
    from src import mailer

    state_file = ROOT / cfg["brands"]["state_file"]
    # Allow tests/local to disable Maps discovery via env override.
    discovery_enabled = cfg.get("discovery", {}).get("enabled", False)
    if env("OUTREACH_DISCOVERY", "1") == "0":
        discovery_enabled = False
    # 1) If enabled, discover new brands from Google Maps (throttled + safe).
    if discovery_enabled:
        try:
            from src import maps_scraper
            res = maps_scraper.run_daily_scrape(cfg)
            log(f"Maps scrape: {res}")
        except Exception as exc:
            log(f"Maps scrape step skipped: {exc}")
    # 2) Refresh emails for any seed brand missing one (AFTER scrape so newly
    #    discovered brands can be enriched in the same run).
    try:
        brands_mod.refresh_brand_emails(cfg)
    except Exception as exc:
        log(f"Enrich step skipped: {exc}")

    result = mailer.daily_run(cfg)
    log(f"Daily run result: {result}")

    # Record last_run (guard against non-dict state).
    from src.common import load_json
    loaded = load_json(state_file)
    state = loaded if isinstance(loaded, dict) else {}
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_json(state_file, state)


def cmd_report(cfg: dict) -> None:
    report = gather_report(cfg)
    save_json(ROOT / "data" / "report.json", report)
    log(f"Report written to data/report.json")


def cmd_sales(cfg: dict) -> None:
    """Reply triage + auto-match + shortlist. Purely automatic."""
    from src import sales as sales_mod
    triage = sales_mod.triage_replies(cfg)
    log(f"Reply triage: {triage}")
    matched = sales_mod.match_briefs(cfg)
    log(f"Auto-match: {matched}")


def cmd_seo(cfg: dict) -> None:
    from src import sales as sales_mod
    res = sales_mod.generate_seo(cfg)
    log(f"SEO pages: {res}")


def cmd_verify(cfg: dict) -> None:
    from src import verify as verify_mod
    health = verify_mod.verify_delivery(cfg)
    log(f"Delivery verification: {health}")


def cmd_automation(cfg: dict) -> None:
    """Auto-quotes, follow-ups, digest, scoring, pipeline, DNC, pool health, alerts."""
    from src import automation as auto_mod
    from src import growth as growth_mod
    scored = auto_mod.score_briefs(cfg)
    log(f"Scored briefs: {len(scored)} (hot={sum(1 for b in scored if b.get('tier')=='hot')})")
    dnc = growth_mod.scan_replies_for_dnc(cfg)
    log(f"DNC scan: {dnc}")
    pruned = growth_mod.prune_brand_pool(cfg)
    log(f"Pool prune: {pruned}")
    pipeline = growth_mod.pipeline_status(cfg)
    log(f"Pipeline: {len(pipeline)} brands")
    quotes = auto_mod.send_auto_quotes(cfg)
    log(f"Auto-quotes: {quotes}")
    followups = auto_mod.send_followups(cfg)
    log(f"Follow-ups: {followups}")
    alert = auto_mod.alert_hot_leads(cfg)
    log(f"Hot-lead alert: {alert}")
    digest = auto_mod.send_weekly_digest(cfg)
    log(f"Weekly digest: {digest}")


def cmd_growth(cfg: dict) -> None:
    from src import growth as growth_mod
    sitemap = growth_mod.generate_sitemap(cfg)
    log(f"Sitemap: {sitemap}")
    pruned = growth_mod.prune_brand_pool(cfg)
    log(f"Pool prune: {pruned}")
    pipeline = growth_mod.pipeline_status(cfg)
    log(f"Pipeline: {len(pipeline)} brands")
    ab = growth_mod.ab_winner(cfg)
    log(f"A/B subject winner: {ab}")


def cmd_onboarding(cfg: dict) -> None:
    """Onboarding funnel: analytics, instant value emails, remarketing, proof, referral."""
    from src import onboarding as ob_mod
    seeded = ob_mod.seed_events_from_data(cfg)
    log(f"Seeded events: {seeded}")
    funnel = ob_mod.funnel_analytics(cfg)
    log(f"Funnel: {funnel}")
    instant = ob_mod.instant_value_emails(cfg)
    log(f"Instant value emails: {instant}")
    remarket = ob_mod.remarket_openers(cfg)
    log(f"Remarket: {remarket}")
    proof = ob_mod.social_proof(cfg)
    log(f"Social proof: {proof}")
    stats = ob_mod.referral_stats(cfg)
    log(f"Referrals: {stats}")
    cta = ob_mod.cta_winner(cfg)
    log(f"CTA winner: {cta}")
    # WhatsApp handoff for any recent hot leads (deep-link, or auto-send if token set).
    handoffs = _wa_handoff_hot_leads(cfg)
    log(f"WhatsApp handoffs: {handoffs}")


def cmd_publish(cfg: dict) -> None:
    """Publish approved influencers + draft onboarding social posts."""
    from src import publication as pub_mod
    published = pub_mod.publish_creators(cfg)
    log(f"Publish creators: {published}")
    drafts = pub_mod.draft_social_posts(cfg)
    log(f"Social drafts: {drafts}")
    # Queue new drafts to Buffer (auto-posting) if a key is configured.
    if cfg.get("buffer", {}).get("enabled", True):
        try:
            from src import buffer as buf_mod
            result = buf_mod.queue_drafts(cfg)
            log(f"Buffer queue: {result}")
        except Exception as exc:
            log(f"Buffer step skipped: {exc}")


def _wa_handoff_hot_leads(cfg: dict) -> dict:
    from src import onboarding as ob_mod
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    hot = [c for c in closing if c.get("status") in ("interested", "negotiating")]
    if not hot:
        return {"handoffs": 0}
    n = 0
    for c in hot[:3]:
        ob_mod.whatsapp_handoff(cfg, phone="", brand=c.get("name", ""), kind="hot_lead")
        n += 1
    return {"handoffs": n, "note": "Deep-links enabled for hot leads; set onboarding.whatsapp.token to auto-send"}


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    mode = argv[0] if argv else "daily"
    cfg = load_config()
    if mode == "daily":
        cmd_daily(cfg)
    elif mode == "enrich":
        cmd_enrich(cfg)
    elif mode == "report":
        cmd_report(cfg)
    elif mode == "sales":
        cmd_sales(cfg)
    elif mode == "seo":
        cmd_seo(cfg)
    elif mode == "verify":
        cmd_verify(cfg)
    elif mode == "automation":
        cmd_automation(cfg)
    elif mode == "growth":
        cmd_growth(cfg)
    elif mode == "onboarding":
        cmd_onboarding(cfg)
    elif mode == "publish":
        cmd_publish(cfg)
    elif mode == "buffer":
        from src import buffer as buf_mod
        result = buf_mod.queue_drafts(cfg)
        log(f"Buffer queue: {result}")
    elif mode == "record":
        # Record a funnel event: python src/run.py record <kind> [email] [referrer]
        from src import onboarding as ob_mod
        kind = argv[1] if len(argv) > 1 else "form_view"
        email = argv[2] if len(argv) > 2 else ""
        ref = argv[3] if len(argv) > 3 else ""
        res = ob_mod.record_event(cfg, kind, email, ref)
        log(f"Event recorded: {res}")
    elif mode == "all":
        cmd_enrich(cfg)
        cmd_daily(cfg)
        cmd_sales(cfg)
        cmd_automation(cfg)
        cmd_growth(cfg)
        cmd_onboarding(cfg)
        cmd_publish(cfg)
        cmd_seo(cfg)
        cmd_verify(cfg)
        cmd_report(cfg)
    else:
        log(f"Unknown mode: {mode}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
