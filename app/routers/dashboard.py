"""API routes for dashboard."""

# /story_app/app/routers/dashboard.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user_from_bearer_token
from app.models.user import User
from app.models.world import World
from app.models.story import Story
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.schemas.base import ApiResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["dashboard"],
)

# --- Dashboard Response Schemas ---
class DashboardSummary(BaseModel):
    """Dashboard summary statistics."""
    total_worlds: int = 0
    total_stories: int = 0
    total_characters: int = 0
    total_locations: int = 0
    total_lore_items: int = 0
    recent_activity_count: int = 0
    system_status: str = "healthy"

class DashboardResponse(BaseModel):
    """Dashboard API response."""
    summary: DashboardSummary

@router.get("/summary", response_model=ApiResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user_from_bearer_token),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get dashboard summary with key metrics for the authenticated user.
    """
    try:
        logger.info(f"Getting dashboard summary for user: {current_user.id}")

        # Get counts for user's content
        worlds_count_query = select(func.count(World.id)).where(World.user_id == current_user.id)
        worlds_result = await db.execute(worlds_count_query)
        worlds_count = worlds_result.scalar() or 0

        stories_count_query = select(func.count(Story.id)).where(Story.user_id == current_user.id)
        stories_result = await db.execute(stories_count_query)
        stories_count = stories_result.scalar() or 0

        characters_count_query = (
            select(func.count(Character.id))
            .join(World, Character.world_id == World.id)
            .where(World.user_id == current_user.id)
        )
        characters_result = await db.execute(characters_count_query)
        characters_count = characters_result.scalar() or 0

        locations_count_query = (
            select(func.count(Location.id))
            .join(World, Location.world_id == World.id)
            .where(World.user_id == current_user.id)
        )
        locations_result = await db.execute(locations_count_query)
        locations_count = locations_result.scalar() or 0

        lore_items_count_query = (
            select(func.count(LoreItem.id))
            .join(World, LoreItem.world_id == World.id)
            .where(World.user_id == current_user.id)
        )
        lore_items_result = await db.execute(lore_items_count_query)
        lore_items_count = lore_items_result.scalar() or 0

        # Create summary
        summary = DashboardSummary(
            total_worlds=worlds_count,
            total_stories=stories_count,
            total_characters=characters_count,
            total_locations=locations_count,
            total_lore_items=lore_items_count,
            recent_activity_count=0,  # TODO: Add recent activity count when user_activity is available
            system_status="healthy"
        )

        response_data = DashboardResponse(summary=summary)

        logger.info(f"Dashboard summary retrieved successfully for user {current_user.id}")

        return ApiResponse.success_response(data=response_data)

    except Exception as e:
        logger.error(f"Error retrieving dashboard summary for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        ) from e
