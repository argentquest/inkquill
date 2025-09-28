"""Add last_viewed_at to blog_posts

Revision ID: add_last_viewed_at
Revises: abdec3ff148b
Create Date: 2025-07-26 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_last_viewed_at'
down_revision: Union[str, None] = 'abdec3ff148b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add last_viewed_at column to blog_posts table
    op.add_column('blog_posts', 
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    # Remove last_viewed_at column
    op.drop_column('blog_posts', 'last_viewed_at')