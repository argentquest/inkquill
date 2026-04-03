# /ai_rag_story_app/alembic/script.py.mako
"""Merge referral tables fix with main branch

Revision ID: abdec3ff148b
Revises: 28c0b2e9091c, fix_referral_tables_creation
Create Date: 2025-07-19 11:51:02.233964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abdec3ff148b'
down_revision: Union[str, None] = ('28c0b2e9091c', 'fix_referral_tables_creation')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass