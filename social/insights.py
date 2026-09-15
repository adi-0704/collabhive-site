"""CollabHive — close the loop between what we post and what works.

149 days of content were scheduled with no feedback path: nothing measured
which posts landed, so the next 149 would have been written on instinct.

This pulls each published post's metrics from Buffer, matches it back to the
calendar entry that produced it, and aggregates performance by content pillar
and by layout. The output answers two questions:

    which TOPICS should we write more of?
    which DESIGNS should we use more of?

    python social/insights.py            # report + write insights.json
    python social/insights.py --json     # machine-readable only

Ranking uses reach-normalised engagement, not raw counts: a post that went out
on a bigger day would otherwise always look better than a good post on a quiet
one.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).parent.resolve()
REPO = HERE.parent
sys.path.insert(0, str(REPO / "outreach"))

from src.buffer import _gql, buffer_key          # noqa: E402
from src.common import load_config                # noqa: E402

CAL = HERE / "calendar" / "calendar.json"
OUT = HERE / "calendar" / "insights.json"

# Signals that actually indicate the content worked, in priority order. Saves
# and shares mean intent; reactions are a reflex and weighted far lower.
WEIGHTS = {"Saves": 4.0, "Shares": 4.0, "Follows": 5.0, "Comments": 3.0, "Reactions": 1.0}


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
    """Weighted engagement per 100 reach.

    Normalising by reach matters: without it, whichever post happened to be
    distributed most would always top the ranking regardless of whether the
    content itself resonated.
    """
    reach = max(float(metrics.get("Reach") or 0), 1.0)
    weighted = sum(WEIGHTS.get(k, 0) * float(metrics.get(k) or 0) for k in WEIGHTS)
    return round(weighted / reach * 100, 2)


def build(cfg: dict) -> dict:
    entries = json.loads(CAL.read_text(encoding="utf-8")) if CAL.exists() else []
    # Match on the first line of the authored body — unique per post by design.
    by_marker = {e["caption_body"].splitlines()[0][:80]: e for e in entries}

    channels = cfg.get("buffer", {}).get("channels", {})
    results: list[dict] = []
    for audience, cid in channels.items():
        if not cid:
            continue
        for post in fetch_sent(cfg, cid):
            metrics = {m["name"]: m["value"] for m in (post.get("metrics") or [])}
            text = (post.get("text") or "")
            marker = text.splitlines()[0][:80] if text else ""
            entry = by_marker.get(marker)
            results.append({
                "audience": audience,
                "sent_at": (post.get("sentAt") or "")[:10],
                "headline": (entry or {}).get("headline", "(not in calendar)"),
                "pillar": (entry or {}).get("pillar", "unknown"),
                "layout": (entry or {}).get("layout", "unknown"),
                "reach": metrics.get("Reach", 0),
                "views": metrics.get("Views", 0),
                "saves": metrics.get("Saves", 0),
                "shares": metrics.get("Shares", 0),
                "follows": metrics.get("Follows", 0),
                "score": score(metrics),
            })

    def agg(key: str) -> list[dict]:
        buckets: dict[tuple, list[dict]] = defaultdict(list)
        for r in results:
            if r[key] == "unknown":
                continue
            buckets[(r["audience"], r[key])].append(r)
        out = []
        for (aud, name), rows in buckets.items():
            out.append({
                "audience": aud, key: name, "posts": len(rows),
                "avg_score": round(sum(x["score"] for x in rows) / len(rows), 2),
                "avg_reach": round(sum(float(x["reach"] or 0) for x in rows) / len(rows), 1),
            })
        return sorted(out, key=lambda x: x["avg_score"], reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "posts_measured": len(results),
        "matched_to_calendar": sum(1 for r in results if r["pillar"] != "unknown"),
        "by_pillar": agg("pillar"),
        "by_layout": agg("layout"),
        "top_posts": sorted(results, key=lambda x: x["score"], reverse=True)[:10],
        "weakest_posts": sorted(results, key=lambda x: x["score"])[:5],
    }


def report(data: dict) -> None:
    log(f"\nMeasured {data['posts_measured']} published post(s), "
        f"{data['matched_to_calendar']} matched to the calendar\n")

    if data["posts_measured"] < 30:
        log("  NOTE: too few posts for the rankings below to mean anything yet.")
        log("  Treat them as directional until roughly 30 posts have run.\n")

    log("TOPICS THAT WORK (avg engagement per 100 reach)")
    log("-" * 52)
    for row in data["by_pillar"][:8]:
        log("  %-8s %-14s %5.1f   (%d post(s), avg reach %.0f)"
            % (row["audience"], row["pillar"], row["avg_score"], row["posts"], row["avg_reach"]))

    log("\nDESIGNS THAT WORK")
    log("-" * 52)
    for row in data["by_layout"][:8]:
        log("  %-8s %-16s %5.1f   (%d post(s))"
            % (row["audience"], row["layout"], row["avg_score"], row["posts"]))

    log("\nBEST POSTS SO FAR")
    log("-" * 52)
    for row in data["top_posts"][:5]:
        log("  %5.1f  [%-7s] %s" % (row["score"], row["audience"], row["headline"][:46]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = load_config()
    if not buffer_key():
        log("BUFFER_ACCESS_TOKEN is not set.")
        return 1
    data = build(cfg)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        report(data)
        log(f"\n  written -> social/calendar/insights.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
