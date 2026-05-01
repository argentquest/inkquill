"""add_app_source_to_forum_threads

Revision ID: f86ce2dc5366
Revises: f7721355d31c
Create Date: 2026-05-01 13:38:04.314526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f86ce2dc5366'
down_revision: Union[str, None] = 'f7721355d31c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('forum_threads', sa.Column('app_source', sa.String(length=32), server_default='storytelling', nullable=False))
    op.create_index('idx_thread_app_source_status', 'forum_threads', ['app_source', 'status'], unique=False)
    op.create_index(op.f('ix_forum_threads_app_source'), 'forum_threads', ['app_source'], unique=False)
    op.alter_column('forum_threads', 'app_source', server_default=None)


def downgrade() -> None:
    op.drop_index(op.f('ix_forum_threads_app_source'), table_name='forum_threads')
    op.drop_index('idx_thread_app_source_status', table_name='forum_threads')
    op.drop_column('forum_threads', 'app_source')
