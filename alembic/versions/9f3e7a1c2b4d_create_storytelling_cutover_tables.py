"""create_storytelling_cutover_tables

Revision ID: 9f3e7a1c2b4d
Revises: f2a1b3c4d5e6
Create Date: 2026-04-05 13:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3e7a1c2b4d"
down_revision: Union[str, None] = "f2a1b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STORYTELLING_TABLES = [
    "storytelling_user_interview_responses",
    "storytelling_brainstorm_sessions",
    "storytelling_worlds",
    "storytelling_brainstorm_favorites",
    "storytelling_locations",
    "storytelling_stories",
    "storytelling_story_classes",
    "storytelling_world_collaborators",
    "storytelling_world_roles",
    "storytelling_acts",
    "storytelling_brainstorm_stories",
    "storytelling_characters",
    "storytelling_location_connections",
    "storytelling_lore_items",
    "storytelling_published_stories",
    "storytelling_story_chat_sessions",
    "storytelling_story_location_associations",
    "storytelling_act_character_associations",
    "storytelling_act_location_associations",
    "storytelling_act_lore_item_associations",
    "storytelling_scenes",
    "storytelling_story_character_associations",
    "storytelling_story_chat_messages",
    "storytelling_story_comments",
    "storytelling_story_lore_item_associations",
    "storytelling_story_ratings",
    "storytelling_scene_character_associations",
    "storytelling_scene_location_associations",
    "storytelling_scene_lore_item_associations",
]

TABLES_WITH_SERIAL_ID = {
    "storytelling_user_interview_responses",
    "storytelling_brainstorm_sessions",
    "storytelling_worlds",
    "storytelling_brainstorm_favorites",
    "storytelling_locations",
    "storytelling_stories",
    "storytelling_story_classes",
    "storytelling_world_collaborators",
    "storytelling_world_roles",
    "storytelling_acts",
    "storytelling_brainstorm_stories",
    "storytelling_characters",
    "storytelling_lore_items",
    "storytelling_published_stories",
    "storytelling_story_chat_sessions",
    "storytelling_story_location_associations",
    "storytelling_act_character_associations",
    "storytelling_act_location_associations",
    "storytelling_act_lore_item_associations",
    "storytelling_scenes",
    "storytelling_story_character_associations",
    "storytelling_story_chat_messages",
    "storytelling_story_comments",
    "storytelling_story_lore_item_associations",
    "storytelling_story_ratings",
    "storytelling_scene_character_associations",
    "storytelling_scene_location_associations",
    "storytelling_scene_lore_item_associations",
}

NEW_TABLE_FOREIGN_KEYS = {
    "storytelling_user_interview_responses": [
        ("user_id", "users", "id", None),
    ],
    "storytelling_brainstorm_sessions": [
        ("user_id", "users", "id", None),
        ("interview_response_id", "storytelling_user_interview_responses", "id", None),
    ],
    "storytelling_worlds": [
        ("user_id", "users", "id", "CASCADE"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
    ],
    "storytelling_brainstorm_favorites": [
        ("user_id", "users", "id", None),
        ("session_id", "storytelling_brainstorm_sessions", "id", None),
    ],
    "storytelling_locations": [
        ("parent_location_id", "storytelling_locations", "id", "SET NULL"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
        ("world_id", "storytelling_worlds", "id", "CASCADE"),
    ],
    "storytelling_stories": [
        ("user_id", "users", "id", None),
        ("world_id", "storytelling_worlds", "id", "RESTRICT"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
    ],
    "storytelling_story_classes": [
        ("world_id", "storytelling_worlds", "id", "CASCADE"),
    ],
    "storytelling_world_collaborators": [
        ("world_id", "storytelling_worlds", "id", "CASCADE"),
        ("user_id", "users", "id", "CASCADE"),
        ("invited_by_user_id", "users", "id", "SET NULL"),
    ],
    "storytelling_world_roles": [
        ("world_id", "storytelling_worlds", "id", "CASCADE"),
        ("created_by_user_id", "users", "id", "SET NULL"),
    ],
    "storytelling_acts": [
        ("system_prompt_id", "prompts", "id", "SET NULL"),
        ("story_class_id", "storytelling_story_classes", "id", "SET NULL"),
        ("story_id", "storytelling_stories", "id", "CASCADE"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
    ],
    "storytelling_brainstorm_stories": [
        ("user_id", "users", "id", None),
        ("favorite_id", "storytelling_brainstorm_favorites", "id", None),
        ("story_id", "storytelling_stories", "id", None),
    ],
    "storytelling_characters": [
        ("world_id", "storytelling_worlds", "id", "CASCADE"),
        ("current_location_id", "storytelling_locations", "id", "SET NULL"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
    ],
    "storytelling_location_connections": [
        ("from_location_id", "storytelling_locations", "id", "CASCADE"),
        ("to_location_id", "storytelling_locations", "id", "CASCADE"),
    ],
    "storytelling_lore_items": [
        ("world_id", "storytelling_worlds", "id", "CASCADE"),
        ("current_location_id", "storytelling_locations", "id", "SET NULL"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
    ],
    "storytelling_published_stories": [
        ("story_id", "storytelling_stories", "id", "CASCADE"),
        ("user_id", "users", "id", "CASCADE"),
    ],
    "storytelling_story_chat_sessions": [
        ("story_id", "storytelling_stories", "id", "CASCADE"),
        ("user_id", "users", "id", "CASCADE"),
    ],
    "storytelling_story_location_associations": [
        ("story_id", "storytelling_stories", "id", "CASCADE"),
        ("location_id", "storytelling_locations", "id", "CASCADE"),
    ],
    "storytelling_act_character_associations": [
        ("act_id", "storytelling_acts", "id", "CASCADE"),
        ("character_id", "storytelling_characters", "id", "CASCADE"),
    ],
    "storytelling_act_location_associations": [
        ("act_id", "storytelling_acts", "id", "CASCADE"),
        ("location_id", "storytelling_locations", "id", "CASCADE"),
    ],
    "storytelling_act_lore_item_associations": [
        ("act_id", "storytelling_acts", "id", "CASCADE"),
        ("lore_item_id", "storytelling_lore_items", "id", "CASCADE"),
    ],
    "storytelling_scenes": [
        ("act_id", "storytelling_acts", "id", "CASCADE"),
        ("story_class_id", "storytelling_story_classes", "id", "SET NULL"),
        ("current_image_id", "generated_images", "id", "SET NULL"),
    ],
    "storytelling_story_character_associations": [
        ("story_id", "storytelling_stories", "id", "CASCADE"),
        ("character_id", "storytelling_characters", "id", "CASCADE"),
    ],
    "storytelling_story_chat_messages": [
        ("session_id", "storytelling_story_chat_sessions", "id", "CASCADE"),
        ("cost_log_id", "ai_call_logs", "id", "SET NULL"),
    ],
    "storytelling_story_comments": [
        ("published_story_id", "storytelling_published_stories", "id", "CASCADE"),
        ("user_id", "users", "id", "CASCADE"),
        ("parent_comment_id", "storytelling_story_comments", "id", "CASCADE"),
    ],
    "storytelling_story_lore_item_associations": [
        ("story_id", "storytelling_stories", "id", "CASCADE"),
        ("lore_item_id", "storytelling_lore_items", "id", "CASCADE"),
    ],
    "storytelling_story_ratings": [
        ("published_story_id", "storytelling_published_stories", "id", "CASCADE"),
        ("user_id", "users", "id", "CASCADE"),
    ],
    "storytelling_scene_character_associations": [
        ("scene_id", "storytelling_scenes", "id", "CASCADE"),
        ("character_id", "storytelling_characters", "id", "CASCADE"),
    ],
    "storytelling_scene_location_associations": [
        ("scene_id", "storytelling_scenes", "id", "CASCADE"),
        ("location_id", "storytelling_locations", "id", "CASCADE"),
    ],
    "storytelling_scene_lore_item_associations": [
        ("scene_id", "storytelling_scenes", "id", "CASCADE"),
        ("lore_item_id", "storytelling_lore_items", "id", "CASCADE"),
    ],
}

SHARED_FOREIGN_KEYS = [
    ("chat_sessions", "chat_sessions_world_id_fkey", "world_id", "storytelling_worlds", "id", "CASCADE"),
    ("job_statuses", "job_statuses_world_id_fkey", "world_id", "storytelling_worlds", "id", "SET NULL"),
    ("uploaded_documents", "uploaded_documents_world_id_fkey", "world_id", "storytelling_worlds", "id", "SET NULL"),
    (
        "uploaded_documents",
        "uploaded_documents_source_character_id_fkey",
        "source_character_id",
        "storytelling_characters",
        "id",
        "SET NULL",
    ),
    (
        "uploaded_documents",
        "uploaded_documents_source_location_id_fkey",
        "source_location_id",
        "storytelling_locations",
        "id",
        "SET NULL",
    ),
    (
        "uploaded_documents",
        "uploaded_documents_source_lore_item_id_fkey",
        "source_lore_item_id",
        "storytelling_lore_items",
        "id",
        "SET NULL",
    ),
    ("forum_threads", "forum_threads_world_id_fkey", "world_id", "storytelling_worlds", "id", "SET NULL"),
    ("forum_threads", "forum_threads_story_id_fkey", "story_id", "storytelling_stories", "id", "SET NULL"),
    (
        "forum_posts",
        "forum_posts_character_id_fkey",
        "character_id",
        "storytelling_characters",
        "id",
        "SET NULL",
    ),
    (
        "forum_posts",
        "forum_posts_location_id_fkey",
        "location_id",
        "storytelling_locations",
        "id",
        "SET NULL",
    ),
    (
        "story_character_association",
        "story_character_association_story_id_fkey",
        "story_id",
        "storytelling_stories",
        "id",
        "CASCADE",
    ),
    (
        "story_character_association",
        "story_character_association_character_id_fkey",
        "character_id",
        "storytelling_characters",
        "id",
        "CASCADE",
    ),
    (
        "story_location_association",
        "story_location_association_story_id_fkey",
        "story_id",
        "storytelling_stories",
        "id",
        "CASCADE",
    ),
    (
        "story_location_association",
        "story_location_association_location_id_fkey",
        "location_id",
        "storytelling_locations",
        "id",
        "CASCADE",
    ),
    (
        "story_lore_item_association",
        "story_lore_item_association_story_id_fkey",
        "story_id",
        "storytelling_stories",
        "id",
        "CASCADE",
    ),
    (
        "story_lore_item_association",
        "story_lore_item_association_lore_item_id_fkey",
        "lore_item_id",
        "storytelling_lore_items",
        "id",
        "CASCADE",
    ),
]

LEGACY_FOREIGN_KEYS = [
    ("chat_sessions", "chat_sessions_world_id_fkey", "world_id", "worlds", "id", "CASCADE"),
    ("job_statuses", "job_statuses_world_id_fkey", "world_id", "worlds", "id", "SET NULL"),
    ("uploaded_documents", "uploaded_documents_world_id_fkey", "world_id", "worlds", "id", "SET NULL"),
    ("uploaded_documents", "uploaded_documents_source_character_id_fkey", "source_character_id", "characters", "id", "SET NULL"),
    ("uploaded_documents", "uploaded_documents_source_location_id_fkey", "source_location_id", "locations", "id", "SET NULL"),
    ("uploaded_documents", "uploaded_documents_source_lore_item_id_fkey", "source_lore_item_id", "lore_items", "id", "SET NULL"),
    ("forum_threads", "forum_threads_world_id_fkey", "world_id", "worlds", "id", "SET NULL"),
    ("forum_threads", "forum_threads_story_id_fkey", "story_id", "stories", "id", "SET NULL"),
    ("forum_posts", "forum_posts_character_id_fkey", "character_id", "characters", "id", "SET NULL"),
    ("forum_posts", "forum_posts_location_id_fkey", "location_id", "locations", "id", "SET NULL"),
    ("story_character_association", "story_character_association_story_id_fkey", "story_id", "stories", "id", "CASCADE"),
    (
        "story_character_association",
        "story_character_association_character_id_fkey",
        "character_id",
        "characters",
        "id",
        "CASCADE",
    ),
    ("story_location_association", "story_location_association_story_id_fkey", "story_id", "stories", "id", "CASCADE"),
    (
        "story_location_association",
        "story_location_association_location_id_fkey",
        "location_id",
        "locations",
        "id",
        "CASCADE",
    ),
    ("story_lore_item_association", "story_lore_item_association_story_id_fkey", "story_id", "stories", "id", "CASCADE"),
    (
        "story_lore_item_association",
        "story_lore_item_association_lore_item_id_fkey",
        "lore_item_id",
        "lore_items",
        "id",
        "CASCADE",
    ),
]


def _table_exists(bind, table_name: str) -> bool:
    return sa.inspect(bind).has_table(table_name)


def _source_table_name(new_table_name: str) -> str:
    return new_table_name.replace("storytelling_", "", 1)


def _quoted_columns(bind, table_name: str) -> str:
    inspector = sa.inspect(bind)
    return ", ".join(f'"{column["name"]}"' for column in inspector.get_columns(table_name))


def _drop_named_constraint(bind, table_name: str, constraint_name: str) -> None:
    if not _table_exists(bind, table_name):
        return
    bind.execute(
        sa.text(
            f'ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS "{constraint_name}"'
        )
    )


def _drop_all_foreign_keys(bind, table_name: str) -> None:
    if not _table_exists(bind, table_name):
        return
    rows = bind.execute(
        sa.text(
            """
            SELECT con.conname
            FROM pg_constraint AS con
            JOIN pg_class AS rel ON rel.oid = con.conrelid
            JOIN pg_namespace AS nsp ON nsp.oid = rel.relnamespace
            WHERE con.contype = 'f'
              AND nsp.nspname = 'public'
              AND rel.relname = :table_name
            """
        ),
        {"table_name": table_name},
    )
    for row in rows:
        bind.execute(
            sa.text(
                f'ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS "{row.conname}"'
            )
        )


def _add_foreign_key(
    bind,
    table_name: str,
    constraint_name: str,
    local_column: str,
    target_table: str,
    target_column: str,
    ondelete: str | None,
) -> None:
    if not _table_exists(bind, table_name) or not _table_exists(bind, target_table):
        return
    clause = (
        f'ALTER TABLE "{table_name}" ADD CONSTRAINT "{constraint_name}" '
        f'FOREIGN KEY ("{local_column}") REFERENCES "{target_table}" ("{target_column}")'
    )
    if ondelete:
        clause += f" ON DELETE {ondelete}"
    bind.execute(sa.text(f"SAVEPOINT fk_{constraint_name[:30]}"))
    try:
        bind.execute(sa.text(clause))
        bind.execute(sa.text(f"RELEASE SAVEPOINT fk_{constraint_name[:30]}"))
    except Exception as e:
        bind.execute(sa.text(f"ROLLBACK TO SAVEPOINT fk_{constraint_name[:30]}"))
        print(f"[skip] Could not add FK {constraint_name}: {e}")


def _ensure_storytelling_table(bind, table_name: str) -> None:
    if _table_exists(bind, table_name):
        return
    source_table = _source_table_name(table_name)
    if not _table_exists(bind, source_table):
        print(f"[skip] Source table missing, skipping storytelling cutover: {source_table}")
        return
    bind.execute(
        sa.text(
            f'CREATE TABLE "{table_name}" (LIKE "{source_table}" INCLUDING ALL)'
        )
    )


def _ensure_storytelling_sequence(bind, table_name: str) -> None:
    if table_name not in TABLES_WITH_SERIAL_ID or not _table_exists(bind, table_name):
        return
    sequence_name = f"{table_name}_id_seq"
    bind.execute(sa.text(f'CREATE SEQUENCE IF NOT EXISTS "{sequence_name}"'))
    bind.execute(
        sa.text(
            f'ALTER SEQUENCE "{sequence_name}" OWNED BY "{table_name}"."id"'
        )
    )
    bind.execute(
        sa.text(
            f"""ALTER TABLE "{table_name}"
            ALTER COLUMN "id" SET DEFAULT nextval('"{sequence_name}"')"""
        )
    )


def _copy_storytelling_data(bind, table_name: str) -> None:
    source_table = _source_table_name(table_name)
    if not _table_exists(bind, table_name) or not _table_exists(bind, source_table):
        return
    row_count = bind.execute(
        sa.text(f'SELECT COUNT(*) FROM "{table_name}"')
    ).scalar_one()
    if row_count:
        return
    columns = _quoted_columns(bind, table_name)
    bind.execute(
        sa.text(
            f'INSERT INTO "{table_name}" ({columns}) SELECT {columns} FROM "{source_table}"'
        )
    )


def _sync_sequence(bind, table_name: str) -> None:
    if table_name not in TABLES_WITH_SERIAL_ID or not _table_exists(bind, table_name):
        return
    bind.execute(
        sa.text(
            """
            SELECT setval(
                pg_get_serial_sequence(:table_name, 'id'),
                COALESCE((SELECT MAX(id) FROM ONLY public.""" + table_name + """), 1),
                COALESCE((SELECT MAX(id) FROM ONLY public.""" + table_name + """), 0) > 0
            )
            """
        ),
        {"table_name": f"public.{table_name}"},
    )


def _add_new_storytelling_foreign_keys(bind) -> None:
    for table_name in STORYTELLING_TABLES:
        _drop_all_foreign_keys(bind, table_name)
        for local_column, target_table, target_column, ondelete in NEW_TABLE_FOREIGN_KEYS.get(table_name, []):
            constraint_name = f"{table_name}_{local_column}_fkey"
            _add_foreign_key(
                bind,
                table_name,
                constraint_name,
                local_column,
                target_table,
                target_column,
                ondelete,
            )


def _repoint_shared_foreign_keys(bind, foreign_keys) -> None:
    for table_name, constraint_name, local_column, target_table, target_column, ondelete in foreign_keys:
        _drop_named_constraint(bind, table_name, constraint_name)
        _add_foreign_key(
            bind,
            table_name,
            constraint_name,
            local_column,
            target_table,
            target_column,
            ondelete,
        )


def upgrade() -> None:
    bind = op.get_bind()

    for table_name in STORYTELLING_TABLES:
        _ensure_storytelling_table(bind, table_name)
        _ensure_storytelling_sequence(bind, table_name)

    _add_new_storytelling_foreign_keys(bind)

    for table_name in STORYTELLING_TABLES:
        _copy_storytelling_data(bind, table_name)
        _sync_sequence(bind, table_name)

    _repoint_shared_foreign_keys(bind, SHARED_FOREIGN_KEYS)


def downgrade() -> None:
    bind = op.get_bind()

    _repoint_shared_foreign_keys(bind, LEGACY_FOREIGN_KEYS)

    for table_name in reversed(STORYTELLING_TABLES):
        if _table_exists(bind, table_name):
            bind.execute(sa.text(f'DROP TABLE "{table_name}" CASCADE'))
