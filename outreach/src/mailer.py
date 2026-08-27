"""CollabHive Outreach — daily mailer (Gmail SMTP, free).

Sends personalized outreach emails to brands in small daily batches with
random delays, keeping volume under the daily cap to avoid spam flags.
Uses stdlib smtplib only — no pip install required.
"""
from __future__ import annotations

import random
import re
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from .common import ROOT, env, load_config, log, gmail_credentials


def _render(subject_template: str, txt: str, html: str, brand: dict, cfg: dict) -> tuple[str, str, str]:
    p = cfg["profile"]
    name = brand.get("name") or brand.get("brand") or "Business"
    first = name.split()[0] if name else "there"
    subject_line = subject_template.format(name=first, brand=name, niche=brand.get("niche", ""))
    ctx = {
        "name": first,
        "brand": name,
        "niche": brand.get("niche", ""),
        "company": p["company"],
        "site_url": p["site_url"],
        "apply_url": p["apply_url"],
        "contact_email": p["contact_email"],
        "phone": p["phone"],
    }
    subj = subject_template.format(**ctx)
    body_txt = txt.format(**ctx)
    body_html = html.format(**ctx)
    return subj, body_txt, body_html


def load_templates(cfg: dict) -> tuple[str, str, str]:
    tdir = ROOT / "templates"
    subject_template = cfg["smtp"].get("subject_line") or \
        "A creator network for {brand} — CollabHive"
    txt = (tdir / "email.txt").read_text(encoding="utf-8")
    html = (tdir / "email.html").read_text(encoding="utf-8")
    return subject_template, txt, html


def send_one(smtp, brand: dict, cfg: dict) -> bool:
    subject_template, txt_tpl, html_tpl = load_templates(cfg)
    subject, body_txt, body_html = _render(subject_template, txt_tpl, html_tpl, brand, cfg)

    to_addr = brand.get("email") or (brand.get("emails") or [""])[0]
    if not to_addr:
        return False
    smtp_cfg = cfg["smtp"]
    from_addr = smtp_cfg["username"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_cfg['from_name']} <{from_addr}>"
    msg["To"] = to_addr
    msg.attach(MIMEText(body_txt, "plain", _charset="utf-8"))
    msg.attach(MIMEText(body_html, "html", _charset="utf-8"))

    try:
        smtp.sendmail(from_addr, [to_addr], msg.as_string())
        return True
    except Exception as exc:
        log(f"  FAIL {to_addr}: {exc}")
        return False


def warmup_delay(cfg: dict) -> float:
    lo = cfg["smtp"]["min_delay_seconds"]
    hi = cfg["smtp"]["max_delay_seconds"]
    return random.uniform(lo, hi)


def daily_run(cfg: dict) -> dict:
    from .brands import select_targets
    from .common import load_json, save_json

    user, password = gmail_credentials()
    if not password:
        log("No OUTREACH_EMAIL_PASS set — set it in GitHub Secrets / .env. Nothing sent.")
        return {"sent": 0, "skipped": 0, "error": "no_password"}

    cap = min(cfg["smtp"]["daily_limit"], cfg["smtp"]["daily_hard_cap"])
    state_file = ROOT / cfg["brands"]["state_file"]
    loaded = load_json(state_file)
    state = loaded if isinstance(loaded, dict) else {}

    targets, _ = select_targets(cfg, state, cap)
    targets = [t for t in targets if t.get("email")]

    if not targets:
        log("No unsent brands with emails available today. (Add brands to seed pool.)")
        return {"sent": 0, "skipped": 0, "pool_empty": True}

    ctx = ssl.create_default_context()
    from .protect import Throttle
    throttle = Throttle(
        max_per_hour=cfg["smtp"]["daily_limit"],
        session_cap=len(targets),
        backoff_after_failures=3,
        min_gap=0.0,
        max_gap=2.0,
    )
    sent = 0
    failed = 0
    delivered_from = 0
    try:
        with smtplib.SMTP(cfg["smtp"]["host"], cfg["smtp"]["port"], timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ctx)
            smtp.ehlo()
            smtp.login(user, password)
            delivered_from = len(targets)
            for brand in targets:
                if throttle.is_circuit_open():
                    log("Circuit breaker open — stopping sends (too many SMTP/auth failures).")
                    break
                throttle.wait()
                ok = send_one(smtp, brand, cfg)
                throttle.record(ok)
                if ok:
                    sent += 1
                    state = record_sent(state, brand)
                    log(f"  SENT {brand.get('email')} <- {brand.get('name')} [{brand.get('niche')}]")
                else:
                    failed += 1
                if brand is not targets[-1]:
                    d = warmup_delay(cfg)
                    log(f"    ...waiting {d:.0f}s")
                    time.sleep(d)
    except Exception as exc:
        log(f"SMTP error: {exc}")

    save_json(state_file, state)
    return {"sent": sent, "attempted": len(targets), "failed": failed, "delivered_from": delivered_from}


def record_sent(state: dict, brand: dict) -> dict:
    from datetime import datetime, timezone
    email = (brand.get("email") or "").lower()
    if email:
        state.setdefault("emailed_emails", [])
        if email not in state["emailed_emails"]:
            state["emailed_emails"].append(email)
    domain = ((brand.get("website") or "").lower().replace("https://", "").replace("http://", "")
              .split("/")[0]).replace("www.", "")
    if domain:
        state.setdefault("emailed_domains", [])
        if domain not in state["emailed_domains"]:
            state["emailed_domains"].append(domain)
    state.setdefault("sent_log", [])
    state["sent_log"].append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "email": email,
        "name": brand.get("name"),
        "niche": brand.get("niche"),
        "city": brand.get("city"),
    })
    return state
