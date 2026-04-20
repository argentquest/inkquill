"""add wikimedia_gallery provider to care_circle_provider_catalog

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d1
Create Date: 2026-04-12 00:05:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "f7a8b9c0d1e2"
down_revision = "e6f7a8b9c0d1"
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
            ('wikimedia_gallery', 'Photo of the Day', '📸', 'memory', true, 43, true, true, 'daily_newsletter')
        ON CONFLICT (provider_key) DO NOTHING
    """)


def downgrade() -> None:
    op.execute(
        "DELETE FROM care_circle_provider_catalog WHERE provider_key = 'wikimedia_gallery'"
    )
