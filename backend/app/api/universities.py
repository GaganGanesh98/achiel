from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models import University, Post, PostStatus
from app.schemas.auth import UniversityOut


router = APIRouter(prefix="/universities", tags=["universities"])


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
