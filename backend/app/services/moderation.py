"""
Profanity / unsafe-language filter.

Strategy:
- `better-profanity` for common English profanity (fast, in-memory).
- A small custom blocklist for slurs and threats beyond the default list.
- Returns a `cleaned` body if profanity is mild (post still publishes but censored), OR
  raises `Unsafe` if the text contains slurs/threats — those don't get a "censored" pass.

Caveats Cursor should NOT pretend away:
- This is English-only. Multilingual moderation needs a real model (Perspective API,
  OpenAI moderation, or fine-tuned classifier). Document this in your roadmap.
- Wordlist-based filters miss context ("the dam project" vs "damn"). The library handles
  leetspeak ($h!t) but won't catch novel circumventions. Pair with the report queue.
"""

import json
from pathlib import Path

from better_profanity import profanity

from app.core.config import settings

profanity.load_censor_words()


def _load_severe_terms() -> set[str]:
    terms: set[str] = set()

    path: Path = settings.severe_terms_path
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip().lower()
            if line and not line.startswith("#"):
                terms.add(line)

    try:
        extra = json.loads(settings.SEVERE_TERMS_JSON)
        if isinstance(extra, list):
            terms.update(str(t).strip().lower() for t in extra if str(t).strip())
    except json.JSONDecodeError:
        pass

    return terms


SEVERE_TERMS: set[str] = _load_severe_terms()


class Unsafe(Exception):
    """Raised when text contains severe terms (slurs, explicit threats)."""

    def __init__(self, message: str = "Content violates community guidelines"):
        super().__init__(message)


def check_and_clean(*texts: str) -> tuple[str, ...]:
    """
    Validate one or more strings. Returns censored versions for mild profanity.
    Raises Unsafe for severe terms.
    """
    results: list[str] = []
    for text in texts:
        lower = text.lower()
        for term in SEVERE_TERMS:
            if term and term in lower:
                raise Unsafe()
        results.append(profanity.censor(text))
    return tuple(results)
