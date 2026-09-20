"""CollabHive - publish today's Instagram Reel on both pages.

    python social/publish_reel.py --dry-run       # show what would publish
    python social/publish_reel.py                 # publish today's reels now
    python social/publish_reel.py --date 2026-09-25

Why this publishes immediately instead of scheduling
----------------------------------------------------
Buffer's free plan allows 10 SCHEDULED posts per channel, and both channels are
already full to that cap with the static 18:00 feed queue. Adding reels to that
queue would mean deleting live, already-scheduled static posts - which is
exactly what must not happen.

`mode: shareNow` publishes straight through without occupying a queue slot, so
the reel stream costs nothing against the cap and the static queue is never
touched. The trade is that the timing comes from the workflow's cron rather than
from Buffer, so the publish lands at 19:30 IST give or take GitHub's usual few
minutes of scheduler drift. For a reel that is immaterial; the peak window is
19:00-21:00, not a single minute.

Idempotency: before publishing, every post already on the channel (any status)
is read and matched against the caption's first line. Re-running the workflow,
or a retry after a partial failure, cannot double-post.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date

HERE = pathlib.Path(__file__).parent.resolve()
REPO = HERE.parent
sys.path.insert(0, str(REPO / "outreach"))

from src.buffer import _queue_post, buffer_key      # noqa: E402
from src.common import load_config                   # noqa: E402

sys.path.insert(0, str(HERE))
from schedule_all import existing_posts              # noqa: E402

CAL = HERE / "calendar" / "reels_calendar.json"
BASE = "https://adi-0704.github.io/collabhive-site/social/calendar/"


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CAL.exists():
        log("No reels_calendar.json - run social/generate_reels.py first.")
        return 1
    entries = json.loads(CAL.read_text(encoding="utf-8"))
    todays = [e for e in entries if e["date"] == args.date]
    if not todays:
        log(f"No reel scheduled for {args.date}. Extend the reel calendar.")
        return 0

    cfg = load_config()
    channels = cfg.get("buffer", {}).get("channels", {})
    org_id = cfg.get("buffer", {}).get("organization_id", "")

    missing = [e for e in todays
               if not (HERE / "calendar" / e["video"]).exists()]
    if missing and not args.dry_run:
        # Publishing a URL that 404s makes Instagram reject the post with a
        # message that looks like an API problem rather than a missing render.
        for e in missing:
            log(f"  NOT RENDERED: {e['video']} - run social/reels.py")
        log("\nRefusing to publish a video that is not committed yet.")
        return 1

    failures = 0
    seen: dict[str, set[str]] = {}
    if not args.dry_run:
        if not buffer_key():
            log("BUFFER_ACCESS_TOKEN is not set.")
            return 1
        seen = {a: existing_posts(cfg, cid) for a, cid in channels.items() if cid}

    for e in todays:
        aud = e["audience"]
        video_url = BASE + e["video"]
        cover_url = BASE + e["cover"]
        log(f"\n[{aud}] reel day {e['day']} - {e['style']}")
        log(f"  {e['headline']}")
        log(f"  video: {video_url}")

        if args.dry_run:
            log("  DRY RUN - not publishing")
            continue

        channel_id = channels.get(aud, "")
        if not channel_id:
            log(f"  SKIP - no buffer.channels.{aud} in config.json")
            continue

        marker = e["caption_body"].splitlines()[0][:80]
        if any(marker in t for t in seen.get(aud, ())):
            log("  SKIP - this reel is already on the channel")
            continue

        try:
            res = _queue_post(cfg, channel_id, e["caption"], org_id,
                              due_at="now", service="instagram",
                              video_url=video_url, thumbnail_url=cover_url)
            if not (isinstance(res, dict) and res.get("ok")):
                raise RuntimeError((res or {}).get("message", "unknown error"))
            log(f"  PUBLISHED (post {res.get('post_id')})")
        except Exception as exc:
            failures += 1
            log(f"  FAILED: {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
