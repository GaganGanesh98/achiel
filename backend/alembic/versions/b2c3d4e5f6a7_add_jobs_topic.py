"""add jobs topic

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-22

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ALTER TYPE cannot run inside a transaction — execute outside one
    op.execute("ALTER TYPE topic ADD VALUE IF NOT EXISTS 'jobs'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values directly.
    # To reverse: recreate the type without 'jobs' and migrate the column.
    # Skipped for dev — just don't downgrade past this migration.
    pass
