"""CollabHive Outreach — email validation before sending.

Delivery rate fell to 28% because addresses scraped out of web pages included
JavaScript filenames, placeholder domains from minified bundles, and no-reply
bots. Every one of those bounces, and bounces are what destroy sender
reputation with Gmail.

This module is the gate that runs BEFORE an address is ever mailed:

    syntax      -> shape, length, character rules
    domain      -> not a placeholder, has a plausible TLD, not an asset file
    role        -> not no-reply@/notifications@/careers@ etc.
    disposable  -> not a throwaway mailbox provider
    mx          -> the domain actually publishes a mail server

The MX check speaks DNS over UDP directly, because the pipeline is
deliberately stdlib-only (no dnspython) so GitHub Actions needs no pip install.
Results are cached to data/mx_cache.json so a domain is resolved once.
"""
from __future__ import annotations

import random
import re
import socket
import struct
import time
from datetime import datetime, timezone

from .common import ROOT, load_json, log, save_json

# Deliberately stricter than the scraping regex in brands.py: this decides
# whether we actually send, so false negatives are cheaper than bounces.
SYNTAX = re.compile(r"^[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,255}\.[A-Za-z]{2,24}$")

# Local parts that are never a human who can say yes to a campaign.
ROLE_PREFIXES = (
    "no-reply", "noreply", "donotreply", "do-not-reply", "no_reply",
    "postmaster", "mailer-daemon", "bounce", "notifications", "notification",
    "alerts", "alert", "automated", "system", "webmaster", "abuse",
    "unsubscribe", "newsletter", "mailer", "back-in-stock", "backinstock",
    "careers", "jobs", "recruitment", "hr", "invoice", "billing", "accounts",
    "payments", "security", "privacy", "legal", "compliance",
    # Trailing separator = sub-addresses only. "support-orders@" is an order
    # notification mailbox; plain "support@" is a real contact and must pass.
    "support-", "orders-", "noreply-",
)

DISPOSABLE_DOMAINS = (
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "throwaway.email", "yopmail.com", "trashmail.com", "sharklasers.com",
    "getnada.com", "maildrop.cc", "mailsac.com", "dispostable.com",
)

# Email service providers — mail sent FROM them, never a brand's own inbox.
ESP_HINTS = (
    "sendgrid", "mailgun", "postmark", "mailchimp", "klaviyo", "sendinblue",
    "createsend", "notifyboost", "mandrill", "sparkpost", "amazonses",
)

ASSET_EXTENSIONS = (
    ".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".woff", ".woff2", ".ttf", ".mp4", ".mp3", ".map", ".json", ".xml", ".php",
)

# Domains that only ever appear as placeholders inside code samples.
PLACEHOLDER_DOMAINS = (
    "example.com", "example.org", "domain.com", "yourdomain.com", "email.com",
    "test.com", "sentry.io", "schema.org", "w3.org", "placeholder.com",
    "company.com", "brand.com", "site.com", "x.com", "y.com", "z.com",
)

MX_CACHE = "data/mx_cache.json"
_PUBLIC_DNS = ("1.1.1.1", "8.8.8.8")


# ---------------------------------------------------------------- syntax
def syntax_ok(email: str) -> bool:
    email = (email or "").strip()
    if not SYNTAX.match(email):
        return False
    local, _, domain = email.partition("@")
    if ".." in email or email.startswith(".") or local.endswith("."):
        return False
    # "c@y.com" / "b@z.com" — real brands do not have one-character domains.
    root = domain.rsplit(".", 1)[0].split(".")[-1]
    if len(root) < 3:
        return False
    return True


def domain_ok(email: str) -> bool:
    domain = (email or "").partition("@")[2].lower()
    if not domain or domain in PLACEHOLDER_DOMAINS:
        return False
    # "files@quinn-live.bundle.js" — a filename, not a mail domain.
    if any(domain.endswith(ext) or ext in domain for ext in ASSET_EXTENSIONS):
        return False
    if any(d in domain for d in DISPOSABLE_DOMAINS):
        return False
    if any(h in domain for h in ESP_HINTS):
        return False
    return True


def role_ok(email: str) -> bool:
    """Reject role mailboxes, whatever separator they use.

    Separators are stripped first: no-reply, no.reply, no_reply and noreply are
    the same mailbox. Matching the literal string missed 'no.reply@' and would
    have sent outreach to an address that can never answer.
    """
    local = (email or "").partition("@")[0].lower().strip()
    flat = re.sub(r"[._\-]", "", local)
    for p in ROLE_PREFIXES:
        # Prefixes ending in a separator target sub-addresses only; normalising
        # them away would reject the plain mailbox (support@ is a real contact).
        if p.endswith(("-", ".", "_")):
            if local.startswith(p):
                return False
            continue
        pf = re.sub(r"[._\-]", "", p)
        if flat == pf or flat.startswith(pf):
            return False
    return True


# ---------------------------------------------------------------- MX (stdlib DNS)
def _dns_query_mx(domain: str, server: str, timeout: float = 3.0) -> bool:
    """Ask a public resolver whether `domain` publishes any MX record.

    Hand-rolled because the pipeline stays dependency-free. Builds a minimal
    DNS query packet, sends it over UDP, and only inspects the answer count —
    we need existence, not the records themselves.
    """
    txn = random.randint(0, 0xFFFF)
    header = struct.pack(">HHHHHH", txn, 0x0100, 1, 0, 0, 0)   # standard query, RD
    qname = b"".join(bytes([len(p)]) + p.encode("idna")
                     for p in domain.split(".") if p) + b"\x00"
    packet = header + qname + struct.pack(">HH", 15, 1)         # QTYPE=MX QCLASS=IN

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(packet, (server, 53))
        data, _ = sock.recvfrom(2048)
    except Exception:
        return False
    finally:
        sock.close()

    if len(data) < 12:
        return False
    rid, flags, _qd, ancount, _ns, _ar = struct.unpack(">HHHHHH", data[:12])
    if rid != txn:
        return False
    if flags & 0x000F:            # RCODE != 0 (NXDOMAIN etc.)
        return False
    return ancount > 0


def has_mx(domain: str, cache: dict | None = None) -> bool:
    """True if the domain can receive mail. Cached; falls back to A-record."""
    domain = (domain or "").lower().strip()
    if not domain:
        return False
    if cache is not None and domain in cache:
        return bool(cache[domain])

    ok = False
    for server in _PUBLIC_DNS:
        if _dns_query_mx(domain, server):
            ok = True
            break
    if not ok:
        # Some small hosts accept mail on the A record. Resolving at all is a
        # far weaker signal than MX, but it beats discarding a live domain.
        try:
            socket.getaddrinfo(domain, None)
            ok = True
        except Exception:
            ok = False

    if cache is not None:
        cache[domain] = ok
    return ok


# ---------------------------------------------------------------- public API
def validate(email: str, cache: dict | None = None, check_mx: bool = True) -> tuple[bool, str]:
    """Return (deliverable, reason). Reason is '' when the address passes."""
    email = (email or "").strip().lower()
    if not syntax_ok(email):
        return False, "bad_syntax"
    if not domain_ok(email):
        return False, "bad_domain"
    if not role_ok(email):
        return False, "role_account"
    if check_mx and not has_mx(email.partition("@")[2], cache):
        return False, "no_mx"
    return True, ""


def load_cache() -> dict:
    c = load_json(ROOT / MX_CACHE)
    return c if isinstance(c, dict) else {}


def save_cache(cache: dict) -> None:
    save_json(ROOT / MX_CACHE, cache)


def clean_pool(cfg: dict, check_mx: bool = True) -> dict:
    """Strip undeliverable addresses out of the brand pool.

    Removes the address, not the brand — a brand with a dead address can still
    be re-enriched later and is worth keeping as a prospect.
    """
    pool_file = ROOT / cfg["brands"]["seed_file"]
    pool = load_json(pool_file)
    pool = pool if isinstance(pool, list) else []
    cache = load_cache()

    reasons: dict[str, int] = {}
    cleaned = 0
    for brand in pool:
        if not isinstance(brand, dict):
            continue
        kept = []
        for addr in (brand.get("emails") or []):
            ok, why = validate(addr, cache, check_mx)
            if ok:
                kept.append(addr)
            else:
                reasons[why] = reasons.get(why, 0) + 1
                cleaned += 1
        if kept != (brand.get("emails") or []):
            brand["emails"] = kept
            brand["email"] = kept[0] if kept else ""
            brand["has_email"] = bool(kept)

    save_json(pool_file, pool)
    save_cache(cache)
    log(f"Pool clean: removed {cleaned} undeliverable address(es) {reasons}")
    return {"removed": cleaned, "reasons": reasons,
            "with_email": sum(1 for b in pool if b.get("emails"))}


def screen_targets(cfg: dict, targets: list[dict]) -> tuple[list[dict], dict]:
    """Final gate immediately before sending. Returns (safe_targets, dropped)."""
    cache = load_cache()
    safe, dropped = [], {}
    for b in targets:
        ok, why = validate(b.get("email", ""), cache, check_mx=True)
        if ok:
            safe.append(b)
        else:
            dropped[why] = dropped.get(why, 0) + 1
            log(f"  screened out {b.get('email')} ({why})")
    save_cache(cache)
    return safe, dropped


def health_summary(cfg: dict) -> dict:
    """Snapshot of pool deliverability, for the ops brief."""
    pool = load_json(ROOT / cfg["brands"]["seed_file"])
    pool = pool if isinstance(pool, list) else []
    cache = load_cache()
    total = good = 0
    for b in pool:
        for addr in (b.get("emails") or []):
            total += 1
            if validate(addr, cache, check_mx=False)[0]:
                good += 1
    return {
        "addresses": total,
        "passing_static_checks": good,
        "mx_cached_domains": len(cache),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
