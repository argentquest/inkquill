"""Database CRUD helpers for user activity."""

# /story_app/app/crud/user_activity.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, distinct
from app.models.user_activity import UserActivity
from app.schemas.user_activity import UserActivityCreate, UserActivityFilter, UserActivityBulkCreate
from typing import List, Dict, Any, Optional
from datetime import UTC, datetime, timedelta
import logging
from uuid import UUID
from fastapi import Request
from app.utils.bot_detection import is_bot_request, get_bot_info, log_bot_activity

logger = logging.getLogger(__name__)

async def create_user_activity(db: AsyncSession, activity_in: UserActivityCreate, request: Request = None) -> Optional[UserActivity]:
    """
    Creates a new user activity log record in the database and commits it immediately.
    This is designed to be called from middleware or endpoints to track user actions.
    
    Args:
        db: Database session
        activity_in: Activity data to log
        request: Optional FastAPI request object for bot detection
        
    Returns:
        UserActivity object if created, None if filtered out (e.g., bot request)
    """
    logger.debug(f"CRUD: Creating user activity log: {activity_in.action_type}")
    
    # Check if this is a bot request and should be filtered
    if request and is_bot_request(request):
        log_bot_activity(request, activity_in.action_type)
        logger.debug(f"CRUD: Filtering out bot activity: {activity_in.action_type}")
        return None
    
    db_activity = UserActivity(**activity_in.model_dump())
    
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    
    logger.debug(f"CRUD: User activity created with ID: {db_activity.id}")
    return db_activity

async def create_user_activities_bulk(db: AsyncSession, activities_in: UserActivityBulkCreate) -> List[UserActivity]:
    """
    Creates multiple user activity log records in a single transaction.
    Useful for batch processing or importing historical data.
    """
    logger.debug(f"CRUD: Creating {len(activities_in.activities)} user activity logs in bulk")
    
    db_activities = []
    for activity_data in activities_in.activities:
        db_activity = UserActivity(**activity_data.model_dump())
        db.add(db_activity)
        db_activities.append(db_activity)
    
    await db.commit()
    for activity in db_activities:
        await db.refresh(activity)
    
    logger.debug(f"CRUD: Bulk created {len(db_activities)} user activities")
    return db_activities

async def get_user_activity(db: AsyncSession, activity_id: UUID) -> Optional[UserActivity]:
    """Get a single user activity by ID."""
    stmt = select(UserActivity).where(UserActivity.id == activity_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_activities(
    db: AsyncSession,
    filter_params: UserActivityFilter
) -> List[UserActivity]:
    """
    Get user activities with flexible filtering options.
    Returns activities matching the specified criteria.
    """
    stmt = select(UserActivity)
    
    # Apply filters
    conditions = []
    
    if filter_params.user_id is not None:
        conditions.append(UserActivity.user_id == filter_params.user_id)
    
    if filter_params.action_type:
        conditions.append(UserActivity.action_type == filter_params.action_type)
    
    if filter_params.action_category:
        conditions.append(UserActivity.action_category == filter_params.action_category)
    
    if filter_params.endpoint:
        conditions.append(UserActivity.endpoint == filter_params.endpoint)
    
    if filter_params.method:
        conditions.append(UserActivity.method == filter_params.method)
    
    if filter_params.status_code is not None:
        conditions.append(UserActivity.status_code == filter_params.status_code)
    
    if filter_params.from_date:
        conditions.append(UserActivity.created_at >= filter_params.from_date)
    
    if filter_params.to_date:
        conditions.append(UserActivity.created_at <= filter_params.to_date)
    
    if filter_params.has_error is not None:
        if filter_params.has_error:
            conditions.append(UserActivity.error_message.is_not(None))
        else:
            conditions.append(UserActivity.error_message.is_(None))
    
    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    # Apply ordering and pagination
    stmt = stmt.order_by(UserActivity.created_at.desc())
    stmt = stmt.offset(filter_params.offset).limit(filter_params.limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_user_activity_summary(
    db: AsyncSession,
    filter_params: UserActivityFilter
) -> Dict[str, Any]:
    """
    Get summary statistics for user activities matching the filter criteria.
    Returns aggregated data useful for analytics and dashboards.
    """
    # Base query conditions
    conditions = []
    
    if filter_params.user_id is not None:
        conditions.append(UserActivity.user_id == filter_params.user_id)
    
    if filter_params.from_date:
        conditions.append(UserActivity.created_at >= filter_params.from_date)
    
    if filter_params.to_date:
        conditions.append(UserActivity.created_at <= filter_params.to_date)
    
    # Total activities count
    count_stmt = select(func.count(UserActivity.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total_activities = count_result.scalar() or 0
    
    # Unique users count
    unique_users_stmt = select(func.count(distinct(UserActivity.user_id)))
    if conditions:
        unique_users_stmt = unique_users_stmt.where(and_(*conditions))
    unique_users_result = await db.execute(unique_users_stmt)
    unique_users = unique_users_result.scalar() or 0
    
    # Total errors count
    error_conditions = conditions + [UserActivity.error_message.is_not(None)]
    errors_stmt = select(func.count(UserActivity.id)).where(and_(*error_conditions))
    errors_result = await db.execute(errors_stmt)
    total_errors = errors_result.scalar() or 0
    
    # Average duration
    avg_duration_stmt = select(func.avg(UserActivity.duration_ms))
    if conditions:
        avg_duration_stmt = avg_duration_stmt.where(and_(*conditions))
    avg_duration_result = await db.execute(avg_duration_stmt)
    avg_duration = avg_duration_result.scalar()
    
    # Most common actions (top 10)
    action_stmt = (
        select(
            UserActivity.action_type,
            func.count(UserActivity.id).label('count')
        )
        .group_by(UserActivity.action_type)
        .order_by(func.count(UserActivity.id).desc())
        .limit(10)
    )
    if conditions:
        action_stmt = action_stmt.where(and_(*conditions))
    action_result = await db.execute(action_stmt)
    most_common_actions = [
        {"action_type": row.action_type, "count": row.count}
        for row in action_result
    ]
    
    # Activities by category
    category_stmt = (
        select(
            UserActivity.action_category,
            func.count(UserActivity.id).label('count')
        )
        .where(UserActivity.action_category.is_not(None))
        .group_by(UserActivity.action_category)
    )
    if conditions:
        category_stmt = category_stmt.where(and_(*conditions))
    category_result = await db.execute(category_stmt)
    activities_by_category = {
        row.action_category: row.count
        for row in category_result
    }
    
    # Activities by status code
    status_stmt = (
        select(
            UserActivity.status_code,
            func.count(UserActivity.id).label('count')
        )
        .where(UserActivity.status_code.is_not(None))
        .group_by(UserActivity.status_code)
    )
    if conditions:
        status_stmt = status_stmt.where(and_(*conditions))
    status_result = await db.execute(status_stmt)
    activities_by_status = {
        str(row.status_code): row.count
        for row in status_result
    }
    
    # Time period
    time_period = {
        "from_date": filter_params.from_date,
        "to_date": filter_params.to_date
    }
    
    return {
        "total_activities": total_activities,
        "unique_users": unique_users,
        "total_errors": total_errors,
        "average_duration_ms": float(avg_duration) if avg_duration else None,
        "most_common_actions": most_common_actions,
        "activities_by_category": activities_by_category,
        "activities_by_status": activities_by_status,
        "time_period": time_period
    }

async def get_user_recent_activities(
    db: AsyncSession,
    user_id: int,
    limit: int = 10
) -> List[UserActivity]:
    """Get the most recent activities for a specific user."""
    stmt = (
        select(UserActivity)
        .where(UserActivity.user_id == user_id)
        .order_by(UserActivity.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def delete_old_activities(
    db: AsyncSession,
    days_to_keep: int = 90
) -> int:
    """
    Delete user activities older than the specified number of days.
    Returns the number of deleted records.
    """
    cutoff_date = datetime.now(UTC) - timedelta(days=days_to_keep)
    
    stmt = select(UserActivity).where(UserActivity.created_at < cutoff_date)
    result = await db.execute(stmt)
    activities_to_delete = result.scalars().all()
    
    for activity in activities_to_delete:
        await db.delete(activity)
    
    await db.commit()
    
    deleted_count = len(activities_to_delete)
    logger.info(f"Deleted {deleted_count} user activities older than {days_to_keep} days")
    
    return deleted_count
