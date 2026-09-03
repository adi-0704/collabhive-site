"""CollabHive Outreach — Buffer auto-posting module.

Reads drafted onboarding social posts (data/social_drafts.json) and queues each
to the user's Buffer channels via the Buffer GraphQL API (api.buffer.com), so
Buffer schedules/publishes them automatically.

Never posts the same draft twice: each draft gets a 'buffered' flag.

The Buffer API key is read from OUTREACH_BUFFER_KEY (env) / GitHub Secret
BUFFER_ACCESS_TOKEN — NEVER committed.
"""
from __future__ import annotations

import json
import urllib.request

from .common import ROOT, env, load_config, load_json, log, save_json


def buffer_key() -> str:
    return env("OUTREACH_BUFFER_KEY") or env("BUFFER_ACCESS_TOKEN") or ""


def _gql(cfg, query: str) -> dict:
    key = buffer_key()
    if not key:
        return {"error": "no_key"}
    url = cfg.get("buffer", {}).get("api_url", "https://api.buffer.com")
    payload = json.dumps({"query": query}).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8", "ignore"))
    except Exception as exc:
        log(f"  buffer API error: {exc}")
        return {"error": str(exc)}


def get_organizations(cfg) -> list[dict]:
    data = _gql(cfg, "query GetOrganizations { account { organizations { id name } } }")
    return (data.get("data", {}).get("account", {}).get("organizations", []) if isinstance(data, dict) else [])


def get_channels(cfg, org_id: str = "") -> list[dict]:
    if not org_id:
        orgs = get_organizations(cfg)
        org_id = orgs[0]["id"] if orgs else ""
    if not org_id:
        return []
    q = ('query GetChannels { channels(input: { organizationId: "%s" }) { id name service } }' % org_id)
    data = _gql(cfg, q)
    return (data.get("data", {}).get("channels", []) if isinstance(data, dict) else [])


def _queue_post(cfg, channel_id: str, text: str, org_id: str, image_url: str = "") -> dict:
    assets = ""
    if image_url:
        assets = ', assets: [{ image: { url: "%s" } }]' % image_url
    q = ('mutation CreatePost { createPost(input: { text: "%s", channelId: "%s", '
         'schedulingType: automatic, mode: addToQueue%s }) { '
         '... on PostActionSuccess { post { id text dueAt } } '
         '... on MutationError { message } } }' % (_escape_gql(text), channel_id, assets))
    resp = _gql(cfg, q)
    res = None
    if isinstance(resp, dict):
        res = resp.get("data", {}).get("createPost", {})
    if res and res.get("post"):
        return {"ok": True, "post_id": res["post"].get("id"), "dueAt": res["post"].get("dueAt")}
    msg = (res or {}).get("message")
    if not msg and isinstance(resp, dict) and resp.get("errors"):
        msg = resp["errors"][0].get("message")
    if not msg and isinstance(resp, dict):
        msg = resp.get("error") or "unknown"
    return {"ok": False, "message": msg or "unknown"}


def _escape_gql(s: str) -> str:
    """Escape a string for safe embedding inside a GraphQL JSON string literal."""
    if s is None:
        return ""
    return (str(s)
            .replace(chr(92), chr(92) * 2)          # backslash
            .replace('"', '\\"')                     # double quote
            .replace("\n", "  ")
            .replace("\r", ""))


def _esc(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip()


def queue_drafts(cfg: dict) -> dict:
    bcfg = cfg.get("buffer", {})
    if not bcfg.get("enabled", True):
        return {"queued": 0, "skipped": "disabled"}
    if not buffer_key():
        return {"queued": 0, "skipped": "no_key"}

    drafts_file = ROOT / cfg["social"]["drafts_file"]
    drafts = load_json(drafts_file)
    drafts = drafts if isinstance(drafts, list) else []
    if not drafts:
        return {"queued": 0, "skipped": "no_drafts"}

    # Resolve org + channels once.
    orgs = get_organizations(cfg)
    org_id = orgs[0]["id"] if orgs else ""
    channels = get_channels(cfg, org_id)
    if not channels:
        return {"queued": 0, "skipped": "no_channels"}

    # Map service -> channel id.
    channel_by_service = {}
    for ch in channels:
        channel_by_service[ch.get("service", "").lower()] = ch["id"]
    # Instagram needs media -> attach a hosted image so the post is valid.
    default_image = bcfg.get("default_image_url", "")

    queued = 0
    failed = 0
    skipped_unwritable = 0
    for d in drafts:
        if d.get("buffered") or d.get("posted"):
            continue
        handle = d.get("handle", "")
        platforms = d.get("platforms", {}) or {}
        text = platforms.get("x") or platforms.get("linkedin") or platforms.get("instagram") or ""
        if not text:
            skipped_unwritable += 1
            continue
        # Pick a channel: text-capable first (text-only OK), else instagram.
        channel_id = ""
        service = ""
        for svc in ("x", "linkedin", "facebook", "threads", "twitter", "mastodon"):
            if svc in channel_by_service:
                channel_id, service = channel_by_service[svc], svc
                break
        if not channel_id and "instagram" in channel_by_service:
            channel_id, service = channel_by_service["instagram"], "instagram"
        if not channel_id:
            skipped_unwritable += 1
            continue

        # Instagram posts require media + a valid type via Buffer; text-only is
        # rejected. Mark these as needs_media so they're not lost, not retried.
        if service == "instagram":
            d["buffer_status"] = "needs_media"
            d["buffer_note"] = ("Instagram requires a media asset. Add an image/video in "
                                "Buffer or connect an X/LinkedIn channel for text posts.")
            save_json(drafts_file, drafts)
            skipped_unwritable += 1
            continue

        res = _queue_post(cfg, channel_id, text, org_id)
        if res.get("ok"):
            d["buffered"] = True
            d["buffer_post_id"] = res.get("post_id")
            d["buffer_due_at"] = res.get("dueAt")
            d["buffer_status"] = "queued"
            queued += 1
            log(f"  BUFFERED {handle} -> {service} post {res.get('post_id')}")
        else:
            failed += 1
            d["buffer_status"] = "error:" + str(res.get("message"))[:60]
            log(f"  BUFFER FAIL {handle}: {res.get('message')}")
        save_json(drafts_file, drafts)

    return {"queued": queued, "failed": failed, "needs_media": skipped_unwritable,
            "channels": len(channels)}


def text_only_ok(text: str, service: str) -> bool:
    """Instagram always requires media, so text-only is only fine on other services."""
    return service != "instagram"
