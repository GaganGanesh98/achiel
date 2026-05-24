"""Tests for German university search and signup domain gating."""

from collections.abc import AsyncIterator
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.db import get_db
from app.models import University
from app.seed.german_universities import seed_rows
from app.services import university_email as uni_email
from main import app


@pytest.fixture
async def api_client(db) -> AsyncIterator[AsyncClient]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


async def _ensure_catalogue_rows(db, *domains: str) -> None:
    by_domain = {row["domain"]: row for row in seed_rows()}
    for domain in domains:
        row = by_domain[domain]
        existing = await db.execute(select(University).where(University.domain == domain))
        if existing.scalar_one_or_none() is None:
            db.add(University(**row))
    await db.commit()


async def test_search_by_short_name(api_client, db):
    await _ensure_catalogue_rows(db, "tum.de")
    resp = await api_client.get("/universities", params={"q": "TUM"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(u.get("short_name") == "TUM" for u in data)


async def test_search_by_alias(api_client, db):
    await _ensure_catalogue_rows(db, "bsbi.de")
    resp = await api_client.get("/universities", params={"q": "BSBI"})
    assert resp.status_code == 200
    names = [u["name"] for u in resp.json()]
    assert any("Berlin School of Business" in n for n in names)


async def test_search_fuzzy_typo(api_client, db):
    await _ensure_catalogue_rows(db, "tum.de", "lmu.de")
    resp = await api_client.get("/universities", params={"q": "Münchn"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_search_empty_returns_first_50(api_client, db):
    await _ensure_catalogue_rows(db, "tum.de", "tu-berlin.de", "lmu.de")
    resp = await api_client.get("/universities")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 50
    if len(data) >= 2:
        assert data[0]["name"] <= data[1]["name"]


async def test_no_country_param_ignored(api_client):
    resp = await api_client.get("/universities", params={"country": "US", "q": "TUM"})
    assert resp.status_code == 200


async def test_signup_rejects_non_german_domain(db, clean_domain_tables):
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(
            db, "student@harvard.edu", record_pending=False
        )
    assert result.status == "rejected"
    assert result.reason == "auth.signup.non_german_domain"


async def test_signup_accepts_de_domain(db, clean_domain_tables):
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(
            db, "student@tu-berlin.de", record_pending=False
        )
    assert result.status == "allowed"


async def test_signup_accepts_allowlisted_non_de(db, clean_domain_tables):
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(
            db, "student@iu.org", record_pending=False
        )
    assert result.status == "allowed"
