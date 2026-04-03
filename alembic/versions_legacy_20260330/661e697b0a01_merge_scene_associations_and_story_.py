# /ai_rag_story_app/alembic/script.py.mako
"""Merge scene associations and story metadata

Revision ID: 661e697b0a01
Revises: add_scene_associations, add_story_metadata_001
Create Date: 2025-06-29 10:25:07.132568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '661e697b0a01'
down_revision: Union[str, None] = ('add_scene_associations', 'add_story_metadata_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass