from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

def _enum_values(enum_cls: type) -> list[str]:
    return [member.value for member in enum_cls]


class AllowedDomainSource(str, PyEnum):
    SEED = "seed"
    ADMIN = "admin"
    PATTERN = "pattern"


class PendingDomainStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PendingDomainConfidence(str, PyEnum):
    HIGH = "high"
    LOW = "low"


class AllowedDomain(Base):
    __tablename__ = "allowed_domains"

    domain: Mapped[str] = mapped_column(Text, primary_key=True)
    source: Mapped[AllowedDomainSource] = mapped_column(
        Enum(
            AllowedDomainSource,
            name="allowed_domain_source",
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    added_by: Mapped[str | None] = mapped_column(Text, nullable=True)


class PendingDomain(Base):
    __tablename__ = "pending_domains"

    domain: Mapped[str] = mapped_column(Text, primary_key=True)
    first_seen_email: Mapped[str] = mapped_column(Text, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    confidence: Mapped[PendingDomainConfidence] = mapped_column(
        Enum(
            PendingDomainConfidence,
            name="pending_domain_confidence",
            values_callable=_enum_values,
        ),
        nullable=False,
    )
    mx_provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_hint: Mapped[str | None] = mapped_column(String(2), nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[PendingDomainStatus] = mapped_column(
        Enum(
            PendingDomainStatus,
            name="pending_domain_status",
            values_callable=_enum_values,
        ),
        default=PendingDomainStatus.PENDING,
        nullable=False,
    )
