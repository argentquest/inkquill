"""remove crossword provider from care_circle_provider_catalog

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Branch Labels: None
Depends On: None
"""

from alembic import op

revision = "a8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM care_circle_provider_catalog WHERE provider_key = 'crossword'")


def downgrade() -> None:
    pass
