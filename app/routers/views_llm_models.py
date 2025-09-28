# /ai_rag_story_app/app/routers/views_llm_models.py
import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.crud import llm_models as crud_llm_models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui/llm-models", tags=["UI LLM Models"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="ui_llm_models")
async def view_llm_models(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Display all available LLM models in a grid view"""
    try:
        # Get all models
        models = await crud_llm_models.get_all_model_configurations(db)
        
        # Get statistics
        stats = await crud_llm_models.get_model_statistics(db)
        
        # Group models by provider
        models_by_provider = {}
        for model in models:
            provider = model.provider.value
            if provider not in models_by_provider:
                models_by_provider[provider] = []
            models_by_provider[provider].append(model)
        
        return templates.TemplateResponse(
            "llm_models/llm_models_grid.html",
            {
                "request": request,
                "current_user": current_user,
                "models_by_provider": models_by_provider,
                "total_count": stats["total_count"],
                "active_count": stats["active_count"],
                "providers": stats["providers"]
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading LLM models page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "current_user": current_user,
                "error_message": "Failed to load LLM models"
            }
        )