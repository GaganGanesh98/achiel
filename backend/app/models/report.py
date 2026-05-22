import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ReportTargetType(str, PyEnum):
    POST = "post"
    COMMENT = "comment"


class ReportReason(str, PyEnum):
    NAMES_INDIVIDUAL = "names_individual"
    DEFAMATION = "defamation"
    HARASSMENT = "harassment"
    SPAM = "spam"
    HATE_SPEECH = "hate_speech"
    SEXUAL_CONTENT = "sexual_content"
    OTHER = "other"


class ReportStatus(str, PyEnum):
    PENDING = "pending"
    RESOLVED_REMOVED = "resolved_removed"
    RESOLVED_KEPT = "resolved_kept"
    DISMISSED = "dismissed"


class ModerationReport(Base):
    __tablename__ = "moderation_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    target_type: Mapped[ReportTargetType] = mapped_column(
        Enum(ReportTargetType, name="report_target_type"), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    reporter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason: Mapped[ReportReason] = mapped_column(
        Enum(ReportReason, name="report_reason"), nullable=False
    )
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"),
        default=ReportStatus.PENDING,
        nullable=False,
    )
    resolver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolver_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reporter = relationship("User", foreign_keys=[reporter_id])
    resolver = relationship("User", foreign_keys=[resolver_id])

    __table_args__ = (
        Index("ix_moderation_reports_status_created", "status", "created_at"),
    )
