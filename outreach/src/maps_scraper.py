"""CollabHive Outreach — Google Maps brand extractor (Playwright, OPTIONAL).

PURPOSE
-------
This is a MANUAL / on-demand "data builder". Run it locally (or via a
workflow_dispatch) to discover small/startup brands across Indian niches from
Google Maps and write them into the brand seed pool. The DAILY automation does
NOT run this — it stays free/safe on the curated seed pool.

WARNING
-------
Scraping Google Maps violates Google's Terms of Service and can result in IP
throttling or account blocks. Use sparingly, low volume, and at your own risk.
Prefer the Places API (paid) or manual curation for long-term reliability.

WHAT IT EXTRACTS
----------------
Per place: name, category, address, city, website, phone, rating, reviews,
latitude/longitude. Emails are NOT available on Maps — our separate
brands.enrich / email extractor pulls emails from each website afterwards.

USAGE
-----
    python -m outreach.src.maps_scraper --write            # append to seed pool
    python -m outreach.src.maps_scraper --niches 3 --limit 6   # subset + smaller run
    python -m outreach.src.maps_scraper --no-write        # dry run (print only)

REQUIRES (local only; not needed by the daily GitHub Action)
    pip install playwright
    playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path

# Allow running as a module from anywhere: add the outreach/ package root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.common import ROOT, load_config, log, save_json  # noqa: E402

MAPS_URL = "https://www.google.com/maps/search/{query}"


def build_search_url(query: str, city: str) -> str:
    q = f"{query} in {city}" if city else query
    return MAPS_URL.format(query=urllib.parse.quote(q))


def run_scrape(cfg: dict, niches_filter: int, limit_per_query: int, write: bool) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        log("Playwright not installed. Run: pip install playwright && playwright install chromium")
        log(f"Import error: {exc}")
        return []

    brand_domain_blacklist = ("google.com", "google.co.in", "facebook.com", "instagram.com")

    # Niche PICK based on filters; default: rotate across all niches.
    categories = cfg["niches"]["categories"]
    if niches_filter:
        categories = categories[:niches_filter]
    elif args_daily_rotation(cfg):
        from datetime import datetime
        idx = int(datetime.now().strftime("%w")) % len(categories)
        categories = [categories[idx]]

    found: dict[str, dict] = {}
    from .protect import Throttle
    throttle = Throttle(
        max_per_hour=cfg.get("discovery", {}).get("max_places_per_run", 25),
        session_cap=50,               # hard stop for a whole manual session
        backoff_after_failures=3,
        min_gap=3.0,
        max_gap=14.0,
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=cfg["emails"].get("user_agent", "CollabHive/1.0"),
            locale="en-IN",
        )

        for cat in categories:
            niche = cat["niche"]
            for query in cat.get("queries", cat.get("keywords", [])):
                for city in cat.get("cities", []):
                    if throttle.is_circuit_open():
                        log("Circuit breaker open — stopping scrape (too many failures).")
                        browser.close()
                        return list(found.values())
                    if throttle.session_exhausted():
                        log("Session cap reached — stopping scrape for now.")
                        browser.close()
                        return list(found.values())
                    throttle.wait()
                    url = build_search_url(query, city)
                    results = scrape_query(page, url, limit_per_query)
                    # Treat an empty/unreachable result as a soft failure.
                    throttle.record(ok=len(results) > 0)
                    for r in results:
                        r["niche"] = niche
                        r["city"] = city
                        r["source"] = "google_maps"
                        website = (r.get("website") or "").lower()
                        if website and any(d in website for d in brand_domain_blacklist):
                            r["website"] = ""
                        key = r["name"].lower()
                        if key not in found:
                            found[key] = r
                    log(f"  [{niche}] '{query}' '{city}' -> {len(results)} places "
                        f"(total {len(found)}, session {throttle._session_count})")
                    time.sleep(throttle._pressure * 2.0 + 1.5)

        browser.close()

    results = list(found.values())

    if write:
        pool_file = ROOT / cfg["brands"]["seed_file"]
        existing = load_seed(pool_file)
        seen = {b.get("name", "").lower() for b in existing}
        added = 0
        for r in results:
            if r["name"].lower() in seen:
                continue
            existing.append({
                "name": r["name"],
                "niche": r["niche"],
                "city": r["city"],
                "website": r.get("website", ""),
                "phone": r.get("phone", ""),
                "email": "",
                "emails": [],
                "source": "google_maps",
            })
            seen.add(r["name"].lower())
            added += 1
        save_json(pool_file, existing)
        log(f"Wrote {added} new brands to {pool_file} (total {len(existing)}).")
    return results


def args_daily_rotation(cfg: dict) -> bool:
    return False  # keep whole-net scrape unless --niches is given


def load_seed(pool_file: Path) -> list[dict]:
    if not pool_file.exists():
        return []
    with open(pool_file, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError:
            data = []
    return data if isinstance(data, list) else []


def scrape_query(page, url: str, limit: int) -> list[dict]:
    """Open one Maps search and pull up to `limit` place details."""
    results: list[dict] = []
    try:
        page.goto(url, timeout=45000, wait_until="domcontentloaded")
        time.sleep(3.5)
        _dismiss_consent(page)

        # Wait for the result feed.
        try:
            page.wait_for_selector("div[role='feed']", timeout=15000)
        except Exception:
            pass

        handles = page.query_selector_all("a[aria-label][href*='/maps/place/']")
        if not handles:
            handles = page.query_selector_all("div[role='feed'] > div > div > a")
        if not handles:
            return results

        for handle in handles[:limit]:
            name = handle.get_attribute("aria-label") or "Unknown"
            try:
                handle.click(timeout=5000)
                time.sleep(1.6)
                detail = _read_detail_panel(page, name)
                results.append(detail)
            except Exception as exc:
                log(f"    skip '{name}': {exc}")
                continue
    except Exception as exc:
        log(f"  query failed ({url[:60]}...): {exc}")
    return results


def _read_detail_panel(page, name: str) -> dict:
    detail = {"name": name, "website": "", "phone": "", "category": "",
              "address": "", "rating": "", "reviews": "", "lat": "", "lng": ""}
    try:
        title_el = page.query_selector("h1")
        if title_el:
            detail["name"] = title_el.inner_text().strip() or name
    except Exception:
        pass

    # Website link.
    for sel in ("a[href^='http']", "a[data-item-id='authority']", "a[jsaction*='website']"):
        try:
            el = page.query_selector(sel)
            if el:
                href = el.get_attribute("href") or ""
                if href and "google." not in href:
                    detail["website"] = href
                    break
        except Exception:
            continue

    # Phone.
    try:
        el = page.query_selector("button[data-item-id^='phone']")
        if el:
            detail["phone"] = el.inner_text().strip()
    except Exception:
        pass

    # Rating + reviews.
    try:
        el = page.query_selector("div.F7nice span[aria-hidden='true']")
        if el:
            detail["rating"] = el.inner_text().strip()
        rev = page.query_selector("div.F7nice span[aria-label*='review']")
        if rev:
            label = rev.get_attribute("aria-label") or ""
            import re
            m = re.search(r"[\d,]+", label)
            if m:
                detail["reviews"] = m.group(0)
    except Exception:
        pass

    # Category + address from the info block.
    try:
        info_el = page.query_selector("button[jsaction*='category']")
        if info_el:
            detail["category"] = info_el.inner_text().strip()
    except Exception:
        pass
    try:
        addr_el = page.query_selector("button[jsaction*='address']")
        if addr_el:
            detail["address"] = addr_el.inner_text().strip()
    except Exception:
        pass

    return detail


def _dismiss_consent(page) -> None:
    for text in ("Accept all", "I agree", "Reject all"):
        try:
            btn = page.query_selector(f"button:has-text('{text}')")
            if btn:
                btn.click(timeout=2000)
                time.sleep(0.6)
                break
        except Exception:
            continue
    # Sometimes a "Stay signed out" prompt appears.
    try:
        stay = page.query_selector("button:has-text('Stay signed out')")
        if stay:
            stay.click(timeout=2000)
            time.sleep(0.6)
    except Exception:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Google Maps brand extractor (optional)")
    parser.add_argument("--niches", type=int, default=0, help="scrape first N niches")
    parser.add_argument("--limit", type=int, default=6, help="places per query (stay low)")
    parser.add_argument("--write", action="store_true", help="append results to seed pool")
    parser.add_argument("--config", default=str(ROOT / "config.json"), help="path to config.json")
    args = parser.parse_args(argv)

    cfg = load_config(Path(args.config))

    log(f"Google Maps scrape (limit={args.limit}/query, write={args.write})")
    log("WARNING: this may violate Google ToS. Use sparingly.")
    results = run_scrape(cfg, args.niches, args.limit, args.write)
    log(f"Done. {len(results)} unique places found.")
    if not args.write:
        for r in results[:20]:
            log(f"  - {r.get('name')} | {r.get('category')} | {r.get('website')} | {r.get('city')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
