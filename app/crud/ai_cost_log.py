"""Database CRUD helpers for ai cost log."""

# /story_app/app/crud/ai_cost_log.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.ai_cost_log import AICallLog
from app.schemas.ai_cost_log import AICallLogCreate
from typing import List, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def create_ai_call_log(db: AsyncSession, log_in: AICallLogCreate) -> AICallLog:
    """
    Creates a new AI call log record in the database and commits it immediately.
    This function now correctly handles the AICallLogCreate schema which includes
    the new model_config_id and input_prompt fields.
    """
    logger.debug("CRUD: Preparing to add and commit AI call log to session.")
    
    # The log_in object (AICallLogCreate schema) already contains all the necessary fields.
    # We can directly create the AICallLog ORM model from it.
    db_log = AICallLog(**log_in.model_dump())
    
    db.add(db_log)
    await db.commit()  # Commits this transaction immediately and independently.
    logger.debug(f"CRUD: Commit successful for AI call log. Log ID: {db_log.id}, Config ID: {db_log.model_config_id}")
    await db.refresh(db_log) # Refresh to get DB defaults like created_at
    return db_log

async def get_recent_ai_calls(db: AsyncSession, user_id: int, limit: int = 5) -> List[AICallLog]:
    """Get recent AI calls for a user, ordered by creation time descending."""
    stmt = (
        select(AICallLog)
        .where(AICallLog.user_id == user_id)
        .order_by(AICallLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_daily_ai_cost_summary(db: AsyncSession, user_id: int) -> Tuple[int, float, int]:
    """Get today's AI cost summary: (total_calls, total_cost, total_tokens)."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    
    stmt = (
        select(
            func.count(AICallLog.id).label('total_calls'),
            func.sum(AICallLog.calculated_cost_usd).label('total_cost'),
            func.sum(AICallLog.total_tokens).label('total_tokens')
        )
        .where(
            and_(
                AICallLog.user_id == user_id,
                AICallLog.created_at >= today_start,
                AICallLog.created_at < tomorrow_start
            )
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    
    return (
        row.total_calls or 0,
        float(row.total_cost) if row.total_cost else 0.0,
        row.total_tokens or 0
    )
