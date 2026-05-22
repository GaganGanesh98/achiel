from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import Comment, Post
from app.models.report import (
    ModerationReport,
    ReportReason,
    ReportStatus,
    ReportTargetType,
)
from app.models.user import User
from app.services.name_screening import AUTO_HIDE_REASON, screen_content, university_hint_from_user

AUTO_FLAG_REASON = ReportReason.NAMES_INDIVIDUAL


async def apply_name_screening_to_post(
    db: AsyncSession, post: Post, user: User
) -> list[dict]:
    hint = university_hint_from_user(user)
    text = f"{post.title}\n{post.body}"
    matches = screen_content(text, hint)
    if not matches:
        return []

    post.is_hidden = True
    post.hidden_reason = AUTO_HIDE_REASON
    db.add(
        ModerationReport(
            target_type=ReportTargetType.POST,
            target_id=post.id,
            reporter_id=None,
            reason=AUTO_FLAG_REASON,
            detail=f"Auto-flagged watchlist matches: {', '.join(m['name'] for m in matches)}",
        )
    )
    return matches


async def apply_name_screening_to_comment(
    db: AsyncSession, comment: Comment, user: User
) -> list[dict]:
    hint = university_hint_from_user(user)
    matches = screen_content(comment.body, hint)
    if not matches:
        return []

    comment.is_hidden = True
    comment.hidden_reason = AUTO_HIDE_REASON
    db.add(
        ModerationReport(
            target_type=ReportTargetType.COMMENT,
            target_id=comment.id,
            reporter_id=None,
            reason=AUTO_FLAG_REASON,
            detail=f"Auto-flagged watchlist matches: {', '.join(m['name'] for m in matches)}",
        )
    )
    return matches


async def load_report_target(
    db: AsyncSession, target_type: ReportTargetType, target_id: UUID
):
    if target_type == ReportTargetType.POST:
        result = await db.execute(
            select(Post)
            .where(Post.id == target_id)
            .options(selectinload(Post.author).selectinload(User.university_link))
        )
        return result.scalar_one_or_none()
    result = await db.execute(
        select(Comment)
        .where(Comment.id == target_id)
        .options(selectinload(Comment.author).selectinload(User.university_link))
    )
    return result.scalar_one_or_none()
