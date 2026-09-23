"""CollabHive - tell a real reply from a robot.

Why this exists
---------------
The original triage classified a reply by searching the subject + a 400-char
snippet for words like "collab". Three things were wrong with that, and they
compounded into a reply rate that was pure fiction:

  1. The subject of a reply is OUR subject, prefixed with "Re:". Our subjects
     contained "collab" ("...ready to collab") and our own name is CollabHive,
     so every reply matched on our own words.
  2. The snippet included the quoted copy of our own email, so even when the
     subject was clean the body matched on the same echo.
  3. Nothing detected auto-responders. Support desks reply instantly with a
     ticket number, and all 20 "hot leads" in the queue were exactly that.

So: decode the message properly, cut the quoted history off, decide whether a
human or a machine wrote it, and only then look for intent.

    clean_text(raw_bytes)  -> readable body, quoted history removed
    is_automated(...)      -> (bool, reason)
    classify(...)          -> interested | negotiating | declined | neutral
"""
from __future__ import annotations

import email as email_lib
import re
from email import policy
from email.header import decode_header, make_header

# --------------------------------------------------------------- decoding
_TAG = re.compile(r"<[^>]+>")
_STYLE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
_BR = re.compile(r"<(br|/p|/div|/tr)[^>]*>", re.I)
_WS = re.compile(r"[ \t\xa0]+")
_NL = re.compile(r"\n{3,}")

_ENTITIES = {
    "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
    "&#39;": "'", "&rsquo;": "'", "&ldquo;": '"', "&rdquo;": '"', "&mdash;": "-",
    "&ndash;": "-", "&zwnj;": "", "&hellip;": "...",
}


def _html_to_text(html: str) -> str:
    s = _STYLE.sub(" ", html)
    s = _BR.sub("\n", s)
    s = _TAG.sub(" ", s)
    for k, v in _ENTITIES.items():
        s = s.replace(k, v)
    s = re.sub(r"&#x?[0-9a-fA-F]+;", " ", s)
    return s


def decode_subject(raw: str) -> str:
    """RFC 2047 subject -> readable text ('=?UTF-8?Q?Re:_...' is unreadable)."""
    try:
        return str(make_header(decode_header(raw or "")))
    except Exception:
        return raw or ""


def _best_body(msg) -> str:
    """Prefer text/plain; fall back to text/html flattened.

    The old version took the FIRST text/plain part in a walk() and stopped.
    On multipart/mixed messages that part is often an empty container or an
    attachment preamble, which is why raw "----==_mimepart_..." boundaries ended
    up stored as the reply body.
    """
    plain, html = [], []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if (part.get_filename() or "").strip():
                continue                      # attachment, not the message
            ctype = part.get_content_type()
            try:
                raw = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                text = raw.decode(charset, "replace")
            except Exception:
                continue
            if ctype == "text/plain":
                plain.append(text)
            elif ctype == "text/html":
                html.append(text)
    else:
        try:
            raw = msg.get_payload(decode=True) or b""
            text = raw.decode(msg.get_content_charset() or "utf-8", "replace")
        except Exception:
            text = ""
        (html if msg.get_content_type() == "text/html" else plain).append(text)

    body = "\n".join(t for t in plain if t.strip())
    if not body.strip():
        body = _html_to_text("\n".join(html))
    # A stray MIME boundary means the part split failed; drop those lines
    # rather than storing them as if a human had typed them.
    body = "\n".join(l for l in body.splitlines()
                     if not l.lstrip().startswith(("----==_", "--_000_", "------=_")))
    return body


# ------------------------------------------------------- quoted-history cut
# Everything below one of these markers is OUR email, not their words.
_QUOTE_MARKERS = [
    re.compile(r"^\s*on .{5,80}\bwrote:\s*$", re.I | re.M),
    re.compile(r"^\s*-{2,}\s*original message\s*-{2,}", re.I | re.M),
    re.compile(r"^\s*_{5,}\s*$", re.M),
    re.compile(r"^\s*from:\s.+$", re.I | re.M),
    re.compile(r"^\s*>{1,}", re.M),
    re.compile(r"^\s*sent from my \w+", re.I | re.M),
]


def strip_quoted(text: str) -> str:
    """Keep only what this person actually typed.

    This is the single most important step: without it the reply contains a
    verbatim copy of our pitch, and any keyword search finds our own words.
    """
    cut = len(text)
    for pat in _QUOTE_MARKERS:
        m = pat.search(text)
        if m and m.start() < cut:
            cut = m.start()
    return text[:cut].strip()


def clean_text(raw_bytes: bytes) -> tuple[str, str, dict]:
    """(subject, body-without-quotes, headers) from a raw RFC822 message."""
    try:
        msg = email_lib.message_from_bytes(raw_bytes, policy=policy.compat32)
    except Exception:
        return "", "", {}
    subject = decode_subject(msg.get("Subject", ""))
    body = strip_quoted(_best_body(msg))
    body = _WS.sub(" ", body)
    body = _NL.sub("\n\n", body).strip()
    headers = {k.lower(): str(v) for k, v in msg.items()}
    return subject, body, headers


# ------------------------------------------------------------- auto-replies
# RFC 3834 and the de-facto headers every autoresponder sets.
_AUTO_HEADERS = ("auto-submitted", "x-autoreply", "x-autorespond",
                 "x-auto-response-suppress", "x-mailer-autoreply")

_AUTO_SUBJECT = re.compile(
    r"\b(out of (the )?office|auto(matic|mated)?[- ]?(reply|response)|"
    r"ticket\s*(id|no|number|received|creation)?\s*[:#]?\s*\d|"
    r"case\s*[:#]\s*\d|ref(erence)?\s*[:#]\s*\d|"
    r"support ticket|we (have )?received your|do[- ]not[- ]reply|"
    r"undeliverable|delivery status|thank you for (contacting|writing))\b", re.I)

_AUTO_BODY = re.compile(
    r"(this is an? (automated|automatic)|do not reply to this (e-?mail|message)|"
    r"your (support )?ticket (id|number|no)|has been (created|received|logged)|"
    r"we('ve| have) received your (e-?mail|message|request|query)|"
    r"our (support )?team will (get back|revert|respond)|"
    r"within \d+[- ]?\d* (business |working )?(hours|days)|"
    r"how was your (support )?experience|rate your (support )?experience|"
    r"currently out of (the )?office|on (annual |maternity )?leave until|"
    r"auto[- ]?generated|"
    # Helpdesk form-letter phrasing. These read as warmth but are template
    # text: "happy to assist" is what a ticket bot says, not a buyer.
    r"happy to (assist|help) you|for (further|any) assistance|"
    r"thank you for (contacting|writing to|reaching out to) (us|our)|"
    r"feel free to (call|contact|reach out to) us|"
    r"your (query|request|concern) (has been|is being)|"
    r"we (will|shall) (get back|revert|reach out) to you)", re.I)

# Mailboxes that are consumer support desks, not people who buy marketing.
_ROBOT_LOCALPARTS = (
    "noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon",
    "postmaster", "bounce", "notification", "notifications", "ticket", "tickets",
    "helpdesk", "auto",
)


def is_automated(subject: str, body: str, headers: dict | None = None,
                 sender: str = "") -> tuple[bool, str]:
    """Is this a machine talking? Returns (verdict, why).

    Header evidence is trusted outright. Subject/body patterns are the fallback
    for the many Indian helpdesks that set no auto headers at all - which is
    most of them, and is why header-only detection would still have let all 20
    ticket acknowledgements through as hot leads.
    """
    headers = headers or {}
    for h in _AUTO_HEADERS:
        v = (headers.get(h) or "").strip().lower()
        if v and v != "no":
            return True, f"header {h}: {v[:40]}"
    if (headers.get("precedence") or "").lower() in ("bulk", "auto_reply", "junk"):
        return True, "precedence: bulk"
    if (headers.get("return-path") or "").strip() in ("<>", ""):
        if headers.get("return-path") == "<>":
            return True, "null return-path (bounce)"

    local = (sender or "").split("@", 1)[0].lower()
    flat = re.sub(r"[.\-_]", "", local)
    for r in _ROBOT_LOCALPARTS:
        if flat.startswith(re.sub(r"[.\-_]", "", r)):
            return True, f"robot mailbox: {local}"

    m = _AUTO_SUBJECT.search(subject or "")
    if m:
        return True, f"subject: {m.group(0)[:40]}"
    m = _AUTO_BODY.search(body or "")
    if m:
        return True, f"body: {m.group(0)[:40]}"
    return False, ""


# ------------------------------------------------------------ intent
def _has_word(text: str, phrase: str) -> bool:
    """Word-boundary match.

    Substring matching made "yes" fire on "yesterday" and "collab" fire on our
    own signature. Multi-word phrases are matched literally but still bounded.
    """
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text) is not None


DECLINED = ["not interested", "no thanks", "not at the moment", "not right now",
            "we'll pass", "we will pass", "unsubscribe", "remove me", "stop",
            "no budget", "don't have budget", "do not have budget"]
NEGOTIATING = ["rate", "rates", "budget", "how much", "price", "pricing",
               "cost", "quote", "commission", "fee", "charges", "proposal"]
# Deliberately excludes "call", "connect" and "happy to": every support
# signature says "feel free to call us" and "stay connected", so they marked
# form letters as warm leads.
INTERESTED = ["interested", "let's talk", "lets talk", "sounds good",
              "would love", "keen", "share more", "tell me more", "send more",
              "schedule a", "discuss", "deck", "portfolio", "media kit",
              "profiles", "shortlist", "let's connect", "send us your",
              "share your"]


def classify(subject: str, body: str, headers: dict | None = None,
             sender: str = "") -> tuple[str, str]:
    """(status, reason). status: automated|declined|negotiating|interested|neutral

    Only the BODY is searched for intent. The subject is excluded on purpose:
    it is our own words coming back with "Re:" in front, which is precisely how
    every auto-acknowledgement was scored as a hot lead.
    """
    auto, why = is_automated(subject, body, headers, sender)
    if auto:
        return "automated", why

    low = (body or "").lower()
    if not low.strip():
        return "neutral", "empty body"
    for k in DECLINED:
        if _has_word(low, k):
            return "declined", k
    for k in NEGOTIATING:
        if _has_word(low, k):
            return "negotiating", k
    for k in INTERESTED:
        if _has_word(low, k):
            return "interested", k
    return "neutral", "no intent signal"
