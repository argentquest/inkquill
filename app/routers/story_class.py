# /ai_rag_story_app/app/routers/story_class.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.schemas.story_class import StoryClassCreate, StoryClassUpdate, StoryClass, StoryClassOption
from app.schemas.base import ApiResponse
from app.crud import story_class as crud_story_class
from app.crud import world as crud_world
from app.crud import story as crud_story

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/story-classes",
    tags=["story-classes"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_story_class(
    *,
    db: AsyncSession = Depends(get_db_session),
    story_class_in: StoryClassCreate,
    world_id: Optional[int] = Query(None, description="World ID to create story class for"),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new story class for a world."""
    # If no world_id provided, use user's first world
    if world_id is None:
        user_worlds = await crud_world.get_worlds_by_user(db=db, user_id=current_user.id, limit=1)
        if not user_worlds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No worlds found. Please create a world first."
            )
        world_id = user_worlds[0].id
    else:
        # Verify user owns the specified world
        world = await crud_world.get_world_for_user(db=db, world_id=world_id, user_id=current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found or access denied"
            )
    
    logger.info(f"User '{current_user.username}' creating story class: {story_class_in.name} for world ID: {world_id}")
    
    story_class = await crud_story_class.create_story_class(
        db=db, story_class_in=story_class_in, world_id=world_id
    )
    await db.commit()
    
    logger.info(f"Story class ID {story_class.id} created successfully for world ID {world_id}")
    return story_class


@router.get("/", response_model=ApiResponse)
async def list_story_classes(
    *,
    db: AsyncSession = Depends(get_db_session),
    world_id: Optional[int] = Query(None, description="World ID to get story classes for"),
    story_id: Optional[int] = Query(None, description="Story ID to get world context from"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """Get all story classes for a world."""
    # Determine world_id from context
    if world_id is None and story_id is not None:
        # Get world_id from story context
        story = await crud_story.get_story_for_user(db=db, story_id=story_id, user_id=current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found or access denied"
            )
        world_id = story.world_id
    elif world_id is None:
        # No context provided, use user's first world
        user_worlds = await crud_world.get_worlds_by_user(db=db, user_id=current_user.id, limit=1)
        if not user_worlds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No worlds found. Please create a world first."
            )
        world_id = user_worlds[0].id
    else:
        # Verify user owns the specified world
        world = await crud_world.get_world_for_user(db=db, world_id=world_id, user_id=current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found or access denied"
            )
    
    logger.info(f"User '{current_user.username}' fetching story classes for world ID: {world_id} (skip: {skip}, limit: {limit})")
    
    story_classes = await crud_story_class.get_story_classes_by_world(
        db=db, world_id=world_id, skip=skip, limit=limit
    )
    
    # If no classes exist, create defaults
    if not story_classes:
        logger.info(f"No story classes found for world ID: {world_id}, creating defaults")
        story_classes = await crud_story_class.get_default_story_classes_for_world(
            db=db, world_id=world_id
        )
    
    logger.info(f"Returning {len(story_classes)} story classes for world ID: {world_id}")
    return story_classes


@router.get("/options", response_model=ApiResponse)
async def list_story_class_options(
    *,
    db: AsyncSession = Depends(get_db_session),
    world_id: Optional[int] = Query(None, description="World ID to get story class options for"),
    current_user: User = Depends(get_current_active_user)
):
    """Get story class options for dropdowns/selectors."""
    # If no world_id provided, use user's first world
    if world_id is None:
        user_worlds = await crud_world.get_worlds_by_user(db=db, user_id=current_user.id, limit=1)
        if not user_worlds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No worlds found. Please create a world first."
            )
        world_id = user_worlds[0].id
    else:
        # Verify user owns the specified world
        world = await crud_world.get_world_for_user(db=db, world_id=world_id, user_id=current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found or access denied"
            )
    
    logger.info(f"User '{current_user.username}' fetching story class options for world ID: {world_id}")
    
    story_classes = await crud_story_class.get_story_classes_by_world(
        db=db, world_id=world_id, limit=100
    )
    
    # If no classes exist, create defaults
    if not story_classes:
        logger.info(f"No story classes found for world ID: {world_id}, creating defaults")
        story_classes = await crud_story_class.get_default_story_classes_for_world(
            db=db, world_id=world_id
        )
    
    options = [
        StoryClassOption(
            id=sc.id,
            name=sc.name,
            color=sc.color,
            description=sc.description
        )
        for sc in story_classes
    ]
    
    logger.info(f"Returning {len(options)} story class options for world ID: {world_id}")
    return options


@router.get("/{story_class_id}", response_model=ApiResponse)
async def get_story_class(
    *,
    db: AsyncSession = Depends(get_db_session),
    story_class_id: int,
    world_id: Optional[int] = Query(None, description="World ID to verify story class belongs to"),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific story class by ID."""
    logger.info(f"User '{current_user.username}' fetching story class ID: {story_class_id}")
    
    # Get the story class first
    story_class = await crud_story_class.get_story_class(db=db, story_class_id=story_class_id)
    
    if not story_class:
        logger.warning(f"Story class ID {story_class_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story class not found"
        )
    
    # Verify user owns the world that contains this story class
    world = await crud_world.get_world_for_user(db=db, world_id=story_class.world_id, user_id=current_user.id)
    if not world:
        logger.warning(f"Story class ID {story_class_id} belongs to world not owned by user '{current_user.username}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story class not found or access denied"
        )
    
    logger.info(f"Story class ID {story_class_id} found for user '{current_user.username}'")
    return story_class


@router.put("/{story_class_id}", response_model=ApiResponse)
async def update_story_class(
    *,
    db: AsyncSession = Depends(get_db_session),
    story_class_id: int,
    story_class_in: StoryClassUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a story class."""
    logger.info(f"User '{current_user.username}' updating story class ID: {story_class_id}")
    
    # Get the story class first
    story_class = await crud_story_class.get_story_class(db=db, story_class_id=story_class_id)
    
    if not story_class:
        logger.warning(f"Story class ID {story_class_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story class not found"
        )
    
    # Verify user owns the world that contains this story class
    world = await crud_world.get_world_for_user(db=db, world_id=story_class.world_id, user_id=current_user.id)
    if not world:
        logger.warning(f"Story class ID {story_class_id} belongs to world not owned by user '{current_user.username}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story class not found or access denied"
        )
    
    story_class = await crud_story_class.update_story_class(
        db=db, db_story_class=story_class, story_class_in=story_class_in
    )
    await db.commit()
    
    logger.info(f"Story class ID {story_class_id} updated successfully for user '{current_user.username}'")
    return story_class


@router.delete("/{story_class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story_class(
    *,
    db: AsyncSession = Depends(get_db_session),
    story_class_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a story class."""
    logger.info(f"User '{current_user.username}' deleting story class ID: {story_class_id}")
    
    # Get the story class first
    story_class = await crud_story_class.get_story_class(db=db, story_class_id=story_class_id)
    
    if not story_class:
        logger.warning(f"Story class ID {story_class_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story class not found"
        )
    
    # Verify user owns the world that contains this story class
    world = await crud_world.get_world_for_user(db=db, world_id=story_class.world_id, user_id=current_user.id)
    if not world:
        logger.warning(f"Story class ID {story_class_id} belongs to world not owned by user '{current_user.username}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story class not found or access denied"
        )
    
    await crud_story_class.delete_story_class(db=db, db_story_class=story_class)
    await db.commit()
    
    logger.info(f"Story class ID {story_class_id} deleted successfully for user '{current_user.username}'")
    return