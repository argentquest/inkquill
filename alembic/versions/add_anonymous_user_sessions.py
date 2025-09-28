"""add anonymous user sessions table

Revision ID: add_anonymous_sessions
Revises: d2608829855a
Create Date: 2025-06-21 11:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_anonymous_sessions'
down_revision = '8caa950b083f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create anonymous_user_sessions table
    op.create_table('anonymous_user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=64), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),  # IPv6 support
        sa.Column('browser_fingerprint', sa.String(length=32), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_anonymous_sessions_user_id', 'anonymous_user_sessions', ['user_id'])
    op.create_index('ix_anonymous_sessions_session_token', 'anonymous_user_sessions', ['session_token'], unique=True)
    op.create_index('ix_anonymous_sessions_ip_address', 'anonymous_user_sessions', ['ip_address'])
    op.create_index('ix_anonymous_sessions_browser_fingerprint', 'anonymous_user_sessions', ['browser_fingerprint'])
    op.create_index('ix_anonymous_sessions_created_at', 'anonymous_user_sessions', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_anonymous_sessions_created_at', table_name='anonymous_user_sessions')
    op.drop_index('ix_anonymous_sessions_browser_fingerprint', table_name='anonymous_user_sessions')
    op.drop_index('ix_anonymous_sessions_ip_address', table_name='anonymous_user_sessions')
    op.drop_index('ix_anonymous_sessions_session_token', table_name='anonymous_user_sessions')
    op.drop_index('ix_anonymous_sessions_user_id', table_name='anonymous_user_sessions')
    
    # Drop table
    op.drop_table('anonymous_user_sessions')