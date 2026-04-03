"""Database CRUD helpers for llm models."""

# /story_app/app/crud/llm_models.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.ai_model_config import AIModelConfiguration
from typing import List, Dict


async def get_all_model_configurations(db: AsyncSession) -> List[AIModelConfiguration]:
    """Get all AI model configurations"""
    result = await db.execute(
        select(AIModelConfiguration).order_by(
            AIModelConfiguration.provider,
            AIModelConfiguration.display_name
        )
    )
    return result.scalars().all()


async def get_model_statistics(db: AsyncSession) -> Dict:
    """Get statistics about AI models"""
    # Total count
    total_result = await db.execute(
        select(func.count(AIModelConfiguration.id))
    )
    total_count = total_result.scalar()
    
    # Active count
    active_result = await db.execute(
        select(func.count(AIModelConfiguration.id)).where(
            AIModelConfiguration.is_active == True
        )
    )
    active_count = active_result.scalar()
    
    # Providers
    provider_result = await db.execute(
        select(AIModelConfiguration.provider).distinct()
    )
    providers = [p.value for p in provider_result.scalars().all()]
    
    return {
        "total_count": total_count,
        "active_count": active_count,
        "providers": providers
    }
