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

import html as _html
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


_BLOCKED = ("instagram.com", "facebook.com", "youtube.com", "duckduckgo", "linkedin.com",
            "twitter.com", "x.com", "bing.com", "microsoft.com")


def _bing_target(href: str) -> str:
    """Bing wraps results in /ck/a?...&u=a1<base64url>; unwrap to the real URL."""
    import base64
    m = re.search(r"[?&]u=a1([A-Za-z0-9_-]+)", href)
    if not m:
        return href if href.startswith("http") else ""
    raw = m.group(1)
    try:
        return base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode("utf-8", "ignore")
    except Exception:
        return ""


def _search(query: str, n: int = 10) -> list[str]:
    """DuckDuckGo first, Bing as fallback (DDG throttles bursts with timeouts)."""
    urls: list[str] = []
    q = urllib.parse.quote(query)
    html = _get("https://html.duckduckgo.com/html/?q=" + q, 12)
    cands = [urllib.parse.unquote(m.group(1)) for m in re.finditer(r"uddg=([^&\"']+)", html)]
    if not cands:
        html = _get("https://www.bing.com/search?setlang=en-IN&cc=IN&q=" + q, 12)
        cands = [_bing_target(_html.unescape(m.group(1)))
                 for m in re.finditer(r'<li class="b_algo".*?<a[^>]+href="([^"]+)"', html, re.S)]
    for u in cands:
        if not u:
            continue
        host = urllib.parse.urlparse(u).netloc.lower()
        if any(b in host for b in _BLOCKED) or u in urls:
            continue
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


def existing_leads(cfg: dict) -> tuple[set[str], set[str], int]:
    """(phones, website hosts, brand count) already in the queue."""
    phones: set[str] = set()
    hosts: set[str] = set()
    brands = 0
    off = 0
    while True:
        rows = _sb_request(cfg, "GET", f"wa_leads?select=phone,website,kind&limit=1000&offset={off}")
        for r in rows:
            phones.add(r["phone"])
            h = urllib.parse.urlparse(r.get("website") or "").netloc.lower().removeprefix("www.")
            if h:
                hosts.add(h)
            brands += r["kind"] == "brand"
        if len(rows) < 1000:
            return phones, hosts, brands
        off += 1000


def push(cfg: dict, leads: list[dict]) -> int:
    if not leads:
        return 0
    rows = _sb_request(cfg, "POST", "wa_leads?on_conflict=phone", leads,
                       prefer="resolution=ignore-duplicates,return=representation")
    return len(rows)


# --------------------------------------------------------------- harvesting
def _today_idx() -> int:
    import os
    off = int(os.environ.get("LEADS_SEED_OFFSET", "0") or 0)
    import datetime
    return datetime.date.today().toordinal() + off


_SKIP_HOSTS = ("amazon.", "flipkart.", "myntra.", "nykaa.com", "justdial.", "indiamart.", "wikipedia.",
               "quora.", "medium.", "reddit.", "pinterest.", "youtube.", "facebook.", "instagram.",
               "linkedin.", "twitter.", "x.com", "duckduckgo", "bing.", "google.", "tripadvisor.",
               "zomato.", "swiggy.", "yelp.", "sulekha.", "tofler.", "crunchbase.", "ambitionbox.",
               "glassdoor.", "naukri.", "shopify.com", "wordpress.", "blogspot.", "ndtv.", "timesofindia.",
               "economictimes.", "hindustantimes.", "forbes.", "yourstory.", "inc42.", "entrackr.",
               "mouthshut.", "trustpilot.", "cdn", "assets", "static", "fonts", "gstatic", "googleapis", "api.",
               "t.me", "whatsapp", "apple.com", "play.google", "cloudflare", "jsdelivr", "unpkg", "w3.org",
               "schema.org", "gravatar", "cambridge.", "merriam", "dictionary", "thefreedictionary",
               "meesho.", "ajio.", "tatacliq.", "shopsy.", "snapdeal.", "paytm.", "jiomart.", "bigbasket.",
               "firstcry.", "lenskart.", "toprankers", "shopifycdn", "myntassets", "github.", "gov.in",
               "nic.in", "pexels.", "unsplash.", "canva.", "freepik.", "w.org", "gmpg.org", "ytimg", "analytics", "tagmanager", "moengage", "wp.me", "bit.ly", "wa.me",
               "cloudfront", "kinsta", "stats.", "visualwebsiteoptimizer", "adbutler", "tally.so", "mordor", "wix.", "godaddy.", "cars24.", "olx.", "99acres.")
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_BAD_MAIL = ("sentry", "example.", "wixpress", "domain.com", ".png", ".jpg", ".webp", ".svg", ".js", "@2x")
_CONTACT_PATHS = ("/pages/contact-us", "/contact-us", "/contact", "/pages/contact", "/about-us", "/pages/about-us")
_TEXT_PHONE = re.compile(r"(?:\+91[\s-]?|0)?([6-9]\d{4}[\s-]?\d{5})")


def _site_name(html: str, host: str) -> str:
    m = re.search(r"property=[\"']og:site_name[\"'][^>]*content=[\"']([^\"']{2,60})", html, re.I)
    if not m:
        m = re.search(r"<title[^>]*>([^<]{2,80})</title>", html, re.I)
    name = _html.unescape((m.group(1) if m else host)).strip()
    name = re.split(r"\s[|–—-]\s", name)[0].strip()
    if name.lower() in ("results", "home", "welcome", "shop", "index", "just a moment...", "403 forbidden"):
        name = host.split(".")[0].title()
    return name[:60] or host


def _scan_site(url: str) -> dict | None:
    """Home + contact pages of one brand site -> name, mobile numbers, emails."""
    parts = urllib.parse.urlparse(url)
    if not parts.netloc:
        return None
    base = f"{parts.scheme or 'https'}://{parts.netloc}"
    host = parts.netloc.lower().removeprefix("www.")
    home = _get(base, 7)
    if not home:
        return None
    pages = [home]
    for path in _CONTACT_PATHS[:4]:
        h = _get(base + path, 6)
        if h:
            pages.append(h)
            if len(pages) >= 3:
                break
    phones: list[str] = []
    emails: list[str] = []
    for h in pages:
        for p in extract_contacts(h)["phones"]:
            if p not in phones:
                phones.append(p)
        # Numbers written as plain text only count when labelled as a contact line.
        for m in _TEXT_PHONE.finditer(re.sub(r"<[^>]+>", " ", h)):
            ctx = re.sub(r"<[^>]+>", " ", h)[max(0, m.start() - 40):m.start()].lower()
            if any(w in ctx for w in ("call", "whatsapp", "contact", "phone", "mobile", "support", "customer")):
                p = normalize_phone(m.group(1))
                if p and p not in phones:
                    phones.append(p)
        for e in _EMAIL.findall(h):
            e = e.lower()
            if e not in emails and not any(b in e for b in _BAD_MAIL):
                emails.append(e)
    if not phones and not emails:
        return None
    return {"name": _site_name(home, host), "website": base, "host": host,
            "phones": phones[:2], "emails": emails[:3]}


def discover_brand_sites(cfg: dict, budget_s: int, max_sites: int, seen_hosts: set[str]) -> list[str]:
    """Search-engine discovery of brand storefronts, rotating niche x keyword x city."""
    cats = cfg["niches"]["categories"]
    end = time.time() + budget_s
    found: list[str] = []
    hosts = set(seen_hosts)
    combos = [(c, k, city) for c in cats for k in c["keywords"] for city in c["cities"]]
    import random
    random.Random(_today_idx()).shuffle(combos)
    patterns = ["Indian D2C {kw} brands list", "best Indian {kw} brands to buy online",
                "emerging {kw} startups India d2c brands", "{kw} brands based in {city} India"]
    for n, (cat, kw, city) in enumerate(combos):
        if time.time() > end or len(found) >= max_sites:
            break
        q = patterns[n % len(patterns)].format(kw=kw, city=city)
        for u in _search(q, 8):
            host = urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
            if host and host not in hosts and not any(b in host for b in _SKIP_HOSTS):
                hosts.add(host)
                found.append(u)
                _niche_of[host] = (cat["niche"], city)
            # List articles link out to many brand storefronts; harvest those links.
            page = _get(u, 8)
            links = 0
            for m in re.finditer(r"href=[\"'](https?://[^\"'#?\s]+)", page):
                lu = m.group(1)
                lh = urllib.parse.urlparse(lu).netloc.lower().removeprefix("www.")
                if (not lh or lh == host or lh in hosts or any(b in lh for b in _SKIP_HOSTS)
                        or any(b in lh for b in _BLOCKED) or lh.count(".") > 2):
                    continue
                hosts.add(lh)
                found.append("https://" + lh)
                _niche_of[lh] = (cat["niche"], city)
                links += 1
                if links >= 40:
                    break
        time.sleep(3.0)
    return found


_niche_of: dict = {}


def harvest_brands(cfg: dict, have: set[str], target: int, budget_s: int, seen_hosts: set[str] | None = None) -> list[dict]:
    """Brands: pool phones + wa.me/tel/contact-page numbers from discovered brand sites."""
    from concurrent.futures import ThreadPoolExecutor
    out: list[dict] = []
    seen = set(have)
    seen_hosts = set(seen_hosts or ())
    pool = load_json(ROOT / cfg["brands"]["seed_file"])
    pool = pool if isinstance(pool, list) else []
    sites = [b["website"] for b in pool if b.get("website")]
    for b in pool:
        if b.get("phone"):
            p = normalize_phone(b["phone"])
            if p and p not in seen:
                seen.add(p)
                out.append({"kind": "brand", "name": b.get("name", ""), "niche": b.get("niche", ""),
                            "city": b.get("city", ""), "website": b.get("website", ""),
                            "phone": p, "phone_source": "google_maps_listing", "source": "brand_pool"})
    t0 = time.time()
    sites += discover_brand_sites(cfg, int(budget_s * 0.4), target * 4, seen_hosts)
    rest = max(budget_s - (time.time() - t0), 30)
    end = time.time() + rest
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = []
        for u in sites:
            futs.append(ex.submit(_scan_site, u))
        for f in futs:
            if len(out) >= target or time.time() > end:
                break
            try:
                r = f.result(timeout=max(end - time.time(), 1))
            except Exception:
                continue
            if not r:
                continue
            niche, city = _niche_of.get(r["host"], ("", ""))
            for p in r["phones"][:1]:
                if p not in seen:
                    seen.add(p)
                    out.append({"kind": "brand", "name": r["name"], "niche": niche, "city": city,
                                "website": r["website"], "phone": p, "phone_source": r["website"],
                                "source": "brand_site", "_emails": r["emails"]})
        for f in futs:
            f.cancel()
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


def _merge_emails(cfg: dict, brands: list[dict]) -> int:
    """Public contact emails found on brand sites feed the email pool."""
    from .common import save_json
    path = ROOT / cfg["brands"]["seed_file"]
    pool = load_json(path)
    pool = pool if isinstance(pool, list) else []
    known = {urllib.parse.urlparse(b.get("website") or "").netloc.lower().removeprefix("www.") for b in pool}
    added = 0
    for b in brands:
        host = urllib.parse.urlparse(b.get("website") or "").netloc.lower().removeprefix("www.")
        if not b.get("_emails") or host in known:
            continue
        known.add(host)
        pool.append({"name": b["name"], "niche": b["niche"], "city": b["city"], "website": b["website"],
                     "email": b["_emails"][0], "emails": b["_emails"], "source": "web_discovery"})
        added += 1
    if added:
        save_json(path, pool)
    return added


def run_harvest(cfg: dict) -> dict:
    lc = cfg.get("leads", {})
    if not lc.get("enabled", True):
        return {"ok": True, "skipped": "disabled"}
    if not _sb(cfg)[1]:
        return {"ok": False, "skipped": "SUPABASE_SERVICE_KEY not set"}
    target = int(lc.get("daily_target_each", 100))
    goal = int(lc.get("total_brand_goal", 1000))
    budget = int(lc.get("max_minutes", 25)) * 60 // 2
    try:
        have, hosts, brand_total = existing_leads(cfg)
        brands, creators, ne = [], [], 0
        if brand_total < goal:
            brands = harvest_brands(cfg, have, target, budget, hosts)
            ne = _merge_emails(cfg, brands)
            for b in brands:
                b.pop("_emails", None)
        creators = harvest_creators(cfg, have | {b["phone"] for b in brands}, target, budget)
        nb, nc = push(cfg, brands), push(cfg, creators)
    except (urllib.error.URLError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    res = {"ok": True, "brands_added": nb, "creators_added": nc, "brand_total": brand_total + nb,
           "brand_goal": goal, "goal_reached": brand_total + nb >= goal, "emails_added": ne}
    log(f"Lead harvest: {res}")
    return res
