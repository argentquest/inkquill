"""sync schema: drop old tables, create chatbot tables, fix index drift

Revision ID: k1l2m3n4o5p6
Revises: f86ce2dc5366, j6k7l8m9n0o1
Create Date: 2026-05-09 13:00:00.000000

What this migration does:
- Creates chatbot_sessions and chatbot_messages (missing from DB)
- Drops old pre-rename storytelling tables (data already in storytelling_* tables)
- Drops scheduled_jobs (APScheduler internal state; recreated on startup)
- Fixes forum_categories.slug index (was unique, should be non-unique)
- Fixes index naming on storytelling_* tables to match current model conventions
- Adds missing FKs on storytelling_acts, storytelling_stories, storytelling_worlds
- Fixes care_circle_patient_provider_feedback NOT NULL columns
- Fixes blog_posts app_source index name
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "k1l2m3n4o5p6"
down_revision: Union[str, tuple] = ("f86ce2dc5366", "j6k7l8m9n0o1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _index_exists(conn, index_name: str) -> bool:
    row = conn.execute(sa.text(
        "SELECT 1 FROM pg_indexes WHERE indexname = :n"
    ), {"n": index_name}).fetchone()
    return row is not None


def _constraint_exists(conn, table: str, name: str) -> bool:
    row = conn.execute(sa.text(
        "SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid "
        "WHERE t.relname = :t AND c.conname = :n"
    ), {"t": table, "n": name}).fetchone()
    return row is not None


def _column_exists(conn, table: str, column: str) -> bool:
    row = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.columns WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": column}).fetchone()
    return row is not None


def _table_exists(conn, table: str) -> bool:
    row = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name=:t AND table_schema='public'"
    ), {"t": table}).fetchone()
    return row is not None


def _fk_exists(conn, table: str, column: str) -> bool:
    row = conn.execute(sa.text(
        "SELECT 1 FROM information_schema.table_constraints tc "
        "JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name "
        "WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_name=:t AND kcu.column_name=:c"
    ), {"t": table, "c": column}).fetchone()
    return row is not None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Create chatbot_sessions
    # ------------------------------------------------------------------
    if not _table_exists(conn, "chatbot_sessions"):
        op.create_table(
            "chatbot_sessions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_chatbot_sessions_id", "chatbot_sessions", ["id"])
        op.create_index("ix_chatbot_sessions_user_id", "chatbot_sessions", ["user_id"])

    # ------------------------------------------------------------------
    # 2. Create chatbot_messages
    # ------------------------------------------------------------------
    if not _table_exists(conn, "chatbot_messages"):
        op.create_table(
            "chatbot_messages",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("session_id", sa.Integer(), sa.ForeignKey("chatbot_sessions.id", ondelete="CASCADE"), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("input_tokens", sa.Integer(), nullable=True),
            sa.Column("output_tokens", sa.Integer(), nullable=True),
            sa.Column("cost_usd", sa.Float(), nullable=True),
            sa.Column("model_name", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_chatbot_messages_id", "chatbot_messages", ["id"])
        op.create_index("ix_chatbot_messages_session_id", "chatbot_messages", ["session_id"])

    # ------------------------------------------------------------------
    # 3. Drop old storytelling tables (data already in storytelling_* tables)
    #    Drop order respects FK dependencies (most dependent first).
    # ------------------------------------------------------------------
    old_tables_ordered = [
        "story_chat_messages",
        "story_chat_sessions",
        "location_connections",
        "scenes",
        "acts",
        "characters",
        "lore_items",
        "stories",
        "story_classes",
        "locations",
        "worlds",
        "scheduled_jobs",
    ]
    for tbl in old_tables_ordered:
        if _table_exists(conn, tbl):
            op.drop_table(tbl)

    # ------------------------------------------------------------------
    # 4. forum_categories: slug index should be non-unique
    # ------------------------------------------------------------------
    if _index_exists(conn, "ix_forum_categories_slug"):
        op.drop_index("ix_forum_categories_slug", table_name="forum_categories")
    op.create_index("ix_forum_categories_slug", "forum_categories", ["slug"], unique=False)

    # ------------------------------------------------------------------
    # 5. Fix storytelling_* index naming (custom names → alembic conventions)
    # ------------------------------------------------------------------
    _storytelling_index_renames = [
        # (table, old_name, new_name, columns)
        ("storytelling_characters", "storytelling_characters_id_idx",    "ix_storytelling_characters_id",    ["id"]),
        ("storytelling_characters", "storytelling_characters_name_idx",  "ix_storytelling_characters_name",  ["name"]),
        ("storytelling_characters", "storytelling_characters_world_id_idx", "ix_storytelling_characters_world_id", ["world_id"]),
        ("storytelling_locations",  "storytelling_locations_id_idx",     "ix_storytelling_locations_id",     ["id"]),
        ("storytelling_locations",  "storytelling_locations_name_idx",   "ix_storytelling_locations_name",   ["name"]),
        ("storytelling_locations",  "storytelling_locations_parent_location_id_idx", "ix_storytelling_locations_parent_location_id", ["parent_location_id"]),
        ("storytelling_locations",  "storytelling_locations_world_id_idx","ix_storytelling_locations_world_id",["world_id"]),
        ("storytelling_lore_items", "storytelling_lore_items_id_idx",    "ix_storytelling_lore_items_id",    ["id"]),
        ("storytelling_lore_items", "storytelling_lore_items_category_idx","ix_storytelling_lore_items_category",["category"]),
        ("storytelling_lore_items", "storytelling_lore_items_title_idx", "ix_storytelling_lore_items_title", ["title"]),
        ("storytelling_lore_items", "storytelling_lore_items_world_id_idx","ix_storytelling_lore_items_world_id",["world_id"]),
        ("storytelling_story_classes","storytelling_story_classes_id_idx","ix_storytelling_story_classes_id", ["id"]),
        ("storytelling_story_classes","storytelling_story_classes_name_idx","ix_storytelling_story_classes_name",["name"]),
        ("storytelling_story_classes","storytelling_story_classes_world_id_idx","ix_storytelling_story_classes_world_id",["world_id"]),
        ("storytelling_acts",       "storytelling_acts_id_idx",          "ix_storytelling_acts_id",          ["id"]),
        ("storytelling_acts",       "storytelling_acts_story_class_id_idx","ix_storytelling_acts_story_class_id",["story_class_id"]),
        ("storytelling_acts",       "storytelling_acts_system_prompt_id_idx","ix_storytelling_acts_system_prompt_id",["system_prompt_id"]),
        ("storytelling_scenes",     "storytelling_scenes_id_idx",        "ix_storytelling_scenes_id",        ["id"]),
        ("storytelling_scenes",     "storytelling_scenes_story_class_id_idx","ix_storytelling_scenes_story_class_id",["story_class_id"]),
        ("storytelling_stories",    "storytelling_stories_id_idx",       "ix_storytelling_stories_id",       ["id"]),
        ("storytelling_stories",    "storytelling_stories_title_idx",    "ix_storytelling_stories_title",    ["title"]),
        ("storytelling_stories",    "storytelling_stories_user_id_idx",  "ix_storytelling_stories_user_id",  ["user_id"]),
        ("storytelling_stories",    "storytelling_stories_world_id_idx", "ix_storytelling_stories_world_id", ["world_id"]),
        ("storytelling_worlds",     "storytelling_worlds_id_idx",        "ix_storytelling_worlds_id",        ["id"]),
        ("storytelling_worlds",     "storytelling_worlds_name_idx",      "ix_storytelling_worlds_name",      ["name"]),
        ("storytelling_worlds",     "storytelling_worlds_user_id_idx",   "ix_storytelling_worlds_user_id",   ["user_id"]),
        ("storytelling_story_chat_messages","storytelling_story_chat_messages_id_idx","ix_storytelling_story_chat_messages_id",["id"]),
        ("storytelling_story_chat_messages","storytelling_story_chat_messages_session_id_idx","ix_storytelling_story_chat_messages_session_id",["session_id"]),
        ("storytelling_story_chat_sessions","storytelling_story_chat_sessions_id_idx","ix_storytelling_story_chat_sessions_id",["id"]),
        ("storytelling_story_chat_sessions","storytelling_story_chat_sessions_story_id_idx","ix_storytelling_story_chat_sessions_story_id",["story_id"]),
        ("storytelling_story_chat_sessions","storytelling_story_chat_sessions_user_id_idx","ix_storytelling_story_chat_sessions_user_id",["user_id"]),
        ("storytelling_location_connections","storytelling_location_connections_from_location_id_idx","ix_storytelling_location_connections_from_location_id",["from_location_id"]),
        ("storytelling_location_connections","storytelling_location_connections_to_location_id_idx","ix_storytelling_location_connections_to_location_id",["to_location_id"]),
    ]
    for table, old_idx, new_idx, cols in _storytelling_index_renames:
        if _index_exists(conn, old_idx) and not _index_exists(conn, new_idx):
            op.drop_index(old_idx, table_name=table)
            op.create_index(new_idx, table, cols)
        elif not _index_exists(conn, old_idx) and not _index_exists(conn, new_idx):
            op.create_index(new_idx, table, cols)

    # ------------------------------------------------------------------
    # 6. storytelling_acts: rename unique constraint
    # ------------------------------------------------------------------
    if _constraint_exists(conn, "storytelling_acts", "storytelling_acts_story_id_act_number_key"):
        op.drop_constraint("storytelling_acts_story_id_act_number_key", "storytelling_acts", type_="unique")
    if not _constraint_exists(conn, "storytelling_acts", "_story_act_number_uc"):
        op.create_unique_constraint("_story_act_number_uc", "storytelling_acts", ["story_id", "act_number"])

    # ------------------------------------------------------------------
    # 7. storytelling_scenes: rename unique constraint
    # ------------------------------------------------------------------
    if _constraint_exists(conn, "storytelling_scenes", "storytelling_scenes_act_id_scene_number_key"):
        op.drop_constraint("storytelling_scenes_act_id_scene_number_key", "storytelling_scenes", type_="unique")
    if not _constraint_exists(conn, "storytelling_scenes", "_act_scene_number_uc"):
        op.create_unique_constraint("_act_scene_number_uc", "storytelling_scenes", ["act_id", "scene_number"])

    # ------------------------------------------------------------------
    # 8. storytelling_stories: add story_type index + current_image_id FK
    # ------------------------------------------------------------------
    if _column_exists(conn, "storytelling_stories", "story_type") and not _index_exists(conn, "ix_storytelling_stories_story_type"):
        op.create_index("ix_storytelling_stories_story_type", "storytelling_stories", ["story_type"])
    if _column_exists(conn, "storytelling_stories", "current_image_id") and not _fk_exists(conn, "storytelling_stories", "current_image_id"):
        op.create_foreign_key(None, "storytelling_stories", "generated_images", ["current_image_id"], ["id"])

    # ------------------------------------------------------------------
    # 9. storytelling_worlds: add new indexes + current_image_id FK
    # ------------------------------------------------------------------
    for col, idx in [("is_free_chat_enabled", "ix_storytelling_worlds_is_free_chat_enabled"),
                     ("is_shadow", "ix_storytelling_worlds_is_shadow")]:
        if _column_exists(conn, "storytelling_worlds", col) and not _index_exists(conn, idx):
            op.create_index(idx, "storytelling_worlds", [col])
    if _column_exists(conn, "storytelling_worlds", "current_image_id") and not _fk_exists(conn, "storytelling_worlds", "current_image_id"):
        op.create_foreign_key(None, "storytelling_worlds", "generated_images", ["current_image_id"], ["id"])

    # ------------------------------------------------------------------
    # 10. storytelling_acts: current_image_id FK
    # ------------------------------------------------------------------
    if _column_exists(conn, "storytelling_acts", "current_image_id") and not _fk_exists(conn, "storytelling_acts", "current_image_id"):
        op.create_foreign_key(None, "storytelling_acts", "generated_images", ["current_image_id"], ["id"])

    # ------------------------------------------------------------------
    # 11. ai_call_logs: model_config_id FK + index
    # ------------------------------------------------------------------
    if _column_exists(conn, "ai_call_logs", "model_config_id"):
        if not _index_exists(conn, "ix_ai_call_logs_model_config_id"):
            op.create_index("ix_ai_call_logs_model_config_id", "ai_call_logs", ["model_config_id"])
        if not _fk_exists(conn, "ai_call_logs", "model_config_id"):
            op.create_foreign_key(None, "ai_call_logs", "ai_model_configurations", ["model_config_id"], ["id"])

    # ------------------------------------------------------------------
    # 12. blog_posts: rename app_source indexes
    # ------------------------------------------------------------------
    if _index_exists(conn, "idx_blog_posts_app_source") and not _index_exists(conn, "ix_blog_posts_app_source"):
        op.drop_index("idx_blog_posts_app_source", table_name="blog_posts")
        op.create_index("ix_blog_posts_app_source", "blog_posts", ["app_source"])
    if _index_exists(conn, "idx_blog_posts_app_source_status"):
        op.drop_index("idx_blog_posts_app_source_status", table_name="blog_posts")

    # ------------------------------------------------------------------
    # 13. care_circle_patient_provider_feedback: fix NOT NULL
    # ------------------------------------------------------------------
    for col in ("created_at", "updated_at"):
        if _column_exists(conn, "care_circle_patient_provider_feedback", col):
            op.alter_column("care_circle_patient_provider_feedback", col, nullable=False)


# ---------------------------------------------------------------------------
# Downgrade — only undo the safe reversible parts; table drops are irreversible
# ---------------------------------------------------------------------------

def downgrade() -> None:
    conn = op.get_bind()

    # Re-allow NULL on care_circle columns
    for col in ("created_at", "updated_at"):
        if _column_exists(conn, "care_circle_patient_provider_feedback", col):
            op.alter_column("care_circle_patient_provider_feedback", col, nullable=True)

    # Restore blog_posts index
    if _index_exists(conn, "ix_blog_posts_app_source") and not _index_exists(conn, "idx_blog_posts_app_source"):
        op.drop_index("ix_blog_posts_app_source", table_name="blog_posts")
        op.create_index("idx_blog_posts_app_source", "blog_posts", ["app_source"])

    # Drop chatbot tables
    if _table_exists(conn, "chatbot_messages"):
        op.drop_table("chatbot_messages")
    if _table_exists(conn, "chatbot_sessions"):
        op.drop_table("chatbot_sessions")

    # Note: old storytelling tables and scheduled_jobs cannot be restored by downgrade.
