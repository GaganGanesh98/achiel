from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models import Post, PostStatus, University
from app.schemas.auth import UniversityOut
from app.schemas.domains import UniversityLookupResponse
from app.services import university_email as uni_email
from app.services.universities import lookup_university

router = APIRouter(prefix="/universities", tags=["universities"])


PENDING_DOMAIN_MESSAGE = (
    "We don't recognise this domain yet — we'll review it within 24 hours and "
    "email you when your account is active."
)

REJECTED_DOMAIN_MESSAGE = (
    "Email domain not allowed. We only accept verified university emails."
)


@router.get("/lookup", response_model=UniversityLookupResponse)
async def lookup_by_domain(
    domain: str = Query(..., min_length=2, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> UniversityLookupResponse:
    domain = domain.lower().strip()
    email = f"preview@{domain}"
    name = lookup_university(email)

    validation = await uni_email.validate_university_email(
        db, email, record_pending=False
    )
    if validation.status == "rejected":
        return UniversityLookupResponse(
            university=None,
            status="rejected",
            message=REJECTED_DOMAIN_MESSAGE,
        )
    if validation.status == "allowed":
        return UniversityLookupResponse(
            university=name or domain,
            status="allowed",
        )
    return UniversityLookupResponse(
        university=name,
        status="pending",
        message=PENDING_DOMAIN_MESSAGE,
    )


@router.get("", response_model=list[UniversityOut])
async def list_universities(
    country: str | None = Query(default=None, min_length=2, max_length=2),
    q: str | None = Query(default=None, min_length=2, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> list[University]:
    stmt = select(University).order_by(University.name)
    if country:
        stmt = stmt.where(University.country == country.upper())
    if q:
        stmt = stmt.where(University.name.ilike(f"%{q}%"))
    result = await db.execute(stmt.limit(50))
    return list(result.scalars().all())


@router.get("/{university_id}/stats")
async def university_stats(university_id: UUID, db: AsyncSession = Depends(get_db)) -> dict:
    uni_exists = await db.execute(select(University.id).where(University.id == university_id))
    if not uni_exists.scalar_one_or_none():
        raise HTTPException(404, "University not found")

    posts_count = await db.execute(
        select(func.count(Post.id)).where(
            Post.university_id == university_id,
            Post.status == PostStatus.PUBLISHED,
        )
    )
    return {"post_count": posts_count.scalar_one()}
