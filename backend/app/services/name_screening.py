import json
import re
from functools import lru_cache
from pathlib import Path

WATCHLIST_PATH = Path(__file__).resolve().parents[2] / "name_watchlist.json"

AUTO_HIDE_REASON = "Pending moderation review — possible naming of individual"


@lru_cache(maxsize=1)
def _load_watchlist() -> list[dict]:
    if not WATCHLIST_PATH.is_file():
        return []
    data = json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))
    return list(data.get("individuals") or [])


def _matches_domain(entry: dict, university_hint: str | None) -> bool:
    domain = entry.get("university_domain")
    if not domain or not university_hint:
        return True
    return domain.strip().lower() == university_hint.strip().lower()


def screen_content(text: str, university_hint: str | None = None) -> list[dict]:
    """Return watchlist entries whose name appears as a whole word in text."""
    if not text or not text.strip():
        return []
    matches: list[dict] = []
    seen: set[str] = set()
    for entry in _load_watchlist():
        name = (entry.get("name") or "").strip()
        if not name or name.lower() in seen:
            continue
        if not _matches_domain(entry, university_hint):
            continue
        pattern = re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE | re.UNICODE)
        if pattern.search(text):
            seen.add(name.lower())
            matches.append(
                {
                    "name": name,
                    "university_domain": entry.get("university_domain"),
                    "role": entry.get("role"),
                }
            )
    return matches


def university_hint_from_user(user) -> str | None:
    if user.university_link and user.university_link.domain:
        return user.university_link.domain
    if user.email and "@" in user.email:
        return user.email.split("@", 1)[1].lower()
    return None
