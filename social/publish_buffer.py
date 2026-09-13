"""CollabHive — queue today's calendar posts to Buffer.

    python social/publish_buffer.py --list-channels   # find your channel IDs
    python social/publish_buffer.py --dry-run         # show what would queue
    python social/publish_buffer.py                   # queue today's posts

Reuses outreach/src/buffer.py (already written and tested) rather than talking
to the Buffer API a second way.

Buffer fetches the image from a public URL, which is why the rendered PNGs are
committed and served by GitHub Pages — that IS the upload step.

Credentials + channel mapping:
    BUFFER_ACCESS_TOKEN            (GitHub Secret, never committed)
    outreach/config.json -> buffer.channels.brand / buffer.channels.creator
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

from src.buffer import (_queue_post, buffer_key, get_channels,   # noqa: E402
                        get_organizations)
from src.common import load_config                                # noqa: E402

CAL = HERE / "calendar" / "calendar.json"
IMAGE_BASE = "https://adi-0704.github.io/collabhive-site/social/calendar/"


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:                     # cp1252 consoles + emoji
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def list_channels(cfg: dict) -> int:
    """Print the Buffer org + channels so the IDs can be put in config.json."""
    if not buffer_key():
        log("BUFFER_ACCESS_TOKEN is not set — export it first.")
        return 1
    orgs = get_organizations(cfg)
    if not orgs:
        log("No organizations returned. Is the token valid?")
        return 1
    for org in orgs:
        log(f"\norganization: {org.get('name')}  id={org.get('id')}")
        for ch in get_channels(cfg, org.get("id", "")):
            log(f"   channel  {ch.get('service','?'):<12} {ch.get('name','?'):<28} "
                f"id={ch.get('id')}")
    log("\nPut the two Instagram ids into outreach/config.json:")
    log('   "buffer": { "channels": { "brand": "<id>", "creator": "<id>" } }')
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--list-channels", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    if args.list_channels:
        return list_channels(cfg)

    if not CAL.exists():
        log("No calendar.json — run social/generate_calendar.py first.")
        return 1
    entries = json.loads(CAL.read_text(encoding="utf-8"))
    todays = [e for e in entries if e["date"] == args.date]
    if not todays:
        log(f"Nothing scheduled for {args.date}. Extend the calendar.")
        return 0

    channels = cfg.get("buffer", {}).get("channels", {})
    org_id = cfg.get("buffer", {}).get("organization_id", "")
    failures = 0

    for e in todays:
        image_url = IMAGE_BASE + e["image"]
        log(f"\n[{e['audience']}] day {e['day']} — {e['layout']}")
        log(f"  {e['headline']}")
        log(f"  image: {image_url}")

        if args.dry_run:
            log("  DRY RUN — not queueing")
            continue

        channel_id = channels.get(e["audience"], "")
        if not channel_id:
            log(f"  SKIP — no buffer.channels.{e['audience']} in config.json "
                f"(run --list-channels).")
            continue
        if not buffer_key():
            log("  SKIP — BUFFER_ACCESS_TOKEN not set.")
            continue
        try:
            res = _queue_post(cfg, channel_id, e["caption"], org_id, image_url)
            if isinstance(res, dict) and res.get("error"):
                raise RuntimeError(res["error"])
            log(f"  QUEUED to Buffer channel {channel_id}")
        except Exception as exc:
            failures += 1
            log(f"  FAILED: {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
