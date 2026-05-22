import uuid
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Topic(str, PyEnum):
    TRAVEL = "travel"
    CULTURE = "culture"
    COST_OF_LIVING = "cost_of_living"
    ACADEMICS = "academics"
    HOUSING = "housing"
    JOBS = "jobs"
    GENERAL = "general"


class Sentiment(str, PyEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class PostStatus(str, PyEnum):
    PUBLISHED = "published"
    FLAGGED = "flagged"
    REMOVED = "removed"


class Post(TimestampMixin, Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[Topic] = mapped_column(Enum(Topic, name="topic"), nullable=False, index=True)
    sentiment: Mapped[Sentiment] = mapped_column(
        Enum(Sentiment, name="sentiment"), nullable=False, index=True
    )
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status"), default=PostStatus.PUBLISHED, nullable=False
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author = relationship("User", back_populates="posts")

    university_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("universities.id"), nullable=True, index=True
    )
    university = relationship("University", back_populates="posts")

    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hidden_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    votes = relationship("PostVote", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_posts_topic_created", "topic", "created_at"),
        Index("ix_posts_status_created", "status", "created_at"),
    )


class PostVote(TimestampMixin, Base):
    __tablename__ = "post_votes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    value: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="post_votes")

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post = relationship("Post", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_vote_user_post"),
        CheckConstraint("value IN (-1, 1)", name="ck_post_vote_value"),
    )


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    body: Mapped[str] = mapped_column(String(2000), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post = relationship("Post", back_populates="comments")

    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    parent = relationship("Comment", remote_side="Comment.id", back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author = relationship("User", back_populates="comments")

    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hidden_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    votes = relationship("CommentVote", back_populates="comment", cascade="all, delete-orphan")


class CommentVote(TimestampMixin, Base):
    __tablename__ = "comment_votes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    value: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="comment_votes")

    comment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    comment = relationship("Comment", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="uq_comment_vote_user_comment"),
        CheckConstraint("value IN (-1, 1)", name="ck_comment_vote_value"),
    )


