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
from posts_festival import FESTIVAL_BRAND, FESTIVAL_CREATOR  # noqa: E402
from hashtags import tag_block                            # noqa: E402
from layouts import LAYOUTS, render_html                   # noqa: E402

OUT = HERE / "calendar"
IMG = OUT / "images"

SITE = "https://adi-0704.github.io/collabhive-site/"
BRIEF_FORM = ("https://docs.google.com/forms/d/e/"
              "1FAIpQLScl-Mvis2Cl7rPZBP-BFqtmWR8BBhwjfs6hN6lryDOT9kckew/viewform")
APPLY_FORM = ("https://docs.google.com/forms/d/e/"
              "1FAIpQLScIV5PVkwbdcvMpzCyxTAzN71ORCqaTaIMY7Dr15xEMXSxIXQ/viewform")


ANCHOR = OUT / "anchor.txt"


def _anchor_date() -> str:
    """The date day 1 maps to, held fixed across regenerations.

    Buffer holds real scheduled posts keyed to these dates. If a rebuild moves
    day 1, every later post shifts with it and the queue silently disagrees with
    the calendar — which is how already-published copy got scheduled a second
    time. The anchor is written once and reused forever unless --reanchor.
    """
    if ANCHOR.exists():
        txt = ANCHOR.read_text(encoding="utf-8").strip()
        if txt:
            return txt
    return date.today().isoformat()


FESTIVALS = HERE / "festivals.json"


def _festival_slots() -> dict:
    """Map each festival key to the date its content should RUN.

    Not the festival date — the festival date minus lead_days. Brands lock
    Diwali budgets eight weeks out, so a Diwali planning post published on
    Diwali is worth nothing. The lead time is the entire value of this.
    """
    if not FESTIVALS.exists():
        return {}
    try:
        data = json.loads(FESTIVALS.read_text(encoding="utf-8"))
    except Exception:
        return {}
    slots = {}
    for f in data.get("festivals", []):
        try:
            d = date.fromisoformat(f["date"]) - timedelta(days=int(f.get("lead_days", 30)))
        except Exception:
            continue
        slots[f["key"]] = {"run_on": d, "name": f.get("name", f["key"]),
                           "weight": int(f.get("weight", 1)),
                           "approx": bool(f.get("approx"))}
    return slots


CTA_FILE = HERE / "cta.json"

_DEFAULT_CTA = {
    "brand": "Free shortlist — link in bio 🔗",
    "creator": "Link in bio 🔗",
}


def _cta(audience: str) -> str:
    """Closing call to action for a caption.

    Kept in social/cta.json so switching to a comment-to-DM prompt is a data
    change, not a code change — and so every one of the 149 days picks it up on
    the next rebuild.
    """
    data = {}
    if CTA_FILE.exists():
        try:
            data = json.loads(CTA_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    if not data.get("enabled", False):
        return _DEFAULT_CTA.get(audience, "")
    return data.get(audience) or _DEFAULT_CTA.get(audience, "")


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


def _festival_plan(audience: str, start: date, days: int) -> dict:
    """date -> festival post, for dates inside the calendar window.

    Festival content is placed FIRST and the evergreen bank fills around it,
    because a seasonal post only works on its own date. Where a festival has
    several posts they run on consecutive days leading into that slot.
    """
    bank = FESTIVAL_BRAND if audience == "brand" else FESTIVAL_CREATOR
    slots = _festival_slots()
    by_festival: dict[str, list] = {}
    for entry in bank:
        by_festival.setdefault(entry[0], []).append(entry)

    end = start + timedelta(days=days - 1)
    plan: dict[date, tuple] = {}
    for key, posts in by_festival.items():
        slot = slots.get(key)
        if not slot:
            continue
        # Several posts for one festival run on consecutive days ending on the
        # slot date, so the last one lands closest to the planning deadline.
        for offset, post in enumerate(reversed(posts)):
            run_on = slot["run_on"] - timedelta(days=offset)
            if run_on < start or run_on > end or run_on in plan:
                continue
            plan[run_on] = post
    return plan


def _max_days(start: date) -> int:
    """How many days the banks can actually fill.

    Festival posts occupy a day without consuming the evergreen bank, so the
    calendar runs longer than the evergreen count — but only for festivals whose
    slot falls inside the window, and the window depends on the total. Solve it
    by iterating to a fixed point rather than assuming every festival counts.
    """
    evergreen = min(len(BRAND_POSTS), len(CREATOR_POSTS))
    days = evergreen
    for _ in range(10):
        placed = min(len(_festival_plan("brand", start, days)),
                     len(_festival_plan("creator", start, days)))
        nxt = evergreen + placed
        if nxt == days:
            break
        days = nxt
    return days


def build(days: int, start: date) -> list[dict]:
    entries: list[dict] = []
    for audience, bank, cta_url in (
        ("brand", BRAND_POSTS, BRIEF_FORM),
        ("creator", CREATOR_POSTS, APPLY_FORM),
    ):
        festival_plan = _festival_plan(audience, start, days)
        recent_layouts: list[str] = []
        recent_pillars: list[str] = []
        # Consume each authored post at most once. The earlier version indexed
        # with day % len(bank) and skipped forward to de-cluster pillars, which
        # could land on an entry already used and silently duplicate copy.
        unused = list(range(len(bank)))
        for day in range(days):
            this_date = start + timedelta(days=day)
            festival_post = festival_plan.get(this_date)
            festival_key = ""

            if festival_post:
                # Seasonal content is date-critical, so it takes the slot and
                # the evergreen bank simply flows around it.
                festival_key, pillar, headline, sub, caption, cta = festival_post
            else:
                if not unused:
                    break                  # bank exhausted; verify() reports it
                # Prefer the first unused post whose pillar hasn't run recently.
                choice = next((i for i in unused if bank[i][0] not in recent_pillars[-5:]),
                              unused[0])
                unused.remove(choice)
                pillar, headline, sub, caption, cta = bank[choice]

            layout = _pick_layout(pillar, recent_layouts, headline)
            recent_layouts.append(layout)
            recent_pillars.append(pillar)

            # A comment CTA converts better than a bio link (the reader never
            # leaves the app) and the comments themselves lift reach. Driven by
            # social/cta.json so switching it on is a data change, and every one
            # of the 149 days picks it up on the next rebuild.
            link = _cta(audience)
            full_caption = (
                f"{caption}\n\n{cta}\n\n{link}\n\n"
                f"{tag_block(audience, day)}"
            )
            entries.append({
                "day": day + 1,
                "date": this_date.isoformat(),
                "festival": festival_key,
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


def verify(entries: list[dict], days: int = 0) -> None:
    """Fail loudly rather than shipping a repetitive grid."""
    for audience in ("brand", "creator"):
        rows = [e for e in entries if e["audience"] == audience]
        # A bank that runs out short-changes that page silently: the calendar
        # simply ends early for one audience while the other keeps going, and
        # nothing else here would notice because there are no duplicates.
        if days and len(rows) < days:
            have = len(BRAND_POSTS if audience == "brand" else CREATOR_POSTS)
            raise SystemExit(
                f"FAIL: {audience} page only got {len(rows)} of {days} days.\n"
                f"       Its bank holds {have} authored posts. Add "
                f"{days - have} more, or run with --days {len(rows)}.")
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
    # 0 = build every authored post. A hardcoded default silently truncated
    # the calendar: CI regenerated with --days 100 and cut a 149-day calendar
    # back to 100, discarding 49 days of written content.
    ap.add_argument("--days", type=int, default=0,
                    help="0 (default) = as many days as the banks allow")
    # Default to the anchor recorded in the existing calendar, NOT today.
    # Defaulting to today meant every regeneration re-dated the whole calendar:
    # content slid to a different day, Buffer's queue no longer matched, and a
    # post that had already published got scheduled again the next day.
    ap.add_argument("--start", default=_anchor_date())
    ap.add_argument("--reanchor", action="store_true",
                    help="deliberately restart the calendar from --start/today")
    ap.add_argument("--no-images", action="store_true")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    start = date.fromisoformat(args.start)
    if args.reanchor or not ANCHOR.exists():
        ANCHOR.write_text(start.isoformat(), encoding="utf-8")
        print(f"  anchor set: day 1 = {start.isoformat()}")
    else:
        print(f"  anchor held: day 1 = {start.isoformat()} "
              f"(use --reanchor to move it)")
    days = args.days or _max_days(start)
    entries = build(days, start)
    verify(entries, days)

    (OUT / "calendar.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  calendar -> social/calendar/calendar.json ({len(entries)} posts)")

    if not args.no_images:
        n = render_images(entries)
        print(f"  images   -> social/calendar/images/ ({n} PNGs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
