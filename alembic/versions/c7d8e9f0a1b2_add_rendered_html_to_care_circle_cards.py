"""add rendered html to care circle cards

Revision ID: c7d8e9f0a1b2
Revises: f2a1b3c4d5e6
Create Date: 2026-04-05 17:58:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7d8e9f0a1b2"
down_revision = "f2a1b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "care_circle_patient_content_cards",
        sa.Column("rendered_html", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("care_circle_patient_content_cards", "rendered_html")
