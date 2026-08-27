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
from src.common import ROOT, env, load_config, log, save_json  # noqa: E402


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
        "last_run": state.get("last_run", ""),
    }
    return report


def cmd_enrich(cfg: dict) -> None:
    res = brands_mod.refresh_brand_emails(cfg)
    log(f"Enrich done: {res}")


def cmd_daily(cfg: dict) -> None:
    from datetime import datetime, timezone
    from src import mailer

    state_file = ROOT / cfg["brands"]["state_file"]
    # 1) If enabled, discover new brands from Google Maps (throttled + safe).
    if cfg.get("discovery", {}).get("enabled", False):
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
    elif mode == "all":
        cmd_enrich(cfg)
        cmd_daily(cfg)
        cmd_report(cfg)
    else:
        log(f"Unknown mode: {mode}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
