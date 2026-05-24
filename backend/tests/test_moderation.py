"""Tests for the moderation pipeline (word list + OpenAI layer)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.core.config import settings
from app.services.moderation import (
    Decision,
    Unsafe,
    check_and_clean,
    classify_content,
    moderate,
    normalize_text,
    reset_moderation_clients,
)


@pytest.fixture(autouse=True)
def _reset_clients():
    reset_moderation_clients()
    yield
    reset_moderation_clients()


@pytest.fixture
def openai_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-key")


def _mock_moderation_response(**scores: float) -> MagicMock:
    defaults = {
        "harassment": 0.0,
        "harassment_threatening": 0.0,
        "hate": 0.0,
        "hate_threatening": 0.0,
        "self_harm_instructions": 0.0,
        "sexual": 0.0,
        "sexual_minors": 0.0,
        "violence": 0.0,
        "violence_graphic": 0.0,
    }
    defaults.update(scores)
    category_scores = MagicMock()
    category_scores.model_dump.return_value = defaults
    result = MagicMock()
    result.category_scores = category_scores
    response = MagicMock()
    response.results = [result]
    return response


def test_clean_text_passes():
    result = moderate("Hello, this is a normal university review.")
    assert result.decision == Decision.ALLOW
    assert result.cleaned_text == "Hello, this is a normal university review."
    assert result.reasons == []


def test_mild_profanity_censored():
    result = moderate("this is shit")
    assert result.decision == Decision.CENSOR
    assert "****" in result.cleaned_text
    assert "wordlist.profanity" in result.reasons


def test_severe_term_blocked():
    result = moderate("please kill yourself now")
    assert result.decision == Decision.BLOCK
    assert "wordlist.severe" in result.reasons


def test_unicode_bypass_blocked_or_censored():
    cases = ["f\u200duck", "ｆｕｃｋ", "fυck"]
    for raw in cases:
        assert normalize_text(raw) == "fuck"
        result = moderate(raw)
        assert result.decision in (Decision.CENSOR, Decision.BLOCK)
        if result.decision == Decision.CENSOR:
            assert "****" in result.cleaned_text


def test_german_severe_term_blocked():
    result = moderate("sieg heil everyone")
    assert result.decision == Decision.BLOCK
    assert "wordlist.severe" in result.reasons


def test_openai_classifier_called_when_key_set(openai_key):
    client = MagicMock()
    client.moderations.create.return_value = _mock_moderation_response(hate=0.82)

    with patch("app.services.moderation._get_openai_client", return_value=client):
        with patch("app.services.moderation._get_cached_categories", return_value=None):
            with patch("app.services.moderation._set_cached_categories"):
                result = classify_content("some borderline text")

    client.moderations.create.assert_called_once()
    assert result.decision == Decision.BLOCK
    assert any(r.startswith("openai.hate=") for r in result.reasons)


def test_openai_classifier_skipped_when_key_missing(caplog: pytest.LogCaptureFixture):
    with patch.object(settings, "OPENAI_API_KEY", None):
        reset_moderation_clients()
        with caplog.at_level("WARNING"):
            result = classify_content("hello")
        assert result.decision == Decision.ALLOW
        assert any("OPENAI_API_KEY not set" in r.message for r in caplog.records)


def test_redis_cache_hit(openai_key):
    client = MagicMock()
    client.moderations.create.return_value = _mock_moderation_response(hate=0.1)

    cached = {"hate": 0.1, "harassment": 0.05}
    with patch("app.services.moderation._get_openai_client", return_value=client):
        with patch(
            "app.services.moderation._get_cached_categories",
            side_effect=[None, cached],
        ) as get_cache:
            with patch("app.services.moderation._set_cached_categories") as set_cache:
                moderate("duplicate text please")
                moderate("duplicate text please")

    client.moderations.create.assert_called_once()
    assert get_cache.call_count == 2
    set_cache.assert_called_once()


def test_check_and_clean_backward_compat():
    cleaned, = check_and_clean("this is shit")
    assert "****" in cleaned

    with pytest.raises(Unsafe):
        check_and_clean("kill yourself")


def test_review_decision_from_openai(openai_key):
    client = MagicMock()
    client.moderations.create.return_value = _mock_moderation_response(harassment=0.45)

    with patch("app.services.moderation._get_openai_client", return_value=client):
        with patch("app.services.moderation._get_cached_categories", return_value=None):
            with patch("app.services.moderation._set_cached_categories"):
                result = moderate("you are awful")

    assert result.decision == Decision.REVIEW
    assert any(r.startswith("openai.harassment=") for r in result.reasons)
