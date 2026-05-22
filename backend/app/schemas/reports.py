from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.report import ReportReason, ReportStatus, ReportTargetType

if TYPE_CHECKING:
    from app.schemas.content import AuthorOut


class ReportCreateIn(BaseModel):
    target_type: ReportTargetType
    target_id: UUID
    reason: ReportReason
    detail: str | None = Field(default=None, max_length=1000)

    @field_validator("detail")
    @classmethod
    def strip_detail(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s or None


class ReportCreatedOut(BaseModel):
    id: UUID
    status: ReportStatus


class ReportPendingOut(BaseModel):
    pending: bool


class ReporterOut(BaseModel):
    id: UUID | None = None
    display_name: str
    email: str | None = None


class ReportedPostOut(BaseModel):
    type: str = "post"
    id: UUID
    title: str
    body: str
    author: AuthorOut
    created_at: datetime
    is_hidden: bool
    hidden_reason: str | None


class ReportedCommentOut(BaseModel):
    type: str = "comment"
    id: UUID
    body: str
    post_id: UUID
    author: AuthorOut
    created_at: datetime
    is_hidden: bool
    hidden_reason: str | None


class AdminReportOut(BaseModel):
    id: UUID
    target_type: ReportTargetType
    target_id: UUID
    reason: ReportReason
    detail: str | None
    status: ReportStatus
    reporter: ReporterOut
    target: ReportedPostOut | ReportedCommentOut
    created_at: datetime
    resolved_at: datetime | None
    resolver_note: str | None


class AdminReportsPageOut(BaseModel):
    items: list[AdminReportOut]
    page: int
    per_page: int
    total: int
    pages: int


class ReportResolveIn(BaseModel):
    action: str = Field(pattern="^(remove|keep|dismiss)$")
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("note")
    @classmethod
    def strip_note(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s or None


def _resolve_schema_refs() -> None:
    from app.schemas.content import AuthorOut

    ReportedPostOut.model_rebuild(_types_namespace={"AuthorOut": AuthorOut})
    ReportedCommentOut.model_rebuild(_types_namespace={"AuthorOut": AuthorOut})


_resolve_schema_refs()
