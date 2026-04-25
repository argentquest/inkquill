"""add membership status and family is_disabled

Revision ID: g3h4i5j6k7l8
Revises: f2a1b3c4d5e6
Create Date: 2026-04-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "g3h4i5j6k7l8"
down_revision: Union[str, None] = "f2a1b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "care_circle_family_memberships",
        sa.Column("status", sa.String(length=20), nullable=True),
    )
    op.execute("UPDATE care_circle_family_memberships SET status = 'active' WHERE status IS NULL")
    op.alter_column("care_circle_family_memberships", "status", nullable=False)

    op.add_column(
        "care_circle_families",
        sa.Column("is_disabled", sa.Boolean(), nullable=True),
    )
    op.execute("UPDATE care_circle_families SET is_disabled = FALSE WHERE is_disabled IS NULL")
    op.alter_column("care_circle_families", "is_disabled", nullable=False)


def downgrade() -> None:
    op.drop_column("care_circle_families", "is_disabled")
    op.drop_column("care_circle_family_memberships", "status")
