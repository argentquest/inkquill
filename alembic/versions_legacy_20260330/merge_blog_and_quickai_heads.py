"""Merge blog engine and quick AI heads

Revision ID: merge_blog_quickai
Revises: abc123def456, fed43f889c62
Create Date: 2025-07-15 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_blog_quickai'
down_revision: Union[str, None] = ('abc123def456', 'fed43f889c62')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a merge migration - no changes needed
    pass


def downgrade() -> None:
    # This is a merge migration - no changes needed
    pass