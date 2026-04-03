# /ai_rag_story_app/alembic/script.py.mako
"""add_step_bonus_transaction_type

Revision ID: 02a3b2386ced
Revises: d6715a14a088
Create Date: 2025-07-13 17:12:24.387288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02a3b2386ced'
down_revision: Union[str, None] = 'd6715a14a088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass