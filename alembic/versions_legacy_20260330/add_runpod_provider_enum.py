"""Add RUNPOD to ai_provider_enum

Revision ID: add_runpod_provider
Revises: 
Create Date: 2025-06-29 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_runpod_provider'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None

def upgrade():
    # Add RUNPOD to the existing ai_provider_enum
    op.execute("ALTER TYPE ai_provider_enum ADD VALUE IF NOT EXISTS 'RUNPOD'")

def downgrade():
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type which is complex
    # For now, we'll leave a comment about manual cleanup if needed
    pass