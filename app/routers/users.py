"""API routes for users."""

# /story_app/app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session
# CORRECTED IMPORT: get_current_active_user is in deps.py, not security.py
from app.core.deps import get_current_active_user
from app.models.user import User as ModelUser # Alias to avoid conflict with Pydantic User
from app.schemas import user as schema_user
from app.schemas.base import ApiResponse
from app.crud import user as crud_user
from app.core.config import settings # For API prefix
from app.models.care_circle import CareCircleFamily

logger = logging.getLogger(__name__)

# --- Router Configuration ---
# All routes in this file will be prefixed with /api/v1/users (when included in main.py)
# and tagged as "users" in OpenAPI documentation.
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)] # Secure all user routes
)

# --- User Endpoint Definitions ---

@router.get("/me", response_model=ApiResponse, name="read_current_user_profile")
async def read_users_me(
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user),
):
    """
    Get profile of the currently authenticated user.
    """
    logger.info(f"User '{current_user.username}' requesting their profile.")
    result = await db.execute(
        select(exists().where(CareCircleFamily.created_by_user_id == current_user.id))
    )
    is_family_owner: bool = result.scalar() or False
    user_read = schema_user.UserRead.model_validate(current_user).model_copy(
        update={"is_family_owner": is_family_owner}
    )
    return ApiResponse.success_response(data=user_read)


@router.put("/me", response_model=ApiResponse, name="update_current_user_profile")
async def update_users_me(
    user_in: schema_user.UserProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user),
):
    """
    Update the currently authenticated user's profile.
    """
    logger.info(f"User '{current_user.username}' updating their profile.")

    update_payload = user_in.model_dump(exclude_unset=True)
    if not update_payload:
        return ApiResponse.success_response(data=schema_user.UserRead.model_validate(current_user))

    if "username" in update_payload and update_payload["username"] != current_user.username:
        existing_user = await crud_user.get_user_by_username(db, update_payload["username"])
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already in use",
            )

    if "email" in update_payload and update_payload["email"] != current_user.email:
        existing_email_user = await crud_user.get_user_by_email(db, update_payload["email"])
        if existing_email_user and existing_email_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already in use",
            )

    updated_user = await crud_user.update_user(
        db=db,
        db_user=current_user,
        user_in=schema_user.UserUpdate(**update_payload),
    )
    await db.commit()
    await db.refresh(updated_user)

    return ApiResponse.success_response(data=schema_user.UserRead.model_validate(updated_user))

@router.get("/{user_id}", response_model=ApiResponse, name="read_user_by_id")
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user) # For authorization check
):
    """
    Get a specific user by their ID.
    Currently, only allows a user to fetch their own profile by ID,
    or an admin to fetch any user (admin logic not yet implemented).
    """
    logger.info(f"User '{current_user.username}' requesting profile for user ID: {user_id}")
    # Basic authorization: users can only fetch their own profile by ID for now.
    # Admins would have broader access (to be implemented if needed).
    if current_user.id != user_id:
        # Future: Add admin role check here to allow admins to fetch any user
        # if not current_user.is_superuser: # Example if you add is_superuser field
        logger.warning(f"User '{current_user.username}' (ID: {current_user.id}) attempted to access profile of user ID: {user_id}. Forbidden.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's profile."
        )

    db_user = await crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        logger.warning(f"User ID {user_id} not found when requested by '{current_user.username}'.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ApiResponse.success_response(data=schema_user.UserRead.model_validate(db_user))

# --- Admin-only route: List all users ---
@router.get("/", response_model=ApiResponse, name="list_all_users")
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """
    Retrieves a list of all users (admin only).
    """
    # Check if current user is admin
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to list all users")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators can list all users"
        )
    
    logger.info(f"Admin '{current_user.username}' listing all users.")
    users = await crud_user.get_users(db, skip=skip, limit=limit)
    return ApiResponse.success_response(
        data=[schema_user.UserRead.model_validate(user) for user in users]
    )


# --- Admin-only route: Toggle user activation status ---
@router.patch("/{user_id}/toggle-active", response_model=ApiResponse, name="toggle_user_active")
async def toggle_user_active(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """
    Toggle the is_active status of a user (admin only).
    """
    # Check if current user is admin
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to toggle user activation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators can toggle user activation status"
        )
    
    # Get the target user
    target_user = await crud_user.get_user(db, user_id=user_id)
    if not target_user:
        logger.warning(f"Admin '{current_user.username}' tried to toggle activation for non-existent user ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if target_user.id == current_user.id:
        logger.warning(f"Admin '{current_user.username}' tried to toggle their own activation status")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot toggle your own activation status"
        )
    
    # Toggle the status
    old_status = target_user.is_active
    new_status = not old_status
    
    update_data = schema_user.UserUpdate(is_active=new_status)
    updated_user = await crud_user.update_user(db=db, db_user=target_user, user_in=update_data)
    await db.commit()
    await db.refresh(updated_user)
    
    action = "activated" if new_status else "deactivated"
    logger.info(f"Admin '{current_user.username}' {action} user '{target_user.username}' (ID: {user_id})")
    
    return ApiResponse.success_response(data=schema_user.UserRead.model_validate(updated_user))


# --- Admin-only route: Edit user details ---
@router.patch("/{user_id}/edit", response_model=ApiResponse, name="edit_user")
async def edit_user(
    user_id: int,
    user_update: schema_user.UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """
    Edit user details: email, display_name, is_admin (admin only).
    """
    # Check if current user is admin
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to edit user details")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only administrators can edit user details"
        )
    
    # Get the target user
    target_user = await crud_user.get_user(db, user_id=user_id)
    if not target_user:
        logger.warning(f"Admin '{current_user.username}' tried to edit non-existent user ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from removing their own admin status
    if (target_user.id == current_user.id and 
        user_update.is_admin is not None and 
        not user_update.is_admin):
        logger.warning(f"Admin '{current_user.username}' tried to remove their own admin status")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin privileges"
        )
    
    # Update the user
    updated_user = await crud_user.update_user(db=db, db_user=target_user, user_in=user_update)
    await db.commit()
    await db.refresh(updated_user)
    
    logger.info(f"Admin '{current_user.username}' edited user '{target_user.username}' (ID: {user_id})")
    
    return ApiResponse.success_response(data=schema_user.UserRead.model_validate(updated_user))

# --- Example: Update user (typically for a user to update their own profile) ---
# @router.put("/me", response_model=ApiResponse, name="update_current_user_profile")
# async def update_users_me(
#     user_in: schema_user.UserUpdate, # Pydantic schema for update data
#     db: AsyncSession = Depends(get_db_session),
#     current_user: ModelUser = Depends(get_current_active_user)
# ):
#     """
#     Update profile of the currently authenticated user.
#     """
#     logger.info(f"User '{current_user.username}' updating their profile.")
#     updated_user = await crud_user.update_user(db=db, db_user=current_user, user_in=user_in)
#     if updated_user is None: # Should not happen if current_user is valid
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for update.")
#     return updated_user

# Add more user-related endpoints as needed (e.g., update, delete by admin, etc.)

