"""CollabHive — schedule the entire calendar into Buffer in one go.

    python social/schedule_all.py --dry-run          # show the plan
    python social/schedule_all.py                    # schedule everything
    python social/schedule_all.py --days 30          # just the next 30 days
    python social/schedule_all.py --time 18:00       # posting time (IST)

Pins every post to an exact time with Buffer's customScheduled mode, so there
is no daily job and no dependency on GitHub Actions. Once this has run, Buffer
holds the whole calendar and publishes it on its own.

Already-scheduled posts are skipped on re-run (matched on the image filename in
the post text), so running this twice will not double-post.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from datetime import datetime, timedelta, timezone

HERE = pathlib.Path(__file__).parent.resolve()
REPO = HERE.parent
sys.path.insert(0, str(REPO / "outreach"))

from src.buffer import _gql, _queue_post, buffer_key   # noqa: E402
from src.common import load_config                      # noqa: E402

CAL = HERE / "calendar" / "calendar.json"
IMAGE_BASE = "https://adi-0704.github.io/collabhive-site/social/calendar/"
IST = timezone(timedelta(hours=5, minutes=30))


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def existing_scheduled(cfg: dict, channel_id: str) -> set[str]:
    """Text of posts already scheduled on this channel, so re-runs are safe.

    channelIds/status live under `filter`, not at the top level. An earlier
    version had them at the top level, which errored and — because the caller
    swallowed it — silently returned an empty set, disabling the duplicate
    protection entirely. A re-run would have double-posted the whole calendar.
    """
    q = ('query Posts { posts(input: { organizationId: "%s", '
         'filter: { channelIds: ["%s"], status: [scheduled] } }) '
         '{ edges { node { id text } } } }'
         % (cfg.get("buffer", {}).get("organization_id", ""), channel_id))
    r = _gql(cfg, q)
    if isinstance(r, dict) and r.get("errors"):
        raise RuntimeError("could not read existing Buffer posts: %s"
                           % r["errors"][0].get("message", "")[:120])
    edges = (((r.get("data") or {}).get("posts") or {}).get("edges") or [])
    return {e["node"].get("text", "") for e in edges}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="0 = whole calendar")
    ap.add_argument("--time", default="18:00", help="posting time, IST, HH:MM")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--start", default="", help="first date to schedule (YYYY-MM-DD)")
    args = ap.parse_args()

    hh, mm = (int(x) for x in args.time.split(":"))
    cfg = load_config()
    channels = cfg.get("buffer", {}).get("channels", {})
    org_id = cfg.get("buffer", {}).get("organization_id", "")

    if not CAL.exists():
        log("No calendar.json — run social/generate_calendar.py first.")
        return 1
    entries = json.loads(CAL.read_text(encoding="utf-8"))

    # Only schedule the future. A past dueAt makes Buffer publish immediately.
    now_ist = datetime.now(IST)
    start = (datetime.strptime(args.start, "%Y-%m-%d").date()
             if args.start else now_ist.date())

    plan = []
    for e in entries:
        d = datetime.strptime(e["date"], "%Y-%m-%d").date()
        if d < start:
            continue
        if args.days and (d - start).days >= args.days:
            continue
        due_ist = datetime(d.year, d.month, d.day, hh, mm, tzinfo=IST)
        if due_ist <= now_ist:
            log(f"  skip {e['audience']} day {e['day']} — {due_ist:%d %b %H:%M} IST "
                f"is in the past")
            continue
        plan.append((e, due_ist))

    if not plan:
        log("Nothing to schedule (all slots are in the past or filtered out).")
        return 0

    log(f"Scheduling {len(plan)} post(s) at {args.time} IST daily")
    log(f"  {plan[0][1]:%d %b %Y}  ->  {plan[-1][1]:%d %b %Y}\n")

    if args.dry_run:
        for e, due in plan[:6]:
            log(f"  {due:%d %b %H:%M} IST  [{e['audience']:<7}] {e['headline'][:52]}")
        if len(plan) > 6:
            log(f"  ... and {len(plan) - 6} more")
        return 0

    if not buffer_key():
        log("BUFFER_ACCESS_TOKEN is not set.")
        return 1

    seen = {a: existing_scheduled(cfg, cid) for a, cid in channels.items() if cid}
    ok = skipped = failed = 0
    full: dict[str, int] = {}     # audience -> posts we couldn't fit

    for e, due in plan:
        channel_id = channels.get(e["audience"], "")
        if not channel_id:
            log(f"  no channel for {e['audience']} — skipping")
            skipped += 1
            continue
        # A channel that hit its plan limit stays full; keep going on the other
        # one rather than aborting the whole run.
        if e["audience"] in full:
            full[e["audience"]] += 1
            continue
        # Dedupe on the unique first line of the caption.
        marker = e["caption"].splitlines()[0][:60]
        if any(marker in t for t in seen.get(e["audience"], ())):
            skipped += 1
            continue

        due_utc = due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            res = _queue_post(cfg, channel_id, e["caption"], org_id,
                              IMAGE_BASE + e["image"], due_at=due_utc,
                              service="instagram")
            if not res.get("ok"):
                raise RuntimeError(res.get("message", "unknown"))
            ok += 1
            if ok % 10 == 0 or ok == 1:
                log(f"  scheduled {ok}/{len(plan)} (latest: {due:%d %b %H:%M} IST)")
        except Exception as exc:
            msg = str(exc)
            if "limit reached" in msg.lower() or "out of" in msg.lower():
                full[e["audience"]] = 1
                log(f"  {e['audience']} channel is FULL — {msg.strip()}")
                continue
            failed += 1
            log(f"  FAILED {e['audience']} day {e['day']}: {exc}")
            if failed >= 5:
                log("\n  Too many failures — stopping.")
                break
        time.sleep(0.35)          # be gentle with the API

    log(f"\nDone. scheduled={ok} skipped={skipped} failed={failed}")
    for aud, n in full.items():
        log(f"  {aud}: {n} post(s) could not be scheduled — channel queue is full.")
    if full:
        log("\n  Buffer's free plan allows 10 scheduled posts per channel.")
        log("  To hold the whole calendar you need a paid plan; otherwise top the")
        log("  queue up periodically (that is what the daily workflow does).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
