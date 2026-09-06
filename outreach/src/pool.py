"""CollabHive Outreach — automated brand pool refill.

Keeps the outreach brand pool topped up from a curated list of Indian D2C
brands (data/seed_brands_extra.json) so daily outreach never runs dry.

The curated list is the source of truth for NEW brands (name, niche, city,
website, and — where known — a public contact email). Each run merges any
brand not already in the pool, deduping by name and by website domain. Brands
that arrive without an email are enriched later by brands.refresh_brand_emails.
"""
from __future__ import annotations

from .common import ROOT, load_config, load_json, log, save_json


def _norm_domain(website: str) -> str:
    if not website:
        return ""
    w = website.strip().lower()
    for prefix in ("https://", "http://", "www."):
        w = w.replace(prefix, "")
    return w.split("/")[0]


def refill(cfg: dict) -> dict:
    """Merge curated brands into the seed pool. Returns counts."""
    curated_file = ROOT / cfg["pool"]["curated_file"]
    pool_file = ROOT / cfg["brands"]["seed_file"]
    curated = load_json(curated_file)
    if not isinstance(curated, list):
        curated = []
    pool = load_json(pool_file)
    if not isinstance(pool, list):
        pool = []

    existing_names = {b.get("name", "").lower().strip() for b in pool}
    existing_domains = {_norm_domain(b.get("website", "")) for b in pool}

    added = 0
    skipped = 0
    refreshed = 0
    for brand in curated:
        if not isinstance(brand, dict):
            continue
        name = (brand.get("name") or "").strip()
        if not name:
            continue
        domain = _norm_domain(brand.get("website", ""))
        if name.lower() in existing_names or (domain and domain in existing_domains):
            skipped += 1
            continue
        entry = {
            "name": name,
            "niche": brand.get("niche", ""),
            "city": brand.get("city", ""),
            "website": (brand.get("website") or "").strip(),
            "email": (brand.get("email") or "").strip(),
            "emails": [e.strip() for e in (brand.get("emails") or []) if e.strip()],
            "source": "curated",
        }
        if not entry["emails"] and entry["email"]:
            entry["emails"] = [entry["email"]]
        pool.append(entry)
        existing_names.add(name.lower())
        if domain:
            existing_domains.add(domain)
        added += 1

    if added:
        save_json(pool_file, pool)
        log(f"Pool refill: added {added} curated brand(s) (total {len(pool)}).")

    return {
        "added": added,
        "skipped_dupes": skipped,
        "pool_total": len(pool),
        "pool_with_email": sum(1 for b in pool if b.get("emails") or b.get("email")),
    }


def pool_health(cfg: dict) -> dict:
    """Report current pool size and how many targets remain."""
    pool_file = ROOT / cfg["brands"]["seed_file"]
    pool = load_json(pool_file)
    if not isinstance(pool, list):
        pool = []
    with_email = [b for b in pool if (b.get("emails") or [b.get("email", "")])[0]]
    return {
        "pool_total": len(pool),
        "with_email": len(with_email),
        "without_email": len(pool) - len(with_email),
    }
