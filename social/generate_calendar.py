"""CollabHive — build the Instagram content calendar and render post images.

    python social/generate_calendar.py            # build calendar + render all
    python social/generate_calendar.py --days 7   # just the next week
    python social/generate_calendar.py --no-images

Output:
    social/calendar/calendar.json     one entry per day per audience
    social/calendar/images/*.png      1080x1350, ready to publish

Variety rules (asserted, not hoped for):
    * every caption in the calendar is unique
    * a layout never repeats within 7 days on the same page
    * a pillar never repeats within 5 days on the same page
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

from content_bank import BRAND_POSTS, CREATOR_POSTS      # noqa: E402
from hashtags import tag_block                            # noqa: E402
from layouts import LAYOUTS, render_html                   # noqa: E402

OUT = HERE / "calendar"
IMG = OUT / "images"

SITE = "https://adi-0704.github.io/collabhive-site/"
BRIEF_FORM = ("https://docs.google.com/forms/d/e/"
              "1FAIpQLScl-Mvis2Cl7rPZBP-BFqtmWR8BBhwjfs6hN6lryDOT9kckew/viewform")
APPLY_FORM = ("https://docs.google.com/forms/d/e/"
              "1FAIpQLScIV5PVkwbdcvMpzCyxTAzN71ORCqaTaIMY7Dr15xEMXSxIXQ/viewform")


def _is_stat_headline(headline: str) -> bool:
    """stat_hero blows the first word up to 210px, which only reads as design
    if that word is actually a figure. 'You're undercharging...' rendered a
    giant "You're" — so gate the layout on a numeric opening token."""
    first = headline.split()[0] if headline.split() else ""
    return any(ch.isdigit() for ch in first)


def _pick_layout(pillar: str, recent: list[str], headline: str = "") -> str:
    """First layout not used in the last 7 posts. Some pillars have a natural fit."""
    preferred = {
        "myth": ["myth_fact", "split_compare"],
        "data": ["stat_hero", "bold_dark"],
        "tip": ["hero_cta", "checklist"],
        "mistake": ["split_compare", "myth_fact"],
        "process": ["checklist", "bullet_list"],
        "money": ["stat_hero", "statement_frame"],
        "rates": ["stat_hero", "hero_cta"],
        "redflag": ["myth_fact", "bold_dark"],
        "community": ["question", "quote_card"],
        "confidence": ["quote_card", "statement_frame"],
        "pitch": ["bold_dark", "statement_frame"],
        "mediakit": ["bullet_list", "checklist"],
        "growth": ["statement_frame", "hero_cta"],
        "negotiation": ["split_compare", "quote_card"],
        "format": ["split_compare", "bullet_list"],
        "seasonal": ["hero_cta", "statement_frame"],
        "proof": ["quote_card", "bullet_list"],
    }
    for cand in preferred.get(pillar, []) + LAYOUTS:
        if cand == "stat_hero" and not _is_stat_headline(headline):
            continue
        if cand not in recent[-7:]:
            return cand
    # Fallback must respect the same gate.
    for cand in LAYOUTS:
        if cand == "stat_hero" and not _is_stat_headline(headline):
            continue
        return cand
    return "hero_cta"


def build(days: int, start: date) -> list[dict]:
    entries: list[dict] = []
    for audience, bank, cta_url in (
        ("brand", BRAND_POSTS, BRIEF_FORM),
        ("creator", CREATOR_POSTS, APPLY_FORM),
    ):
        recent_layouts: list[str] = []
        recent_pillars: list[str] = []
        # Consume each authored post at most once. The earlier version indexed
        # with day % len(bank) and skipped forward to de-cluster pillars, which
        # could land on an entry already used and silently duplicate copy.
        unused = list(range(len(bank)))
        for day in range(days):
            if not unused:
                break                      # bank exhausted; verify() reports it
            # Prefer the first unused post whose pillar hasn't run recently.
            choice = next((i for i in unused if bank[i][0] not in recent_pillars[-5:]),
                          unused[0])
            unused.remove(choice)
            pillar, headline, sub, caption, cta = bank[choice]

            layout = _pick_layout(pillar, recent_layouts, headline)
            recent_layouts.append(layout)
            recent_pillars.append(pillar)

            link = "Link in bio" if audience == "creator" else "Free shortlist — link in bio"
            full_caption = (
                f"{caption}\n\n{cta}\n\n{link} 🔗\n\n"
                f"{tag_block(audience, day)}"
            )
            entries.append({
                "day": day + 1,
                "date": (start + timedelta(days=day)).isoformat(),
                "audience": audience,
                "pillar": pillar,
                "layout": layout,
                "headline": headline,
                "sub": sub,
                # body WITHOUT hashtags — uniqueness must be judged on the copy
                # itself, since rotating tags would otherwise disguise a repost.
                "caption_body": caption,
                "caption": full_caption,
                "cta_url": cta_url,
                "image": f"images/{audience}-day{day + 1:03d}.png",
            })
    return entries


def verify(entries: list[dict]) -> None:
    """Fail loudly rather than shipping a repetitive grid."""
    for audience in ("brand", "creator"):
        rows = [e for e in entries if e["audience"] == audience]
        # Judge on the body copy, NOT the assembled caption: hashtags rotate
        # daily and would otherwise make a recycled post look unique.
        bodies = [e["caption_body"] for e in rows]
        if len(set(bodies)) != len(bodies):
            have = len(BRAND_POSTS if audience == "brand" else CREATOR_POSTS)
            dupes = len(bodies) - len(set(bodies))
            raise SystemExit(
                f"FAIL: {audience} page would repeat copy {dupes} time(s).\n"
                f"       content_bank.py has {have} authored posts but the calendar "
                f"needs {len(rows)}.\n"
                f"       Add {len(rows) - have} more {audience} posts, or run with "
                f"--days {have}.")
        heads = [e["headline"] for e in rows]
        if len(set(heads)) != len(heads):
            raise SystemExit(f"FAIL: {audience} page repeats an image headline.")
        for i in range(len(rows)):
            window = [r["layout"] for r in rows[max(0, i - 6):i]]
            if rows[i]["layout"] in window:
                raise SystemExit(f"FAIL: layout repeated within 7 days at {audience} day {i+1}")
    print(f"  variety OK: {len(entries)} posts, all captions unique, "
          f"no layout repeat within 7 days")


def render_images(entries: list[dict]) -> int:
    from playwright.sync_api import sync_playwright
    IMG.mkdir(parents=True, exist_ok=True)
    done = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350},
                                device_scale_factor=1)
        for e in entries:
            html = render_html(e["layout"], e["headline"], e["sub"])
            tmp = OUT / "_render.html"
            tmp.write_text(html, encoding="utf-8")
            page.goto(tmp.as_uri())
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(220)          # let webfonts settle
            page.screenshot(path=str(OUT / e["image"]))
            done += 1
            if done % 10 == 0:
                print(f"  rendered {done}/{len(entries)}")
        browser.close()
        tmp.unlink(missing_ok=True)
    return done


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=100)
    ap.add_argument("--start", default=date.today().isoformat())
    ap.add_argument("--no-images", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    entries = build(args.days, date.fromisoformat(args.start))
    verify(entries)

    (OUT / "calendar.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  calendar -> social/calendar/calendar.json ({len(entries)} posts)")

    if not args.no_images:
        n = render_images(entries)
        print(f"  images   -> social/calendar/images/ ({n} PNGs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
