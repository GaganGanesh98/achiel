from unittest.mock import patch

import pytest
from sqlalchemy import select

from app.models.domain import PendingDomain, PendingDomainConfidence
from app.services import university_email as uni_email
from tests.conftest import allow_domain


@pytest.mark.parametrize(
    "email,domain",
    [
        ("student@srh-university.de", "srh-university.de"),
        ("user@mit.edu", "mit.edu"),
    ],
)
async def test_known_university_domains_allowed(
    db, clean_domain_tables, email: str, domain: str
) -> None:
    await allow_domain(db, domain)
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(db, email)
    assert result.status == "allowed"


async def test_disposable_domain_rejected(db, clean_domain_tables) -> None:
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(db, "x@mailinator.com")
    assert result.status == "rejected"
    assert "Disposable" in result.reason


async def test_no_mx_rejected(db, clean_domain_tables) -> None:
    with patch.object(uni_email, "domain_has_mx", return_value=False):
        result = await uni_email.validate_university_email(db, "funny@abc.com")
    assert result.status == "rejected"
    assert "MX" in result.reason


async def test_unknown_plausible_pending_high(db, clean_domain_tables) -> None:
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(db, "user@ox.ac.uk")
    assert result.status == "pending"
    row = (
        await db.execute(select(PendingDomain).where(PendingDomain.domain == "ox.ac.uk"))
    ).scalar_one()
    assert row.confidence == PendingDomainConfidence.HIGH


async def test_unknown_low_confidence_pending(db, clean_domain_tables) -> None:
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(db, "user@newuni.education")
    assert result.status == "pending"
    row = (
        await db.execute(
            select(PendingDomain).where(PendingDomain.domain == "newuni.education")
        )
    ).scalar_one()
    assert row.confidence == PendingDomainConfidence.LOW


async def test_pending_domain_request_count_increments(db, clean_domain_tables) -> None:
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        await uni_email.validate_university_email(db, "a@newuni.education")
        await uni_email.validate_university_email(db, "b@newuni.education")
    await db.commit()
    row = (
        await db.execute(
            select(PendingDomain).where(PendingDomain.domain == "newuni.education")
        )
    ).scalar_one()
    assert row.request_count == 2
