"""CollabHive Outreach — daily WhatsApp lead harvest (brands + creators).

Collects ONLY contact details that the business/creator has published
themselves for enquiries: a wa.me / api.whatsapp.com link, a tel: link, or a
mobile number on their own contact/collab page, or the business phone on a
Google Maps listing. Personal numbers are never guessed, and nothing is pulled
from inside Instagram.

The leads (they hold phone numbers) go to the PRIVATE Supabase table
`wa_leads`, never to this public git repo. The admin page `whatsapp.html`
reads that table and sends via one-click wa.me links, capped server-side at
10 first messages + 5 follow-ups per IST day.

Needs the env var SUPABASE_SERVICE_KEY (GitHub secret). Without it the run
harvests nothing to disk and says so.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from .common import ROOT, env, load_json, log

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

_WA_LINK = re.compile(
    r"(?:wa\.me/|api\.whatsapp\.com/send\?[^\"'\s>]*?phone=|whatsapp://send\?[^\"'\s>]*?phone=)\+?(\d{10,13})",
    re.I)
_TEL_LINK = re.compile(r"tel:\s*([+\d][\d\s().-]{8,16})", re.I)
_IG_HANDLE = re.compile(r"instagram\.com/([A-Za-z0-9_.]{2,30})/?(?:[\"'?#\s<]|$)", re.I)
_IG_SKIP = {"p", "reel", "reels", "explore", "accounts", "stories", "tv", "about",
            "developer", "legal", "direct"}


def normalize_phone(raw: str) -> str:
    """Indian WhatsApp-capable mobile -> '91XXXXXXXXXX', else ''."""
    d = re.sub(r"\D", "", raw or "")
    if len(d) == 12 and d.startswith("91"):
        d = d[2:]
    elif len(d) == 11 and d.startswith("0"):
        d = d[1:]
    if len(d) == 10 and d[0] in "6789" and len(set(d)) > 3:
        return "91" + d
    return ""


def extract_contacts(html: str) -> dict:
    phones: list[str] = []
    for m in _WA_LINK.finditer(html):
        p = normalize_phone(m.group(1))
        if p and p not in phones:
            phones.append(p)
    for m in _TEL_LINK.finditer(html):
        p = normalize_phone(m.group(1))
        if p and p not in phones:
            phones.append(p)
    handles = []
    for m in _IG_HANDLE.finditer(html):
        h = m.group(1).lower().rstrip(".")
        if h not in _IG_SKIP and h not in handles:
            handles.append(h)
    return {"phones": phones, "handles": handles}


def _get(url: str, timeout: int = 8) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-IN,en"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read(600_000).decode("utf-8", "ignore")
    except Exception:
        return ""


def _search(query: str, n: int = 10) -> list[str]:
    html = _get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query), 12)
    urls = []
    for m in re.finditer(r'uddg=([^&"\']+)', html):
        u = urllib.parse.unquote(m.group(1))
        host = urllib.parse.urlparse(u).netloc.lower()
        if any(b in host for b in ("instagram.com", "facebook.com", "youtube.com", "duckduckgo",
                                    "linkedin.com", "twitter.com", "x.com")):
            continue
        if u not in urls:
            urls.append(u)
        if len(urls) >= n:
            break
    return urls


# ---------------------------------------------------------------- Supabase
def _sb(cfg: dict) -> tuple[str, str]:
    url = (cfg.get("leads", {}).get("supabase_url") or "").rstrip("/")
    return url, env("SUPABASE_SERVICE_KEY", "")


def _sb_request(cfg: dict, method: str, path: str, body=None, prefer: str = "") -> object:
    url, key = _sb(cfg)
    headers = {"apikey": key, "Authorization": "Bearer " + key,
               "Content-Type": "application/json"}
    if prefer:
        headers["Prefer"] = prefer
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url + "/rest/v1/" + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    return json.loads(raw) if raw else []


def existing_phones(cfg: dict) -> set[str]:
    have: set[str] = set()
    off = 0
    while True:
        rows = _sb_request(cfg, "GET", f"wa_leads?select=phone&limit=1000&offset={off}")
        have.update(r["phone"] for r in rows)
        if len(rows) < 1000:
            return have
        off += 1000


def push(cfg: dict, leads: list[dict]) -> int:
    if not leads:
        return 0
    rows = _sb_request(cfg, "POST", "wa_leads?on_conflict=phone", leads,
                       prefer="resolution=ignore-duplicates,return=representation")
    return len(rows)


# --------------------------------------------------------------- harvesting
def _today_idx() -> int:
    import datetime
    return datetime.date.today().toordinal()


def harvest_brands(cfg: dict, have: set[str], target: int, budget_s: int) -> list[dict]:
    """Brands: Maps-listing phones already in the pool, then wa.me/tel on sites."""
    out: list[dict] = []
    seen = set(have)
    pool = load_json(ROOT / cfg["brands"]["seed_file"])
    pool = pool if isinstance(pool, list) else []
    end = time.time() + budget_s
    for b in pool:
        if len(out) >= target or time.time() > end:
            break
        cands = []
        if b.get("phone"):
            cands.append((normalize_phone(b["phone"]), "google_maps_listing"))
        if not cands or not cands[0][0]:
            cands = []
            if b.get("website"):
                found = extract_contacts(_get(b["website"]))["phones"]
                cands = [(p, b["website"]) for p in found[:1]]
        for phone, src in cands:
            if phone and phone not in seen:
                seen.add(phone)
                out.append({"kind": "brand", "name": b.get("name", ""), "niche": b.get("niche", ""),
                            "city": b.get("city", ""), "website": b.get("website", ""),
                            "phone": phone, "phone_source": src, "source": "brand_pool"})
    return out


def harvest_creators(cfg: dict, have: set[str], target: int, budget_s: int) -> list[dict]:
    """Creators: public collab/contact pages that publish a WhatsApp number."""
    out: list[dict] = []
    seen = set(have)
    cats = cfg["niches"]["categories"]
    end = time.time() + budget_s
    i = _today_idx()
    tried = 0
    while len(out) < target and time.time() < end and tried < len(cats) * 8:
        cat = cats[(i + tried) % len(cats)]
        kw = cat["keywords"][(i + tried // len(cats)) % len(cat["keywords"])]
        city = cat["cities"][(i + tried) % len(cat["cities"])]
        tried += 1
        q = f'{cat["niche"].split(" & ")[0]} influencer {city} "for collaborations" whatsapp {kw}'
        for page in _search(q):
            if len(out) >= target or time.time() > end:
                break
            c = extract_contacts(_get(page))
            if not c["phones"]:
                continue
            handle = c["handles"][0] if c["handles"] else ""
            for phone in c["phones"][:1]:
                if phone in seen:
                    continue
                seen.add(phone)
                out.append({"kind": "creator", "name": handle or urllib.parse.urlparse(page).netloc,
                            "handle": handle, "niche": cat["niche"], "city": city,
                            "website": page, "phone": phone, "phone_source": page,
                            "source": "public_web"})
            time.sleep(1.5)
    return out


def run_harvest(cfg: dict) -> dict:
    lc = cfg.get("leads", {})
    if not lc.get("enabled", True):
        return {"ok": True, "skipped": "disabled"}
    if not _sb(cfg)[1]:
        return {"ok": False, "skipped": "SUPABASE_SERVICE_KEY not set"}
    target = int(lc.get("daily_target_each", 100))
    budget = int(lc.get("max_minutes", 25)) * 60 // 2
    try:
        have = existing_phones(cfg)
        brands = harvest_brands(cfg, have, target, budget)
        creators = harvest_creators(cfg, have | {b["phone"] for b in brands}, target, budget)
        nb, nc = push(cfg, brands), push(cfg, creators)
    except (urllib.error.URLError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    res = {"ok": True, "brands_added": nb, "creators_added": nc, "target_each": target,
           "met_target": nb >= target and nc >= target}
    log(f"Lead harvest: {res}")
    return res
