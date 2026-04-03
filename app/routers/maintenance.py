"""API routes for maintenance."""

# /story_app/app/routers/maintenance.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from app.core.maintenance import MaintenanceManager
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/maintenance",
    tags=["maintenance"]
)

@router.get("/status", name="get_maintenance_status")
async def get_maintenance_status() -> ApiResponse:
    """Get current maintenance status - public endpoint for all users"""
    try:
        status = MaintenanceManager.get_maintenance_status()
        return ApiResponse.success_response({
            "enabled": status.get("enabled", False),
            "message": status.get("message"),
            "estimated_end_time": status.get("estimated_end_time")
        })
    except Exception as e:
        logger.error(f"Error getting maintenance status: {e}")
        return ApiResponse.success_response({"enabled": False, "message": None})

@router.post("/enable", name="enable_maintenance_mode")
async def enable_maintenance_mode(
    message: str = "The application is getting an update and will be back in about 5 minutes.",
    duration_minutes: int = 5,
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """Enable maintenance mode - admin only"""
    
    # Check if user is admin
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can enable maintenance mode"
        )
    
    try:
        MaintenanceManager.set_maintenance_mode(
            enabled=True,
            message=message,
            duration_minutes=duration_minutes
        )
        logger.info(f"Maintenance mode enabled by user {current_user.username} for {duration_minutes} minutes")
        return ApiResponse.success_response({"status": "Maintenance mode enabled", "message": message})
    except Exception as e:
        logger.error(f"Failed to enable maintenance mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable maintenance mode"
        )

@router.post("/disable", name="disable_maintenance_mode")
async def disable_maintenance_mode(
    current_user: User = Depends(get_current_active_user)
) -> ApiResponse:
    """Disable maintenance mode - admin only"""
    
    # Check if user is admin
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can disable maintenance mode"
        )
    
    try:
        MaintenanceManager.set_maintenance_mode(enabled=False)
        logger.info(f"Maintenance mode disabled by user {current_user.username}")
        return ApiResponse.success_response({"status": "Maintenance mode disabled"})
    except Exception as e:
        logger.error(f"Failed to disable maintenance mode: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable maintenance mode"
        )
