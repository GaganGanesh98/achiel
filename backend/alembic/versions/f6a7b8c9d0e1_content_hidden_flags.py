"""content_hidden_flags

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("is_hidden", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column("posts", sa.Column("hidden_reason", sa.String(length=255), nullable=True))
    op.add_column(
        "comments",
        sa.Column("is_hidden", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column("comments", sa.Column("hidden_reason", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("comments", "hidden_reason")
    op.drop_column("comments", "is_hidden")
    op.drop_column("posts", "hidden_reason")
    op.drop_column("posts", "is_hidden")
