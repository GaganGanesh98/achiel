from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api._post_helpers import build_post_out, build_posts_out
from app.core.db import get_db
from app.core.limiter import limiter
from app.core.security import get_current_user, require_verified
from app.models import Post, PostStatus, Topic, User
from app.schemas.content import PostCreate, PostOut, VoteCountsOut, VoteIn
from app.services.content_visibility import post_visibility_filter, viewer_can_see_post
from app.services.moderation import Unsafe, check_and_clean
from app.services.moderation_actions import apply_name_screening_to_post
from app.services.votes import upsert_post_vote


router = APIRouter(prefix="/posts", tags=["posts"])


def parse_topic(topic: str | None) -> Topic | None:
    if topic is None:
        return None
    normalized = topic.strip().lower()
    try:
        return Topic(normalized)
    except ValueError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Invalid topic. Allowed: {[t.value for t in Topic]}",
        )


@router.get("", response_model=list[PostOut])
async def list_feed(
    topic: str | None = None,
    university_id: UUID | None = None,
    country: str | None = Query(default=None, min_length=2, max_length=2),
    sort: str = Query(default="new", pattern="^(new|top)$"),
    cursor: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> list[PostOut]:
    topic_enum = parse_topic(topic)

    visibility = post_visibility_filter(user)
    stmt = (
        select(Post)
        .where(Post.status == PostStatus.PUBLISHED)
        .where(visibility)
        .options(selectinload(Post.author).selectinload(User.university_link))
        .options(selectinload(Post.university))
        .limit(limit)
    )

    if topic_enum:
        stmt = stmt.where(Post.topic == topic_enum)
    if university_id:
        stmt = stmt.where(Post.university_id == university_id)
    if country:
        from app.models import University as Uni

        stmt = stmt.join(Uni, Post.university_id == Uni.id).where(
            Uni.country == country.upper()
        )

    if sort == "new":
        if cursor:
            stmt = stmt.where(Post.created_at < cursor)
        stmt = stmt.order_by(Post.created_at.desc())
    else:
        stmt = stmt.order_by(Post.score.desc(), Post.created_at.desc())

    result = await db.execute(stmt)
    posts = list(result.scalars().all())
    return await build_posts_out(posts, db, user)


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_post(
    request: Request,
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> PostOut:
    try:
        cleaned_title, cleaned_body = check_and_clean(payload.title, payload.body)
    except Unsafe as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    post = Post(
        title=cleaned_title,
        body=cleaned_body,
        topic=payload.topic,
        sentiment=payload.sentiment,
        author_id=user.id,
        university_id=user.university_id,
    )
    db.add(post)
    await db.flush()
    await apply_name_screening_to_post(db, post, user)
    await db.commit()
    await db.refresh(post, ["author", "university"])
    await db.refresh(post.author, ["university_link"])
    return await build_post_out(post, db, user)


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> PostOut:
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id, Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.author).selectinload(User.university_link))
        .options(selectinload(Post.university))
    )
    post = result.scalar_one_or_none()
    if not post or not viewer_can_see_post(post, user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    return await build_post_out(post, db, user)


@router.post("/{post_id}/vote", response_model=VoteCountsOut)
async def vote_post(
    post_id: UUID,
    payload: VoteIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> VoteCountsOut:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    my_vote = await upsert_post_vote(db, post, user.id, payload.value)
    await db.commit()
    await db.refresh(post)

    return VoteCountsOut(
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        score=post.score,
        my_vote=my_vote,
    )
