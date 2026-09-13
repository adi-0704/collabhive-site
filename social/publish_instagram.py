"""CollabHive — publish today's calendar post to Instagram (Graph API).

    python social/publish_instagram.py            # publish today's posts
    python social/publish_instagram.py --dry-run  # show what WOULD post
    python social/publish_instagram.py --date 2026-09-20

No Buffer, no third party. The Instagram Graph API publishes directly, which
is why the images must live at a PUBLIC url — the API fetches the image itself
rather than accepting an upload. GitHub Pages serves social/calendar/images/
for free, so committing the PNG is the upload step.

Publishing is two calls:
    1. POST /{ig_user_id}/media          -> creates a container, returns id
    2. POST /{ig_user_id}/media_publish  -> publishes that container

Credentials come from the environment (GitHub Secrets), never the repo:
    IG_BRAND_USER_ID    / IG_BRAND_TOKEN
    IG_CREATOR_USER_ID  / IG_CREATOR_TOKEN

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

HERE = pathlib.Path(__file__).parent.resolve()
CAL = HERE / "calendar" / "calendar.json"
GRAPH = "https://graph.facebook.com/v21.0"

# Where the committed images are publicly served from.
IMAGE_BASE = "https://adi-0704.github.io/collabhive-site/social/calendar/"

ACCOUNTS = {
    "brand": ("IG_BRAND_USER_ID", "IG_BRAND_TOKEN"),
    "creator": ("IG_CREATOR_USER_ID", "IG_CREATOR_TOKEN"),
}


def log(msg: str) -> None:
    """Captions contain emoji; Windows consoles default to cp1252 and raise on
    them. Logging must never be the thing that kills a publish run."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def _post(url: str, params: dict) -> dict:
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")[:400]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from None


def publish_one(ig_user_id: str, token: str, image_url: str, caption: str) -> str:
    """Create a media container, wait for it to finish, then publish it."""
    container = _post(f"{GRAPH}/{ig_user_id}/media", {
        "image_url": image_url, "caption": caption, "access_token": token,
    })
    cid = container.get("id")
    if not cid:
        raise RuntimeError(f"no container id returned: {container}")

    # Instagram fetches the image asynchronously; publishing too early fails.
    for attempt in range(10):
        time.sleep(3)
        status_url = f"{GRAPH}/{cid}?fields=status_code&access_token={urllib.parse.quote(token)}"
        try:
            with urllib.request.urlopen(status_url, timeout=30) as r:
                st = json.loads(r.read().decode("utf-8", "ignore")).get("status_code")
        except Exception:
            st = None
        if st == "FINISHED":
            break
        if st == "ERROR":
            raise RuntimeError(f"container {cid} failed to process the image")
        log(f"    container {st or 'PENDING'} ({attempt + 1}/10)")

    published = _post(f"{GRAPH}/{ig_user_id}/media_publish", {
        "creation_id": cid, "access_token": token,
    })
    pid = published.get("id")
    if not pid:
        raise RuntimeError(f"publish failed: {published}")
    return pid


def main() -> int:
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not CAL.exists():
        log("No calendar.json — run social/generate_calendar.py first.")
        return 1
    entries = json.loads(CAL.read_text(encoding="utf-8"))
    todays = [e for e in entries if e["date"] == args.date]
    if not todays:
        log(f"Nothing scheduled for {args.date}. Calendar may need extending.")
        return 0

    failures = 0
    for e in todays:
        image_url = IMAGE_BASE + e["image"]
        log(f"\n[{e['audience']}] day {e['day']} — {e['layout']}")
        log(f"  image: {image_url}")
        log(f"  {e['headline']}")

        if args.dry_run:
            log("  DRY RUN — not publishing")
            log("  caption:\n" + "\n".join("    " + l for l in e["caption"].splitlines()))
            continue

        id_var, token_var = ACCOUNTS[e["audience"]]
        ig_user_id, token = os.environ.get(id_var, ""), os.environ.get(token_var, "")
        if not ig_user_id or not token:
            log(f"  SKIP — {id_var}/{token_var} not set in the environment.")
            continue
        try:
            pid = publish_one(ig_user_id, token, image_url, e["caption"])
            log(f"  PUBLISHED -> media id {pid}")
        except Exception as exc:
            failures += 1
            log(f"  FAILED: {exc}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
