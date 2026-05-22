"""domain_validation_tables

Revision ID: g7h8i9j0k1l2
Revises: a7b8c9d0e1f2
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_enum_if_missing(name: str, values: str) -> None:
    op.execute(
        f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values});
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )


def upgrade() -> None:
    op.execute(
        "ALTER TYPE verification_status ADD VALUE IF NOT EXISTS 'verified_pending'"
    )
    op.execute(
        "ALTER TYPE verification_status ADD VALUE IF NOT EXISTS 'awaiting_domain_review'"
    )

    _create_enum_if_missing("allowed_domain_source", "'seed', 'admin', 'pattern'")
    _create_enum_if_missing("pending_domain_confidence", "'high', 'low'")
    _create_enum_if_missing("pending_domain_status", "'pending', 'approved', 'rejected'")

    allowed_source = postgresql.ENUM(
        "seed", "admin", "pattern", name="allowed_domain_source", create_type=False
    )
    pending_confidence = postgresql.ENUM(
        "high", "low", name="pending_domain_confidence", create_type=False
    )
    pending_status = postgresql.ENUM(
        "pending", "approved", "rejected", name="pending_domain_status", create_type=False
    )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "allowed_domains" not in inspector.get_table_names():
        op.create_table(
        "allowed_domains",
        sa.Column("domain", sa.Text(), primary_key=True),
        sa.Column("source", allowed_source, nullable=False),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("added_by", sa.Text(), nullable=True),
        )

    if "pending_domains" not in inspector.get_table_names():
        op.create_table(
        "pending_domains",
        sa.Column("domain", sa.Text(), primary_key=True),
        sa.Column("first_seen_email", sa.Text(), nullable=False),
        sa.Column("request_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("confidence", pending_confidence, nullable=False),
        sa.Column("mx_provider", sa.Text(), nullable=True),
        sa.Column("country_hint", sa.String(2), nullable=True),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "status",
            pending_status,
            server_default="pending",
            nullable=False,
        ),
        )


def downgrade() -> None:
    op.drop_table("pending_domains")
    op.drop_table("allowed_domains")
    op.execute("DROP TYPE IF EXISTS pending_domain_status")
    op.execute("DROP TYPE IF EXISTS pending_domain_confidence")
    op.execute("DROP TYPE IF EXISTS allowed_domain_source")
