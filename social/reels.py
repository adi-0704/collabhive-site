"""CollabHive — generate Instagram Reels from the content calendar.

Reels reach people who do not follow you; feed posts mostly reach people who
already do. Same copy, far wider distribution.

Each reel is an animated 1080x1920 HTML page recorded by Playwright, then
converted to H.264 MP4 (Instagram will not accept the WebM that Chromium
produces). A still frame is exported alongside as the cover.

    python social/reels.py --days 14           # next 14 days of reels
    python social/reels.py --day 2026-09-25    # one specific day
    python social/reels.py --check             # report tooling only

Output:
    social/calendar/reels/<audience>-dayNNN.mp4
    social/calendar/reels/<audience>-dayNNN.jpg   (cover)

ffmpeg is required for the MP4 conversion. It is preinstalled on GitHub
Actions' ubuntu runners, which is where this is meant to run; locally it is an
optional extra and the script says so plainly rather than producing a file
Instagram will silently reject.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

from reel_styles import pick_style, render as render_style   # noqa: E402

CAL = HERE / "calendar" / "calendar.json"
REELS = HERE / "calendar" / "reels"

W, H = 1080, 1920
DURATION_MS = 7000          # long enough to read, short enough to loop well

_FONT = ("https://fonts.googleapis.com/css2?"
         "family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap")


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


# ---------------------------------------------------------------- animation
# Styles live in reel_styles.py so the feed is not one template with new words.


def record(entry: dict, out_dir: pathlib.Path) -> pathlib.Path | None:
    """Record one reel to WebM and return the raw file."""
    from playwright.sync_api import sync_playwright

    cta = "Link in bio" if entry["audience"] == "creator" else "Free shortlist"
    html = render_style(entry["style"], entry["headline"], entry["sub"],
                        cta, entry["audience"])
    tmp_html = out_dir / "_reel.html"
    tmp_html.write_text(html, encoding="utf-8")

    raw_dir = out_dir / "_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": W, "height": H},
                                  record_video_dir=str(raw_dir),
                                  record_video_size={"width": W, "height": H})
        page = ctx.new_page()
        page.goto(tmp_html.as_uri())
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(DURATION_MS)
        # Cover frame taken at the end, when all the text has arrived.
        page.screenshot(path=str(out_dir / (pathlib.Path(entry["image"]).stem + ".jpg")),
                        quality=90, type="jpeg")
        ctx.close()
        browser.close()
    tmp_html.unlink(missing_ok=True)

    vids = sorted(raw_dir.glob("*.webm"), key=lambda p: p.stat().st_mtime)
    return vids[-1] if vids else None


def to_mp4(webm: pathlib.Path, dest: pathlib.Path) -> bool:
    """Convert to H.264/AAC MP4. Instagram rejects WebM outright."""
    cmd = [
        "ffmpeg", "-y", "-i", str(webm),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p",              # required for broad playback
        "-vf", f"scale={W}:{H},fps=30",
        "-movflags", "+faststart",          # lets playback start before full download
        "-an",                               # silent: audio is added in-app if wanted
        str(dest),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
        return dest.exists() and dest.stat().st_size > 0
    except Exception as exc:
        log(f"    ffmpeg failed: {exc}")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--day", default="", help="single date, YYYY-MM-DD")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if args.check:
        log("ffmpeg  : %s" % ("found" if have_ffmpeg() else "MISSING"))
        try:
            import playwright  # noqa: F401
            log("playwright: found")
        except ImportError:
            log("playwright: MISSING")
        return 0

    if not CAL.exists():
        log("No calendar.json — run generate_calendar.py first.")
        return 1
    if not have_ffmpeg():
        log("ffmpeg is not installed, so the MP4 conversion cannot run.")
        log("Instagram will not accept the raw WebM that Chromium produces.")
        log("This is built to run in GitHub Actions, where ffmpeg is preinstalled.")
        return 1

    entries = json.loads(CAL.read_text(encoding="utf-8"))
    if args.day:
        wanted = [e for e in entries if e["date"] == args.day]
    else:
        today = date.today()
        end = today + timedelta(days=args.days)
        wanted = [e for e in entries
                  if today.isoformat() <= e["date"] <= end.isoformat()]
    if not wanted:
        log("Nothing in that window.")
        return 0

    REELS.mkdir(parents=True, exist_ok=True)
    made = failed = 0
    recent: dict[str, list[str]] = {}
    for idx, entry in enumerate(wanted):
        aud = entry["audience"]
        entry["style"] = pick_style(entry["headline"], idx, recent.get(aud, []))
        recent.setdefault(aud, []).append(entry["style"])
        stem = pathlib.Path(entry["image"]).stem
        dest = REELS / f"{stem}.mp4"
        if dest.exists():
            continue
        log(f"  {entry['date']} [{entry['audience']:<7}] {entry['style']:<8} "
            f"{entry['headline'][:38]}")
        webm = record(entry, REELS)
        if not webm:
            failed += 1
            log("    recording produced nothing")
            continue
        if to_mp4(webm, dest):
            made += 1
            log(f"    -> {dest.name} ({dest.stat().st_size // 1024} KB)")
        else:
            failed += 1
        webm.unlink(missing_ok=True)

    shutil.rmtree(REELS / "_raw", ignore_errors=True)
    log(f"\nDone. reels={made} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
