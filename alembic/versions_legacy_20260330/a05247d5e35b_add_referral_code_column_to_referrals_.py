# /ai_rag_story_app/alembic/script.py.mako
"""Add referral_code column to referrals table

Revision ID: a05247d5e35b
Revises: 7cb2cea8948c
Create Date: 2025-07-18 12:40:50.269741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a05247d5e35b'
down_revision: Union[str, None] = '7cb2cea8948c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Simply add the missing referral_code column
    op.add_column('referrals', sa.Column('referral_code', sa.String(50), nullable=False, server_default=''))
    
    # Create index for the new column
    op.create_index(op.f('ix_referrals_referral_code'), 'referrals', ['referral_code'], unique=False)
    
    # Update existing records to have referral_code = referrer_user_id
    op.execute("UPDATE referrals SET referral_code = CAST(referrer_user_id AS VARCHAR)")
    
    # Remove the server default after updating existing records
    op.alter_column('referrals', 'referral_code', server_default=None)


def downgrade() -> None:
    # Remove the referral_code column and its index
    op.drop_index(op.f('ix_referrals_referral_code'), table_name='referrals')
    op.drop_column('referrals', 'referral_code')