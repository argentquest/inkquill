"""Add story metadata fields and new prompt types

Revision ID: add_story_metadata_001
Revises: 
Create Date: 2024-12-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_story_metadata_001'
down_revision = None  # Update this with your latest migration revision
branch_labels = None
depends_on = None


def upgrade():
    # Add new enum values to prompt_type_enum
    # Note: PostgreSQL doesn't support ALTER TYPE in a transaction by default
    # So we need to handle this carefully
    
    # First, add the new enum values
    op.execute("ALTER TYPE prompt_type_enum ADD VALUE IF NOT EXISTS 'CHARACTER_ROLE'")
    op.execute("ALTER TYPE prompt_type_enum ADD VALUE IF NOT EXISTS 'STORY_GENRE'")
    op.execute("ALTER TYPE prompt_type_enum ADD VALUE IF NOT EXISTS 'STORY_TONE'")
    op.execute("ALTER TYPE prompt_type_enum ADD VALUE IF NOT EXISTS 'STORY_CONFLICT'")
    
    # Add new columns to stories table (check if they exist first)
    # Get connection to check column existence
    connection = op.get_bind()
    
    # Check if story_genre column exists
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stories' AND column_name='story_genre'
    """))
    if not result.fetchone():
        op.add_column('stories', sa.Column('story_genre', sa.String(length=100), nullable=True))
    
    # Check if story_tone column exists
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stories' AND column_name='story_tone'
    """))
    if not result.fetchone():
        op.add_column('stories', sa.Column('story_tone', sa.String(length=100), nullable=True))
    
    # Check if primary_conflict_type column exists
    result = connection.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='stories' AND column_name='primary_conflict_type'
    """))
    if not result.fetchone():
        op.add_column('stories', sa.Column('primary_conflict_type', sa.String(length=100), nullable=True))


def downgrade():
    # Remove columns from stories table
    op.drop_column('stories', 'primary_conflict_type')
    op.drop_column('stories', 'story_tone')
    op.drop_column('stories', 'story_genre')
    
    # Note: We cannot remove enum values in PostgreSQL
    # The enum values will remain in the type definition