# /ai_rag_story_app/alembic/script.py.mako
"""Add missing timestamp columns to referrals table

Revision ID: b15c32f8e42d
Revises: a05247d5e35b
Create Date: 2025-07-18 12:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b15c32f8e42d'
down_revision: Union[str, None] = 'a05247d5e35b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing timestamp columns
    op.add_column('referrals', sa.Column('first_story_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('referrals', sa.Column('first_publish_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove the timestamp columns
    op.drop_column('referrals', 'first_publish_at')
    op.drop_column('referrals', 'first_story_at')