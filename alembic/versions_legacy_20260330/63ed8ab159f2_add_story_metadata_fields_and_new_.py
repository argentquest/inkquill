# /ai_rag_story_app/alembic/script.py.mako
"""Add story metadata fields and new prompt types

Revision ID: 63ed8ab159f2
Revises: 688359a08e08
Create Date: 2025-06-26 09:47:12.112198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63ed8ab159f2'
down_revision: Union[str, None] = '688359a08e08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass