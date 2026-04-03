"""Service helpers for summary generation service."""

# app/services/summary_generation_service.py
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.exceptions import ServiceResponseException

from app.models.act import Act
from app.models.scene import Scene
from app.crud.act import update_act
from app.crud.scene import update_scene
from app.schemas.act import ActUpdate
from app.schemas.scene import SceneUpdate
from app.services.sk_kernel_instance import kernel
from app.services.sk_constants import STORY_ANALYSIS_PLUGIN_NAME
from app.services.cost_tracker_service import log_ai_call
from app.crud.ai_model_config import get_default_model_config

logger = logging.getLogger(__name__)

async def generate_ai_summary_for_act(
    db: AsyncSession,
    act: Act,
    updater_user_id: int
) -> Optional[str]:
    """
    Generate an AI summary for an act based on its description/content.
    Updates the act's ai_summary field in the database.
    
    Args:
        db: Database session
        act: The Act model instance to generate summary for
        updater_user_id: ID of the user performing the update
        
    Returns:
        The generated summary text, or None if generation failed
    """
    if not act.description or not act.description.strip():
        logger.info(f"Act {act.id} has no content to summarize")
        return None
        
    try:
        # Get default model configuration
        active_model = await get_default_model_config(db)
        model_name = active_model.model_name if active_model else None
        
        # Get the summary generation function
        function_name = "GenerateTextSummary"
        function = kernel.get_function(plugin_name=STORY_ANALYSIS_PLUGIN_NAME, function_name=function_name)
        
        # Prepare arguments
        kernel_arguments = {
            "text_to_summarize": act.description
        }
        
        # Generate summary
        result = await kernel.invoke(function, **kernel_arguments)
        
        if result and result.value:
            # Handle case where result.value might be a list
            if isinstance(result.value, list):
                summary = str(result.value[0]).strip() if result.value else ""
            else:
                summary = str(result.value).strip()
            
            # Update the act with the generated summary
            act_update = ActUpdate(ai_summary=summary)
            await update_act(db, db_act=act, act_update=act_update, updater_user_id=updater_user_id)
            
            # Track costs - would need to extract usage from result to properly log
            # For now, skip cost tracking since we don't have token usage data
            # TODO: Extract usage metadata from semantic kernel result
            
            logger.info(f"Generated AI summary for act {act.id}: {summary[:100]}...")
            return summary
        else:
            logger.warning(f"No summary generated for act {act.id}")
            return None
            
    except ServiceResponseException as e:
        logger.error(f"AI service error generating summary for act {act.id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating summary for act {act.id}: {e}", exc_info=True)
        return None


async def generate_ai_summary_for_scene(
    db: AsyncSession,
    scene: Scene,
    updater_user_id: int
) -> Optional[str]:
    """
    Generate an AI summary for a scene based on its content.
    Updates the scene's ai_summary field in the database.
    
    Args:
        db: Database session
        scene: The Scene model instance to generate summary for
        updater_user_id: ID of the user performing the update
        
    Returns:
        The generated summary text, or None if generation failed
    """
    if not scene.content or not scene.content.strip():
        logger.info(f"Scene {scene.id} has no content to summarize")
        return None
        
    try:
        # Get default model configuration
        active_model = await get_default_model_config(db)
        model_name = active_model.model_name if active_model else None
        
        # Get the summary generation function
        function_name = "GenerateTextSummary"
        function = kernel.get_function(plugin_name=STORY_ANALYSIS_PLUGIN_NAME, function_name=function_name)
        
        # Prepare arguments
        kernel_arguments = {
            "text_to_summarize": scene.content
        }
        
        # Generate summary
        result = await kernel.invoke(function, **kernel_arguments)
        
        if result and result.value:
            # Handle case where result.value might be a list
            if isinstance(result.value, list):
                summary = str(result.value[0]).strip() if result.value else ""
            else:
                summary = str(result.value).strip()
            
            # Update the scene with the generated summary
            scene_update = SceneUpdate(ai_summary=summary)
            await update_scene(db, db_scene=scene, scene_in=scene_update)
            
            # Track costs - would need to extract usage from result to properly log
            # For now, skip cost tracking since we don't have token usage data
            # TODO: Extract usage metadata from semantic kernel result
            
            logger.info(f"Generated AI summary for scene {scene.id}: {summary[:100]}...")
            return summary
        else:
            logger.warning(f"No summary generated for scene {scene.id}")
            return None
            
    except ServiceResponseException as e:
        logger.error(f"AI service error generating summary for scene {scene.id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating summary for scene {scene.id}: {e}", exc_info=True)
        return None


async def update_act_with_ai_summary(
    db: AsyncSession,
    act_id: int,
    updater_user_id: int
) -> Optional[str]:
    """
    Convenience function to fetch an act and generate/update its AI summary.
    
    Args:
        db: Database session
        act_id: ID of the act to update
        updater_user_id: ID of the user performing the update
        
    Returns:
        The generated summary text, or None if generation failed
    """
    from app.crud.act import get_act
    
    act = await get_act(db, act_id=act_id)
    if not act:
        logger.error(f"Act {act_id} not found")
        return None
        
    return await generate_ai_summary_for_act(db, act, updater_user_id)


async def update_scene_with_ai_summary(
    db: AsyncSession,
    scene_id: int,
    updater_user_id: int
) -> Optional[str]:
    """
    Convenience function to fetch a scene and generate/update its AI summary.
    
    Args:
        db: Database session
        scene_id: ID of the scene to update
        updater_user_id: ID of the user performing the update
        
    Returns:
        The generated summary text, or None if generation failed
    """
    from app.crud.scene import get_scene
    
    scene = await get_scene(db, scene_id=scene_id)
    if not scene:
        logger.error(f"Scene {scene_id} not found")
        return None
        
    return await generate_ai_summary_for_scene(db, scene, updater_user_id)