# /story_app/alembic/script.py.mako
"""add_app_source_to_blog_posts

Revision ID: f7721355d31c
Revises: i5j6k7l8m9n0
Create Date: 2026-05-01 12:19:08.874441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7721355d31c'
down_revision: Union[str, None] = 'i5j6k7l8m9n0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add app_source column to blog_posts with default 'storytelling'
    op.add_column('blog_posts', sa.Column('app_source', sa.String(32), nullable=False, server_default='storytelling'))
    op.create_index('idx_blog_posts_app_source', 'blog_posts', ['app_source'])
    op.create_index('idx_blog_posts_app_source_status', 'blog_posts', ['app_source', 'status'])


def downgrade() -> None:
    op.drop_index('idx_blog_posts_app_source_status', table_name='blog_posts')
    op.drop_index('idx_blog_posts_app_source', table_name='blog_posts')
    op.drop_column('blog_posts', 'app_source')
