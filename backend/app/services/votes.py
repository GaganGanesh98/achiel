"""Shared vote upsert logic for posts and comments."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Comment, CommentVote, Post, PostVote


def _apply_counter_delta(
    entity: Post | Comment,
    old_value: int | None,
    new_value: int,
) -> None:
    if old_value == 1:
        entity.upvotes -= 1
    elif old_value == -1:
        entity.downvotes -= 1
    if new_value == 1:
        entity.upvotes += 1
    elif new_value == -1:
        entity.downvotes += 1
    entity.score = entity.upvotes - entity.downvotes


async def upsert_post_vote(
    db: AsyncSession,
    post: Post,
    user_id: UUID,
    value: int,
) -> int:
    """Upsert post vote; value 0 removes. Returns my_vote (-1, 0, or 1)."""
    result = await db.execute(
        select(PostVote).where(PostVote.user_id == user_id, PostVote.post_id == post.id)
    )
    existing = result.scalar_one_or_none()
    old_value = existing.value if existing else None

    if value == 0:
        if existing:
            _apply_counter_delta(post, old_value, 0)
            await db.delete(existing)
        return 0

    if existing:
        if existing.value != value:
            _apply_counter_delta(post, old_value, value)
            existing.value = value
    else:
        _apply_counter_delta(post, None, value)
        db.add(PostVote(user_id=user_id, post_id=post.id, value=value))

    return value


async def upsert_comment_vote(
    db: AsyncSession,
    comment: Comment,
    user_id: UUID,
    value: int,
) -> int:
    """Upsert comment vote; value 0 removes. Returns my_vote (-1, 0, or 1)."""
    result = await db.execute(
        select(CommentVote).where(
            CommentVote.user_id == user_id, CommentVote.comment_id == comment.id
        )
    )
    existing = result.scalar_one_or_none()
    old_value = existing.value if existing else None

    if value == 0:
        if existing:
            _apply_counter_delta(comment, old_value, 0)
            await db.delete(existing)
        return 0

    if existing:
        if existing.value != value:
            _apply_counter_delta(comment, old_value, value)
            existing.value = value
    else:
        _apply_counter_delta(comment, None, value)
        db.add(CommentVote(user_id=user_id, comment_id=comment.id, value=value))

    return value
