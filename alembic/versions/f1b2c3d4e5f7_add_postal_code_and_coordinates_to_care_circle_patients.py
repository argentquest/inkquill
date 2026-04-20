"""add_postal_code_and_coordinates_to_care_circle_patients

Revision ID: f1b2c3d4e5f7
Revises: e8f9a0b1c2d3
Create Date: 2026-04-19 12:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1b2c3d4e5f7"
down_revision = "e8f9a0b1c2d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "care_circle_patient_profiles",
        sa.Column("postal_code", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "care_circle_patient_profiles",
        sa.Column("latitude", sa.Float(), nullable=True),
    )
    op.add_column(
        "care_circle_patient_profiles",
        sa.Column("longitude", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("care_circle_patient_profiles", "longitude")
    op.drop_column("care_circle_patient_profiles", "latitude")
    op.drop_column("care_circle_patient_profiles", "postal_code")
