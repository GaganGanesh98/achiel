"""phase3_jobs_sentiment_votes_comments

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE sentiment AS ENUM ('positive', 'neutral', 'negative')")
    sentiment_enum = postgresql.ENUM(
        "positive", "neutral", "negative", name="sentiment", create_type=False
    )

    op.add_column(
        "posts",
        sa.Column("sentiment", sentiment_enum, nullable=True),
    )
    op.execute("UPDATE posts SET sentiment = 'neutral' WHERE sentiment IS NULL")
    op.alter_column("posts", "sentiment", nullable=False)

    op.add_column(
        "posts",
        sa.Column("upvotes", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "posts",
        sa.Column("downvotes", sa.Integer(), server_default="0", nullable=False),
    )

    op.execute(
        """
        UPDATE posts p SET
          upvotes = COALESCE((
            SELECT COUNT(*)::int FROM votes v
            WHERE v.post_id = p.id AND v.value = 1
          ), 0),
          downvotes = COALESCE((
            SELECT COUNT(*)::int FROM votes v
            WHERE v.post_id = p.id AND v.value = -1
          ), 0),
          score = COALESCE((
            SELECT SUM(v.value)::int FROM votes v WHERE v.post_id = p.id
          ), 0)
        """
    )

    op.rename_table("votes", "post_votes")
    op.alter_column(
        "post_votes",
        "value",
        existing_type=sa.Integer(),
        type_=sa.SmallInteger(),
        existing_nullable=False,
    )
    op.create_check_constraint(
        "ck_post_vote_value", "post_votes", "value IN (-1, 1)"
    )
    op.drop_constraint("uq_vote_user_post", "post_votes", type_="unique")
    op.create_unique_constraint(
        "uq_post_vote_user_post", "post_votes", ["user_id", "post_id"]
    )

    op.add_column(
        "comments",
        sa.Column("parent_comment_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_comments_parent_comment_id",
        "comments",
        "comments",
        ["parent_comment_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_comments_parent_comment_id", "comments", ["parent_comment_id"])

    op.add_column(
        "comments",
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "comments",
        sa.Column("score", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "comments",
        sa.Column("upvotes", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "comments",
        sa.Column("downvotes", sa.Integer(), server_default="0", nullable=False),
    )

    op.execute(
        """
        UPDATE comments SET is_deleted = true
        WHERE status::text IN ('removed', 'flagged', 'REMOVED', 'FLAGGED')
        """
    )
    op.drop_column("comments", "status")

    op.alter_column(
        "comments",
        "body",
        existing_type=sa.Text(),
        type_=sa.String(length=2000),
        existing_nullable=False,
    )

    op.create_table(
        "comment_votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("value", sa.SmallInteger(), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("comment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "comment_id", name="uq_comment_vote_user_comment"),
        sa.CheckConstraint("value IN (-1, 1)", name="ck_comment_vote_value"),
    )
    op.create_index("ix_comment_votes_comment_id", "comment_votes", ["comment_id"])


def downgrade() -> None:
    op.drop_index("ix_comment_votes_comment_id", table_name="comment_votes")
    op.drop_table("comment_votes")

    op.add_column(
        "comments",
        sa.Column(
            "status",
            postgresql.ENUM(
                "PUBLISHED",
                "FLAGGED",
                "REMOVED",
                name="post_status",
                create_type=False,
            ),
            server_default=sa.text("'PUBLISHED'::post_status"),
            nullable=False,
        ),
    )
    op.execute(
        "UPDATE comments SET status = 'REMOVED' WHERE is_deleted = true"
    )
    op.execute(
        "UPDATE comments SET status = 'PUBLISHED' WHERE is_deleted = false"
    )
    op.drop_column("comments", "downvotes")
    op.drop_column("comments", "upvotes")
    op.drop_column("comments", "score")
    op.drop_column("comments", "is_deleted")
    op.drop_index("ix_comments_parent_comment_id", table_name="comments")
    op.drop_constraint("fk_comments_parent_comment_id", "comments", type_="foreignkey")
    op.drop_column("comments", "parent_comment_id")
    op.alter_column(
        "comments",
        "body",
        existing_type=sa.String(length=2000),
        type_=sa.Text(),
        existing_nullable=False,
    )

    op.drop_constraint("uq_post_vote_user_post", "post_votes", type_="unique")
    op.create_unique_constraint("uq_vote_user_post", "post_votes", ["user_id", "post_id"])
    op.drop_constraint("ck_post_vote_value", "post_votes", type_="check")
    op.alter_column(
        "post_votes",
        "value",
        existing_type=sa.SmallInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.rename_table("post_votes", "votes")

    op.drop_column("posts", "downvotes")
    op.drop_column("posts", "upvotes")
    op.drop_column("posts", "sentiment")
    op.execute("DROP TYPE sentiment")
