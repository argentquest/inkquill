"""Merge all migration heads

Revision ID: final_merge_all_heads
Revises: merge_blog_quickai, 7a34b61c6d39
Create Date: 2025-07-16 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'final_merge_all_heads'
down_revision: Union[str, None] = ('merge_blog_quickai', '7a34b61c6d39')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a merge migration - no changes needed
    pass


def downgrade() -> None:
    # This is a merge migration - no changes needed
    pass