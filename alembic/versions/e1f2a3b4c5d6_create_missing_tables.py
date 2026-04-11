"""create_missing_tables

Creates tables defined in SQLAlchemy models that are absent from the database.
This migration uses checkfirst=True so it is safe to run on any DB state.

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-04-10 19:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tables that exist in the DB already and must not be dropped or recreated.
EXISTING_TABLES = {
    "acts", "ai_call_logs", "alembic_version",
    "care_circle_families", "care_circle_family_memberships",
    "care_circle_patient_content_cards", "care_circle_patient_profiles",
    "care_circle_provider_catalog", "care_circle_provider_patient_configs",
    "care_circle_provider_run_logs", "care_circle_provider_session_outputs",
    "characters", "generated_images", "job_statuses",
    "location_connections", "locations", "lore_items", "prompts",
    "scenes", "stories", "story_character_association",
    "story_chat_messages", "story_chat_sessions", "story_classes",
    "story_location_association", "story_lore_item_association",
    "storytelling_acts", "storytelling_characters",
    "storytelling_location_connections", "storytelling_locations",
    "storytelling_lore_items", "storytelling_scenes", "storytelling_stories",
    "storytelling_story_chat_messages", "storytelling_story_chat_sessions",
    "storytelling_story_classes", "storytelling_worlds",
    "uploaded_documents", "users", "worlds",
}


def upgrade() -> None:
    bind = op.get_bind()

    # Import all models so Base.metadata is fully populated.
    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from app.db.database import Base
    import app.models  # noqa: F401 — registers all ORM models

    # create_all with checkfirst=True skips tables that already exist.
    # This is safe to run on any DB state — it will only create missing tables.
    inspector = sa.inspect(bind)
    tables_in_db = set(inspector.get_table_names(schema="public"))
    missing = sorted(name for name in Base.metadata.tables if name not in tables_in_db)

    if missing:
        Base.metadata.create_all(bind=bind, checkfirst=True)
        print(f"[migrate] Created {len(missing)} missing tables: {missing}")
    else:
        print("[migrate] No missing tables detected — nothing to do.")


def downgrade() -> None:
    # This migration is additive-only; downgrade is a no-op to avoid
    # accidentally dropping tables that may have live data.
    pass
