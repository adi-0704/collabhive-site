"""CollabHive - build the REEL calendar. Separate stream from the static feed.

    python social/generate_reels.py              # build the whole reel calendar
    python social/generate_reels.py --days 30
    python social/generate_reels.py --reanchor --start 2026-09-21

Output:
    social/calendar/reels_calendar.json   one entry per day per audience
    social/calendar/reel_anchor.txt       the date reel day 1 maps to

Why this is not part of generate_calendar.py
--------------------------------------------
The static feed and the reel stream publish on the same days at different
times, and they must not say the same thing twice. Keeping the two calendars
apart means:

  * the static queue is never touched by a reel rebuild - it is already live in
    Buffer on its own dates and any re-dating would reshuffle published posts
  * the reel anchor can start today/tomorrow without moving static day 1
  * verify() can assert zero overlap between the two banks, which is the actual
    guarantee being made to the reader

Variety rules (asserted, not hoped for):
    * every reel body and headline is unique within the reel calendar
    * no reel headline or body appears anywhere in the static calendar bank
    * a style never repeats on consecutive days on the same page
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

from content_bank import BRAND_POSTS, CREATOR_POSTS       # noqa: E402
from hashtags import tag_block                             # noqa: E402
from reel_bank import REEL_BRAND_POSTS, REEL_CREATOR_POSTS  # noqa: E402
from reel_styles import _is_stat, pick_style               # noqa: E402

OUT = HERE / "calendar"
ANCHOR = OUT / "reel_anchor.txt"
CAL = OUT / "reels_calendar.json"

BRIEF_FORM = ("https://docs.google.com/forms/d/e/"
              "1FAIpQLScl-Mvis2Cl7rPZBP-BFqtmWR8BBhwjfs6hN6lryDOT9kckew/viewform")
APPLY_FORM = ("https://docs.google.com/forms/d/e/"
              "1FAIpQLScIV5PVkwbdcvMpzCyxTAzN71ORCqaTaIMY7Dr15xEMXSxIXQ/viewform")

CTA_LINK = {
    "brand": "Free shortlist - link in bio 🔗",
    "creator": "Link in bio 🔗",
}


def _anchor_date() -> str:
    """The date reel day 1 maps to, held fixed across rebuilds.

    Same reasoning as the static anchor: Buffer holds real scheduled reels keyed
    to these dates, so a rebuild that moves day 1 shifts everything after it and
    the queue silently stops matching the calendar.
    """
    if ANCHOR.exists():
        txt = ANCHOR.read_text(encoding="utf-8").strip()
        if txt:
            return txt
    # Reels start tomorrow, not today - today's slot has usually passed by the
    # time this runs, and a due date in the past makes Buffer publish instantly.
    return (date.today() + timedelta(days=1)).isoformat()


def _static_copy() -> tuple[set[str], set[str]]:
    """Every headline and body in the static banks, for the overlap check."""
    heads, bodies = set(), set()
    for bank in (BRAND_POSTS, CREATOR_POSTS):
        for entry in bank:
            # (pillar, headline, sub, caption, cta)
            heads.add(entry[1].strip().lower())
            bodies.add(entry[3].strip().lower())
    return heads, bodies


def build(days: int, start: date) -> list[dict]:
    entries: list[dict] = []
    for audience, bank, cta_url in (
        ("brand", REEL_BRAND_POSTS, BRIEF_FORM),
        ("creator", REEL_CREATOR_POSTS, APPLY_FORM),
    ):
        recent_styles: list[str] = []
        for day in range(min(days, len(bank))):
            pillar, headline, sub, caption, cta = bank[day]
            this_date = start + timedelta(days=day)

            # Style is decided here, not at render time, so the renderer and the
            # scheduler cannot disagree about what a given day looks like.
            #
            # `stat` and `reveal` are gated on the headline (a number to enlarge,
            # a question to answer), so plain rotation almost never reaches them
            # - a first pass produced 6 stats and zero reveals out of 200. When a
            # headline does qualify, take the gated style rather than waiting for
            # the rotation to come round.
            style = pick_style(headline, day, recent_styles)
            for gated, eligible in (("reveal", headline.rstrip().endswith("?")),
                                    ("stat", _is_stat(headline))):
                if eligible and (not recent_styles or recent_styles[-1] != gated):
                    style = gated
                    break
            recent_styles.append(style)

            full_caption = (
                f"{caption}\n\n{cta}\n\n{CTA_LINK[audience]}\n\n"
                f"{tag_block(audience, 1000 + day)}"
            )
            stem = f"reel-{audience}-day{day + 1:03d}"
            entries.append({
                "day": day + 1,
                "date": this_date.isoformat(),
                "audience": audience,
                "pillar": pillar,
                "style": style,
                "headline": headline,
                "sub": sub,
                "cta": cta,
                # Body without hashtags - uniqueness is judged on the copy, since
                # rotating tags would otherwise disguise a repeat.
                "caption_body": caption,
                "caption": full_caption,
                "cta_url": cta_url,
                "video": f"reels/{stem}.mp4",
                "cover": f"reels/{stem}.jpg",
            })
    return entries


def verify(entries: list[dict], days: int = 0) -> None:
    """Fail the build rather than shipping a repeat or a clash with the feed."""
    static_heads, static_bodies = _static_copy()

    for audience in ("brand", "creator"):
        rows = [e for e in entries if e["audience"] == audience]
        have = len(REEL_BRAND_POSTS if audience == "brand" else REEL_CREATOR_POSTS)
        if days and len(rows) < days:
            raise SystemExit(
                f"FAIL: {audience} reels only got {len(rows)} of {days} days.\n"
                f"       reel_bank.py holds {have} authored reels for this page. "
                f"Add {days - have} more, or run with --days {len(rows)}.")

        bodies = [e["caption_body"] for e in rows]
        if len(set(bodies)) != len(bodies):
            raise SystemExit(f"FAIL: {audience} reels repeat body copy "
                             f"{len(bodies) - len(set(bodies))} time(s).")
        heads = [e["headline"] for e in rows]
        if len(set(heads)) != len(heads):
            raise SystemExit(f"FAIL: {audience} reels repeat a headline.")

        # The whole point of the separate stream: a follower seeing the 18:00
        # post and the reel later the same day must see two different ideas.
        for e in rows:
            if e["headline"].strip().lower() in static_heads:
                raise SystemExit(
                    f"FAIL: reel headline also appears in the static bank:\n"
                    f"       {e['headline']}")
            if e["caption_body"].strip().lower() in static_bodies:
                raise SystemExit(
                    f"FAIL: reel body also appears in the static bank "
                    f"(day {e['day']}, {audience}).")
            # Whole-body equality is not enough. The scheduler dedupes on the
            # first 80 characters of the body, so a reel whose opening line sits
            # INSIDE a longer static post is a duplicate as far as the reader
            # and the scheduler are concerned - it silently lost a reel slot on
            # 27 Sep. Catch the overlap here instead.
            opener = e["caption_body"].splitlines()[0][:80].strip().lower()
            if opener and any(opener in b for b in static_bodies):
                raise SystemExit(
                    f"FAIL: reel opening line already appears inside a static "
                    f"post ({audience} day {e['day']}): {opener[:70]}")

        for i in range(1, len(rows)):
            if rows[i]["style"] == rows[i - 1]["style"]:
                raise SystemExit(f"FAIL: style repeated on consecutive days at "
                                 f"{audience} reel day {i + 1}")

    styles: dict[str, int] = {}
    for e in entries:
        styles[e["style"]] = styles.get(e["style"], 0) + 1
    spread = ", ".join(f"{k}={v}" for k, v in sorted(styles.items()))
    print(f"  variety OK: {len(entries)} reels, all copy unique, "
          f"no overlap with the static feed")
    print(f"  styles: {spread}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0,
                    help="0 (default) = as many days as the reel bank allows")
    ap.add_argument("--start", default=_anchor_date())
    ap.add_argument("--reanchor", action="store_true",
                    help="deliberately restart the reel calendar from --start")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(args.start)
    if args.reanchor or not ANCHOR.exists():
        ANCHOR.write_text(start.isoformat(), encoding="utf-8")
        print(f"  reel anchor set: reel day 1 = {start.isoformat()}")
    else:
        print(f"  reel anchor held: reel day 1 = {start.isoformat()} "
              f"(use --reanchor to move it)")

    days = args.days or min(len(REEL_BRAND_POSTS), len(REEL_CREATOR_POSTS))
    entries = build(days, start)
    verify(entries, days)

    CAL.write_text(json.dumps(entries, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    last = max(e["date"] for e in entries)
    print(f"  calendar -> social/calendar/reels_calendar.json "
          f"({len(entries)} reels, through {last})")
    print("  next: python social/reels.py --days N   (renders the MP4s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
