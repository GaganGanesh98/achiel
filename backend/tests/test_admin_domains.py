import uuid
from datetime import datetime, timezone
from unittest.mock import patch

from sqlalchemy import select

from app.api.admin_domains import approve_pending_domain
from app.models import AllowedDomain, PendingDomain, User, VerificationStatus
from app.models.domain import PendingDomainConfidence, PendingDomainStatus
from app.services import university_email as uni_email
from tests.conftest import allow_domain


async def _create_awaiting_user(db, email: str) -> User:
    user = User(
        email=email,
        hashed_password="hashed",
        display_name="Test User",
        country="DE",
        verification_status=VerificationStatus.AWAITING_DOMAIN_REVIEW,
        is_verified=True,
    )
    db.add(user)
    await db.flush()
    return user


async def test_admin_approve_unlocks_waiting_accounts(db, clean_domain_tables) -> None:
    domain = "newuni.education"
    now = datetime.now(timezone.utc)
    db.add(
        PendingDomain(
            domain=domain,
            first_seen_email="first@newuni.education",
            request_count=1,
            confidence=PendingDomainConfidence.LOW,
            first_seen_at=now,
            last_seen_at=now,
            status=PendingDomainStatus.PENDING,
        )
    )
    suffix = uuid.uuid4().hex[:8]
    user = await _create_awaiting_user(db, f"student-{suffix}@{domain}")
    await db.commit()

    admin = User(
        email=f"admin-{suffix}@test.edu",
        hashed_password="x",
        display_name="Admin",
        country="US",
        is_admin=True,
        verification_status=VerificationStatus.VERIFIED,
        is_verified=True,
    )

    with patch("app.api.admin_domains.notify.notify_domain_approved"):
        await approve_pending_domain(domain, db=db, admin=admin)

    await db.refresh(user)
    assert user.verification_status == VerificationStatus.VERIFIED
    allowed = (
        await db.execute(select(AllowedDomain).where(AllowedDomain.domain == domain))
    ).scalar_one_or_none()
    assert allowed is not None

    pending = (
        await db.execute(select(PendingDomain).where(PendingDomain.domain == domain))
    ).scalar_one()
    assert pending.status == PendingDomainStatus.APPROVED


async def test_mit_edu_allowed_when_seeded(db, clean_domain_tables) -> None:
    await allow_domain(db, "mit.edu")
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(db, "student@mit.edu")
    assert result.status == "allowed"
