"""Fix: Add ai_summary fields to stories, acts, and scenes

Revision ID: fix_add_ai_summary
Revises: 474bda25467b
Create Date: 2025-06-25 09:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fix_add_ai_summary'
down_revision: Union[str, None] = '474bda25467b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add ai_summary column to stories table
    op.add_column('stories', sa.Column('ai_summary', sa.Text(), nullable=True))
    
    # Add ai_summary column to acts table
    op.add_column('acts', sa.Column('ai_summary', sa.Text(), nullable=True))
    
    # Add ai_summary column to scenes table
    op.add_column('scenes', sa.Column('ai_summary', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove ai_summary column from scenes table
    op.drop_column('scenes', 'ai_summary')
    
    # Remove ai_summary column from acts table
    op.drop_column('acts', 'ai_summary')
    
    # Remove ai_summary column from stories table
    op.drop_column('stories', 'ai_summary')