# /ai_rag_story_app/alembic/script.py.mako
"""Add QUICK_AI prompt type and sample prompts

Revision ID: fed43f889c62
Revises: 645076dc14c2
Create Date: 2025-07-15 11:11:40.078475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fed43f889c62'
down_revision: Union[str, None] = '645076dc14c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass