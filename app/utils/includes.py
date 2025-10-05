# /ai_rag_story_app/app/utils/includes.py

from typing import List, Dict, Any, Optional
from fastapi import Query
import logging

logger = logging.getLogger(__name__)

async def parse_include_param(
    include: Optional[str] = Query(None, description="Comma-separated list of related entities to include (e.g., 'characters,locations,lore_items')")
) -> List[str]:
    """
    Parse the include query parameter into a list of relation names.

    Args:
        include: Comma-separated string of relations to include

    Returns:
        List of relation names to include

    Example:
        GET /api/v1/worlds/1?include=characters,locations,lore_items
        ->
        ["characters", "locations", "lore_items"]
    """
    if not include:
        return []

    try:
        # Split by comma, strip whitespace, filter out empty strings
        relations = [rel.strip() for rel in include.split(',') if rel.strip()]
        return relations
    except Exception as e:
        logger.warning(f"Failed to parse include parameter '{include}': {e}")
        return []

async def apply_includes_to_query(base_query, include_fields: List[str], valid_relations: Dict[str, Any]):
    """
    Apply selectinload options to a SQLAlchemy query based on include parameters.

    Args:
        base_query: The base SQLAlchemy query
        include_fields: List of field names to include
        valid_relations: Dict mapping field names to their selectinload options

    Returns:
        Query with appropriate selectinload options applied

    Example:
        from sqlalchemy.orm import selectinload
        valid_relations = {
            "characters": selectinload(World.characters),
            "locations": selectinload(World.locations),
            "stories": selectinload(World.stories),
        }
    """
    query = base_query

    for field in include_fields:
        if field in valid_relations:
            query = query.options(valid_relations[field])
        else:
            logger.warning(f"Ignoring unknown include field: {field}")

    return query

class IncludeManager:
    """
    Utility class for managing include parameters and their validation.
    """

    def __init__(self, valid_relations: Dict[str, Any]):
        """
        Initialize with valid relation mappings.

        Args:
            valid_relations: Dict mapping relation names to selectinload options
        """
        self.valid_relations = valid_relations

    def parse_includes(self, include_str: Optional[str]) -> Dict[str, bool]:
        """
        Parse include string and return dict of includes.

        Returns:
            Dict with relation names as keys and True as values if they should be included
        """
        include_fields = await parse_include_param(include_str)
        return {field: True for field in include_fields if field in self.valid_relations}

    async def apply_to_query(self, query, include_str: Optional[str]):
        """
        Apply includes to a SQLAlchemy query.

        Args:
            query: Base SQLAlchemy query
            include_str: Include parameter string

        Returns:
            Modified query with selectinload options
        """
        include_fields = await parse_include_param(include_str)
        return await apply_includes_to_query(query, include_fields, self.valid_relations)