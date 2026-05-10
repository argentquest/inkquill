"""add care_mode to care_circle_patient_profiles

Revision ID: n4o5p6q7r8s9
Revises: m3n4o5p6q7r8
Create Date: 2026-05-10 14:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "n4o5p6q7r8s9"
down_revision: Union[str, None] = "m3n4o5p6q7r8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "care_circle_patient_profiles",
        sa.Column("care_mode", sa.String(50), nullable=False, server_default="memory_care"),
    )


def downgrade() -> None:
    op.drop_column("care_circle_patient_profiles", "care_mode")
