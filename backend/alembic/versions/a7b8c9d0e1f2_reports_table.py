"""reports_table

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

report_target_type = postgresql.ENUM(
    "post", "comment", name="report_target_type", create_type=False
)
report_reason = postgresql.ENUM(
    "names_individual",
    "defamation",
    "harassment",
    "spam",
    "hate_speech",
    "sexual_content",
    "other",
    name="report_reason",
    create_type=False,
)
report_status = postgresql.ENUM(
    "pending",
    "resolved_removed",
    "resolved_kept",
    "dismissed",
    name="report_status",
    create_type=False,
)


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS reports CASCADE")

    report_target_type.create(op.get_bind(), checkfirst=True)
    report_reason.create(op.get_bind(), checkfirst=True)
    report_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "moderation_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("target_type", report_target_type, nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reason", report_reason, nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column(
            "status",
            report_status,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("resolver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolver_note", sa.Text(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolver_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_moderation_reports_target_id", "moderation_reports", ["target_id"]
    )
    op.create_index(
        "ix_moderation_reports_status_created",
        "moderation_reports",
        ["status", "created_at"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX uq_moderation_report_pending_per_reporter
        ON moderation_reports (reporter_id, target_type, target_id)
        WHERE status = 'pending' AND reporter_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_moderation_report_pending_per_reporter")
    op.drop_index("ix_moderation_reports_status_created", table_name="moderation_reports")
    op.drop_index("ix_moderation_reports_target_id", table_name="moderation_reports")
    op.drop_table("moderation_reports")
    op.execute("DROP TYPE IF EXISTS report_status")
    op.execute("DROP TYPE IF EXISTS report_reason")
    op.execute("DROP TYPE IF EXISTS report_target_type")

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reporter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="CASCADE"),
    )
