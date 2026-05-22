import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.domain import _enum_values


class VerificationStatus(str, PyEnum):
    PENDING = "PENDING"
    VERIFIED_PENDING = "verified_pending"
    AWAITING_DOMAIN_REVIEW = "awaiting_domain_review"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(60), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)

    university: Mapped[str | None] = mapped_column(String(255), nullable=True)
    program: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year_of_study: Mapped[str | None] = mapped_column(String(20), nullable=True)

    university_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("universities.id"), nullable=True
    )
    university_link = relationship("University", back_populates="users")

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(
            VerificationStatus,
            name="verification_status",
            values_callable=_enum_values,
        ),
        default=VerificationStatus.PENDING,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_moderator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    post_votes = relationship("PostVote", back_populates="user", cascade="all, delete-orphan")
    comment_votes = relationship(
        "CommentVote", back_populates="user", cascade="all, delete-orphan"
    )
