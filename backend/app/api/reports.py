from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.security import get_current_user_strict, require_admin, require_verified
from app.models import Comment, ModerationReport, Post, ReportReason, ReportStatus, ReportTargetType, User
from app.schemas.content import AuthorOut  # noqa: E402 — after schemas loaded
from app.schemas.reports import (
    AdminReportOut,
    AdminReportsPageOut,
    ReportCreateIn,
    ReportCreatedOut,
    ReportedCommentOut,
    ReportedPostOut,
    ReportPendingOut,
    ReportResolveIn,
    ReporterOut,
)
from app.services.moderation_actions import load_report_target

router = APIRouter(tags=["reports"])
admin_router = APIRouter(prefix="/admin/reports", tags=["admin"])


async def _ensure_target_exists(
    db: AsyncSession, target_type: ReportTargetType, target_id: UUID
) -> Post | Comment:
    target = await load_report_target(db, target_type, target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reported content not found")
    return target


@router.post("/reports", response_model=ReportCreatedOut, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: ReportCreateIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> ReportCreatedOut:
    await _ensure_target_exists(db, payload.target_type, payload.target_id)

    dup = await db.execute(
        select(ModerationReport.id).where(
            ModerationReport.reporter_id == user.id,
            ModerationReport.target_type == payload.target_type,
            ModerationReport.target_id == payload.target_id,
            ModerationReport.status == ReportStatus.PENDING,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "You already have a pending report for this content",
        )

    report = ModerationReport(
        target_type=payload.target_type,
        target_id=payload.target_id,
        reporter_id=user.id,
        reason=payload.reason,
        detail=payload.detail,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return ReportCreatedOut(id=report.id, status=report.status)


@router.get("/reports/pending", response_model=ReportPendingOut)
async def check_pending_report(
    target_type: ReportTargetType,
    target_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_verified),
) -> ReportPendingOut:
    result = await db.execute(
        select(ModerationReport.id).where(
            ModerationReport.reporter_id == user.id,
            ModerationReport.target_type == target_type,
            ModerationReport.target_id == target_id,
            ModerationReport.status == ReportStatus.PENDING,
        )
    )
    return ReportPendingOut(pending=result.scalar_one_or_none() is not None)


def _reporter_out(report: ModerationReport) -> ReporterOut:
    if report.reporter_id is None:
        return ReporterOut(display_name="Auto", email=None)
    if report.reporter:
        return ReporterOut(
            id=report.reporter.id,
            display_name=report.reporter.display_name,
            email=report.reporter.email,
        )
    return ReporterOut(display_name="Deleted user", email=None)


def _target_out(target) -> ReportedPostOut | ReportedCommentOut:
    author = AuthorOut.model_validate(target.author)
    if isinstance(target, Post):
        return ReportedPostOut(
            id=target.id,
            title=target.title,
            body=target.body,
            author=author,
            created_at=target.created_at,
            is_hidden=target.is_hidden,
            hidden_reason=target.hidden_reason,
        )
    return ReportedCommentOut(
        id=target.id,
        body=target.body,
        post_id=target.post_id,
        author=author,
        created_at=target.created_at,
        is_hidden=target.is_hidden,
        hidden_reason=target.hidden_reason,
    )


def _statuses_for_filter(status_filter: str) -> list[ReportStatus]:
    if status_filter == "resolved":
        return [ReportStatus.RESOLVED_REMOVED, ReportStatus.RESOLVED_KEPT]
    try:
        return [ReportStatus(status_filter)]
    except ValueError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid status")


@admin_router.get("", response_model=AdminReportsPageOut)
async def list_admin_reports(
    status_filter: str = Query(default="pending", alias="status"),
    page: int = Query(default=1, ge=1),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> AdminReportsPageOut:
    statuses = _statuses_for_filter(status_filter)
    per_page = 20
    count_stmt = select(func.count(ModerationReport.id)).where(
        ModerationReport.status.in_(statuses)
    )
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(ModerationReport)
        .where(ModerationReport.status.in_(statuses))
        .options(
            selectinload(ModerationReport.reporter),
            selectinload(ModerationReport.resolver),
        )
        .order_by(ModerationReport.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(stmt)
    reports = list(result.scalars().all())

    items: list[AdminReportOut] = []
    for report in reports:
        target = await load_report_target(db, report.target_type, report.target_id)
        if not target:
            continue
        items.append(
            AdminReportOut(
                id=report.id,
                target_type=report.target_type,
                target_id=report.target_id,
                reason=report.reason,
                detail=report.detail,
                status=report.status,
                reporter=_reporter_out(report),
                target=_target_out(target),
                created_at=report.created_at,
                resolved_at=report.resolved_at,
                resolver_note=report.resolver_note,
            )
        )

    pages = max(1, ceil(total / per_page)) if total else 1
    return AdminReportsPageOut(
        items=items,
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
    )


@admin_router.post("/{report_id}/resolve", response_model=AdminReportOut)
async def resolve_report(
    report_id: UUID,
    payload: ReportResolveIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AdminReportOut:
    result = await db.execute(
        select(ModerationReport)
        .where(ModerationReport.id == report_id)
        .options(selectinload(ModerationReport.reporter))
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found")
    if report.status != ReportStatus.PENDING:
        raise HTTPException(status.HTTP_409_CONFLICT, "Report already resolved")

    target = await load_report_target(db, report.target_type, report.target_id)
    if not target:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reported content not found")

    now = datetime.now(timezone.utc)
    report.resolver_id = admin.id
    report.resolver_note = payload.note
    report.resolved_at = now

    if payload.action == "remove":
        hidden_reason = f"Removed after report: {report.reason.value}"
        if isinstance(target, Post):
            target.is_hidden = True
            target.hidden_reason = hidden_reason
        else:
            target.is_hidden = True
            target.hidden_reason = hidden_reason
        report.status = ReportStatus.RESOLVED_REMOVED
    elif payload.action == "keep":
        report.status = ReportStatus.RESOLVED_KEPT
    elif payload.action == "dismiss":
        report.status = ReportStatus.DISMISSED
    else:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid action")

    await db.commit()
    await db.refresh(report)
    if target:
        await db.refresh(target, ["author"])
        if target.author:
            await db.refresh(target.author, ["university_link"])

    return AdminReportOut(
        id=report.id,
        target_type=report.target_type,
        target_id=report.target_id,
        reason=report.reason,
        detail=report.detail,
        status=report.status,
        reporter=_reporter_out(report),
        target=_target_out(target),
        created_at=report.created_at,
        resolved_at=report.resolved_at,
        resolver_note=report.resolver_note,
    )
