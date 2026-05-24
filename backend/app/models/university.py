import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class University(TimestampMixin, Base):
    __tablename__ = "universities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    short_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    aliases: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    state: Mapped[str | None] = mapped_column(String(64), nullable=True)
    type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_legacy: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    users = relationship("User", back_populates="university_link")
    posts = relationship("Post", back_populates="university")
