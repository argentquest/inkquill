"""add family_name to care_circle_patient_profiles

Revision ID: a1b2c3d4e5f6
Revises: e1f2a3b4c5d6
Create Date: 2026-04-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "care_circle_patient_profiles",
        sa.Column("family_name", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("care_circle_patient_profiles", "family_name")
