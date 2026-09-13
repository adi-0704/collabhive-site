"""CollabHive Outreach — shared helpers.

Configuration loading, path resolution, logging, and small utilities.
Everything is dependency-free (stdlib only) so the GitHub Action needs no pip
install step and the whole system stays free.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# The outreach/ package root (this file lives in outreach/src/).
# Override with OUTREACH_ROOT (used by tests to sandbox data).
ROOT = Path(os.environ.get("OUTREACH_ROOT", Path(__file__).resolve().parent.parent))


def load_config(path: Path | None = None) -> dict:
    cfg_path = path or (ROOT / "config.json")
    with open(cfg_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


_DOTENV_LOADED = False


def load_dotenv(path: Path | None = None) -> int:
    """Load outreach/.env into os.environ (stdlib only, no python-dotenv).

    Real environment variables always win, so GitHub Actions secrets are never
    overridden by a stale local file. Runs once per process; returns how many
    keys were set.
    """
    global _DOTENV_LOADED
    if _DOTENV_LOADED and path is None:
        return 0
    env_path = path or (ROOT / ".env")
    if path is None:
        _DOTENV_LOADED = True
    if not env_path.exists():
        return 0
    loaded = 0
    with open(env_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                loaded += 1
    return loaded


def env(key: str, default: str = "") -> str:
    load_dotenv()
    return os.environ.get(key, default)


def gmail_credentials() -> tuple[str, str]:
    """Return (username, app_password) from environment or fall back to config.

    The app password must never be committed. GitHub Actions injects it as
    OUTREACH_EMAIL_USER / OUTREACH_EMAIL_PASS secrets. Local runs can place
    them in outreach/.env (gitignored), which load_dotenv() reads on first use.
    """
    cfg = load_config()
    user = env("OUTREACH_EMAIL_USER", cfg["smtp"]["username"])
    password = env("OUTREACH_EMAIL_PASS", "")
    return user, password


def load_json(path: Path) -> list | dict:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return []


def save_json(path: Path, data: list | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def log(msg: str) -> None:
    """Print a log line, surviving consoles that can't encode the characters.

    Brand/creator names routinely contain non-Latin-1 characters, and Windows
    consoles default to cp1252 — printing one raised UnicodeEncodeError and
    killed the whole run. Never let logging be the thing that breaks the job.
    """
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(str(msg).encode(encoding, "replace").decode(encoding, "replace"), flush=True)
