"""user_university_fields

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("university", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("program", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("year_of_study", sa.String(length=20), nullable=True))
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "users", sa.Column("verification_token", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column("verification_token_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_verification_token", "users", ["verification_token"], unique=True)

    op.execute(
        """
        UPDATE users SET is_verified = true
        WHERE verification_status::text IN ('verified', 'VERIFIED')
        """
    )
    op.execute("UPDATE users SET country = 'DE' WHERE country IS NULL")
    op.alter_column("users", "country", nullable=False)

    op.execute(
        """
        UPDATE users u SET university = uni.name
        FROM universities uni
        WHERE u.university_id = uni.id AND u.university IS NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_users_verification_token", table_name="users")
    op.drop_column("users", "verification_token_expires_at")
    op.drop_column("users", "verification_token")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "year_of_study")
    op.drop_column("users", "program")
    op.drop_column("users", "university")
    op.alter_column("users", "country", nullable=True)
