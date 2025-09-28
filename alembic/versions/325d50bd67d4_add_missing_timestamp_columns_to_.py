# /ai_rag_story_app/alembic/script.py.mako
"""Add missing timestamp columns to referrals table

Revision ID: 325d50bd67d4
Revises: b15c32f8e42d
Create Date: 2025-07-18 12:46:17.954809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '325d50bd67d4'
down_revision: Union[str, None] = 'b15c32f8e42d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass