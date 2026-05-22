from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import require_admin
from app.models import (
    AllowedDomain,
    AllowedDomainSource,
    PendingDomain,
    PendingDomainStatus,
    User,
    VerificationStatus,
)
from app.schemas.domains import PendingDomainOut, PendingDomainRejectIn
from app.services import domain_notifications as notify

admin_router = APIRouter(prefix="/admin/pending-domains", tags=["admin"])


@admin_router.get("", response_model=list[PendingDomainOut])
async def list_pending_domains(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> list[PendingDomain]:
    result = await db.execute(
        select(PendingDomain)
        .where(PendingDomain.status == PendingDomainStatus.PENDING)
        .order_by(
            PendingDomain.confidence.desc(),
            PendingDomain.request_count.desc(),
        )
    )
    return list(result.scalars().all())


@admin_router.post("/{domain}/approve", response_model=PendingDomainOut)
async def approve_pending_domain(
    domain: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> PendingDomain:
    domain = domain.lower().strip()
    result = await db.execute(
        select(PendingDomain).where(PendingDomain.domain == domain)
    )
    pending = result.scalar_one_or_none()
    if pending is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pending domain not found")

    now = datetime.now(timezone.utc)
    existing_allowed = await db.execute(
        select(AllowedDomain).where(AllowedDomain.domain == domain)
    )
    if existing_allowed.scalar_one_or_none() is None:
        db.add(
            AllowedDomain(
                domain=domain,
                source=AllowedDomainSource.ADMIN,
                added_at=now,
                added_by=admin.email,
            )
        )

    pending.status = PendingDomainStatus.APPROVED

    users_result = await db.execute(
        select(User).where(
            User.verification_status == VerificationStatus.AWAITING_DOMAIN_REVIEW,
            User.email.like(f"%@{domain}"),
        )
    )
    unlocked = list(users_result.scalars().all())
    for user in unlocked:
        user.verification_status = VerificationStatus.VERIFIED
        user.is_verified = True

    await db.commit()
    await db.refresh(pending)

    for user in unlocked:
        await notify.notify_domain_approved(user.email, domain)

    return pending


@admin_router.post("/{domain}/reject", response_model=PendingDomainOut)
async def reject_pending_domain(
    domain: str,
    payload: PendingDomainRejectIn,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> PendingDomain:
    domain = domain.lower().strip()
    result = await db.execute(
        select(PendingDomain).where(PendingDomain.domain == domain)
    )
    pending = result.scalar_one_or_none()
    if pending is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pending domain not found")

    pending.status = PendingDomainStatus.REJECTED

    users_result = await db.execute(
        select(User).where(
            User.verification_status.in_(
                [
                    VerificationStatus.AWAITING_DOMAIN_REVIEW,
                    VerificationStatus.VERIFIED_PENDING,
                ]
            ),
            User.email.like(f"%@{domain}"),
        )
    )
    affected = list(users_result.scalars().all())
    for user in affected:
        user.verification_status = VerificationStatus.REJECTED
        user.is_active = False

    await db.commit()
    await db.refresh(pending)

    for user in affected:
        await notify.notify_domain_rejected(user.email, domain, payload.reason)

    return pending
