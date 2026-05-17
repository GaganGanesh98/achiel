from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.security import get_current_user, require_verified
from app.models import (
    Comment,
    Post,
    PostStatus,
    Report,
    Topic,
    User,
    Vote,
)
from app.schemas.content import (
    CommentCreate,
    CommentOut,
    PostCreate,
    PostOut,
    ReportCreate,
    VoteIn,
)
from app.services.moderation import Unsafe, check_and_clean


router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostOut])
async def list_feed(
    topic: Topic | None = None,
    university_id: UUID | None = None,
    country: str | None = Query(default=None, min_length=2, max_length=2),
    sort: str = Query(default="new", pattern="^(new|top)$"),
    cursor: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> list[PostOut]:
    """
    Keyset pagination: pass the `created_at` of the last item as `cursor`.
    No OFFSET — performance stays constant as the feed grows.
    """
    stmt = (
        select(Post)
        .where(Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.author).selectinload(User.university))
        .options(selectinload(Post.university))
        .limit(limit)
    )

    if topic:
        stmt = stmt.where(Post.topic == topic)
    if university_id:
        stmt = stmt.where(Post.university_id == university_id)
    if country:
        # filter via the user's university country
        from app.models import University as Uni
        stmt = stmt.join(Uni, Post.university_id == Uni.id).where(Uni.country == country.upper())

    if sort == "new":
        if cursor:
            stmt = stmt.where(Post.created_at < cursor)
        stmt = stmt.order_by(Post.created_at.desc())
    else:  # top
        stmt = stmt.order_by(Post.score.desc(), Post.created_at.desc())

    result = await db.execute(stmt)
    posts = result.scalars().all()

    # Attach user_vote for the requesting user
    out: list[PostOut] = []
    if user:
        post_ids = [p.id for p in posts]
        votes_result = await db.execute(
            select(Vote).where(Vote.user_id == user.id, Vote.post_id.in_(post_ids))
        )
        votes_by_post = {v.post_id: v.value for v in votes_result.scalars()}
        for p in posts:
            data = PostOut.model_validate(p)
            data.user_vote = votes_by_post.get(p.id)
            out.append(data)
    else:
        out = [PostOut.model_validate(p) for p in posts]

    return out


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> Post:
    try:
        cleaned_title, cleaned_body = check_and_clean(payload.title, payload.body)
    except Unsafe as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    post = Post(
        title=cleaned_title,
        body=cleaned_body,
        topic=payload.topic,
        author_id=user.id,
        university_id=user.university_id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post, ["author", "university"])
    # eager-load author.university for response
    await db.refresh(post.author, ["university"])
    return post


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> Post:
    result = await db.execute(
        select(Post)
        .where(Post.id == post_id, Post.status == PostStatus.PUBLISHED)
        .options(selectinload(Post.author).selectinload(User.university))
        .options(selectinload(Post.university))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")
    out = PostOut.model_validate(post)
    if user:
        v_result = await db.execute(
            select(Vote).where(Vote.user_id == user.id, Vote.post_id == post.id)
        )
        v = v_result.scalar_one_or_none()
        out.user_vote = v.value if v else None
    return out


@router.post("/{post_id}/vote", response_model=PostOut)
async def vote(
    post_id: UUID,
    payload: VoteIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> Post:
    if payload.value not in (-1, 0, 1):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "value must be -1, 0, or 1")

    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    existing_result = await db.execute(
        select(Vote).where(Vote.user_id == user.id, Vote.post_id == post.id)
    )
    existing = existing_result.scalar_one_or_none()

    delta = 0
    if existing:
        if payload.value == 0:
            delta = -existing.value
            await db.delete(existing)
        elif existing.value != payload.value:
            delta = payload.value - existing.value
            existing.value = payload.value
    elif payload.value != 0:
        delta = payload.value
        db.add(Vote(user_id=user.id, post_id=post.id, value=payload.value))

    if delta:
        await db.execute(
            update(Post).where(Post.id == post.id).values(score=Post.score + delta)
        )
    await db.commit()
    return await get_post(post_id, db, user)


@router.post(
    "/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> Comment:
    post_exists = await db.execute(
        select(Post.id).where(Post.id == post_id, Post.status == PostStatus.PUBLISHED)
    )
    if not post_exists.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    try:
        (cleaned,) = check_and_clean(payload.body)
    except Unsafe as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    comment = Comment(body=cleaned, post_id=post_id, author_id=user.id)
    db.add(comment)
    await db.execute(
        update(Post).where(Post.id == post_id).values(comment_count=Post.comment_count + 1)
    )
    await db.commit()
    await db.refresh(comment, ["author"])
    await db.refresh(comment.author, ["university"])
    return comment


@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def list_comments(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id, Comment.status == PostStatus.PUBLISHED)
        .options(selectinload(Comment.author).selectinload(User.university))
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().all())


@router.post("/{post_id}/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_post(
    post_id: UUID,
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> None:
    post_exists = await db.execute(select(Post.id).where(Post.id == post_id))
    if not post_exists.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    db.add(Report(post_id=post_id, reporter_id=user.id, reason=payload.reason))

    # Auto-flag if reports cross a threshold
    count_result = await db.execute(
        select(func.count(Report.id)).where(Report.post_id == post_id, Report.resolved == False)  # noqa: E712
    )
    reports_count = count_result.scalar_one()
    if reports_count + 1 >= 3:
        await db.execute(
            update(Post).where(Post.id == post_id).values(status=PostStatus.FLAGGED)
        )

    await db.commit()
