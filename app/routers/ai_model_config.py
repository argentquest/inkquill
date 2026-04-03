"""API routes for ai model config."""

# /story_app/app/routers/ai_model_config.py
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.schemas.ai_model_config import AIModelConfigurationRead
from app.schemas.base import ApiResponse
from app.crud import ai_model_config as crud_ai_model_config
from app.models.ai_cost_log import AICallLog
from sqlalchemy import select, desc, func

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai-models",
    tags=["ai-models"],
    dependencies=[Depends(get_current_active_user)]
)

@router.get("/", response_model=ApiResponse)
async def list_ai_model_configurations(
    db: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a list of all active AI model configurations available for use.
    """
    logger.info("API: Request to list all active AI model configurations.")
    configs = await crud_ai_model_config.get_all_model_configs(db)
    if not configs:
        logger.warning("API: No active AI model configurations found in the database.")
        # Return an empty list, which is a valid response.
        # The frontend should handle the "No presets found" message.
    return ApiResponse.success_response(
        data=[AIModelConfigurationRead.model_validate(config) for config in configs]
    )

@router.get("/user-available", response_model=ApiResponse)
async def get_user_available_models(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve AI model configurations available for the current user.
    Currently returns all active configurations, but could be filtered by user permissions in the future.
    """
    logger.info(f"API: Request for user-available AI models for user {current_user.id}")
    configs = await crud_ai_model_config.get_all_model_configs(db)
    if not configs:
        logger.warning("API: No active AI model configurations found for user.")
    return ApiResponse.success_response(
        data=[AIModelConfigurationRead.model_validate(config) for config in configs]
    )

@router.get("/cost-logs/recent")
async def get_recent_cost_logs(
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recent AI cost logs for debugging and verification.
    Only returns logs for the current user.
    """
    try:
        # Get total count for this user
        count_result = await db.execute(
            select(func.count(AICallLog.id)).where(AICallLog.user_id == current_user.id)
        )
        total_count = count_result.scalar()
        
        # Get recent logs for this user
        result = await db.execute(
            select(AICallLog)
            .where(AICallLog.user_id == current_user.id)
            .order_by(desc(AICallLog.created_at))
            .limit(limit)
        )
        logs = result.scalars().all()
        
        # Convert to dict for JSON response
        recent_logs = []
        for log in logs:
            recent_logs.append({
                "id": log.id,
                "call_type": log.call_type,
                "model_name": log.model_name,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "total_tokens": log.total_tokens,
                "calculated_cost_usd": float(log.calculated_cost_usd),
                "duration_ms": log.duration_ms,
                "object_id": log.object_id,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
        
        return ApiResponse.success_response(
            data={
                "total_count": total_count,
                "recent_logs": recent_logs,
                "act_review_count": len([l for l in recent_logs if l["call_type"] == "act_review"])
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching cost logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching cost logs")
