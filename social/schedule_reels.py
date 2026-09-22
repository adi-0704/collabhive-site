"""CollabHive - schedule the REEL calendar into Buffer.

    python social/schedule_reels.py --dry-run        # show the plan
    python social/schedule_reels.py                  # top the reel queue up
    python social/schedule_reels.py --time 19:30     # posting time (IST)
    python social/schedule_reels.py --max-queue 5    # slots this stream may use

The reel twin of schedule_all.py. Same mechanism - each reel is pinned to an
exact time with Buffer's customScheduled mode, so once this has run Buffer
publishes on its own and nothing depends on a workflow firing at 19:30.

Sharing the cap
---------------
Buffer's free plan allows 10 SCHEDULED posts per channel, counted across the
whole channel rather than per day (verified against the live account: an 11th
post on a day that already had one was rejected with "You have 10 scheduled
posts out of 10 allowed"). The static feed and this stream therefore split the
pool 5/5 - five days of runway each, both publishing every day, refilled by the
daily top-up as slots free up.

A reel is only scheduled if its MP4 is committed. Buffer pulls the video from
the public GitHub Pages URL, so an unrendered day would be scheduled against a
404 and fail at publish time, silently, hours later.

The .jpg covers rendered alongside each MP4 are not uploaded - Instagram does
not accept custom video thumbnails. They exist as a local preview of what the
reel looks like; the real cover comes from COVER_MS.
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

from src.buffer import _queue_post, buffer_key        # noqa: E402
from src.common import load_config                     # noqa: E402

sys.path.insert(0, str(HERE))
from schedule_all import (existing_posts, scheduled_slots,   # noqa: E402
                          stream_count)

CAL = HERE / "calendar" / "reels_calendar.json"
BASE = "https://adi-0704.github.io/collabhive-site/social/calendar/"
IST = timezone(timedelta(hours=5, minutes=30))

# Instagram picks the reel cover from a frame offset, not an uploaded image.
# The animation runs 7s and the last line lands around 5s, so grab a frame once
# everything is on screen - an offset near zero gives a blank opening frame.
COVER_MS = 6000


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="0 = whole calendar")
    # 19:00-21:00 IST is the peak window for reels in India - after the commute,
    # before the late-night drop-off. 19:30 sits in the middle of it and well
    # clear of the 18:00 static post, so the two never compete.
    ap.add_argument("--time", default="19:30", help="posting time, IST, HH:MM")
    ap.add_argument("--max-queue", type=int, default=5,
                    help="slots this stream may use on a channel")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--start", default="", help="first date (YYYY-MM-DD)")
    args = ap.parse_args()

    hh, mm = (int(x) for x in args.time.split(":"))
    cfg = load_config()
    channels = cfg.get("buffer", {}).get("channels", {})
    org_id = cfg.get("buffer", {}).get("organization_id", "")

    if not CAL.exists():
        log("No reels_calendar.json - run social/generate_reels.py first.")
        return 1
    entries = json.loads(CAL.read_text(encoding="utf-8"))

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
            continue
        if not (HERE / "calendar" / e["video"]).exists():
            log(f"  skip {e['audience']} reel day {e['day']} - {e['video']} "
                f"not rendered yet")
            continue
        plan.append((e, due_ist))

    if not plan:
        log("Nothing to schedule (past, filtered out, or not rendered).")
        return 0

    log(f"Reel queue: {len(plan)} candidate(s) at {args.time} IST daily")
    log(f"  {plan[0][1]:%d %b %Y}  ->  {plan[-1][1]:%d %b %Y}\n")

    if args.dry_run:
        for e, due in plan[:10]:
            log(f"  {due:%d %b %H:%M} IST  [{e['audience']:<7}] {e['style']:<8} "
                f"{e['headline'][:46]}")
        if len(plan) > 10:
            log(f"  ... and {len(plan) - 10} more")
        return 0

    if not buffer_key():
        log("BUFFER_ACCESS_TOKEN is not set.")
        return 1

    seen = {a: existing_posts(cfg, cid) for a, cid in channels.items() if cid}
    slots = {a: scheduled_slots(cfg, cid) for a, cid in channels.items() if cid}
    budget = {a: max(0, args.max_queue - stream_count(v, hh, mm))
              for a, v in slots.items()}
    for aud in sorted(slots):
        log(f"  {aud}: {stream_count(slots[aud], hh, mm)} reels of "
            f"{len(slots[aud])} scheduled, {budget[aud]} slot(s) free "
            f"(cap {args.max_queue})")

    ok = skipped = failed = 0
    for e, due in plan:
        aud = e["audience"]
        channel_id = channels.get(aud, "")
        if not channel_id:
            log(f"  no channel for {aud} - skipping")
            skipped += 1
            continue
        if budget.get(aud, 0) <= 0:
            skipped += 1
            continue
        marker = e["caption_body"].splitlines()[0][:80]
        if any(marker in t for t in seen.get(aud, ())):
            skipped += 1
            continue

        due_utc = due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            res = _queue_post(cfg, channel_id, e["caption"], org_id,
                              due_at=due_utc, service="instagram",
                              video_url=BASE + e["video"],
                              thumbnail_ms=COVER_MS)
            if not res.get("ok"):
                raise RuntimeError(res.get("message", "unknown"))
            ok += 1
            budget[aud] -= 1
            log(f"  scheduled [{aud:<7}] {due:%d %b %H:%M} IST  "
                f"{e['headline'][:44]}")
        except Exception as exc:
            msg = str(exc)
            if "limit reached" in msg.lower():
                budget[aud] = 0
                log(f"  {aud} channel is FULL - {msg.strip()}")
                continue
            failed += 1
            log(f"  FAILED {aud} reel day {e['day']}: {exc}")
            if failed >= 5:
                log("\n  Too many failures - stopping.")
                break
        time.sleep(0.35)

    log(f"\nDone. scheduled={ok} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
