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


def env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def gmail_credentials() -> tuple[str, str]:
    """Return (username, app_password) from environment or fall back to config.

    The app password must never be committed. GitHub Actions injects it as
    OUTREACH_EMAIL_USER / OUTREACH_EMALL_PASS secrets. Local runs can place
    them in outreach/.env (gitignored) or set them as env vars.
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
    print(msg, flush=True)
