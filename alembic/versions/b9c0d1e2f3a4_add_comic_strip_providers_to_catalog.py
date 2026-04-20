"""add comic strip providers to care_circle_provider_catalog

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
Branch Labels: None
Depends On: None
"""

from alembic import op

revision = "b9c0d1e2f3a4"
down_revision = "a8b9c0d1e2f3"
branch_labels = None
depends_on = None

_PROVIDERS = [
    ("comic_abe_martin",    "Abe Martin",             "📰", "entertainment", 50),
    ("comic_brownies",      "The Brownies",            "🧙", "entertainment", 51),
    ("comic_mr_skygack",    "Mr. Skygack from Mars",   "🚀", "entertainment", 52),
    ("comic_dino_cartoons", "Dinosaur Cartoons",       "🦕", "entertainment", 53),
]


def upgrade() -> None:
    for provider_key, label, icon, category, display_order in _PROVIDERS:
        op.execute(f"""
            INSERT INTO care_circle_provider_catalog
                (provider_key, label, icon, category, enabled, display_order,
                 patient_visible, family_visible, source_app)
            VALUES
                ('{provider_key}', '{label}', '{icon}', '{category}',
                 false, {display_order}, true, true, 'care_circle')
            ON CONFLICT (provider_key) DO NOTHING
        """)


def downgrade() -> None:
    for provider_key, *_ in _PROVIDERS:
        op.execute(
            f"DELETE FROM care_circle_provider_catalog WHERE provider_key = '{provider_key}'"
        )
