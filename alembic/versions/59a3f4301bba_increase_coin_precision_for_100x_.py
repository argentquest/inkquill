# /ai_rag_story_app/alembic/script.py.mako
"""increase_coin_precision_for_100x_devaluation

Revision ID: 59a3f4301bba
Revises: 7a34b61c6d39
Create Date: 2025-07-10 23:58:45.390668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59a3f4301bba'
down_revision: Union[str, None] = '7a34b61c6d39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass