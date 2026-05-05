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
    op.drop_constraint('forum_categories_slug_key', 'forum_categories', type_='unique')
    op.create_unique_constraint('uq_forum_category_app_source_slug', 'forum_categories', ['app_source', 'slug'])
    op.alter_column('forum_categories', 'app_source', server_default=None)
    op.alter_column('forum_categories', 'name', existing_type=sa.String(length=100), nullable=False)


def downgrade() -> None:
    op.drop_constraint('uq_forum_category_app_source_slug', 'forum_categories', type_='unique')
    op.create_unique_constraint('forum_categories_slug_key', 'forum_categories', ['slug'])
    op.drop_index(op.f('ix_forum_categories_app_source'), table_name='forum_categories')
    op.drop_column('forum_categories', 'app_source')
