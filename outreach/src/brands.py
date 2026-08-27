"""CollabHive Outreach — brand lead generation.

Free, ToS-safe discovery:
  1. Load a curated seed pool of small/startup brands (data/brands_seed.json).
  2. For brands missing an email, fetch their website and extract public
     contact emails (regex + mailto: links + common contact pages).

No paid API and no Google Maps scraping. The seed pool is the source of
"which brands to target"; you grow it over time (or I can populate it).
"""
from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from .common import ROOT, load_config, log

EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
)
BANNED_DOMAINS = (
    "example.com", "sentry.io", "wixpress.com", "schema.org", "w3.org",
    "domain.com", "email.com", "yourdomain.com", "godaddy.com", "placeholder",
)
CONTACT_PATHS = ("", "contact", "contact-us", "contactus", "about", "about-us", "team", "careers")


def _fetch(url: str, timeout: int = 12, ua: str = "") -> str | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua or "CollabHive/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            content_type = resp.headers.get("Content-Type", "")
            if "html" not in content_type and "text" not in content_type:
                return None
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def _normalize_email(raw: str) -> str:
    return raw.strip().strip(".'\"<>;:,").lower().replace("%40", "@")


def _is_good(email: str, brand_domain: str) -> bool:
    if len(email) < 6 or "@" not in email:
        return False
    local, _, domain = email.partition("@")
    if not local or not domain:
        return False
    if domain in BANNED_DOMAINS:
        return False
    if any(b.lower() in domain for b in BANNED_DOMAINS):
        return False
    # Skip image/spam-looking addresses and role email list providers.
    if domain.endswith(".png") or domain.endswith(".jpg") or domain.endswith(".jpeg"):
        return False
    return True


def emails_from_html(html: str, brand_domain: str, limit: int = 3) -> list[str]:
    found: list[str] = []
    # mailto: links are the most reliable.
    for m in re.finditer(r'mailto:([^"\'\s>]+)', html, re.IGNORECASE):
        email = _normalize_email(m.group(1))
        if email and email not in found:
            found.append(email)
    # Generic emails anywhere in the page.
    for m in EMAIL_RE.finditer(html):
        email = _normalize_email(m.group(0))
        if email and email not in found:
            found.append(email)
    # Prefer emails that share the brand's domain.
    ranked = [e for e in found if brand_domain and brand_domain in e] + \
             [e for e in found if not (brand_domain and brand_domain in e)]
    out: list[str] = []
    for e in ranked:
        if _is_good(e, brand_domain) and e not in out:
            out.append(e)
        if len(out) >= limit:
            break
    return out


def brand_emails(brand: dict, ua: str, timeout: int, limit: int = 3) -> list[str]:
    """Return discovered emails for a brand. brand['website'] is required."""
    website = (brand.get("website") or "").strip()
    if not website:
        return []
    if not website.startswith("http"):
        website = "https://" + website
    parsed = urllib.parse.urlparse(website)
    brand_domain = parsed.netloc.lower().replace("www.", "")
    base = f"{parsed.scheme}://{parsed.netloc}"

    html = _fetch(website, timeout, ua)
    emails: list[str] = []
    if html:
        emails = emails_from_html(html, brand_domain, limit)
    if len(emails) < limit:
        for path in CONTACT_PATHS:
            if path == "":
                continue
            page = _fetch(f"{base}/{path}", timeout, ua)
            if page:
                for e in emails_from_html(page, brand_domain, limit - len(emails)):
                    if e not in emails:
                        emails.append(e)
                if len(emails) >= limit:
                    break
            time.sleep(0.2)
    return emails[:limit]


def enrich_brand(brand: dict, ua: str, timeout: int, limit: int = 3) -> dict:
    """Given a seed brand (with website), add discovered emails."""
    brand = dict(brand)
    existing = [e for e in brand.get("emails", []) if _is_good(e, "")]
    if not existing or len(existing) < limit:
        try:
            found = brand_emails(brand, ua, timeout, limit)
            merged: list[str] = []
            for e in list(existing) + found:
                e = _normalize_email(e)
                if e not in merged and _is_good(e, ""):
                    merged.append(e)
            brand["emails"] = merged[:limit]
        except Exception:
            brand["emails"] = existing
    else:
        brand["emails"] = existing
    if brand.get("emails"):
        brand["has_email"] = True
    else:
        brand["has_email"] = False
    return brand


def load_seed_pool(cfg: dict) -> list[dict]:
    from .common import load_json
    seed_file = ROOT / cfg["brands"]["seed_file"]
    rows = load_json(seed_file)
    if not isinstance(rows, list):
        rows = []
    return rows


def refresh_brand_emails(cfg: dict) -> dict:
    """Re-enrich every seed brand that has a website. Returns counts."""
    ua = cfg["emails"].get("user_agent", "CollabHive/1.0")
    timeout = cfg["emails"].get("fetch_timeout_seconds", 12)
    limit = cfg["emails"].get("max_emails_per_brand", 3)
    pool = load_seed_pool(cfg)
    cap = cfg["emails"].get("fetch_max_brands_per_run", 12)
    updated = 0
    processed = 0
    for idx, brand in enumerate(pool):
        if not brand.get("website"):
            continue
        # Re-skip brands that already have emails, and cap per-run work so the
        # daily job stays well within its time budget (unreachable sites are slow).
        if brand.get("emails") or (processed >= cap):
            continue
        before = len(brand.get("emails", []))
        enriched = enrich_brand(brand, ua, timeout, limit)
        pool[idx] = enriched
        processed += 1
        if enriched.get("emails") and len(enriched["emails"]) > before:
            updated += 1
    from .common import save_json
    save_json(ROOT / cfg["brands"]["seed_file"], pool)
    return {"brands": len(pool), "with_emails": sum(1 for b in pool if b.get("emails")), "updated": updated, "processed": processed}


def select_targets(cfg: dict, state: dict, limit: int) -> tuple[list[dict], dict]:
    """Pick up to `limit` unsent brands, rotating across niches/cities.

    Returns (selected_brands, updated_state). Skips brands already emailed
    and brands with no email. Rotates niche per day so outreach spreads over
    the week.
    """
    pool = load_seed_pool(cfg)
    if not isinstance(state, dict):
        state = {}
    sent = set(state.get("emailed_domains", []))
    sent_emails = set(state.get("emailed_emails", []))

    candidates: list[dict] = []
    for b in pool:
        if not isinstance(b, dict):
            continue
        emails = b.get("emails") or ([b["email"]] if b.get("email") else [])
        email = (b.get("email") or (emails[0] if emails else "") or "").strip().lower()
        domain = ((b.get("website") or "").lower().replace("https://", "").replace("http://", "").split("/")[0]).replace("www.", "")
        if not email or email in sent_emails:
            continue
        if domain and domain in sent:
            continue
        b = dict(b)
        b["email"] = email
        b["emails"] = b.get("emails") or [email]
        candidates.append(b)

    # Order for niche rotation: prefer today's niche, spread cities.
    from datetime import datetime as _dt, timedelta
    today_idx = int(_dt.now().strftime("%w"))
    niches = cfg["niches"]["categories"]
    primary = niches[today_idx % len(niches)]["niche"]
    candidates.sort(key=lambda b: (b.get("niche") != primary, b.get("city") or ""))

    selected = candidates[:limit]
    return selected, state
