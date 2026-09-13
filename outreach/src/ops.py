"""CollabHive Outreach — operations layer (health watchdog + daily CEO brief).

The pipeline runs unattended, so the failure mode that actually costs money is a
SILENT one: the daily job stops committing and nobody notices for a week. This
module is the safety net.

  * health_check   -> inspect state/report/pool and return a list of checks,
                      each with an ok/warn/fail status and a human explanation.
  * ceo_brief      -> one daily email: what the business did in 24h, what needs
                      a human decision, and any failing health checks up top.
  * run_ops        -> entrypoint used by `python src/run.py ops`.

Read-only with respect to business state: it never sends outreach, never edits
the pool. It only reads data/ and sends ONE internal email to the owner.
Stdlib only.
"""
from __future__ import annotations

from datetime import datetime, timezone

from .common import ROOT, env, gmail_credentials, load_json, log, save_json

# Status constants, ordered by severity.
OK, WARN, FAIL = "ok", "warn", "fail"


def _age_hours(ts_value: str) -> float | None:
    """Hours since an ISO timestamp, or None if unparseable/missing."""
    if not ts_value:
        return None
    try:
        ts = datetime.fromisoformat(ts_value)
    except (ValueError, TypeError):
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - ts).total_seconds() / 3600.0


def _check(name: str, status: str, detail: str, fix: str = "") -> dict:
    return {"name": name, "status": status, "detail": detail, "fix": fix}


# ---------- health checks ----------
def health_check(cfg: dict) -> list[dict]:
    """Inspect the pipeline's own output and report what's broken.

    Every check is deliberately derived from committed data (state.json /
    report.json / the seed pool) so it detects a job that died mid-run — the
    exact failure that went unnoticed for a week.
    """
    checks: list[dict] = []
    ocfg = cfg.get("ops", {})

    state = load_json(ROOT / cfg["brands"]["state_file"])
    state = state if isinstance(state, dict) else {}
    sent_log = state.get("sent_log", []) if isinstance(state.get("sent_log"), list) else []

    # 1) Did the pipeline run at all recently?
    stale_h = float(ocfg.get("stale_run_hours", 36))
    run_age = _age_hours(state.get("last_run", ""))
    if run_age is None:
        checks.append(_check("pipeline_ran", FAIL, "No last_run timestamp in state.json.",
                             "Trigger the Outreach Daily Run workflow manually."))
    elif run_age > stale_h:
        checks.append(_check("pipeline_ran", FAIL,
                             f"Last pipeline run was {run_age:.0f}h ago (limit {stale_h:.0f}h).",
                             "Check the Actions tab — the scheduled job is failing or disabled."))
    else:
        checks.append(_check("pipeline_ran", OK, f"Last run {run_age:.0f}h ago."))

    # 2) Is mail actually going out? (Only a problem if we HAVE someone to mail.)
    sendable = _sendable_count(cfg, state)
    quiet_h = float(ocfg.get("stale_send_hours", 48))
    send_age = _age_hours(sent_log[-1].get("ts", "")) if sent_log else None
    if send_age is None:
        checks.append(_check("mail_flowing", WARN, "No outreach email has ever been recorded.",
                             "Confirm OUTREACH_EMAIL_PASS is set in repo secrets."))
    elif send_age > quiet_h and sendable > 0:
        checks.append(_check("mail_flowing", FAIL,
                             f"No email sent for {send_age:.0f}h, but {sendable} brand(s) are ready to contact.",
                             "Usually a missing/expired Gmail app password (OUTREACH_EMAIL_PASS)."))
    elif send_age > quiet_h:
        checks.append(_check("mail_flowing", WARN,
                             f"No email sent for {send_age:.0f}h — but 0 brands are currently sendable.",
                             "This is a pool problem, not a mail problem. See prospect_pool."))
    else:
        checks.append(_check("mail_flowing", OK, f"Last email sent {send_age:.0f}h ago."))

    # 3) Prospect pool depth — the pipeline goes quiet when this hits zero.
    low = int(ocfg.get("low_pool_threshold", 10))
    if sendable == 0:
        checks.append(_check("prospect_pool", FAIL, "0 brands left to contact — outreach is starved.",
                             "Add brands to data/brands_seed.json or run the Maps discovery workflow."))
    elif sendable < low:
        checks.append(_check("prospect_pool", WARN,
                             f"Only {sendable} contactable brand(s) left (threshold {low}).",
                             "Top up the seed pool this week or outreach stops."))
    else:
        checks.append(_check("prospect_pool", OK, f"{sendable} brand(s) ready to contact."))

    # 4) Hot leads waiting on a human — this is unbooked revenue sitting idle.
    stale_lead_h = float(ocfg.get("stale_lead_hours", 48))
    stale_leads = _stale_hot_leads(cfg, stale_lead_h)
    if stale_leads:
        names = ", ".join(l.get("email", "?") for l in stale_leads[:5])
        checks.append(_check("hot_leads", WARN,
                             f"{len(stale_leads)} hot lead(s) with no quote for >{stale_lead_h:.0f}h: {names}",
                             "Reply personally — these are the closest thing to revenue you have."))
    else:
        checks.append(_check("hot_leads", OK, "No hot leads are being ignored."))

    # 5) Creator supply. creators_pool.json is rebuilt from the applicant sheet
    #    each run (it is untracked, since it holds creator PII and this repo is
    #    public). If the sheet read fails, the pool silently empties and every
    #    shortlist/quote downstream produces nothing — so check it explicitly.
    creators = load_json(ROOT / cfg["sales"]["creator_pool_file"])
    creators = creators if isinstance(creators, list) else []
    if not creators:
        checks.append(_check("creator_supply", FAIL,
                             "Creator pool is EMPTY — no shortlists or quotes can be produced.",
                             "The applicant sheet read failed. Confirm the sheet in "
                             "publish.applicant_sheet_id is still shared 'Anyone with the link'."))
    elif len(creators) < int(ocfg.get("low_creator_threshold", 10)):
        checks.append(_check("creator_supply", WARN,
                             f"Only {len(creators)} creator(s) in the pool.",
                             "Recruit more creators or brand matching gets thin."))
    else:
        checks.append(_check("creator_supply", OK, f"{len(creators)} creators available for matching."))

    # 6) Deliverability — a high bounce rate poisons the sending domain.
    health = load_json(ROOT / cfg.get("verification", {}).get("health_file", "data/delivery_health.json"))
    health = health if isinstance(health, dict) else {}
    if health.get("flagged"):
        checks.append(_check("deliverability", FAIL,
                             f"Delivery flagged: {health.get('delivery_rate_pct', 0)}% delivered, "
                             f"{health.get('bounces', 0)} bounce(s).",
                             "Pause sending and clean the pool before Gmail throttles the account."))
    else:
        checks.append(_check("deliverability", OK,
                             f"{health.get('delivery_rate_pct', 0)}% delivered, {health.get('bounces', 0)} bounce(s)."))

    return checks


def _sendable_count(cfg: dict, state: dict) -> int:
    """How many brands could receive an email right now (same rules as the mailer)."""
    try:
        from .brands import select_targets
        targets, _ = select_targets(cfg, state, 10_000)
        return len(targets)
    except Exception as exc:  # never let the watchdog itself crash the run
        log(f"  ops: sendable count unavailable ({exc})")
        return 0


def _stale_hot_leads(cfg: dict, older_than_h: float) -> list[dict]:
    """Interested/negotiating replies that never received a quote."""
    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    quotes = load_json(ROOT / cfg.get("quotes", {}).get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    quoted_emails = {(q.get("email") or "").lower() for q in quotes}
    out = []
    for c in closing:
        if c.get("status") not in ("interested", "negotiating"):
            continue
        if (c.get("email") or "").lower() in quoted_emails:
            continue
        age = _age_hours(c.get("ts", ""))
        if age is not None and age > older_than_h:
            out.append(c)
    return out


def worst_status(checks: list[dict]) -> str:
    """Most severe status across all checks."""
    for level in (FAIL, WARN):
        if any(c["status"] == level for c in checks):
            return level
    return OK


# ---------- daily CEO brief ----------
def gather_metrics(cfg: dict) -> dict:
    """The numbers a CEO actually needs: what moved in the last 24h and 7d."""
    state = load_json(ROOT / cfg["brands"]["state_file"])
    state = state if isinstance(state, dict) else {}
    sent_log = state.get("sent_log", []) if isinstance(state.get("sent_log"), list) else []

    def _within(hours: float) -> int:
        n = 0
        for e in sent_log:
            age = _age_hours(e.get("ts", ""))
            if age is not None and age <= hours:
                n += 1
        return n

    closing = load_json(ROOT / cfg["sales"]["closing_file"])
    closing = closing if isinstance(closing, list) else []
    by_status: dict[str, int] = {}
    for c in closing:
        s = c.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1

    quotes = load_json(ROOT / cfg.get("quotes", {}).get("created_file", "data/quotes_sent.json"))
    quotes = quotes if isinstance(quotes, list) else []
    creators = load_json(ROOT / cfg["sales"]["creator_pool_file"])
    creators = creators if isinstance(creators, list) else []
    drafts = load_json(ROOT / cfg.get("social", {}).get("drafts_file", "data/social_drafts.json"))
    drafts = drafts if isinstance(drafts, list) else []
    seo_dir = ROOT / cfg.get("seo", {}).get("output_dir", "../seo-pages")
    seo_pages = len(list(seo_dir.glob("*.html"))) if seo_dir.exists() else 0

    pipeline_value = 0
    for q in quotes:
        try:
            pipeline_value += int(float(q.get("total") or 0))
        except (TypeError, ValueError):
            continue

    return {
        "sent_24h": _within(24),
        "sent_7d": _within(24 * 7),
        "sent_total": len(sent_log),
        "replies_total": len(closing),
        "interested": by_status.get("interested", 0),
        "negotiating": by_status.get("negotiating", 0),
        "declined": by_status.get("declined", 0),
        "quotes_sent": len(quotes),
        "pipeline_value": pipeline_value,
        "creators": len(creators),
        "social_drafts": len(drafts),
        "seo_pages": seo_pages,
        "reply_rate_pct": round(len(closing) / len(state.get("emailed_emails", [])) * 100, 1)
        if state.get("emailed_emails") else 0.0,
    }


def render_brief(cfg: dict, checks: list[dict], metrics: dict) -> tuple[str, str]:
    """Return (subject, plain-text body) for the daily brief."""
    status = worst_status(checks)
    icon = {OK: "✅", WARN: "⚠️", FAIL: "🚨"}[status]
    today = datetime.now(timezone.utc).strftime("%d %b %Y")
    subject = f"{icon} CollabHive daily brief — {today}"

    lines = [f"CollabHive — daily brief, {today}", ""]

    problems = [c for c in checks if c["status"] in (WARN, FAIL)]
    if problems:
        lines.append("NEEDS YOUR ATTENTION")
        lines.append("-" * 40)
        for c in problems:
            mark = "FAIL" if c["status"] == FAIL else "WARN"
            lines.append(f"[{mark}] {c['detail']}")
            if c["fix"]:
                lines.append(f"       -> {c['fix']}")
        lines.append("")
    else:
        lines.append("All systems healthy. Nothing needs you today.")
        lines.append("")

    lines += [
        "SALES",
        "-" * 40,
        f"  Emails sent      : {metrics['sent_24h']} today / {metrics['sent_7d']} this week "
        f"({metrics['sent_total']} all time)",
        f"  Replies          : {metrics['replies_total']} ({metrics['reply_rate_pct']}% reply rate)",
        f"  Hot leads        : {metrics['interested']} interested, {metrics['negotiating']} negotiating",
        f"  Quotes sent      : {metrics['quotes_sent']}",
        f"  Pipeline value   : INR {metrics['pipeline_value']:,}",
        "",
        "SUPPLY & MARKETING",
        "-" * 40,
        f"  Creators onboard : {metrics['creators']}",
        f"  Social drafts    : {metrics['social_drafts']} queued",
        f"  SEO pages live   : {metrics['seo_pages']}",
        "",
        "SYSTEM HEALTH",
        "-" * 40,
    ]
    for c in checks:
        lines.append(f"  [{c['status'].upper():4}] {c['name']}: {c['detail']}")

    lines += [
        "",
        "-" * 40,
        "Dashboard: " + cfg["profile"].get("site_url", "").rstrip("/") + "/outreach/dashboard/",
        "This brief is generated by the ops workflow. It sends no outreach itself.",
    ]
    return subject, "\n".join(lines)


def run_ops(cfg: dict) -> dict:
    """Health check + daily brief. Saves a snapshot, emails the owner."""
    checks = health_check(cfg)
    metrics = gather_metrics(cfg)
    status = worst_status(checks)

    for c in checks:
        log(f"  [{c['status'].upper():4}] {c['name']}: {c['detail']}")

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checks": checks,
        "metrics": metrics,
    }
    save_json(ROOT / "data" / "ops_health.json", snapshot)

    subject, body = render_brief(cfg, checks, metrics)
    sent = _email_brief(cfg, subject, body)
    return {"status": status, "problems": sum(1 for c in checks if c["status"] != OK),
            "emailed": sent, "metrics": metrics}


def _email_brief(cfg: dict, subject: str, body: str) -> bool:
    """Send the brief to the owner. Never raises — ops must not break the run."""
    ocfg = cfg.get("ops", {})
    if not ocfg.get("email_brief", True):
        log("Ops brief email disabled in config.")
        return False
    to = ocfg.get("to_email") or cfg["profile"]["contact_email"]
    user, password = gmail_credentials()
    if not password:
        log("No OUTREACH_EMAIL_PASS — brief computed but not emailed.")
        return False
    try:
        from .automation import _send_mime
        _send_mime(cfg, user, password, to, subject, body, f"<pre>{_escape(body)}</pre>")
        log(f"Daily brief emailed to {to}")
        return True
    except Exception as exc:
        log(f"Brief email FAILED: {exc}")
        return False


def _escape(s: str) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
