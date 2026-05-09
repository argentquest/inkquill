"""add unique constraint on users.provider_id

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-05-09 13:30:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "l2m3n4o5p6q7"
down_revision: Union[str, None] = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(sa.text(
        "SELECT 1 FROM pg_constraint c JOIN pg_class t ON t.oid = c.conrelid "
        "WHERE t.relname = 'users' AND c.contype = 'u' AND pg_get_constraintdef(c.oid) LIKE '%provider_id%'"
    )).fetchone()
    if not exists:
        op.create_unique_constraint("uq_users_provider_id", "users", ["provider_id"])


def downgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(sa.text(
        "SELECT 1 FROM pg_constraint WHERE conname = 'uq_users_provider_id'"
    )).fetchone()
    if exists:
        op.drop_constraint("uq_users_provider_id", "users", type_="unique")
