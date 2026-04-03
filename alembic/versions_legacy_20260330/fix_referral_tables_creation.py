"""Fix referral tables creation

Revision ID: fix_referral_tables_creation
Revises: b15c32f8e42d
Create Date: 2025-07-19 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fix_referral_tables_creation'
down_revision: Union[str, None] = 'b15c32f8e42d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if referrals table exists, if not create it
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'referrals'
    """))
    
    if not result.fetchone():
        # Create referrals table
        op.create_table('referrals',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('referrer_user_id', sa.Integer(), nullable=False),
            sa.Column('referred_user_id', sa.Integer(), nullable=True),
            sa.Column('anonymous_session_id', sa.String(255), nullable=True),
            sa.Column('referral_code', sa.String(50), nullable=False),
            sa.Column('source_platform', sa.String(50), nullable=True),
            sa.Column('source_content_type', sa.String(50), nullable=True),
            sa.Column('source_content_id', sa.String(255), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.String(500), nullable=True),
            sa.Column('referral_url', sa.String(1000), nullable=True),
            sa.Column('is_converted', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('has_created_story', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('has_published_story', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('first_story_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('first_publish_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['referrer_user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['referred_user_id'], ['users.id'], ondelete='SET NULL')
        )
        
        # Create indexes
        op.create_index('ix_referrals_referrer_user_id', 'referrals', ['referrer_user_id'])
        op.create_index('ix_referrals_referred_user_id', 'referrals', ['referred_user_id'])
        op.create_index('ix_referrals_anonymous_session_id', 'referrals', ['anonymous_session_id'])
        op.create_index('ix_referrals_referral_code', 'referrals', ['referral_code'])
        op.create_index('ix_referrals_is_converted', 'referrals', ['is_converted'])
        op.create_index('ix_referrals_created_at', 'referrals', ['created_at'])
    
    # Check if referral_rewards table exists, if not create it
    result = conn.execute(sa.text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'referral_rewards'
    """))
    
    if not result.fetchone():
        # Create referral_rewards table
        op.create_table('referral_rewards',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('referral_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('reward_type', sa.String(50), nullable=False),
            sa.Column('coin_amount', sa.Integer(), nullable=False),
            sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['referral_id'], ['referrals.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
        )
        
        # Create indexes
        op.create_index('ix_referral_rewards_referral_id', 'referral_rewards', ['referral_id'])
        op.create_index('ix_referral_rewards_user_id', 'referral_rewards', ['user_id'])
        op.create_index('ix_referral_rewards_reward_type', 'referral_rewards', ['reward_type'])
        op.create_index('ix_referral_rewards_awarded_at', 'referral_rewards', ['awarded_at'])
    
    # Check if referral_limits table exists, if not create it
    result = conn.execute(sa.text("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'referral_limits'
    """))
    
    if not result.fetchone():
        # Create referral_limits table
        op.create_table('referral_limits',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('total_coins_earned', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('visit_rewards_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('registration_rewards_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('story_rewards_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('publish_rewards_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.UniqueConstraint('user_id', 'date', name='uq_referral_limits_user_date')
        )
        
        # Create indexes
        op.create_index('ix_referral_limits_user_id', 'referral_limits', ['user_id'])
        op.create_index('ix_referral_limits_date', 'referral_limits', ['date'])
    
    # Check if users table has referral columns, if not add them
    result = conn.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'referred_by_user_id'
    """))
    
    if not result.fetchone():
        # Add referral columns to users table
        op.add_column('users', sa.Column('referred_by_user_id', sa.Integer(), nullable=True))
        op.add_column('users', sa.Column('referral_count', sa.Integer(), nullable=False, server_default='0'))
        
        # Update existing users
        op.execute("UPDATE users SET referral_count = 0 WHERE referral_count IS NULL")
        
        # Add foreign key constraint
        op.create_foreign_key(None, 'users', 'users', ['referred_by_user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Drop all referral tables and columns
    op.drop_table('referral_limits')
    op.drop_table('referral_rewards') 
    op.drop_table('referrals')
    
    # Drop referral columns from users table
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_column('users', 'referral_count')
    op.drop_column('users', 'referred_by_user_id')