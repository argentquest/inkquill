"""add tag_taxonomy_entries table

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2026-05-10 12:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "m3n4o5p6q7r8"
down_revision: Union[str, None] = "l2m3n4o5p6q7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tag_taxonomy_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("field_key", sa.String(64), nullable=False),
        sa.Column("category", sa.String(128), nullable=False),
        sa.Column("label", sa.String(256), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(32), nullable=False, server_default="curated"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("field_key", "label", name="uq_tag_taxonomy_field_label"),
    )
    op.create_index("ix_tag_taxonomy_field_active", "tag_taxonomy_entries", ["field_key", "is_active"])


def downgrade() -> None:
    op.drop_index("ix_tag_taxonomy_field_active", table_name="tag_taxonomy_entries")
    op.drop_table("tag_taxonomy_entries")
