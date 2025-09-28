# /ai_rag_story_app/app/crud/ai_model_config.py
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.ai_model_config import AIModelConfiguration, AIModelTypeEnum

logger = logging.getLogger(__name__)

async def get_all_model_configs(db: AsyncSession) -> List[AIModelConfiguration]:
    """
    Retrieves all active GENERATION AI model configurations suitable for chat, ordered by their display name.
    This filters out EMBEDDING models and IMAGE GENERATION models since they're not used for chat conversations.
    """
    logger.info("CRUD: Fetching all active generation AI model configurations suitable for chat.")
    result = await db.execute(
        select(AIModelConfiguration)
        .filter(
            AIModelConfiguration.is_active == True,
            AIModelConfiguration.model_type == AIModelTypeEnum.GENERATION,
            ~AIModelConfiguration.display_name.ilike('%Image Generation%'),
            ~AIModelConfiguration.display_name.ilike('%DALL-E%')
        )
        .order_by(AIModelConfiguration.display_name)
    )
    return result.scalars().all()

async def get_model_config_by_id(db: AsyncSession, config_id: int) -> Optional[AIModelConfiguration]:
    """
    Retrieves a single AI model configuration by its ID.
    """
    logger.debug(f"CRUD: Fetching AI model configuration with ID: {config_id}")
    return await db.get(AIModelConfiguration, config_id)

async def get_default_model_config(db: AsyncSession) -> Optional[AIModelConfiguration]:
    """
    Retrieves the default AI model configuration for registered users.
    Returns the first active generation model, preferably GPT-4o Mini for cost efficiency.
    """
    logger.debug("CRUD: Fetching default AI model configuration for registered users")
    
    # Try to get GPT-4o Mini first (cost-efficient)
    result = await db.execute(
        select(AIModelConfiguration)
        .filter(
            AIModelConfiguration.is_active == True,
            AIModelConfiguration.model_type == AIModelTypeEnum.GENERATION,
            AIModelConfiguration.display_name.ilike('%gpt-4o-mini%')
        )
        .limit(1)
    )
    default_config = result.scalar_one_or_none()
    
    if default_config:
        logger.info(f"Using GPT-4o Mini as default model: {default_config.display_name}")
        return default_config
    
    # Fallback to any active generation model
    result = await db.execute(
        select(AIModelConfiguration)
        .filter(
            AIModelConfiguration.is_active == True,
            AIModelConfiguration.model_type == AIModelTypeEnum.GENERATION,
            ~AIModelConfiguration.display_name.ilike('%Image Generation%'),
            ~AIModelConfiguration.display_name.ilike('%DALL-E%')
        )
        .order_by(AIModelConfiguration.display_name)
        .limit(1)
    )
    default_config = result.scalar_one_or_none()
    
    if default_config:
        logger.info(f"Using fallback model as default: {default_config.display_name}")
    else:
        logger.warning("No active generation model found for default configuration")
    
    return default_config

async def get_public_chat_default_model_config(db: AsyncSession) -> Optional[AIModelConfiguration]:
    """
    Retrieves the AI model configuration designated for public chat.
    Returns the model marked with is_public_chat_default=True, or falls back to GPT-4o Mini.
    """
    logger.debug("CRUD: Fetching public chat default AI model configuration")
    
    # First try to get the model specifically marked for public chat
    result = await db.execute(
        select(AIModelConfiguration)
        .filter(
            AIModelConfiguration.is_active == True,
            AIModelConfiguration.model_type == AIModelTypeEnum.GENERATION,
            AIModelConfiguration.is_public_chat_default == True
        )
        .limit(1)
    )
    public_default_config = result.scalar_one_or_none()
    
    if public_default_config:
        logger.info(f"Using designated public chat default model: {public_default_config.display_name}")
        return public_default_config
    
    # Fallback to GPT-4o Mini (most cost-effective for public users)
    result = await db.execute(
        select(AIModelConfiguration)
        .filter(
            AIModelConfiguration.is_active == True,
            AIModelConfiguration.model_type == AIModelTypeEnum.GENERATION,
            AIModelConfiguration.display_name.ilike('%gpt-4o-mini%')
        )
        .limit(1)
    )
    fallback_config = result.scalar_one_or_none()
    
    if fallback_config:
        logger.info(f"Using GPT-4o Mini as fallback for public chat: {fallback_config.display_name}")
        return fallback_config
    
    # Final fallback to any active generation model
    result = await db.execute(
        select(AIModelConfiguration)
        .filter(
            AIModelConfiguration.is_active == True,
            AIModelConfiguration.model_type == AIModelTypeEnum.GENERATION,
            ~AIModelConfiguration.display_name.ilike('%Image Generation%'),
            ~AIModelConfiguration.display_name.ilike('%DALL-E%')
        )
        .order_by(AIModelConfiguration.display_name)
        .limit(1)
    )
    final_fallback = result.scalar_one_or_none()
    
    if final_fallback:
        logger.warning(f"Using final fallback model for public chat: {final_fallback.display_name}")
    else:
        logger.error("No active generation model found for public chat")
    
    return final_fallback


class AIModelConfigCRUD:
    """CRUD class for AI Model Configuration operations"""
    
    async def get_all_model_configs(self, db: AsyncSession) -> List[AIModelConfiguration]:
        return await get_all_model_configs(db)
    
    async def get_model_config_by_id(self, db: AsyncSession, config_id: int) -> Optional[AIModelConfiguration]:
        return await get_model_config_by_id(db, config_id)
    
    async def get_default_model_config(self, db: AsyncSession) -> Optional[AIModelConfiguration]:
        return await get_default_model_config(db)
    
    async def get_public_chat_default_model_config(self, db: AsyncSession) -> Optional[AIModelConfiguration]:
        return await get_public_chat_default_model_config(db)

# Create instance for import
ai_model_crud = AIModelConfigCRUD()