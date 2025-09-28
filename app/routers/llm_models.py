# /ai_rag_story_app/app/routers/llm_models.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db_session, get_current_user
from app.schemas.llm_models import LLMModelsResponse, LLMModelRead
from app.crud import llm_models as crud_llm_models
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm-models", tags=["LLM Models"])


@router.get("/", response_model=LLMModelsResponse)
async def get_llm_models(
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get all LLM model configurations.
    
    This endpoint is public and doesn't require authentication,
    but logged-in users may see additional information.
    """
    try:
        # Get all models
        models = await crud_llm_models.get_all_model_configurations(db)
        
        # Get statistics
        stats = await crud_llm_models.get_model_statistics(db)
        
        # Convert to response schema
        model_reads = [
            LLMModelRead.model_validate(model) for model in models
        ]
        
        return LLMModelsResponse(
            models=model_reads,
            total_count=stats["total_count"],
            active_count=stats["active_count"],
            providers=stats["providers"]
        )
        
    except Exception as e:
        logger.error(f"Error fetching LLM models: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch LLM models")