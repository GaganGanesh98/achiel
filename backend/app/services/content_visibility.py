from sqlalchemy import or_

from app.models.content import Comment, Post
from app.models.user import User


def post_visibility_filter(user: User | None):
    """SQLAlchemy filter: which posts are visible in list/detail for this viewer."""
    if user and user.is_admin:
        return True
    if user:
        return or_(Post.is_hidden.is_(False), Post.author_id == user.id)
    return Post.is_hidden.is_(False)


def comment_visibility_filter(user: User | None):
    if user and user.is_admin:
        return True
    if user:
        return or_(Comment.is_hidden.is_(False), Comment.author_id == user.id)
    return Comment.is_hidden.is_(False)


def viewer_can_see_post(post: Post, user: User | None) -> bool:
    if not post.is_hidden:
        return True
    if user is None:
        return False
    if user.is_admin or post.author_id == user.id:
        return True
    return False


def viewer_can_see_comment(comment: Comment, user: User | None) -> bool:
    if not comment.is_hidden:
        return True
    if user is None:
        return False
    if user.is_admin or comment.author_id == user.id:
        return True
    return False
