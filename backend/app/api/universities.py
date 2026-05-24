from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models import Post, PostStatus, University, User
from app.schemas.auth import UniversityOut
from app.schemas.domains import UniversityLookupResponse
from app.services import university_email as uni_email
from app.services.german_catalogue import NON_GERMAN_DOMAIN_KEY
from app.services.universities import lookup_university

router = APIRouter(prefix="/universities", tags=["universities"])

PENDING_DOMAIN_MESSAGE = (
    "Wir kennen diese Domain noch nicht — wir prüfen sie innerhalb von 24 Stunden "
    "und schicken dir eine E-Mail, sobald dein Konto aktiv ist."
)

REJECTED_DOMAIN_MESSAGE = (
    "CampusVoice ist derzeit nur für Studierende an deutschen Hochschulen. "
    "CampusVoice is currently for students at German universities only."
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
        message = (
            validation.reason
            if validation.reason == NON_GERMAN_DOMAIN_KEY
            else REJECTED_DOMAIN_MESSAGE
        )
        return UniversityLookupResponse(
            university=None,
            status="rejected",
            message=message,
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


def _active_universities_filter():
    return University.deleted_at.is_(None), University.is_legacy.is_(False)


@router.get("", response_model=list[UniversityOut])
async def list_universities(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
) -> list[UniversityOut]:
    active_deleted, active_legacy = _active_universities_filter()
    verified_count = (
        select(func.count(User.id))
        .where(User.university_id == University.id, User.is_verified.is_(True))
        .correlate(University)
        .scalar_subquery()
    )

    if not q:
        stmt = (
            select(University, verified_count.label("verified_student_count"))
            .where(active_deleted, active_legacy)
            .order_by(University.name)
            .limit(50)
        )
    else:
        needle = q.lower().strip()
        like = f"%{needle}%"
        stmt = (
            select(University, verified_count.label("verified_student_count"))
            .where(
                active_deleted,
                active_legacy,
                or_(
                    func.lower(University.name).like(like),
                    func.lower(University.short_name).like(like),
                    func.cast(University.aliases, String).ilike(like),
                    func.similarity(func.lower(University.name), needle) > 0.3,
                    func.similarity(func.lower(func.coalesce(University.short_name, "")), needle)
                    > 0.3,
                ),
            )
            .order_by(
                func.similarity(func.lower(University.name), needle).desc(),
                University.name,
            )
            .limit(50)
        )

    result = await db.execute(stmt)
    rows = result.all()
    out: list[UniversityOut] = []
    for uni, count in rows:
        item = UniversityOut.model_validate(uni)
        item.verified_student_count = int(count or 0)
        out.append(item)
    return out


@router.get("/{university_id}", response_model=UniversityOut)
async def get_university(
    university_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> UniversityOut:
    active_deleted, active_legacy = _active_universities_filter()
    verified_count = (
        select(func.count(User.id))
        .where(User.university_id == University.id, User.is_verified.is_(True))
        .correlate(University)
        .scalar_subquery()
    )
    result = await db.execute(
        select(University, verified_count.label("verified_student_count"))
        .where(
            University.id == university_id,
            active_deleted,
            active_legacy,
        )
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(404, "University not found")
    uni, count = row
    item = UniversityOut.model_validate(uni)
    item.verified_student_count = int(count or 0)
    return item


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
