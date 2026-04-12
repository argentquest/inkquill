"""add display_order to care_circle_provider_patient_configs

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-12 00:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "care_circle_provider_patient_configs",
        sa.Column("display_order", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("care_circle_provider_patient_configs", "display_order")
