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

from better_profanity import profanity

# Init once at import. better_profanity uses its bundled list by default.
profanity.load_censor_words()

# Extend with severe terms that should outright reject, not just censor.
# Keep this list private and short. Don't enumerate slurs in source — reference an env-loaded
# file in real deployment. For MVP scaffold, leave a placeholder so Cursor doesn't auto-fill it.
SEVERE_TERMS: set[str] = set()  # populate from env or external file before deploy


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
