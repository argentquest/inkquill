"""add_app_source_to_forum_categories

Revision ID: j6k7l8m9n0o1
Revises: i5j6k7l8m9n0
Create Date: 2026-05-03 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'j6k7l8m9n0o1'
down_revision: Union[str, None] = 'i5j6k7l8m9n0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('forum_categories', sa.Column('app_source', sa.String(length=32), server_default='storytelling', nullable=False))
    op.create_index(op.f('ix_forum_categories_app_source'), 'forum_categories', ['app_source'], unique=False)
    # Drop whichever unique constraint exists on slug/name — name varies by how the table was created
    conn = op.get_bind()
    existing = conn.execute(sa.text(
        "SELECT conname FROM pg_constraint "
        "WHERE conrelid = 'forum_categories'::regclass AND contype = 'u'"
    )).fetchall()
    existing_names = {r[0] for r in existing}
    for candidate in ('forum_categories_slug_key', 'forum_categories_name_key', 'uq_forum_category_app_source_slug'):
        if candidate in existing_names and candidate != 'uq_forum_category_app_source_slug':
            op.drop_constraint(candidate, 'forum_categories', type_='unique')
    if 'uq_forum_category_app_source_slug' not in existing_names:
        op.create_unique_constraint('uq_forum_category_app_source_slug', 'forum_categories', ['app_source', 'slug'])
    op.alter_column('forum_categories', 'app_source', server_default=None)
    op.alter_column('forum_categories', 'name', existing_type=sa.String(length=100), nullable=False)


def downgrade() -> None:
    conn = op.get_bind()
    existing = {r[0] for r in conn.execute(sa.text(
        "SELECT conname FROM pg_constraint WHERE conrelid='forum_categories'::regclass AND contype='u'"
    )).fetchall()}
    if 'uq_forum_category_app_source_slug' in existing:
        op.drop_constraint('uq_forum_category_app_source_slug', 'forum_categories', type_='unique')
    if 'forum_categories_slug_key' not in existing:
        op.create_unique_constraint('forum_categories_slug_key', 'forum_categories', ['slug'])
    op.drop_index(op.f('ix_forum_categories_app_source'), table_name='forum_categories')
    op.drop_column('forum_categories', 'app_source')
