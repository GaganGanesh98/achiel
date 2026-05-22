from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api._comment_helpers import build_comment_out, build_comments_out
from app.core.db import get_db
from app.core.security import get_current_user, require_verified
from app.models import Comment, Post, PostStatus, User
from app.schemas.content import CommentCreate, CommentOut, VoteCountsOut, VoteIn
from app.services.content_visibility import comment_visibility_filter, viewer_can_see_post
from app.services.moderation import Unsafe, check_and_clean
from app.services.moderation_actions import apply_name_screening_to_comment
from app.services.votes import upsert_comment_vote


router = APIRouter(tags=["comments"])


@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
async def list_comments(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
) -> list[CommentOut]:
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post or post.status != PostStatus.PUBLISHED or not viewer_can_see_post(post, user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    visibility = comment_visibility_filter(user)
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .where(visibility)
        .options(selectinload(Comment.author).selectinload(User.university_link))
        .order_by(Comment.score.desc(), Comment.created_at.asc())
    )
    comments = list(result.scalars().all())
    return await build_comments_out(comments, db, user)


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: UUID,
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> CommentOut:
    post_exists = await db.execute(
        select(Post.id).where(Post.id == post_id, Post.status == PostStatus.PUBLISHED)
    )
    if not post_exists.scalar_one_or_none():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")

    if payload.parent_comment_id:
        parent_result = await db.execute(
            select(Comment).where(
                Comment.id == payload.parent_comment_id,
                Comment.post_id == post_id,
                Comment.is_deleted == False,  # noqa: E712
            )
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Parent comment not found")

    try:
        (cleaned,) = check_and_clean(payload.body)
    except Unsafe as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    comment = Comment(
        body=cleaned,
        post_id=post_id,
        author_id=user.id,
        parent_comment_id=payload.parent_comment_id,
    )
    db.add(comment)
    await db.flush()
    await apply_name_screening_to_comment(db, comment, user)
    await db.execute(
        update(Post).where(Post.id == post_id).values(comment_count=Post.comment_count + 1)
    )
    await db.commit()
    await db.refresh(comment, ["author"])
    await db.refresh(comment.author, ["university_link"])
    return await build_comment_out(comment, db, user)


@router.post("/comments/{comment_id}/vote", response_model=VoteCountsOut)
async def vote_comment(
    comment_id: UUID,
    payload: VoteIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> VoteCountsOut:
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment or comment.is_deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")

    my_vote = await upsert_comment_vote(db, comment, user.id, payload.value)
    await db.commit()
    await db.refresh(comment)

    return VoteCountsOut(
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        score=comment.score,
        my_vote=my_vote,
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> None:
    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.author))
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comment not found")

    if comment.author_id != user.id and not user.is_moderator:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not allowed to delete this comment")

    if not comment.is_deleted:
        comment.is_deleted = True
        await db.commit()
