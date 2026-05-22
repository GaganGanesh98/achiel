from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Comment, CommentVote
from app.models.user import User
from app.schemas.content import AuthorOut, CommentOut
from app.schemas.content import WatchlistMatchOut
from app.services.name_screening import screen_content, university_hint_from_user


def comment_body_for_response(comment: Comment, user: User | None = None) -> str:
    if comment.is_deleted:
        return "[removed]"
    if comment.is_hidden and user and comment.author_id == user.id:
        return comment.body
    return comment.body


async def build_comment_out(
    comment: Comment,
    db: AsyncSession,
    user: User | None,
) -> CommentOut:
    my_vote = 0
    if user:
        v_result = await db.execute(
            select(CommentVote).where(
                CommentVote.user_id == user.id, CommentVote.comment_id == comment.id
            )
        )
        v = v_result.scalar_one_or_none()
        my_vote = v.value if v else 0

    watchlist_matches = None
    if user and comment.is_hidden and comment.author_id == user.id:
        hint = university_hint_from_user(user)
        matches = screen_content(comment.body, hint)
        if matches:
            watchlist_matches = [WatchlistMatchOut(**m) for m in matches]

    return CommentOut(
        id=comment.id,
        body=comment_body_for_response(comment, user),
        post_id=comment.post_id,
        parent_comment_id=comment.parent_comment_id,
        is_deleted=comment.is_deleted,
        score=comment.score,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        author=AuthorOut.model_validate(comment.author),
        created_at=comment.created_at,
        my_vote=my_vote,
        is_hidden=comment.is_hidden,
        hidden_reason=comment.hidden_reason,
        watchlist_matches=watchlist_matches,
    )


async def build_comments_out(
    comments: list[Comment],
    db: AsyncSession,
    user: User | None,
) -> list[CommentOut]:
    votes_by_comment: dict[UUID, int] = {}
    if user and comments:
        comment_ids = [c.id for c in comments]
        votes_result = await db.execute(
            select(CommentVote).where(
                CommentVote.user_id == user.id, CommentVote.comment_id.in_(comment_ids)
            )
        )
        votes_by_comment = {v.comment_id: v.value for v in votes_result.scalars()}

    out: list[CommentOut] = []
    for c in comments:
        my_vote = votes_by_comment.get(c.id, 0)
        out.append(await build_comment_out(c, db, user))
    return out
