"""CollabHive — content analytics engine.

Not just a report. This measures every published post, decides which topics and
designs are actually earning attention, and writes weights that the calendar
generator reads — so the content plan adapts to evidence instead of instinct.

    python social/insights.py              # full report + weights
    python social/insights.py --json       # machine-readable
    python social/insights.py --weights    # just the weights table

Three things it is deliberately careful about:

  * Reach-normalised scoring. Raw engagement rewards whichever post the
    algorithm happened to distribute, not the post that deserved it.
  * Sample size. One post is an anecdote. Confidence scales with volume, and
    weights stay near neutral until a pillar has enough posts to justify moving.
  * Trend, not just average. A pillar that was strong in month one and weak in
    month three is a different story from a flat average, and the average hides
    it completely.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

HERE = pathlib.Path(__file__).parent.resolve()
REPO = HERE.parent
sys.path.insert(0, str(REPO / "outreach"))

from src.buffer import _gql, buffer_key          # noqa: E402
from src.common import load_config                # noqa: E402

CAL = HERE / "calendar" / "calendar.json"
OUT = HERE / "calendar" / "insights.json"
WEIGHTS_FILE = HERE / "calendar" / "weights.json"

# What genuinely signals the content landed. A save or a share is intent; a
# follow is the strongest signal available; a reaction is largely reflex.
WEIGHTS = {"Saves": 4.0, "Shares": 4.0, "Follows": 5.0, "Comments": 3.0, "Reactions": 1.0}

# Below this many posts a pillar cannot move its own weight much — otherwise a
# single lucky post would reshape months of planning.
MIN_CONFIDENT_POSTS = 6
WEIGHT_FLOOR, WEIGHT_CEIL = 0.5, 2.0


def log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(enc, "replace").decode(enc, "replace"), flush=True)


def fetch_sent(cfg: dict, channel_id: str) -> list[dict]:
    """Every published post on a channel, with metrics. Paginated."""
    org = cfg.get("buffer", {}).get("organization_id", "")
    rows: list[dict] = []
    after = ""
    for _ in range(20):
        cursor = ', after: "%s"' % after if after else ""
        q = ('query { posts(first: 50%s, input: { organizationId: "%s", '
             'filter: { channelIds: ["%s"], status: [sent] } }) '
             '{ pageInfo { hasNextPage endCursor } edges { node { id sentAt text '
             'metrics { name value } } } } }' % (cursor, org, channel_id))
        r = _gql(cfg, q)
        if isinstance(r, dict) and r.get("errors"):
            raise RuntimeError(r["errors"][0].get("message", "")[:140])
        page = ((r.get("data") or {}).get("posts") or {})
        rows += [e["node"] for e in (page.get("edges") or [])]
        info = page.get("pageInfo") or {}
        if not info.get("hasNextPage"):
            break
        after = info.get("endCursor") or ""
        if not after:
            break
    return rows


def score(metrics: dict) -> float:
    """Weighted engagement per 100 reach."""
    reach = max(float(metrics.get("Reach") or 0), 1.0)
    weighted = sum(WEIGHTS.get(k, 0) * float(metrics.get(k) or 0) for k in WEIGHTS)
    return round(weighted / reach * 100, 2)


def collect(cfg: dict) -> list[dict]:
    """Published posts joined back to the calendar entry that produced them."""
    entries = json.loads(CAL.read_text(encoding="utf-8")) if CAL.exists() else []
    by_marker = {e["caption_body"].splitlines()[0][:80]: e for e in entries}

    results: list[dict] = []
    for audience, cid in (cfg.get("buffer", {}).get("channels", {}) or {}).items():
        if not cid:
            continue
        for post in fetch_sent(cfg, cid):
            metrics = {m["name"]: m["value"] for m in (post.get("metrics") or [])}
            text = post.get("text") or ""
            entry = by_marker.get(text.splitlines()[0][:80] if text else "")
            results.append({
                "audience": audience,
                "sent_at": (post.get("sentAt") or "")[:10],
                "headline": (entry or {}).get("headline", "(not in calendar)"),
                "pillar": (entry or {}).get("pillar", "unknown"),
                "layout": (entry or {}).get("layout", "unknown"),
                "festival": (entry or {}).get("festival", ""),
                "reach": float(metrics.get("Reach") or 0),
                "views": float(metrics.get("Views") or 0),
                "saves": float(metrics.get("Saves") or 0),
                "shares": float(metrics.get("Shares") or 0),
                "follows": float(metrics.get("Follows") or 0),
                "comments": float(metrics.get("Comments") or 0),
                "score": score(metrics),
            })
    return results


def _confidence(n: int) -> float:
    """0..1 — how much a group's result should be allowed to move decisions."""
    return min(1.0, n / MIN_CONFIDENT_POSTS)


def analyse(results: list[dict], key: str) -> list[dict]:
    """Group performance with a confidence-damped weight.

    The weight is what the calendar actually consumes. A pillar scoring double
    the average on two posts does NOT get a 2x weight — confidence pulls it back
    toward neutral until the sample justifies the claim.
    """
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for r in results:
        if r[key] in ("unknown", ""):
            continue
        buckets[(r["audience"], r[key])].append(r)

    out = []
    for audience in {a for a, _ in buckets}:
        rows = {k[1]: v for k, v in buckets.items() if k[0] == audience}
        all_scores = [x["score"] for grp in rows.values() for x in grp]
        baseline = statistics.mean(all_scores) if all_scores else 0.0

        for name, grp in rows.items():
            scores = [x["score"] for x in grp]
            avg = statistics.mean(scores)
            conf = _confidence(len(grp))
            # Ratio to the page's own baseline, damped by confidence.
            ratio = (avg / baseline) if baseline > 0 else 1.0
            weight = 1.0 + (ratio - 1.0) * conf
            out.append({
                "audience": audience, key: name, "posts": len(grp),
                "avg_score": round(avg, 2),
                "median_score": round(statistics.median(scores), 2),
                "avg_reach": round(statistics.mean([x["reach"] for x in grp]), 1),
                "total_follows": int(sum(x["follows"] for x in grp)),
                "confidence": round(conf, 2),
                "weight": round(max(WEIGHT_FLOOR, min(WEIGHT_CEIL, weight)), 2),
            })
    return sorted(out, key=lambda x: (x["audience"], -x["avg_score"]))


def trend(results: list[dict]) -> dict:
    """Recent 30 days vs everything before. Averages hide direction."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    out = {}
    for audience in {r["audience"] for r in results}:
        rows = [r for r in results if r["audience"] == audience]
        recent = [r["score"] for r in rows if r["sent_at"] >= cutoff]
        older = [r["score"] for r in rows if r["sent_at"] < cutoff]
        out[audience] = {
            "recent_posts": len(recent),
            "recent_avg": round(statistics.mean(recent), 2) if recent else None,
            "previous_avg": round(statistics.mean(older), 2) if older else None,
            "direction": (
                "improving" if recent and older and statistics.mean(recent) > statistics.mean(older)
                else "declining" if recent and older else "insufficient data"),
        }
    return out


def recommendations(pillars: list[dict], results: list[dict]) -> list[str]:
    """Plain-language actions, stated only where the sample supports them."""
    recs: list[str] = []
    total = len(results)
    if total < MIN_CONFIDENT_POSTS * 2:
        recs.append(f"Only {total} posts measured. Nothing below is conclusive yet — "
                    f"treat it as direction, not instruction.")

    for audience in sorted({p["audience"] for p in pillars}):
        rows = [p for p in pillars if p["audience"] == audience and p["posts"] >= 2]
        if len(rows) < 2:
            continue
        best = max(rows, key=lambda x: x["avg_score"])
        worst = min(rows, key=lambda x: x["avg_score"])
        if best["confidence"] >= 0.5:
            recs.append(f"[{audience}] write more '{best['pillar']}' — "
                        f"{best['avg_score']} avg over {best['posts']} posts.")
        if worst["avg_score"] < best["avg_score"] * 0.5 and worst["confidence"] >= 0.5:
            recs.append(f"[{audience}] '{worst['pillar']}' is underperforming at "
                        f"{worst['avg_score']} — cut back or change the angle.")

    zero = [r for r in results if r["score"] == 0 and r["reach"] > 0]
    if len(zero) > total * 0.4:
        recs.append(f"{len(zero)} of {total} posts got reach but zero saves, shares "
                    f"or follows. The content is being seen and not acted on — "
                    f"the CTA is the thing to change.")
    return recs


def build(cfg: dict) -> dict:
    results = collect(cfg)
    by_pillar = analyse(results, "pillar")
    by_layout = analyse(results, "layout")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "posts_measured": len(results),
        "matched_to_calendar": sum(1 for r in results if r["pillar"] != "unknown"),
        "trend": trend(results),
        "by_pillar": by_pillar,
        "by_layout": by_layout,
        "recommendations": recommendations(by_pillar, results),
        "top_posts": sorted(results, key=lambda x: x["score"], reverse=True)[:10],
        "weakest_posts": sorted([r for r in results if r["reach"] > 0],
                                key=lambda x: x["score"])[:5],
    }


def write_weights(data: dict) -> dict:
    """The file generate_calendar.py reads to bias pillar selection."""
    weights: dict[str, dict[str, float]] = {}
    for row in data["by_pillar"]:
        weights.setdefault(row["audience"], {})[row["pillar"]] = row["weight"]
    payload = {
        "generated_at": data["generated_at"],
        "posts_measured": data["posts_measured"],
        "_note": "Written by insights.py from real Buffer metrics. Weights are "
                 "damped by sample size, so a pillar needs volume before it can "
                 "meaningfully shift the plan. generate_calendar.py reads this.",
        "pillar_weights": weights,
    }
    WEIGHTS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    return payload


def report(data: dict) -> None:
    log(f"\nCONTENT ANALYTICS — {data['posts_measured']} published post(s), "
        f"{data['matched_to_calendar']} matched\n")

    log("TREND (last 30 days vs before)")
    log("-" * 58)
    for aud, t in sorted(data["trend"].items()):
        log("  %-8s recent %-6s previous %-6s  %s"
            % (aud, t["recent_avg"] if t["recent_avg"] is not None else "-",
               t["previous_avg"] if t["previous_avg"] is not None else "-",
               t["direction"]))

    log("\nTOPICS  (score = weighted engagement per 100 reach)")
    log("-" * 58)
    log("  %-8s %-14s %6s %6s %5s %6s" % ("PAGE", "PILLAR", "SCORE", "POSTS", "CONF", "WEIGHT"))
    for row in data["by_pillar"][:12]:
        log("  %-8s %-14s %6.1f %6d %5.2f %6.2f"
            % (row["audience"], row["pillar"], row["avg_score"],
               row["posts"], row["confidence"], row["weight"]))

    log("\nDESIGNS")
    log("-" * 58)
    for row in data["by_layout"][:8]:
        log("  %-8s %-16s %6.1f  (%d post(s))"
            % (row["audience"], row["layout"], row["avg_score"], row["posts"]))

    log("\nWHAT TO DO")
    log("-" * 58)
    for rec in data["recommendations"]:
        log("  * " + rec)

    log("\nBEST POSTS")
    log("-" * 58)
    for row in data["top_posts"][:5]:
        log("  %6.1f [%-7s] %s" % (row["score"], row["audience"], row["headline"][:44]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--weights", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    if not buffer_key():
        log("BUFFER_ACCESS_TOKEN is not set.")
        return 1
    data = build(cfg)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    payload = write_weights(data)

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.weights:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        report(data)
        log("\n  insights -> social/calendar/insights.json")
        log("  weights  -> social/calendar/weights.json (read by the generator)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
