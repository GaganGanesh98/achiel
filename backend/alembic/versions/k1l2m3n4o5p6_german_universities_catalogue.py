"""german universities catalogue

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-05-23

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, insert

from app.seed.german_universities import seed_rows

revision: str = "k1l2m3n4o5p6"
down_revision: Union[str, None] = "j0k1l2m3n4o5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.add_column("universities", sa.Column("short_name", sa.String(40), nullable=True))
    op.add_column(
        "universities",
        sa.Column("aliases", JSONB, nullable=False, server_default="[]"),
    )
    op.add_column("universities", sa.Column("state", sa.String(64), nullable=True))
    op.add_column("universities", sa.Column("type", sa.String(32), nullable=True))
    op.add_column("universities", sa.Column("website", sa.String(255), nullable=True))
    op.add_column(
        "universities",
        sa.Column("is_legacy", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "universities",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    rows = seed_rows()
    catalogue_domains = [row["domain"] for row in rows]

    conn = op.get_bind()
    if catalogue_domains:
        conn.execute(
            sa.text(
                """
                UPDATE universities u
                SET is_legacy = true
                WHERE NOT (u.domain = ANY(:domains))
                  AND EXISTS (
                    SELECT 1 FROM users usr WHERE usr.university_id = u.id
                  )
                """
            ),
            {"domains": catalogue_domains},
        )
        conn.execute(
            sa.text(
                """
                UPDATE universities
                SET deleted_at = NOW()
                WHERE NOT (domain = ANY(:domains))
                  AND is_legacy = false
                  AND NOT EXISTS (
                    SELECT 1 FROM users usr WHERE usr.university_id = universities.id
                  )
                """
            ),
            {"domains": catalogue_domains},
        )

    op.drop_column("universities", "country")

    universities = sa.table(
        "universities",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("domain", sa.String),
        sa.column("city", sa.String),
        sa.column("short_name", sa.String),
        sa.column("aliases", JSONB),
        sa.column("state", sa.String),
        sa.column("type", sa.String),
        sa.column("website", sa.String),
        sa.column("is_legacy", sa.Boolean),
        sa.column("deleted_at", sa.DateTime(timezone=True)),
    )

    for row in rows:
        stmt = (
            insert(universities)
            .values(
                id=uuid4(),
                name=row["name"],
                domain=row["domain"],
                city=row["city"],
                short_name=row["short_name"],
                aliases=row["aliases"],
                state=row["state"],
                type=row["type"],
                website=row["website"],
                is_legacy=False,
                deleted_at=None,
            )
            .on_conflict_do_update(
                index_elements=["domain"],
                set_={
                    "name": row["name"],
                    "city": row["city"],
                    "short_name": row["short_name"],
                    "aliases": row["aliases"],
                    "state": row["state"],
                    "type": row["type"],
                    "website": row["website"],
                    "is_legacy": False,
                    "deleted_at": None,
                },
            )
        )
        conn.execute(stmt)

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_universities_name_trgm
        ON universities USING gin (lower(name) gin_trgm_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_universities_short_name_trgm
        ON universities USING gin (lower(COALESCE(short_name, '')) gin_trgm_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_universities_aliases
        ON universities USING gin (aliases)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_universities_aliases")
    op.execute("DROP INDEX IF EXISTS idx_universities_short_name_trgm")
    op.execute("DROP INDEX IF EXISTS idx_universities_name_trgm")

    op.add_column(
        "universities",
        sa.Column("country", sa.String(2), nullable=False, server_default="DE"),
    )
    op.drop_column("universities", "deleted_at")
    op.drop_column("universities", "is_legacy")
    op.drop_column("universities", "website")
    op.drop_column("universities", "type")
    op.drop_column("universities", "state")
    op.drop_column("universities", "aliases")
    op.drop_column("universities", "short_name")
