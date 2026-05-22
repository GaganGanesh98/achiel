from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.domain import PendingDomainConfidence, PendingDomainStatus


class PendingDomainOut(BaseModel):
    domain: str
    first_seen_email: str
    request_count: int
    confidence: PendingDomainConfidence
    mx_provider: str | None
    country_hint: str | None
    first_seen_at: datetime
    last_seen_at: datetime
    status: PendingDomainStatus

    model_config = {"from_attributes": True}


class PendingDomainRejectIn(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class UniversityLookupResponse(BaseModel):
    university: str | None
    status: Literal["allowed", "pending", "rejected"] | None = None
    message: str | None = None
