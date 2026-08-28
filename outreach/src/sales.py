"""CollabHive Outreach — sales & reach module.

Purely automatic (no human input):
  * triage_replies  -> Gmail IMAP scan of replies to outreach emails; classify
                       as interested/negotiating/declined and build a closing queue.
  * match_briefs    -> score brand briefs against the creator pool; emit a
                       daily shortlist of best-fit creators per brief.
  * build_quote     -> generate a campaign quote (rate * posts + commission).
  * generate_seo    -> programmatic niche x city SEO landing pages.

All state persists to outreach/data/ so results show in the dashboard and the
static site. Uses stdlib only.
"""
from __future__ import annotations

import json
import random
import re
import time
import urllib.request
from datetime import datetime, timedelta, timezone

from .common import ROOT, env, load_config, load_json, log, save_json

COMMISSION_LABEL = "commission_pct"


# ---------- reply triage (Gmail IMAP) ----------
def _imap_search(cfg: dict, user: str, password: str, hours: int):
    """Return raw (headers, subject, from_email, snippet) tuples of recent inbox mail."""
    import imaplib
    import email as email_lib
    from email.header import decode_header, make_header

    host = cfg["sales"].get("imap_host", "imap.gmail.com")
    port = cfg["sales"].get("imap_port", 993)
    try:
        conn = imaplib.IMAP4_SSL(host, port, timeout=30)
    except Exception as exc:
        log(f"IMAP connect failed: {exc}")
        return []
    try:
        conn.login(user, password)
        conn.select("INBOX")
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%d-%b-%Y")
        status, data = conn.search(None, f'(SINCE "{since}")')
        ids = data[0].split() if data and data[0] else []
        out: list[dict] = []
        seen: set[str] = set()
        for num in ids[-60:]:  # cap scan
            try:
                status, msg_data = conn.fetch(num, "(RFC822.HEADER BODY[TEXT])")
                raw = msg_data[0][1]
                email_lib.message_from_bytes(raw)
                # fetch header
                hdr = _fetch_header(conn, num)
                frm = hdr.get("from", "")
                subj = hdr.get("subject", "")
                frm_email = _extract_email(frm)
                if frm_email and frm_email.lower() not in seen and frm_email.lower() != user.lower():
                    seen.add(frm_email.lower())
                    snippet = _fetch_snippet(conn, num)
                    out.append({"from": frm_email, "subject": subj, "snippet": snippet})
            except Exception:
                continue
        return out
    except Exception as exc:
        log(f"IMAP search failed: {exc}")
        return []
    finally:
        try:
            conn.logout()
        except Exception:
            pass


def _fetch_header(conn, num):
    import email as email_lib
    status, data = conn.fetch(num, "(BODY.PEEK[HEADER])")
    if not data or not data[0]:
        return {}
    try:
        msg = email_lib.message_from_bytes(data[0][1])
    except Exception:
        return {}
    out = {}
    for k in ("from", "subject", "to"):
        v = msg.get(k)
        if v:
            try:
                out[k] = str(make_header(decode_header(v)))
            except Exception:
                out[k] = v
    return out


def _fetch_snippet(conn, num):
    import email as email_lib
    status, data = conn.fetch(num, "(BODY[TEXT])")
    if not data or not data[0]:
        return ""
    try:
        msg = email_lib.message_from_bytes(data[0][1])
    except Exception:
        return ""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True) or b""
                try:
                    body = body.decode("utf-8", "ignore")
                except Exception:
                    body = ""
                break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            try:
                body = payload.decode("utf-8", "ignore")
            except Exception:
                body = ""
    return " ".join(body.split())[:400]


def _extract_email(value: str) -> str:
    m = re.search(r"[\w.\-+]+@[\w.\-]+\.\w+", value or "")
    return m.group(0) if m else ""


def classify_reply(text: str, cfg: dict) -> str:
    low = (text or "").lower()
    kw = cfg["sales"].get("reply_keywords", {})
    if any(k in low for k in kw.get("declined", [])):
        return "declined"
    if any(k in low for k in kw.get("negotiating", [])):
        return "negotiating"
    if any(k in low for k in kw.get("interested", [])):
        return "interested"
    return "unknown"


def triage_replies(cfg: dict) -> dict:
    """Scan inbox for replies to our brand outreach and update the closing queue."""
    user = cfg["smtp"]["username"]
    password = env("OUTREACH_EMAIL_PASS", "")
    if not password:
        log("No OUTREACH_EMAIL_PASS set — reply triage needs Gmail IMAP credentials.")
        return {"triage": "skipped", "reason": "no_password"}

    hours = cfg["sales"].get("reply_lookback_hours", 48)
    msgs = _imap_search(cfg, user, password, hours)
    if not msgs:
        return {"scanned": 0, "new": 0, "triage": "no_replies"}

    closing_file = ROOT / cfg["sales"]["closing_file"]
    existing = load_json(closing_file)
    closing = existing if isinstance(existing, list) else []
    by_email = {c.get("email", "").lower(): c for c in closing}

    new = 0
    queued_by_status = {"interested": 0, "negotiating": 0, "declined": 0, "unknown": 0}
    for m in msgs:
        em = m["from"].lower()
        status = classify_reply(m["subject"] + " " + m["snippet"], cfg)
        if status == "unknown":
            continue
        if em in by_email:
            continue
        closing.append({
            "email": m["from"],
            "subject": m["subject"],
            "snippet": m["snippet"],
            "status": status,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        by_email[em] = True
        new += 1
        queued_by_status[status] = queued_by_status.get(status, 0) + 1
        log(f"  [{status.upper()}] {m['from']} | {m['subject']}")

    save_json(closing_file, closing)
    return {"scanned": len(msgs), "new": new, "triage": "ok", "by_status": queued_by_status}


# ---------- auto-match (briefs <-> creators) ----------
def _norm_niche(n: str) -> str:
    return (n or "").strip().lower()


def _tokens_intersect(a: str, b: str) -> bool:
    ta = set(_norm_niche(a).split())
    tb = set(_norm_niche(b).split())
    # also allow partial substring match across words
    low_a, low_b = _norm_niche(a), _norm_niche(b)
    if ta & tb:
        return True
    if low_a and low_b and (low_a in low_b or low_b in low_a):
        return True
    return False


def _score(brief: dict, creator: dict) -> float:
    """Heuristic 0..1 score: niche match, city match, budget fit, reach."""
    score = 0.0
    niche_match = _tokens_intersect(brief.get("niche", ""), creator.get("niche", ""))
    if niche_match:
        score += 0.4
    city_match = _norm_niche(brief.get("city", "")).strip() \
        and _tokens_intersect(brief.get("city", ""), creator.get("city", ""))
    if city_match:
        score += 0.25
    budget = _to_int(brief.get("budget", ""))
    rate = _to_int(creator.get("rate", ""))
    followers = _to_int(creator.get("followers", ""))
    if budget and rate:
        # how many creators the budget can afford; more affordable fit = better
        afford = min(1.0, budget / (rate * 4))
        score += 0.2 * afford
    if followers:
        score += 0.15 * min(1.0, followers / 40000)
    return round(score, 3)


def _to_int(v) -> int:
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(v)
    s = re.sub(r"[^\d]", "", str(v))
    return int(s) if s else 0


def load_creators(cfg: dict) -> list[dict]:
    """Creator pool: prefer applicant sheet (public gviz), fall back to seed file."""
    pool_file = ROOT / cfg["sales"]["creator_pool_file"]
    seed = load_json(pool_file)
    seed = seed if isinstance(seed, list) else []
    return seed


def load_briefs(cfg: dict) -> list[dict]:
    """Brand briefs from the brief form sheet (if public) + seed file."""
    rows = _load_brief_sheet(cfg)
    f = ROOT / cfg["sales"]["brand_briefs_file"]
    seed = load_json(f)
    seed = seed if isinstance(seed, list) else []
    rows.extend(seed)
    return [b for b in rows if _norm_niche(b.get("status", "active")).strip() not in ("closed", "done", "won")]


def _load_brief_sheet(cfg: dict) -> list[dict]:
    """Read the CollabHive Brand Briefs sheet via the public gviz JSON endpoint.

    Maps the sheet columns (brand, name, email, city, goal, niche, budget,
    creators, posts) into brief-ish objects. Returns [] if not readable.
    """
    sid = cfg["sales"].get("brand_briefs_sheet_id", "")
    if not sid:
        return []
    url = ("https://docs.google.com/spreadsheets/d/%s/gviz/tq?tqx=out:json&headers=1" % sid)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            text = resp.read().decode("utf-8", "ignore")
        data = _parse_gviz(text)
    except Exception:
        return []
    briefs = []
    for row in data:
        briefs.append({
            "brand": row.get("Brand / business name", "") or row.get("brand", ""),
            "niche": row.get("Which niche are you in (or closest to)?", "") or row.get("niche", ""),
            "city": row.get("City & country", "") or row.get("city", ""),
            "budget": row.get("Budget range (INR)", "") or row.get("budget", ""),
            "goal": row.get("What is your primary goal?", "") or row.get("goal", ""),
            "note": row.get("Describe your campaign / product", "") or row.get("note", ""),
            "status": "sheet",
        })
    return briefs


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


def match_briefs(cfg: dict) -> dict:
    briefs = load_briefs(cfg)
    creators = load_creators(cfg)
    if not briefs:
        return {"matched": 0, "reason": "no_briefs"}
    if not creators:
        return {"matched": 0, "reason": "no_creators"}
    max_per = cfg["sales"].get("max_shortlist_per_brief", 6)
    shortlist = []
    for brief in briefs:
        scored = []
        for c in creators:
            s = _score(brief, c)
            if s > 0:
                scored.append({"creator": c, "score": s})
        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[:max_per]
        shortlist.append({
            "brand": brief.get("brand", "?"),
            "niche": brief.get("niche", ""),
            "city": brief.get("city", ""),
            "budget": brief.get("budget", ""),
            "goal": brief.get("goal", ""),
            "note": brief.get("note", ""),
            "matches": [
                {"name": m["creator"].get("name"), "handle": m["creator"].get("handle"),
                 "niche": m["creator"].get("niche"), "city": m["creator"].get("city"),
                 "followers": m["creator"].get("followers"), "rate": m["creator"].get("rate"),
                 "score": m["score"]} for m in top
            ],
        })
    out_file = ROOT / cfg["sales"]["shortlist_file"]
    save_json(out_file, {"generated_at": datetime.now(timezone.utc).isoformat(), "shortlist": shortlist})
    return {"matched": len(shortlist), "briefs": len(briefs), "creators": len(creators)}


# ---------- auto quote builder ----------
def build_quote(cfg: dict, brief: dict, creators: list[dict]) -> dict:
    """Generate a campaign quote: sum(rate*posts) + commission."""
    posts = max(1, int(brief.get("posts", 1)))
    total = sum(_to_int(c.get("rate", 0)) * posts for c in creators)
    commission = round(total * cfg["sales"].get("commission_pct", 10) / 100, 2)
    total_with_commission = round(total + commission, 2)
    return {
        "brand": brief.get("brand", "?"),
        "creators": [c.get("handle", "") for c in creators],
        "posts_per_creator": posts,
        "creator_payout": total,
        "commission": commission,
        "commission_pct": cfg["sales"].get("commission_pct", 10),
        "total": total_with_commission,
        "currency": "INR",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------- programmatic SEO pages ----------
def generate_seo(cfg: dict) -> dict:
    seo = cfg.get("seo", {})
    if not seo.get("enabled", True):
        return {"pages": 0, "skipped": "disabled"}
    creators = load_creators(cfg)
    niches = cfg["niches"]["categories"]
    out_dir = ROOT / seo.get("output_dir", "../seo-pages")
    out_dir.mkdir(parents=True, exist_ok=True)
    site = seo.get("site_url", cfg["profile"]["site_url"])
    page_count = 0
    links = []
    for cat in niches:
        niche = cat["niche"]
        for city in cat.get("cities", []):
            matches = [c for c in creators
                       if _tokens_intersect(niche, c.get("niche", ""))
                       and _tokens_intersect(city, c.get("city", ""))]
            if len(matches) < 2:
                continue
            slug = f"{_slug(niche)}-in-{_slug(city)}"
            page_count += 1
            html = _render_seo_page(niche, city, matches, site, cfg)
            (out_dir / f"{slug}.html").write_text(html, encoding="utf-8")
            links.append((niche, city, slug, len(matches)))
    # Index page (crawlable entry point).
    idx = _render_seo_index(links, site)
    (out_dir / "index.html").write_text(idx, encoding="utf-8")
    return {"pages": page_count, "dir": str(out_dir)}


def _render_seo_index(links, site) -> str:
    rows = "".join(
        f"<tr><td>{_esc(n)}</td><td>{_esc(c)}</td><td><a href='{slug}.html'>{slug}</a></td><td>{m}</td></tr>"
        for n, c, slug, m in links
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Influencers by Niche & City — CollabHive</title>
<meta name="robots" content="index,follow"><link rel="canonical" href="{site}">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
<style>body{{font-family:'Plus Jakarta Sans',sans-serif;background:#f8f8fb;color:#1b1a21;margin:0}}
.wrap{{max-width:1000px;margin:0 auto;padding:40px 20px}}table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #ececf1;border-radius:12px}}
th,td{{padding:12px 16px;text-align:left;border-bottom:1px solid #f0f0f4;font-size:.9rem}}th{{color:#8a8a99;font-size:.78rem;text-transform:uppercase}}
a{{color:#6C3BFF;text-decoration:none}}</style></head><body><div class="wrap">
<h1>Influencer Marketing — every niche &amp; city</h1>
<p>Curated creator directories on CollabHive by niche and location.</p>
<table><thead><tr><th>Niche</th><th>City</th><th>Page</th><th>Creators</th></tr></thead><tbody>{rows}</tbody></table>
<p><a href="{site}">← Back to CollabHive</a></p>
</div></body></html>"""


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _render_seo_page(niche, city, creators, site, cfg) -> str:
    cards = ""
    for c in creators[:12]:
        rate = c.get("rate") or 0
        fb = c.get("followers") or 0
        cards += _creator_card(c, site)
    desc = f"Best {niche} influencers in {city} on CollabHive. Curated creators for brand collaborations across {city}. Book {niche} creators with fair 10% commission."
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{niche} Influencers in {city} — CollabHive</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{site}">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
<style>
body{{font-family:'Plus Jakarta Sans',sans-serif;background:#f8f8fb;color:#1b1a21;margin:0}}
.wrap{{max-width:1100px;margin:0 auto;padding:40px 20px}}
h1{{font-size:2rem;margin:0}} .sub{{color:#8a8a99;margin:8px 0 32px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:16px}}
.card{{background:#fff;border:1px solid #ececf1;border-radius:14px;padding:20px}}
.card h3{{margin:0 0 4px}}.handle{{color:#6C3BFF;font-weight:600;font-size:.9rem}}
.meta{{color:#8a8a99;font-size:.82rem;margin-top:6px}}
.btn{{display:inline-block;background:#6C3BFF;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:700;margin-top:32px}}
</style></head><body><div class="wrap">
<h1>{niche} Influencers in {city}</h1>
<div class="sub">Curated {niche} creators on CollabHive ready for brand collaborations. Fair 10% commission, creators keep 90%.</div>
<div class="grid">{cards}</div>
<a class="btn" href="{site}">Explore all creators →</a>
</div></body></html>"""


def _creator_card(c: dict, site) -> str:
    fb = c.get("followers") or 0
    fb_str = f"{fb/1000:.1f}K" if fb >= 1000 else str(fb)
    rate = c.get("rate") or 0
    return (f"<div class='card'><h3>{_esc(c.get('name') or 'Creator')}</h3>"
            f"<div class='handle'>{_esc(c.get('handle') or '')}</div>"
            f"<div class='meta'>{_esc(c.get('niche') or '')} · {fb_str} followers</div>"
            f"<div class='meta'>From ₹{rate:,}/post</div></div>")


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
