# /ai_rag_story_app/alembic/script.py.mako
"""update_cta_position_values_to_uppercase

Revision ID: ad74669d1951
Revises: cdacb86451e6
Create Date: 2025-08-09 14:57:24.221672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad74669d1951'
down_revision: Union[str, None] = 'cdacb86451e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, add the new enum values to the existing enum
    connection = op.get_bind()
    
    # Add new uppercase enum values to the existing CTAPosition enum
    new_enum_values = [
        'HOME_SIDEBAR_TOP',
        'HOME_MAIN_TOP', 
        'HOME_MAIN_BOTTOM',
        'HOME_SIDEBAR_BOTTOM',
        'STORY_LIST_TOP',
        'WORLD_LIST_TOP',
        'BLOG_SIDEBAR'
    ]
    
    for enum_value in new_enum_values:
        try:
            connection.execute(
                sa.text(f"ALTER TYPE ctaposition ADD VALUE '{enum_value}'")
            )
        except Exception:
            # Value might already exist, skip
            pass
    
    # Update existing CTA position values to match new enum format
    position_mappings = {
        'home_sidebar_top': 'HOME_SIDEBAR_TOP',
        'home_main_top': 'HOME_MAIN_TOP', 
        'home_main_bottom': 'HOME_MAIN_BOTTOM',
        'home_sidebar_bottom': 'HOME_SIDEBAR_BOTTOM',
        'story_list_top': 'STORY_LIST_TOP',
        'world_list_top': 'WORLD_LIST_TOP',
        'blog_sidebar': 'BLOG_SIDEBAR'
    }
    
    for old_value, new_value in position_mappings.items():
        try:
            connection.execute(
                sa.text(
                    "UPDATE cta_contents SET position = :new_value WHERE position = :old_value"
                ),
                {"old_value": old_value, "new_value": new_value}
            )
        except Exception as e:
            # Skip if old value doesn't exist
            pass


def downgrade() -> None:
    # Reverse the position value updates
    connection = op.get_bind()
    
    # Revert position values back to lowercase format
    position_mappings = {
        'HOME_SIDEBAR_TOP': 'home_sidebar_top',
        'HOME_MAIN_TOP': 'home_main_top',
        'HOME_MAIN_BOTTOM': 'home_main_bottom',
        'HOME_SIDEBAR_BOTTOM': 'home_sidebar_bottom',
        'STORY_LIST_TOP': 'story_list_top',
        'WORLD_LIST_TOP': 'world_list_top',
        'BLOG_SIDEBAR': 'blog_sidebar'
    }
    
    for old_value, new_value in position_mappings.items():
        connection.execute(
            sa.text(
                "UPDATE cta_contents SET position = :new_value WHERE position = :old_value"
            ),
            {"old_value": old_value, "new_value": new_value}
        )