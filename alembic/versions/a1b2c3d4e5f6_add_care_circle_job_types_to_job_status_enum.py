"""add_care_circle_job_types_to_job_status_enum

Revision ID: a9b8c7d6e5f4
Revises: f1b2c3d4e5f7
Create Date: 2026-04-20 11:05:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "a9b8c7d6e5f4"
down_revision = "f1b2c3d4e5f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE job_type_enum ADD VALUE IF NOT EXISTS 'CARE_CIRCLE_DAILY_SESSION'"
    )
    op.execute(
        "ALTER TYPE job_type_enum ADD VALUE IF NOT EXISTS 'CARE_CIRCLE_DAILY_NEWSLETTER'"
    )


def downgrade() -> None:
    # PostgreSQL enum values cannot be removed safely in place.
    pass
