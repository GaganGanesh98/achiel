import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class University(Base):
    __tablename__ = "universities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)  # ISO-3166-1 alpha-2
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)

    users = relationship("User", back_populates="university_link")
    posts = relationship("Post", back_populates="university")
