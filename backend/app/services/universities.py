"""University display-name lookup from email domain."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_UNIVERSITIES_PATH = _BACKEND_ROOT / "universities.json"


@lru_cache
def _load_university_map() -> dict[str, str]:
    if not _UNIVERSITIES_PATH.exists():
        return {}
    with _UNIVERSITIES_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return {k.lower().strip(): v for k, v in data.items()}


def extract_domain(email: str) -> str:
    return email.split("@", 1)[1].lower().strip()


def lookup_university(email: str) -> str | None:
    """Return mapped university name for the email domain, or None."""
    domain = extract_domain(email)
    return _load_university_map().get(domain)
