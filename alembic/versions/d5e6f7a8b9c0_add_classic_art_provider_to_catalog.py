"""add classic_art provider to care_circle_provider_catalog

Revision ID: d5e6f7a8b9c0
Revises: c3d4e5f6a7b8
Create Date: 2026-04-12 00:03:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "d5e6f7a8b9c0"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


provider_catalog = sa.table(
    "care_circle_provider_catalog",
    sa.column("provider_key", sa.String()),
    sa.column("label", sa.String()),
    sa.column("icon", sa.String()),
    sa.column("category", sa.String()),
    sa.column("enabled", sa.Boolean()),
    sa.column("display_order", sa.Integer()),
    sa.column("patient_visible", sa.Boolean()),
    sa.column("family_visible", sa.Boolean()),
    sa.column("source_app", sa.String()),
)


def upgrade() -> None:
    op.execute("""
        INSERT INTO care_circle_provider_catalog
            (provider_key, label, icon, category, enabled, display_order, patient_visible, family_visible, source_app)
        VALUES
            ('classic_art', 'Art of the Day', '🖼️', 'memory', true, 41, true, true, 'daily_newsletter')
        ON CONFLICT (provider_key) DO NOTHING
    """)


def downgrade() -> None:
    op.execute(
        "DELETE FROM care_circle_provider_catalog WHERE provider_key = 'classic_art'"
    )
