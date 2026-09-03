"""CollabHive Outreach — influencer publish & social onboarding module.

Takes the influencer applicants (from the public Google Form responses sheet)
and:
  * publish_creators -> push approved creators into the site's creator pool
    (data/creators_pool.json, read by the directory) and optionally into the
    live Supabase `creators` table so they appear on the website for brands.
  * draft_social_posts -> generate ready-to-post onboarding captions for
    Instagram / LinkedIn / X that welcome each new creator and mention their
    @handle + link.

Stdlib only. Persists to outreach/data/.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from .common import ROOT, load_config, load_json, log, save_json


# ---------- applicant sheet (public gviz) ----------
def _parse_gviz(text):
    m = re.search(r"google\.visualization\.Query\.setResponse\((.*)\);?\s*$", text)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
        table = data.get("table", {})
        cols = [c.get("label", "") for c in table.get("cols", [])]
        rows = []
        for r in table.get("rows", []):
            obj = {}
            c = r.get("c", [])
            for i, lab in enumerate(cols):
                v = c[i].get("v") if i < len(c) and c[i] else ""
                if isinstance(v, dict) and "$t" in v:
                    v = v["$t"]
                obj[lab] = v
            rows.append(obj)
        return rows
    except Exception:
        return []


def pull_applicants(cfg: dict) -> list[dict]:
    """Read the influencer application sheet into creator-shaped dicts."""
    sid = cfg["publish"].get("applicant_sheet_id", "")
    if not sid:
        return []
    url = ("https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:json&headers=1" % sid)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            text = resp.read().decode("utf-8", "ignore")
    except Exception:
        return []
    rows = _parse_gviz(text)
    creators = []
    for r in rows:
        name = r.get("Full name", "")
        handle = _norm_handle(r.get("Instagram handle", ""))
        if not name and not handle:
            continue
        creators.append({
            "name": name,
            "handle": handle,
        "niche": r.get("Primary content niche", ""),
        "city": _clean_city(r.get("City & country", "")),
        "followers": _to_int(r.get("Followers (total across platforms)", "")),
        "rate_internal": _clean_rate(r.get("Your rate (starting from)", "")),
        "platforms": r.get("Platforms you create on", ""),
        "email": (r.get("Email address", "") or "").strip().lower(),
        "phone": r.get("Phone / WhatsApp", ""),
        "about": r.get("Links to your best 3 recent posts", ""),
        "source": "applicant",
    })
    return creators


def _norm_handle(h: str) -> str:
    h = (h or "").strip()
    if not h:
        return ""
    if not h.startswith("@"):
        h = "@" + h
    return h.split("?")[0].strip()


def _clean_city(c: str) -> str:
    c = (c or "").strip()
    # Drop trailing country/state noise; keep the city.
    c = re.split(r",\s*(india|in|pakistan|bangladesh|nepal|sri lanka|dubai)\s*$", c, flags=re.I)[0]
    c = re.split(r"\(\s*", c)[0]
    c = re.sub(r"\s*,\s*,+\s*", ", ", c).strip(" ,")
    return c[:40] if c else ""


def _to_int(v):
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip().replace(",", "").lower()
    mult = 1
    if "m" in s[:3] or s.endswith("m"):
        mult = 1000000
    elif "k" in s[:3] or s.endswith("k"):
        mult = 1000
    elif "l" in s[:3] or s.endswith("l"):  # lakh
        mult = 100000
    num = re.sub(r"[^\d.]", "", s)
    if not num:
        return 0
    try:
        return int(float(num) * mult)
    except ValueError:
        return 0


def _clean_rate(r):
    if not r:
        return ""
    return re.sub(r"\s+", " ", str(r)).strip()


def _strip_private(c: dict) -> dict:
    """Remove internal fields (rate/price/contact) before public publishing."""
    out = {}
    for k, v in c.items():
        if k in ("rate", "rate_internal", "email", "phone", "about"):
            continue  # never expose rate, price, or direct contact publicly
        out[k] = v
    return out


# ---------- publish to pool + site ----------
def publish_creators(cfg: dict) -> dict:
    pcfg = cfg.get("publish", {})
    if not pcfg.get("enabled", True):
        return {"published": 0, "skipped": "disabled"}
    applicants = pull_applicants(cfg)
    if not applicants:
        return {"published": 0, "skipped": "no_applicants"}

    pool_file = ROOT / pcfg.get("creator_pool_file", "data/creators_pool.json")
    pool = load_json(pool_file)
    pool = pool if isinstance(pool, list) else []
    by_handle = {(c.get("handle") or "").lower(): c for c in pool if isinstance(c, dict)}

    min_fb = pcfg.get("min_followers_publish", 0)
    added = 0
    updated = 0
    published = []
    for a in applicants:
        if not a.get("name") or not a.get("handle"):
            continue
        if a.get("followers", 0) < min_fb:
            continue
        key = a["handle"].lower()
        entry = {k: v for k, v in a.items() if v not in (None, "", [], 0)}
        if key in by_handle:
            # Update existing record with any new fields.
            changed = False
            for k, v in entry.items():
                if k not in by_handle[key] or not by_handle[key].get(k):
                    by_handle[key][k] = v
                    changed = True
            if changed:
                updated += 1
            published.append(by_handle[key])
        else:
            by_handle[key] = entry
            pool.append(entry)
            published.append(entry)
            added += 1

    save_json(pool_file, pool)

    # Public record: strip rate/price so it's never shown on the site.
    public = [_strip_private(c) for c in published]
    published_file = ROOT / pcfg.get("published_file", "data/published_creators.json")
    save_json(published_file, {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(public),
        "creators": public,
    })

    # Publish to the live site's Supabase `creators` table (optional).
    site_result = "not_configured"
    if pcfg.get("publish_to_site", True):
        site_result = _publish_to_supabase(cfg, public)

    log(f"Publish: added={added}, updated={updated}, site={site_result}")
    return {"published": len(published), "added": added, "updated": updated, "site": site_result}


def _publish_to_supabase(cfg, creators) -> dict:
    """Insert approved creators into the Supabase `creators` table (postgrest)."""
    supabase_url = _env_url(cfg)  # from config.js
    anon_key = _env_anon(cfg)
    if not supabase_url or not anon_key:
        return "no_supabase_config"

    # Existing handles so we never duplicate a creator on the site.
    existing = _fetch_existing_handles(supabase_url, anon_key)

    created = 0
    for c in creators:
        handle = c.get("handle", "").lower()
        if handle and handle in existing:
            continue
        row = {
            "name": c.get("name", ""),
            "handle": c.get("handle", ""),
            "niche": c.get("niche", ""),
            "followers": _followers_str(c.get("followers", "")),
            "city": c.get("city", ""),
            # No rate/price and no email are ever published publicly.
            "links": c.get("about", "") or c.get("platforms", ""),
            "about": c.get("about", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
        }
        try:
            req = urllib.request.Request(
                supabase_url.rstrip("/") + "/rest/v1/creators",
                data=json.dumps(row).encode(),
                headers={
                    "apikey": anon_key,
                    "Authorization": "Bearer " + anon_key,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal",
                },
                method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status in (200, 201):
                    created += 1
        except Exception as exc:
            log(f"  supabase insert {c.get('handle')}: {exc}")
    return {"created": created, "total": len(creators)}


def _fetch_existing_handles(supabase_url, anon_key) -> set:
    try:
        req = urllib.request.Request(supabase_url.rstrip("/") + "/rest/v1/creators?select=handle",
                                     headers={"apikey": anon_key, "Authorization": "Bearer " + anon_key})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rows = json.loads(resp.read().decode("utf-8", "ignore"))
        return {r.get("handle", "").lower() for r in rows if isinstance(r, dict)}
    except Exception:
        return set()


def _env_url(cfg):
    """Supabase URL from outreach config, or parse the site's assets/js/config.js."""
    if cfg.get("supabase", {}).get("url"):
        return cfg["supabase"]["url"]
    return _parse_site_config().get("url", "")


def _env_anon(cfg):
    if cfg.get("supabase", {}).get("anon_key"):
        return cfg["supabase"]["anon_key"]
    return _parse_site_config().get("anon", "")


def _parse_site_config() -> dict:
    """Read supabaseUrl / supabaseAnonKey from the site's assets/js/config.js."""
    try:
        cfg_js = (ROOT.parent / "assets" / "js" / "config.js").read_text(encoding="utf-8")
    except Exception:
        return {}
    out = {}
    m = re.search(r'supabaseUrl:\s*"([^"]+)"', cfg_js)
    if m:
        out["url"] = m.group(1)
    m = re.search(r'supabaseAnonKey:\s*"([^"]+)"', cfg_js)
    if m:
        out["anon"] = m.group(1)
    return out


# ---------- social onboarding posts ----------
def draft_social_posts(cfg: dict) -> dict:
    scfg = cfg.get("social", {})
    if not scfg.get("enabled", True):
        return {"drafted": 0, "skipped": "disabled"}

    published = load_json(ROOT / cfg["publish"]["published_file"])
    published = published if isinstance(published, dict) else {}
    creators = published.get("creators", []) if isinstance(published, dict) else []
    if not creators:
        return {"drafted": 0, "skipped": "no_published"}

    hashtags = scfg.get("hashtags", [])
    site_url = cfg["profile"]["site_url"]
    platforms = scfg.get("platforms", ["instagram", "linkedin", "x"])
    include_link = scfg.get("include_link", True)
    include_handle = scfg.get("include_handle", True)

    # Existing drafts (dedupe by handle so we don't re-draft).
    drafts_file = ROOT / scfg.get("drafts_file", "data/social_drafts.json")
    existing = load_json(drafts_file)
    by_handle = {}
    if isinstance(existing, list):
        for d in existing:
            by_handle[d.get("handle", "").lower()] = d

    drafts = []
    for c in creators:
        handle = c.get("handle", "")
        if not handle or handle.lower() in by_handle:
            continue
        post = build_post(cfg, c, hashtags, include_handle, include_link, site_url)
        drafts.append({
            "handle": handle,
            "name": c.get("name", ""),
            "niche": c.get("niche", ""),
            "followers": c.get("followers", 0),
            "city": c.get("city", ""),
            "platforms": {p: post.get(p, "") for p in platforms},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "posted": False,
        })
        by_handle[handle.lower()] = True

    # Merge with existing drafts.
    merged = existing if isinstance(existing, list) else []
    for d in drafts:
        merged.append(d)
    save_json(drafts_file, merged)
    return {"drafted": len(drafts), "total": len(merged)}


def build_post(cfg, c, hashtags, include_handle, include_link, site_url) -> dict:
    name = c.get("name", "this creator")
    handle = c.get("handle", "")
    niche = c.get("niche", "")
    followers = c.get("followers", 0)
    city = c.get("city", "")
    fb_str = _followers_str(followers)
    tag = "#" + " #".join(hashtags)

    intro = ("We're thrilled to welcome %s to the CollabHive creator network! 🎉"
             % (name if include_handle and not handle else (name + " %s" % handle)))

    niche_line = (" Specialist: %s." % niche) if niche else ""
    city_line = (" Based in %s." % city) if city else ""
    reach_line = (" With %s followers, they're ready to create authentic brand collabs."
                  % fb_str) if followers else ""
    cta_link = ("\n\nWant to collab? Start a campaign → %s" % site_url) if include_link else ""
    handle_tag = (" %s" % handle) if (include_handle and handle) else ""

    body = (intro + niche_line + city_line + reach_line + handle_tag +
            "\n\n" + tag + cta_link)

    ig = body
    li = ("🚀 New on CollabHive: %s is joining our creator network!\n\n"
          "Niche: %s\nLocation: %s\nFollowers: %s\n\n%s\n\n%s"
          % (name + (" (" + handle + ")" if handle else ""),
             niche or "Creator", city or "India", fb_str or "—", scf(), tag + cta_link))
    x = ("%s is now on CollabHive%s%s — ready for brand collabs. %s%s"
         % (name, (" (%s)" % handle) if handle else "", niche_line, tag, cta_link))
    return {"instagram": ig, "linkedin": li, "x": x}


def scf():
    return "CollabHive matches creators to brands across every niche."


def _followers_str(n) -> str:
    try:
        n = int(n)
        if n >= 1000000:
            return "%.1fM" % (n / 1000000)
        if n >= 1000:
            return "%.1fK" % (n / 1000)
        return str(n)
    except (ValueError, TypeError):
        return str(n or "")
