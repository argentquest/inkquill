# /ai_rag_story_app/alembic/script.py.mako
"""merge_migration_heads

Revision ID: ce27762e9a53
Revises: 2d8244251988, add_runpod_provider
Create Date: 2025-06-30 12:21:47.806389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce27762e9a53'
down_revision: Union[str, None] = ('2d8244251988', 'add_runpod_provider')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass