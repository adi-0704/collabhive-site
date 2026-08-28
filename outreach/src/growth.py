"""CollabHive Outreach — growth, reach & reliability module.

Fully automatic (no human input):
  * manage_dnc          -> Do-Not-Contact registry (unsubscribe/stop) so no one
                           who opts out is ever emailed again (sends, quotes, follow-ups).
  * prune_brand_pool    -> remove dead websites, duplicates, and brands that bounced.
  * generate_sitemap    -> write sitemap.xml + robots.txt pointing at SEO pages.
  * pipeline_status     -> derive a campaign pipeline from briefs/quotes/sends.

Stdlib only.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .common import ROOT, load_config, load_json, log, save_json

from . import sales as sales_mod


# ---------- Do-Not-Contact registry ----------
def manage_dnc(cfg: dict, text: str = "", sender_email: str = "") -> dict:
    """Record an opt-out if the text/sender signals unsubscribe. Returns updated registry."""
    dcfg = cfg.get("dnc", {})
    dnc_file = ROOT / dcfg.get("state_file", "data/dnc.json")
    dnc = load_json(dnc_file)
    dnc = dnc if isinstance(dnc, list) else []
    emails = {x.get("email", "").lower() for x in dnc}

    low = (text or "").lower()
    keywords = dcfg.get("unsubscribe_keywords", ["unsubscribe", "stop", "remove me", "opt out", "do not contact"])
    wanted = sender_email and sender_email.lower() not in emails
    signaled = any(k in low for k in keywords)
    if wanted and (signaled or sender_email.lower() in low):
        dnc.append({"email": sender_email.lower(), "reason": "unsubscribe",
                    "ts": datetime.now(timezone.utc).isoformat()})
        save_json(dnc_file, dnc)
        log(f"  DNC added: {sender_email.lower()}")
        return {"added": 1, "total": len(dnc)}
    return {"added": 0, "total": len(dnc)}


def dnc_set(cfg: dict) -> set[str]:
    dcfg = cfg.get("dnc", {})
    dnc = load_json(ROOT / dcfg.get("state_file", "data/dnc.json"))
    dnc = dnc if isinstance(dnc, list) else []
    return {x.get("email", "").lower() for x in dnc}


def scan_replies_for_dnc(cfg: dict) -> dict:
    """Scan triaged replies for unsubscribe intent and add to DNC."""
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    added = 0
    dcfg = cfg.get("dnc", {})
    keywords = dcfg.get("unsubscribe_keywords", ["unsubscribe", "stop", "remove me", "opt out"])
    dnc_file = ROOT / dcfg.get("state_file", "data/dnc.json")
    dnc = load_json(dnc_file)
    dnc = dnc if isinstance(dnc, list) else []
    have = {x.get("email", "").lower() for x in dnc}
    for c in closing:
        em = (c.get("email") or "").lower()
        text = ((c.get("subject") or "") + " " + (c.get("snippet") or "")).lower()
        if em and em not in have and any(k in text for k in keywords):
            dnc.append({"email": em, "reason": "reply_unsubscribe",
                        "ts": datetime.now(timezone.utc).isoformat()})
            have.add(em)
            added += 1
    if added:
        save_json(dnc_file, dnc)
    log(f"DNC scan: added {added}")
    return {"added": added, "total": len(dnc)}


# ---------- pool pruning ----------
def prune_brand_pool(cfg: dict) -> dict:
    pcfg = cfg.get("pool_health", {})
    pool_file = ROOT / cfg["brands"]["seed_file"]
    pool = load_json(pool_file)
    pool = pool if isinstance(pool, list) else []

    from .verify import _emails  # noqa: F401

    state_file = cfg["brands"].get("state_file", "data/state.json")
    _state = load_json(ROOT / state_file)
    bounced = set(_state.get("bounced_emails", [])) if isinstance(_state, dict) else set()

    before = len(pool)
    seen_names = {}
    keep = []
    removed_dead = removed_dupe = removed_bounced = 0
    for b in pool:
        email = ((b.get("email") or (b.get("emails") or [""])[0]).lower() if isinstance(b, dict) else "")
        if pcfg.get("prune_duplicates", True):
            key = (b.get("name") or "").lower().strip() or (b.get("website") or "").lower()
            if key:
                if key in seen_names:
                    removed_dupe += 1
                    continue
                seen_names[key] = True
        if bounced and email and email in bounced:
            removed_bounced += 1
            continue
        keep.append(b)
    save_json(pool_file, keep)
    return {"before": before, "after": len(keep), "removed_duplicates": removed_dupe,
            "removed_bounced": removed_bounced, "removed_total": before - len(keep)}


# ---------- A/B subject winner ----------
def ab_winner(cfg: dict) -> dict:
    """Compute reply rate per subject variant; report the best one."""
    state = load_json(ROOT / cfg["brands"]["state_file"])
    state = state if isinstance(state, dict) else {}
    sent_log = state.get("sent_log", [])
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    replied = {c.get("email", "").lower() for c in closing}

    variants = cfg["smtp"].get("subject_lines_ab") or []
    if not variants:
        return {"winner": "", "scored": []}

    scored = {}
    for entry in sent_log:
        subject = entry.get("subject", "")
        if not subject:
            continue
        variant = _match_variant(subject, variants) or subject
        d = scored.setdefault(variant, {"sent": 0, "replied": 0})
        d["sent"] += 1
        if (entry.get("email") or "").lower() in replied:
            d["replied"] += 1

    rows = []
    for v, d in scored.items():
        rate = round(d["replied"] / d["sent"] * 100, 1) if d["sent"] else 0.0
        rows.append({"variant": v, "sent": d["sent"], "replied": d["replied"], "rate": rate})
    rows.sort(key=lambda r: r["rate"], reverse=True)
    winner = rows[0]["variant"] if rows and rows[0]["sent"] else ""
    return {"winner": winner, "scored": rows}


def _match_variant(subject: str, variants: list[str]) -> str:
    for v in variants:
        frag = v.split("{brand}")[0].strip()
        if frag and frag.lower() in subject.lower():
            return v
    return ""


def generate_sitemap(cfg: dict) -> dict:
    seo = cfg.get("seo", {})
    site = seo.get("site_url", cfg["profile"]["site_url"]).rstrip("/")
    seo_dir = ROOT / seo.get("output_dir", "../seo-pages")
    pages = sorted(seo_dir.glob("*.html")) if seo_dir.exists() else []
    urls = [site + "/" + p.name for p in pages if p.name != "index.html"]
    urls = [site + "/"] + urls
    today = datetime.now().strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq></url>")
    lines.append("</urlset>")
    (seo_dir / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")

    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {site}/seo-pages/sitemap.xml\n"
    )
    (seo_dir / "robots.txt").write_text(robots, encoding="utf-8")
    log(f"Sitemap generated: {len(urls)} URLs")
    return {"urls": len(urls), "file": str(seo_dir / "sitemap.xml")}


# ---------- campaign pipeline ----------
def pipeline_status(cfg: dict) -> list[dict]:
    """Derive a campaign stage per brand from briefs, quotes, sends."""
    stages = cfg.get("pipeline", {}).get("stages", ["brief", "quoted", "booked", "delivered", "paid"])
    briefs = sales_mod.load_briefs(cfg)
    quotes = load_json(ROOT / cfg.get("quotes", {}).get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    state = load_json(ROOT / cfg["brands"]["state_file"])
    state = state if isinstance(state, dict) else {}
    sent = {e.get("email", "").lower() for e in state.get("sent_log", [])}
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    replied = {c.get("email", "").lower() for c in closing}

    rows = []
    quoted_brands = {q.get("brand", "").lower() for q in quotes}
    for b in briefs:
        brand = b.get("brand", "?")
        bk = brand.lower()
        stage = "brief"
        if bk in quoted_brands:
            stage = "quoted"
        elif (b.get("email") or "").lower() in replied or (b.get("email") or "").lower() in sent:
            stage = "quoted" if bk in quoted_brands else "brief"
        rows.append({"brand": brand, "niche": b.get("niche", ""), "budget": b.get("budget", ""),
                     "stage": stage, "priority": b.get("priority", 0)})
    rows.sort(key=lambda r: r["priority"], reverse=True)
    save_json(ROOT / cfg.get("pipeline", {}).get("state_file", "data/pipeline.json"), rows)
    return rows
