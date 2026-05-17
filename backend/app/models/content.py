import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Text, ForeignKey, Enum, Integer, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Topic(str, PyEnum):
    TRAVEL = "travel"
    CULTURE = "culture"
    COST_OF_LIVING = "cost_of_living"
    ACADEMICS = "academics"
    HOUSING = "housing"
    GENERAL = "general"


class PostStatus(str, PyEnum):
    PUBLISHED = "published"
    FLAGGED = "flagged"     # caught by moderation, awaiting review
    REMOVED = "removed"     # soft-deleted by mod or author


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[Topic] = mapped_column(Enum(Topic, name="topic"), nullable=False, index=True)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status"), default=PostStatus.PUBLISHED, nullable=False
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author = relationship("User", back_populates="posts")

    # Denormalised so feeds can filter by uni without a join
    university_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("universities.id"), nullable=True, index=True
    )
    university = relationship("University", back_populates="posts")

    # Cached counters — updated on vote/comment create. Cheap and avoids COUNT(*) in feed.
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="post", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_posts_topic_created", "topic", "created_at"),
        Index("ix_posts_status_created", "status", "created_at"),
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status", create_type=False),
        default=PostStatus.PUBLISHED,
        nullable=False,
    )

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post = relationship("Post", back_populates="comments")

    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    author = relationship("User", back_populates="comments")


class VoteValue(int, PyEnum):
    UP = 1
    DOWN = -1


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 or -1

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="votes")

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    post = relationship("Post", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_vote_user_post"),
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    resolved: Mapped[bool] = mapped_column(default=False, nullable=False)

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    post = relationship("Post", back_populates="reports")

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
