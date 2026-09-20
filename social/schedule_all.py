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
REELS_DIR = HERE / "calendar" / "reels"
IST = timezone(timedelta(hours=5, minutes=30))


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def existing_posts(cfg: dict, channel_id: str) -> set[str]:
    """Text of every post on this channel, whatever its status.

    Must include `sent`, not just `scheduled`. Checking only scheduled posts
    meant already-published content was invisible to the dedupe, so a post that
    went out yesterday could be scheduled again today — which is exactly what
    happened when a calendar regeneration shifted the day/date mapping.

    channelIds/status live under `filter`, not at the top level; an earlier
    version put them at the top level, errored, and silently returned an empty
    set, disabling duplicate protection altogether.
    """
    org = cfg.get("buffer", {}).get("organization_id", "")
    texts: set[str] = set()
    after = ""
    # MUST paginate. The default page is small, so an unpaginated read returned
    # only part of the history — the dedupe then missed an already-sent post and
    # scheduled it again. Walk every page before deciding anything is new.
    for _ in range(20):
        cursor = ', after: "%s"' % after if after else ""
        q = ('query Posts { posts(first: 50%s, input: { organizationId: "%s", '
             'filter: { channelIds: ["%s"], '
             'status: [scheduled, sent, sending, draft, needs_approval, error] } }) '
             '{ pageInfo { hasNextPage endCursor } edges { node { id text } } } }'
             % (cursor, org, channel_id))
        r = _gql(cfg, q)
        if isinstance(r, dict) and r.get("errors"):
            raise RuntimeError("could not read existing Buffer posts: %s"
                               % r["errors"][0].get("message", "")[:120])
        page = ((r.get("data") or {}).get("posts") or {})
        texts |= {e["node"].get("text", "") for e in (page.get("edges") or [])}
        info = page.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        after = info.get("endCursor") or ""
        if not after:
            break
    return texts


def scheduled_days(cfg: dict, channel_id: str) -> set[str]:
    """Dates (YYYY-MM-DD) that already hold a scheduled post on this channel."""
    org = cfg.get("buffer", {}).get("organization_id", "")
    days: set[str] = set()
    after = ""
    for _ in range(20):
        cursor = ', after: "%s"' % after if after else ""
        q = ('query { posts(first: 50%s, input: { organizationId: "%s", '
             'filter: { channelIds: ["%s"], status: [scheduled] } }) '
             '{ pageInfo { hasNextPage endCursor } edges { node { dueAt } } } }'
             % (cursor, org, channel_id))
        r = _gql(cfg, q)
        if isinstance(r, dict) and r.get("errors"):
            break
        page = ((r.get("data") or {}).get("posts") or {})
        for e in (page.get("edges") or []):
            due = (e["node"].get("dueAt") or "")[:10]
            if due:
                days.add(due)
        info = page.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        after = info.get("endCursor") or ""
        if not after:
            break
    return days


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="0 = whole calendar")
    ap.add_argument("--time", default="18:00", help="posting time, IST, HH:MM")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-fill-gaps", action="store_true",
                    help="leave empty days empty instead of back-filling")
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

    seen = {a: existing_posts(cfg, cid) for a, cid in channels.items() if cid}
    scheduled_dates = {a: scheduled_days(cfg, cid) for a, cid in channels.items() if cid}

    # Fill empty days with unused content.
    #
    # The scheduler normally asks "what does the calendar say for this date?".
    # If that content is already queued under a different date — which happens
    # whenever the calendar and the queue drift apart — the date is skipped and
    # stays empty forever. 24 Sep was left blank exactly this way.
    #
    # So: any future date with no post gets the next piece of content that is
    # not already in Buffer, whatever date the calendar had assigned it.
    if not args.no_fill_gaps:
        used = {a: set() for a in channels}
        filled: list[tuple[dict, datetime]] = []
        for e, due in plan:
            aud = e["audience"]
            marker = e["caption_body"].splitlines()[0][:80]
            if any(marker in t for t in seen.get(aud, ())):
                used[aud].add(marker)
        for e, due in plan:
            aud = e["audience"]
            day = due.date().isoformat()
            if day in scheduled_dates.get(aud, set()):
                continue                      # that day already has a post
            marker = e["caption_body"].splitlines()[0][:80]
            if marker in used[aud]:
                # Content already live elsewhere — find the first unused piece
                # and move it into this empty slot instead of skipping the day.
                for cand, _ in plan:
                    if cand["audience"] != aud:
                        continue
                    cm = cand["caption_body"].splitlines()[0][:80]
                    if cm in used[aud] or any(cm in t for t in seen.get(aud, ())):
                        continue
                    used[aud].add(cm)
                    filled.append((cand, due))
                    log(f"  gap-fill: {day} [{aud}] <- {cand['headline'][:44]}")
                    break
                continue
            used[aud].add(marker)
            filled.append((e, due))
        plan = filled
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
        marker = e["caption_body"].splitlines()[0][:80]
        if any(marker in t for t in seen.get(e["audience"], ())):
            skipped += 1
            continue

        due_utc = due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Publish as a reel when one has been rendered for this day, since reels
        # reach non-followers. Falls back to the still image otherwise, so a
        # missing video never blocks the post.
        stem = pathlib.Path(e["image"]).stem
        video_url = thumb_url = ""
        if (REELS_DIR / f"{stem}.mp4").exists():
            video_url = IMAGE_BASE + f"reels/{stem}.mp4"
            if (REELS_DIR / f"{stem}.jpg").exists():
                thumb_url = IMAGE_BASE + f"reels/{stem}.jpg"
        try:
            res = _queue_post(cfg, channel_id, e["caption"], org_id,
                              IMAGE_BASE + e["image"], due_at=due_utc,
                              service="instagram", video_url=video_url,
                              thumbnail_url=thumb_url)
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
