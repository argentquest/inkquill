"""remove Mimi and Eunice provider from care circle

Revision ID: e8f9a0b1c2d3
Revises: c676f7f89dc4, f7a8b9c0d1e2
Create Date: 2026-04-19 10:05:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e8f9a0b1c2d3"
down_revision: Union[str, Sequence[str], None] = ("c676f7f89dc4", "f7a8b9c0d1e2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PROVIDER_KEY = "comic_mimi_eunice"


def upgrade() -> None:
    op.execute(
        f"DELETE FROM care_circle_provider_session_outputs WHERE provider_key = '{PROVIDER_KEY}'"
    )
    op.execute(
        f"DELETE FROM care_circle_provider_run_logs WHERE provider_key = '{PROVIDER_KEY}'"
    )
    op.execute(
        f"DELETE FROM care_circle_patient_content_cards WHERE provider_key = '{PROVIDER_KEY}'"
    )
    op.execute(
        f"DELETE FROM care_circle_provider_patient_configs WHERE provider_key = '{PROVIDER_KEY}'"
    )
    op.execute(
        f"DELETE FROM care_circle_provider_catalog WHERE provider_key = '{PROVIDER_KEY}'"
    )


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO care_circle_provider_catalog
            (provider_key, label, icon, category, enabled, display_order,
             patient_visible, family_visible, source_app)
        VALUES
            ('comic_mimi_eunice', 'Mimi & Eunice', '🗞️', 'entertainment',
             true, 57, true, true, 'daily_newsletter')
        ON CONFLICT (provider_key) DO NOTHING
        """
    )
