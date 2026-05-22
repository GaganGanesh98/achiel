"""allowed_domain_source_manual

Revision ID: i9j0k1l2m3n4
Revises: g7h8i9j0k1l2
Create Date: 2026-05-22

"""

from typing import Sequence, Union

from alembic import op

revision: str = "i9j0k1l2m3n4"
down_revision: Union[str, None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE allowed_domain_source ADD VALUE IF NOT EXISTS 'manual'"
    )


def downgrade() -> None:
    pass
