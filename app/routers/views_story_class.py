# /ai_rag_story_app/app/routers/views_story_class.py

from fastapi import APIRouter, Depends, Request, Query, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.crud import world as crud_world
from app.crud import story as crud_story
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ui/story-classes",
    tags=["story-classes-ui"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, name="story_classes_list_ui")
async def story_classes_list_ui(
    request: Request,
    world_id: Optional[int] = Query(None, description="World ID to show story classes for"),
    story_id: Optional[int] = Query(None, description="Story ID to get world context from"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Story classes management page."""
    logger.info(f"User '{current_user.username}' accessing story classes management page")
    
    # Determine world context and get world info
    world = None
    context_info = ""
    
    if world_id is not None:
        # Direct world context
        world = await crud_world.get_world_for_user(db=db, world_id=world_id, user_id=current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found or access denied"
            )
        context_info = f"for {world.name}"
        
    elif story_id is not None:
        # Get world from story context
        story = await crud_story.get_story_for_user(db=db, story_id=story_id, user_id=current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found or access denied"
            )
        world = story.world
        world_id = story.world_id
        context_info = f"for {world.name} (from story '{story.title}')"
        
    else:
        # No context provided, use user's first world
        user_worlds = await crud_world.get_worlds_by_user(db=db, user_id=current_user.id, limit=1)
        if user_worlds:
            world = user_worlds[0]
            world_id = world.id
            context_info = f"for {world.name} (default world)"
        else:
            context_info = "No world context available"
    
    return templates.TemplateResponse(
        "pages/story_class_list.html",
        {
            "request": request,
            "current_user": current_user,
            "world": world,
            "world_id": world_id,
            "story_id": story_id,
            "context_info": context_info,
            "project_name": settings.APP_PROJECT_NAME,
            "page_title": f"Story Classes {context_info}" if context_info else "Story Classes"
        }
    )