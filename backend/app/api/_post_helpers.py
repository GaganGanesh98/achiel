from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Post, PostVote
from app.models.user import User
from app.schemas.content import PostOut
from app.schemas.content import WatchlistMatchOut
from app.services.name_screening import screen_content, university_hint_from_user


async def build_post_out(
    post: Post,
    db: AsyncSession,
    user: User | None,
) -> PostOut:
    my_vote = 0
    if user:
        v_result = await db.execute(
            select(PostVote).where(PostVote.user_id == user.id, PostVote.post_id == post.id)
        )
        v = v_result.scalar_one_or_none()
        my_vote = v.value if v else 0

    out = PostOut.model_validate(post)
    out.my_vote = my_vote
    out.user_vote = my_vote if my_vote != 0 else None
    if user and post.is_hidden and post.author_id == user.id:
        hint = university_hint_from_user(user)
        matches = screen_content(f"{post.title}\n{post.body}", hint)
        if matches:
            out.watchlist_matches = [WatchlistMatchOut(**m) for m in matches]
    return out


async def build_posts_out(
    posts: list[Post],
    db: AsyncSession,
    user: User | None,
) -> list[PostOut]:
    votes_by_post: dict[UUID, int] = {}
    if user and posts:
        post_ids = [p.id for p in posts]
        votes_result = await db.execute(
            select(PostVote).where(PostVote.user_id == user.id, PostVote.post_id.in_(post_ids))
        )
        votes_by_post = {v.post_id: v.value for v in votes_result.scalars()}

    out: list[PostOut] = []
    for p in posts:
        row = await build_post_out(p, db, user)
        my_vote = votes_by_post.get(p.id, 0)
        row.my_vote = my_vote
        row.user_vote = my_vote if my_vote != 0 else None
        out.append(row)
    return out
