"""add care circle domain tables

Revision ID: 7b8f4c2a1d10
Revises: 535e181d0d25
Create Date: 2026-04-03 22:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "7b8f4c2a1d10"
down_revision = "535e181d0d25"
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

providers = [
    {"provider_key": "weather", "label": "Weather", "icon": "☀️", "category": "core", "enabled": True, "display_order": 1, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "joke", "label": "Daily Joy", "icon": "😄", "category": "wellbeing", "enabled": True, "display_order": 2, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "nostalgia", "label": "Time Machine", "icon": "🕰️", "category": "memory", "enabled": True, "display_order": 3, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "puzzle", "label": "Puzzle", "icon": "🧩", "category": "games", "enabled": True, "display_order": 4, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "brain_booster", "label": "Brain Booster", "icon": "🧠", "category": "games", "enabled": True, "display_order": 5, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "sensory", "label": "Sensory", "icon": "🎵", "category": "wellbeing", "enabled": True, "display_order": 6, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "ai_trivia", "label": "AI Trivia", "icon": "💡", "category": "games", "enabled": True, "display_order": 7, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "daily_quote", "label": "Daily Quote", "icon": "✨", "category": "core", "enabled": True, "display_order": 8, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "dog_photo", "label": "Furry Friend", "icon": "🐶", "category": "memory", "enabled": True, "display_order": 9, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "cat_fact", "label": "Cat Fact", "icon": "🐱", "category": "memory", "enabled": True, "display_order": 10, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "gratitude", "label": "Gratitude", "icon": "🙏", "category": "wellbeing", "enabled": True, "display_order": 11, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "gentle_exercise", "label": "Gentle Exercise", "icon": "🤼", "category": "wellbeing", "enabled": True, "display_order": 12, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "daily_affirmation", "label": "Affirmation", "icon": "💛", "category": "core", "enabled": True, "display_order": 13, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "nature_scene", "label": "Nature Scene", "icon": "🌿", "category": "memory", "enabled": False, "display_order": 14, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "simple_recipe", "label": "Simple Recipe", "icon": "🍳", "category": "lifestyle", "enabled": True, "display_order": 15, "patient_visible": False, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "this_day_history", "label": "On This Day", "icon": "📅", "category": "memory", "enabled": True, "display_order": 16, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "riddle", "label": "Daily Riddle", "icon": "🤔", "category": "games", "enabled": True, "display_order": 17, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "missing_vowels", "label": "Missing Vowels", "icon": "🔤", "category": "games", "enabled": True, "display_order": 18, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "finish_phrase", "label": "Finish the Phrase", "icon": "💬", "category": "games", "enabled": True, "display_order": 19, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "odd_one_out", "label": "Odd One Out", "icon": "🎯", "category": "games", "enabled": True, "display_order": 20, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "word_scramble", "label": "Word Scramble", "icon": "🔀", "category": "games", "enabled": True, "display_order": 21, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "song_of_the_day", "label": "Song of the Day", "icon": "🎵", "category": "memory", "enabled": True, "display_order": 22, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "complete_the_duo", "label": "Complete the Duo", "icon": "🤝", "category": "games", "enabled": True, "display_order": 23, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "spot_the_difference", "label": "Spot the Difference", "icon": "🔍", "category": "games", "enabled": True, "display_order": 24, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "pen_pal_letter", "label": "Pen Pal Letter", "icon": "✉️", "category": "wellbeing", "enabled": True, "display_order": 25, "patient_visible": False, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "gridless_crossword", "label": "Gridless Crossword", "icon": "📝", "category": "games", "enabled": True, "display_order": 26, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "world_news", "label": "World News", "icon": "🌍", "category": "core", "enabled": True, "display_order": 27, "patient_visible": False, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "hobby_spotlight", "label": "Hobby Spotlight", "icon": "🎨", "category": "lifestyle", "enabled": True, "display_order": 28, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "family_greeting", "label": "Family Greeting", "icon": "👨‍👩‍👧", "category": "core", "enabled": True, "display_order": 29, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "local_history", "label": "Local History", "icon": "🏛️", "category": "memory", "enabled": True, "display_order": 30, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "personal_affirmation", "label": "Personal Affirmation", "icon": "💪", "category": "wellbeing", "enabled": True, "display_order": 31, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
    {"provider_key": "activity_suggestion", "label": "Activity Suggestion", "icon": "🌟", "category": "wellbeing", "enabled": True, "display_order": 32, "patient_visible": True, "family_visible": True, "source_app": "daily_newsletter"},
]


def upgrade() -> None:
    op.create_table(
        "care_circle_families",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_care_circle_families_id"), "care_circle_families", ["id"], unique=False)

    op.create_table(
        "care_circle_family_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("care_circle_families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("family_id", "user_id", name="uq_care_circle_family_user"),
    )
    op.create_index(op.f("ix_care_circle_family_memberships_id"), "care_circle_family_memberships", ["id"], unique=False)
    op.create_index(op.f("ix_care_circle_family_memberships_family_id"), "care_circle_family_memberships", ["family_id"], unique=False)
    op.create_index(op.f("ix_care_circle_family_memberships_user_id"), "care_circle_family_memberships", ["user_id"], unique=False)

    op.create_table(
        "care_circle_patient_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("family_id", sa.Integer(), sa.ForeignKey("care_circle_families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("stage", sa.String(length=50), nullable=False),
        sa.Column("access_state", sa.String(length=50), nullable=False),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.Column("delivery_time", sa.String(length=20), nullable=True),
        sa.Column("delivery_days", sa.JSON(), nullable=False),
        sa.Column("auth_image_keys", sa.JSON(), nullable=False),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_care_circle_patient_profiles_id"), "care_circle_patient_profiles", ["id"], unique=False)
    op.create_index(op.f("ix_care_circle_patient_profiles_family_id"), "care_circle_patient_profiles", ["family_id"], unique=False)

    op.create_table(
        "care_circle_provider_catalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_key", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("icon", sa.String(length=20), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("patient_visible", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("family_visible", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_app", sa.String(length=100), nullable=False, server_default="daily_newsletter"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("provider_key"),
    )
    op.create_index(op.f("ix_care_circle_provider_catalog_id"), "care_circle_provider_catalog", ["id"], unique=False)
    op.create_index(op.f("ix_care_circle_provider_catalog_provider_key"), "care_circle_provider_catalog", ["provider_key"], unique=False)

    op.create_table(
        "care_circle_patient_content_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("care_circle_patient_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider_key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("card_kind", sa.String(length=50), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_care_circle_patient_content_cards_id"), "care_circle_patient_content_cards", ["id"], unique=False)
    op.create_index(op.f("ix_care_circle_patient_content_cards_patient_id"), "care_circle_patient_content_cards", ["patient_id"], unique=False)
    op.create_index(op.f("ix_care_circle_patient_content_cards_provider_key"), "care_circle_patient_content_cards", ["provider_key"], unique=False)

    op.bulk_insert(provider_catalog, providers)


def downgrade() -> None:
    op.drop_index(op.f("ix_care_circle_patient_content_cards_provider_key"), table_name="care_circle_patient_content_cards")
    op.drop_index(op.f("ix_care_circle_patient_content_cards_patient_id"), table_name="care_circle_patient_content_cards")
    op.drop_index(op.f("ix_care_circle_patient_content_cards_id"), table_name="care_circle_patient_content_cards")
    op.drop_table("care_circle_patient_content_cards")

    op.drop_index(op.f("ix_care_circle_provider_catalog_provider_key"), table_name="care_circle_provider_catalog")
    op.drop_index(op.f("ix_care_circle_provider_catalog_id"), table_name="care_circle_provider_catalog")
    op.drop_table("care_circle_provider_catalog")

    op.drop_index(op.f("ix_care_circle_patient_profiles_family_id"), table_name="care_circle_patient_profiles")
    op.drop_index(op.f("ix_care_circle_patient_profiles_id"), table_name="care_circle_patient_profiles")
    op.drop_table("care_circle_patient_profiles")

    op.drop_index(op.f("ix_care_circle_family_memberships_user_id"), table_name="care_circle_family_memberships")
    op.drop_index(op.f("ix_care_circle_family_memberships_family_id"), table_name="care_circle_family_memberships")
    op.drop_index(op.f("ix_care_circle_family_memberships_id"), table_name="care_circle_family_memberships")
    op.drop_table("care_circle_family_memberships")

    op.drop_index(op.f("ix_care_circle_families_id"), table_name="care_circle_families")
    op.drop_table("care_circle_families")
