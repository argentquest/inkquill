# /ai_rag_story_app/app/routers/views_world_chat.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db_session
from app.models.user import User
from app.crud import world as world_crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/ui/world-chat/{world_id}", response_class=HTMLResponse, name="ui_world_chat")
async def world_chat_page(
    request: Request,
    world_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """World chat page"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"World chat page requested for world_id={world_id}, user_id={current_user.id}")
        
        # Verify user owns the world
        world = await world_crud.get_world_for_user(db, world_id, current_user.id)
        logger.info(f"World query result: {world}")
        
        if not world:
            logger.warning(f"World {world_id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found"
            )
        
        logger.info(f"Rendering world_chat.html template for world: {world.name}")
        
        return templates.TemplateResponse(
            "pages/world_chat.html",
            {
                "request": request,
                "current_user": current_user,
                "world": world
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in world chat page: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load world chat page: {str(e)}"
        )