"""
Profanity / unsafe-language filter with optional OpenAI omni-moderation layer.

Layers (in order):
1. Unicode normalisation (NFKC, zero-width strip, confusable mapping).
2. Word list — severe terms block; mild English profanity censored.
3. OpenAI `omni-moderation-latest` when OPENAI_API_KEY is set (cached in Redis).

Caveats:
- Word lists miss novel circumventions and context; pair with reports + API layer.
- Without OPENAI_API_KEY the service degrades to word-list-only (warning logged once).
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import confusables
from better_profanity import profanity
from openai import OpenAI
from redis import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

profanity.load_censor_words()

_ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u206a-\u206f\ufeff]")

CACHE_PREFIX = "mod:omni:"
CACHE_TTL_SECONDS = 7 * 24 * 3600

BLOCK_THRESHOLD = 0.5
REVIEW_THRESHOLD = 0.3

# API field name -> canonical slash key used in reasons / ModerationResult.categories
_SCORE_KEY_MAP: dict[str, str] = {
    "harassment": "harassment",
    "harassment_threatening": "harassment/threatening",
    "hate": "hate",
    "hate_threatening": "hate/threatening",
    "self_harm_instructions": "self-harm/instructions",
    "sexual": "sexual",
    "sexual_minors": "sexual/minors",
    "violence": "violence",
    "violence_graphic": "violence/graphic",
}

BLOCK_CATEGORIES = frozenset(
    {
        "hate",
        "hate/threatening",
        "harassment/threatening",
        "self-harm/instructions",
        "sexual/minors",
        "violence/graphic",
    }
)

REVIEW_CATEGORIES = frozenset({"harassment", "sexual", "violence"})

_openai_client: OpenAI | None = None
_redis_sync: Redis | None = None
_missing_key_logged = False


class Decision(StrEnum):
    ALLOW = "allow"
    CENSOR = "censor"
    REVIEW = "review"
    BLOCK = "block"


@dataclass
class ModerationResult:
    decision: Decision
    cleaned_text: str
    reasons: list[str]
    categories: dict[str, float]


class Unsafe(Exception):
    """Raised when text contains severe terms (slurs, explicit threats)."""

    def __init__(self, message: str = "Content violates community guidelines"):
        super().__init__(message)


def normalize_text(text: str) -> str:
    """NFKC, strip zero-width chars, map Unicode confusables to ASCII."""
    text = unicodedata.normalize("NFKC", text)
    text = _ZERO_WIDTH_RE.sub("", text)
    forms = confusables.normalize(text, prioritize_alpha=True)
    return forms[0] if forms else text


def _load_terms_from_file(path: Path) -> set[str]:
    terms: set[str] = set()
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip().lower()
            if line and not line.startswith("#"):
                terms.add(line)
    return terms


def _load_terms_from_json(raw: str) -> set[str]:
    terms: set[str] = set()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            terms.update(str(t).strip().lower() for t in parsed if str(t).strip())
    except json.JSONDecodeError:
        pass
    return terms


def _load_severe_terms() -> set[str]:
    terms = _load_terms_from_file(settings.severe_terms_path)
    terms |= _load_terms_from_file(settings.severe_terms_de_path)
    terms |= _load_terms_from_json(settings.SEVERE_TERMS_JSON)
    terms |= _load_terms_from_json(settings.SEVERE_TERMS_DE_JSON)
    return terms


SEVERE_TERMS: set[str] = _load_severe_terms()


def _text_hash(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _get_redis_sync() -> Redis | None:
    global _redis_sync
    if _redis_sync is None:
        try:
            _redis_sync = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_sync.ping()
        except Exception:
            logger.debug("Redis unavailable for moderation cache", exc_info=True)
            _redis_sync = None
    return _redis_sync


def _cache_key(normalized: str) -> str:
    return f"{CACHE_PREFIX}{_text_hash(normalized)}"


def _get_cached_categories(normalized: str) -> dict[str, float] | None:
    client = _get_redis_sync()
    if client is None:
        return None
    try:
        raw = client.get(_cache_key(normalized))
        if raw:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): float(v) for k, v in data.items()}
    except Exception:
        logger.debug("Moderation cache read failed", exc_info=True)
    return None


def _set_cached_categories(normalized: str, categories: dict[str, float]) -> None:
    client = _get_redis_sync()
    if client is None:
        return
    try:
        client.setex(_cache_key(normalized), CACHE_TTL_SECONDS, json.dumps(categories))
    except Exception:
        logger.debug("Moderation cache write failed", exc_info=True)


def _get_openai_client() -> OpenAI | None:
    global _openai_client
    if not settings.OPENAI_API_KEY:
        return None
    if _openai_client is None:
        _openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def _categories_from_api_scores(category_scores) -> dict[str, float]:
    raw = category_scores.model_dump()
    return {
        _SCORE_KEY_MAP[key]: float(raw[key] or 0.0)
        for key in _SCORE_KEY_MAP
        if key in raw
    }


def _decision_from_categories(categories: dict[str, float]) -> tuple[Decision, list[str]]:
    reasons: list[str] = []
    for cat in BLOCK_CATEGORIES:
        score = categories.get(cat, 0.0)
        if score >= BLOCK_THRESHOLD:
            reasons.append(f"openai.{cat}={score:.2f}")
    if reasons:
        return Decision.BLOCK, reasons

    for cat in REVIEW_CATEGORIES:
        score = categories.get(cat, 0.0)
        if score >= REVIEW_THRESHOLD:
            reasons.append(f"openai.{cat}={score:.2f}")
    if reasons:
        return Decision.REVIEW, reasons

    return Decision.ALLOW, []


def _call_openai_moderation(normalized: str, *, lang: str | None) -> dict[str, float]:
    """Invoke OpenAI omni-moderation-latest; returns category scores."""
    _ = lang  # reserved for future locale hints; model is multilingual
    client = _get_openai_client()
    if client is None:
        return {}

    cached = _get_cached_categories(normalized)
    if cached is not None:
        return cached

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=normalized,
    )
    categories = _categories_from_api_scores(response.results[0].category_scores)
    _set_cached_categories(normalized, categories)
    return categories


def _wordlist_layer(text: str, normalized: str) -> tuple[Decision | None, str, list[str]]:
    """Severe terms -> BLOCK; mild profanity -> CENSOR. None decision = no wordlist hit."""
    lower = normalized.lower()
    for term in SEVERE_TERMS:
        if term and term in lower:
            return Decision.BLOCK, text, ["wordlist.severe"]

    if profanity.contains_profanity(normalized):
        return Decision.CENSOR, profanity.censor(normalized), ["wordlist.profanity"]

    return None, text, []


def classify_content(text: str, *, lang: str | None = None) -> ModerationResult:
    """
    OpenAI omni-moderation layer only (after normalisation).
    Falls back to ALLOW when OPENAI_API_KEY is missing.
    """
    global _missing_key_logged

    normalized = normalize_text(text)
    if not settings.OPENAI_API_KEY:
        if not _missing_key_logged:
            logger.warning(
                "OPENAI_API_KEY not set; classify_content uses word-list-only degraded mode"
            )
            _missing_key_logged = True
        return ModerationResult(
            decision=Decision.ALLOW,
            cleaned_text=text,
            reasons=[],
            categories={},
        )

    categories = _call_openai_moderation(normalized, lang=lang)
    decision, reasons = _decision_from_categories(categories)
    return ModerationResult(
        decision=decision,
        cleaned_text=text,
        reasons=reasons,
        categories=categories,
    )


def moderate(text: str, *, lang: str | None = None) -> ModerationResult:
    """Full pipeline: normalise, word list, then OpenAI classifier."""
    normalized = normalize_text(text)

    wl_decision, cleaned, wl_reasons = _wordlist_layer(text, normalized)
    if wl_decision == Decision.BLOCK:
        return ModerationResult(
            decision=Decision.BLOCK,
            cleaned_text=text,
            reasons=wl_reasons,
            categories={},
        )

    decision = wl_decision or Decision.ALLOW
    reasons = list(wl_reasons)
    categories: dict[str, float] = {}

    if settings.OPENAI_API_KEY:
        categories = _call_openai_moderation(normalized, lang=lang)
        api_decision, api_reasons = _decision_from_categories(categories)
        if api_decision == Decision.BLOCK:
            return ModerationResult(
                decision=Decision.BLOCK,
                cleaned_text=text,
                reasons=wl_reasons + api_reasons,
                categories=categories,
            )
        if api_decision == Decision.REVIEW:
            decision = Decision.REVIEW
            reasons.extend(api_reasons)
    else:
        global _missing_key_logged
        if not _missing_key_logged:
            logger.warning(
                "OPENAI_API_KEY not set; moderate() uses word-list-only degraded mode"
            )
            _missing_key_logged = True

    return ModerationResult(
        decision=decision,
        cleaned_text=cleaned,
        reasons=reasons,
        categories=categories,
    )


def check_and_clean(*texts: str) -> tuple[str, ...]:
    """
    Validate one or more strings. Returns censored versions for mild profanity.
    Raises Unsafe for severe terms. Applies Unicode normalisation before checks.
    """
    results: list[str] = []
    for text in texts:
        result = moderate(text)
        if result.decision == Decision.BLOCK:
            raise Unsafe()
        results.append(result.cleaned_text)
    return tuple(results)


def reset_moderation_clients() -> None:
    """Test helper: clear cached OpenAI / Redis clients and missing-key log flag."""
    global _openai_client, _redis_sync, _missing_key_logged
    _openai_client = None
    _redis_sync = None
    _missing_key_logged = False
