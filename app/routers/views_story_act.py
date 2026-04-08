"""API routes for views story act."""

# /story_app/app/routers/views_story_act.py

from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.core import security as core_security 
from app.crud import user as crud_user
from app.core.storage_deps import LocalStorageClient, get_blob_service_client
from app.core.storage_deps import LocalStorageClient
from app.models.user import User
from app.models.story import Story
from app.models.act import Act
from app.models.scene import Scene
from app.models.prompt import PromptTypeEnum, Prompt as ModelPrompt
from app.models.world import World as ModelWorld
from app.schemas.story import StoryRead
from app.schemas.base import ApiResponse
from app.schemas.character import CharacterInStoryRead
from app.schemas.location import LocationInStoryRead
from app.schemas.lore_item import LoreItemInStoryRead
from app.crud import story as crud_story
from app.crud import act as crud_act
from app.crud import scene as crud_scene
from app.crud import prompt as crud_prompt
from app.crud import world as crud_world
from app.crud import character as crud_character
from app.crud import location as crud_location
from app.crud import lore_item as crud_lore_item
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ui",
    tags=["ui-story-act-scene-views"]
)

templates = Jinja2Templates(directory="app/templates")

# --- HELPER FUNCTIONS ---

async def get_optional_current_user_for_story_views(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Get current user for story views, return None if not authenticated."""
    token = request.cookies.get("access_token")
    if not token:
        logger.debug("No access_token cookie found in request for story views.")
        return None
    try:
        payload: Optional[Dict[str, Any]] = await core_security.decode_access_token(token=token)
        if payload is None:
            logger.warning("Token decoding returned None for story views.")
            return None
        username_from_payload: Optional[str] = payload.get("sub")
        if username_from_payload is None:
            logger.warning("Username (sub) not found in token payload for story views.")
            return None
    except core_security.JWTError as e: 
        logger.warning(f"JWTError during token decoding in story views: {str(e)}")
        return None
    except Exception as e_unhandled: 
        logger.error(f"Unexpected error processing token in story views: {e_unhandled}", exc_info=True)
        return None
    
    user = await crud_user.get_user_by_username(db, username=username_from_payload)
    if user is None:
        logger.warning(f"User '{username_from_payload}' from token not found in DB for story views.")
        return None
    if not user.is_active: 
        logger.info(f"User '{user.username}' is inactive, treating as no current user for story views.")
        return None
    logger.debug(f"User '{user.username}' successfully retrieved for story views.")
    return user
async def _check_and_get_image_url(blob_service_client: LocalStorageClient, blob_path: Optional[str]) -> Optional[str]:
    """Provide internal router support for check and get image url."""
    if not blob_path:
        return None
    try:
        blob_client = blob_service_client.get_blob_client(container="generated-images", blob=blob_path)
        if await blob_client.exists():
            return blob_client.url
    except Exception as e:
        logger.warning(f"Could not check for blob '{blob_path}' due to error: {e}")
    return None

# --- Story UI Page Endpoints ---
@router.get("/stories", response_class=HTMLResponse, name="ui_list_stories")
async def list_stories_ui(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user_for_story_views),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /stories."""
    if current_user:
        logger.info(f"User {current_user.username} accessing their stories list.")
        stories_db = await crud_story.get_stories_by_user(db, user_id=current_user.id)
        
        stories_for_template = []
        for story_item in stories_db:
            story_read = StoryRead.model_validate(story_item)
            path_to_check = story_item.current_image.blob_path if story_item.current_image else story_item.image_blob_path
            story_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
            stories_for_template.append(story_read)
    else:
        # Check for anonymous user session
        anon_user_id = request.cookies.get("anon_user_id")
        if anon_user_id:
            try:
                # Get anonymous user
                from app.services.anonymous_user_service import anonymous_user_service
                existing_user = await db.execute(
                    select(User).where(User.id == int(anon_user_id))
                )
                anon_user = existing_user.scalar_one_or_none()
                
                if anon_user and await anonymous_user_service.is_anonymous_user(anon_user):
                    logger.info(f"Anonymous user {anon_user.username} accessing their stories list.")
                    stories_db = await crud_story.get_stories_by_user(db, user_id=anon_user.id)
                    
                    stories_for_template = []
                    for story_item in stories_db:
                        story_read = StoryRead.model_validate(story_item)
                        path_to_check = story_item.current_image.blob_path if story_item.current_image else story_item.image_blob_path
                        story_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
                        stories_for_template.append(story_read)
                    
                    # Set current_user to the anonymous user for template consistency
                    current_user = anon_user
                else:
                    # Invalid anonymous session, show empty list
                    logger.info("Invalid anonymous session, showing empty stories list.")
                    stories_for_template = []
            except (ValueError, Exception) as e:
                # Error getting anonymous user, show empty list
                logger.warning(f"Error getting anonymous user: {e}")
                stories_for_template = []
        else:
            logger.info("No user session found, showing empty stories list.")
            # For users without any session, show empty list
            stories_for_template = []
    
    return templates.TemplateResponse(
        "pages/stories_list.html",
        {"request": request, "stories": stories_for_template, "current_user": current_user}
    )

@router.get("/stories/new", response_class=HTMLResponse, name="ui_create_story_form_generic")
async def create_story_ui_form_generic(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user_for_story_views)
):
    # Redirect anonymous users to register page
    """Handle GET /stories/new."""
    if current_user is None:
        register_url = str(request.url_for('ui_register_form'))
        return RedirectResponse(url=register_url, status_code=status.HTTP_302_FOUND)
    
    logger.info(f"User {current_user.username} accessing generic create new story form.")
    available_worlds = await crud_world.get_worlds_by_user(db, user_id=current_user.id)
    if not available_worlds:
        logger.warning(f"User {current_user.username} has no worlds to associate with a new story. Showing error on form.")
        return templates.TemplateResponse(
            "pages/story_form.html",
            {
                "request": request, "story": None, "current_user": current_user,
                "project_name": settings.APP_PROJECT_NAME,
                "form_action_url": request.url_for('create_new_story'), 
                "pre_selected_world_id": None, "world_for_story_form": None,
                "available_worlds_for_story_form": [], "no_worlds_exist_error": True
            }
        )
    return templates.TemplateResponse(
        "pages/story_form.html",
        {
            "request": request, "story": None, "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "form_action_url": request.url_for('create_new_story'), 
            "pre_selected_world_id": None, "world_for_story_form": None,
            "available_worlds_for_story_form": available_worlds, "no_worlds_exist_error": False
        }
    )

@router.get("/stories/basic/new", response_class=HTMLResponse, name="ui_create_basic_story_form")
async def create_basic_story_ui_form(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user_for_story_views)
):
    """Display the Basic Story creation form"""
    if current_user:
        logger.info(f"User {current_user.username} accessing Basic Story creation form.")
    else:
        # Check for anonymous user session to show proper user info
        anon_user_id = request.cookies.get("anon_user_id")
        if anon_user_id:
            try:
                from app.services.anonymous_user_service import anonymous_user_service
                existing_user = await db.execute(
                    select(User).where(User.id == int(anon_user_id))
                )
                anon_user = existing_user.scalar_one_or_none()
                
                if anon_user and await anonymous_user_service.is_anonymous_user(anon_user):
                    current_user = anon_user
                    logger.info(f"Anonymous user {anon_user.username} accessing Basic Story creation form.")
                else:
                    logger.info("Anonymous user (no valid session) accessing Basic Story creation form.")
            except (ValueError, Exception):
                logger.info("Anonymous user (invalid session) accessing Basic Story creation form.")
        else:
            logger.info("Anonymous user (no session) accessing Basic Story creation form.")
    
    return templates.TemplateResponse(
        "pages/basic_story_form.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.get("/stories/basic/quick-start", name="ui_quick_start_basic_story")
async def quick_start_basic_story(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user_for_story_views)
):
    """Create a basic story with 'Untitled' title and redirect to editor"""
    try:
        if current_user:
            logger.info(f"User {current_user.username} quick-starting a basic story.")
        else:
            logger.info("Anonymous user quick-starting a basic story.")
            # For the quick-start, we need to redirect to login or create anonymous user
            # Since this is a GET request that redirects, let's redirect to the form instead
            return RedirectResponse(
                url=request.url_for('ui_create_basic_story_form'),
                status_code=status.HTTP_302_FOUND
            )
        
        # Import necessary services
        from app.services.story_service import story_service, BasicStoryCreate
        
        # Create Basic Story with "Untitled" title
        story_data = BasicStoryCreate(
            title="Untitled",
            short_description=None
        )
        
        story, first_act = await story_service.create_basic_story(
            db=db,
            story_data=story_data,
            user=current_user
        )
        
        # Commit the transaction
        await db.commit()
        
        logger.info(f"Quick-start basic story created: {story.id} with first act: {first_act.id}")
        
        # Redirect to the basic story editor
        return RedirectResponse(
            url=request.url_for('ui_edit_basic_story_acts', story_id=story.id),
            status_code=status.HTTP_302_FOUND
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to quick-start Basic Story: {e}")
        # Redirect to the form if there's an error
        return RedirectResponse(
            url=request.url_for('ui_create_basic_story_form'),
            status_code=status.HTTP_302_FOUND
        )

@router.get("/worlds/{world_id}/stories/new", response_class=HTMLResponse, name="ui_create_story_for_world_form")
async def create_story_for_world_ui_form(
    request: Request,
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /worlds/{world_id}/stories/new."""
    logger.info(f"User {current_user.username} accessing create new story form FOR world ID: {world_id}")
    db_world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not db_world:
        raise HTTPException(status_code=404, detail="Target world not found or not accessible.")
    available_worlds = await crud_world.get_worlds_by_user(db, user_id=current_user.id)
    return templates.TemplateResponse(
        "pages/story_form.html",
        {
            "request": request, "story": None, "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "form_action_url": request.url_for('create_new_story'),
            "pre_selected_world_id": db_world.id, "world_for_story_form": db_world,
            "available_worlds_for_story_form": available_worlds, "no_worlds_exist_error": False
        }
    )

@router.get("/stories/{story_id}", response_class=HTMLResponse, name="ui_story_detail")
async def story_detail_ui(
    request: Request,
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /stories/{story_id}."""
    logger.info(f"User {current_user.username} viewing details for story ID: {story_id}")
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible")
    
    acts = await crud_act.get_acts_by_story(db, story_id=story.id)
    
    # Get act-level associations
    from app.models.act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
    from app.models.character import Character
    from app.models.location import Location
    from app.models.lore_item import LoreItem
    from sqlalchemy.orm import selectinload
    
    # Fetch act associations with elements
    act_associations = {}
    for act in acts:
        # Characters in this act
        char_result = await db.execute(
            select(ActCharacterAssociation, Character)
            .join(Character)
            .where(ActCharacterAssociation.act_id == act.id)
        )
        act_chars = [{"character": char, "roles": assoc.roles} for assoc, char in char_result.fetchall()]
        
        # Locations in this act
        loc_result = await db.execute(
            select(ActLocationAssociation, Location)
            .join(Location)
            .where(ActLocationAssociation.act_id == act.id)
        )
        act_locs = [{"location": loc, "roles": assoc.roles} for assoc, loc in loc_result.fetchall()]
        
        # Lore items in this act
        lore_result = await db.execute(
            select(ActLoreItemAssociation, LoreItem)
            .join(LoreItem)
            .where(ActLoreItemAssociation.act_id == act.id)
        )
        act_lore = [{"lore_item": lore, "roles": assoc.roles} for assoc, lore in lore_result.fetchall()]
        
        act_associations[act.id] = {
            "characters": act_chars,
            "locations": act_locs,
            "lore_items": act_lore
        }
    
    linked_characters_raw = await crud_character.get_characters_for_story(db, story_id=story.id)
    linked_locations_raw = await crud_location.get_locations_for_story(db, story_id=story.id)
    linked_lore_items_raw = await crud_lore_item.get_lore_items_for_story(db, story_id=story.id)

    characters_for_template = []
    for char_data in linked_characters_raw:
        char_obj = char_data.get("character")
        if not char_obj: continue
        char_read = CharacterInStoryRead.model_validate(char_obj)
        char_read.role_in_story = char_data.get('role_in_story')
        path_to_check = char_obj.current_image.blob_path if char_obj.current_image else char_obj.image_blob_path
        char_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        characters_for_template.append(char_read)

    locations_for_template = []
    for loc_data in linked_locations_raw:
        loc_obj = loc_data.get("location")
        if not loc_obj: continue
        loc_read = LocationInStoryRead.model_validate(loc_obj)
        loc_read.significance_to_story = loc_data.get('significance_to_story')
        path_to_check = loc_obj.current_image.blob_path if loc_obj.current_image else loc_obj.image_blob_path
        loc_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        locations_for_template.append(loc_read)

    lore_for_template = []
    for lore_data in linked_lore_items_raw:
        lore_obj = lore_data.get("lore_item")
        if not lore_obj: continue
        lore_read = LoreItemInStoryRead.model_validate(lore_obj)
        lore_read.relevance_to_story = lore_data.get('relevance_to_story')
        path_to_check = lore_obj.current_image.blob_path if lore_obj.current_image else lore_obj.image_blob_path
        lore_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        lore_for_template.append(lore_read)
    
    return templates.TemplateResponse(
        "pages/story_detail.html",
        {
            "request": request, "story": story, "acts": acts, "current_user": current_user,
            "linked_characters": characters_for_template,
            "linked_locations": locations_for_template,
            "linked_lore_items": lore_for_template,
            "act_associations": act_associations
        }
    )

@router.get("/stories/{story_id}/edit", response_class=HTMLResponse, name="ui_edit_story_form")
async def edit_story_ui_form(
    request: Request,
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /stories/{story_id}/edit."""
    logger.info(f"User {current_user.username} accessing edit form for story ID: {story_id}")
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible")
    
    path_to_check = story.current_image.blob_path if story.current_image else story.image_blob_path
    image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    available_worlds = await crud_world.get_worlds_by_user(db, user_id=current_user.id)
    world_for_story_form = None
    if story.world_id:
        world_for_story_form = await crud_world.get_world_for_user(db, world_id=story.world_id, user_id=current_user.id)
        if not world_for_story_form:
             logger.error(f"Data integrity concern: Story ID {story.id} has world_id {story.world_id}, but world not found/accessible for user {current_user.username}.")
    return templates.TemplateResponse(
        "pages/story_form.html",
        {
            "request": request, "story": story, "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "form_action_url": request.url_for('update_existing_story', story_id=story.id),
            "available_worlds_for_story_form": available_worlds,
            "pre_selected_world_id": story.world_id,
            "world_for_story_form": world_for_story_form,
            "no_worlds_exist_error": not available_worlds and not story.world_id,
            "image_url": image_url
        }
    )

@router.get("/stories/basic/{story_id}/editor", response_class=HTMLResponse, name="ui_basic_story_editor")
async def basic_story_editor_ui(
    request: Request,
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user_for_story_views)
):
    """Basic Story editor UI - Simplified writing interface for Basic Stories"""
    if current_user:
        logger.info(f"User {current_user.username} accessing Basic Story editor for story ID: {story_id}")
    else:
        logger.info(f"Anonymous user accessing Basic Story editor for story ID: {story_id}")
    
    try:
        # Handle anonymous users - they need to have the story associated with their session
        if current_user is None:
            # For anonymous users, we need to get their user from cookies
            from app.services.anonymous_user_service import anonymous_user_service
            from sqlalchemy import select
            
            anon_user_id = request.cookies.get("anon_user_id")
            if not anon_user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Anonymous session not found. Please create a new story."
                )
            
            try:
                # Get anonymous user
                existing_user = await db.execute(
                    select(User).where(User.id == int(anon_user_id))
                )
                current_user = existing_user.scalar_one_or_none()
                
                if not current_user or not await anonymous_user_service.is_anonymous_user(current_user):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid anonymous session. Please create a new story."
                    )
            except (ValueError, Exception):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid anonymous session. Please create a new story."
                )
        
        # Get and validate story
        story = await crud_story.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Verify it's a Basic Story
        if story.story_type != 'basic':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This editor is for Basic Stories only"
            )
        
        # Get the first act (Basic Stories only have one act)
        acts = await crud_act.get_acts_by_story(db, story_id)
        if not acts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No acts found for this story"
            )
        
        first_act = acts[0]  # Acts are ordered by act_number
        
        return templates.TemplateResponse(
            "pages/basic_story_editor.html",
            {
                "request": request,
                "story": story,
                "act": first_act,
                "current_user": current_user,
                "project_name": settings.APP_PROJECT_NAME
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load Basic Story editor for story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load story editor"
        )

# --- Act UI Page Endpoints ---
@router.get("/stories/{story_id}/acts/new", response_class=HTMLResponse, name="ui_create_act_form")
async def create_act_ui_form(
    request: Request,
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /stories/{story_id}/acts/new."""
    story_check = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible to create an act for.")

    user_system_prompts = await crud_prompt.get_prompts_by_user(db,user_id=current_user.id,prompt_type=PromptTypeEnum.SYSTEM,is_active=True)
    shared_system_prompts = await crud_prompt.get_shared_prompts(db,prompt_type=PromptTypeEnum.SYSTEM,is_active=True)
    combined_prompts_dict: Dict[int, ModelPrompt]={p.id:p for p in user_system_prompts}
    for p_shared in shared_system_prompts:
        if p_shared.id not in combined_prompts_dict:
            combined_prompts_dict[p_shared.id] = p_shared
    available_system_prompts=sorted(list(combined_prompts_dict.values()),key=lambda p_sort:p_sort.title)

    return templates.TemplateResponse(
        "pages/act_form.html",
        {
            "request":request,"act":None,"story_id":story_id,"story":story_check,
            "current_user":current_user,"project_name":settings.APP_PROJECT_NAME,
            "form_action_url":request.url_for('create_new_act_for_story',story_id=story_id), 
            "available_system_prompts":available_system_prompts
        }
    )

@router.get("/acts/{act_id}/edit", response_class=HTMLResponse, name="ui_edit_act_form")
async def edit_act_ui_form(
    request: Request,
    act_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /acts/{act_id}/edit."""
    act = await crud_act.get_act(db, act_id=act_id) 
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this act (story ownership).")

    user_system_prompts = await crud_prompt.get_prompts_by_user(db,user_id=current_user.id,prompt_type=PromptTypeEnum.SYSTEM,is_active=True)
    shared_system_prompts = await crud_prompt.get_shared_prompts(db,prompt_type=PromptTypeEnum.SYSTEM,is_active=True)
    combined_prompts_dict: Dict[int, ModelPrompt]={p.id:p for p in user_system_prompts}
    for p_shared in shared_system_prompts:
        if p_shared.id not in combined_prompts_dict:
            combined_prompts_dict[p_shared.id] = p_shared
    available_system_prompts=sorted(list(combined_prompts_dict.values()),key=lambda p_sort:p_sort.title)

    return templates.TemplateResponse(
        "pages/act_form.html",
        {
            "request":request,"act":act,"story_id":act.story_id,"story":story,
            "current_user":current_user,"project_name":settings.APP_PROJECT_NAME,
            "form_action_url":request.url_for('update_existing_act',act_id=act.id), 
            "available_system_prompts":available_system_prompts
        }
    )

@router.get("/stories/{story_id}/acts/{act_id}/edit-content", response_class=HTMLResponse, name="ui_act_editor")
async def act_editor_ui(
    request: Request,
    story_id: int,
    act_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /stories/{story_id}/acts/{act_id}/edit-content."""
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible.")
    act = await crud_act.get_act(db, act_id=act_id) 
    if not act or act.story_id != story.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found for this story.")

    user_system_prompts = await crud_prompt.get_prompts_by_user(db,user_id=current_user.id,prompt_type=PromptTypeEnum.SYSTEM,is_active=True)
    shared_system_prompts = await crud_prompt.get_shared_prompts(db,prompt_type=PromptTypeEnum.SYSTEM,is_active=True)
    combined_prompts_dict: Dict[int, ModelPrompt]={p.id:p for p in user_system_prompts}
    for p_shared in shared_system_prompts:
        if p_shared.id not in combined_prompts_dict:
            combined_prompts_dict[p_shared.id] = p_shared
    available_system_prompts_for_editor=sorted(list(combined_prompts_dict.values()),key=lambda p_sort:p_sort.title)

    story_world = None
    world_characters: List[Any] = [] 
    world_locations: List[Any] = []
    world_lore_items: List[Any] = []

    if story.world_id:
        story_world = await crud_world.get_world_for_user(db, world_id=story.world_id, user_id=current_user.id)
        if story_world: 
            world_characters = await crud_character.get_characters_by_world(db, world_id=story.world_id, limit=500)
            world_locations = await crud_location.get_locations_by_world(db, world_id=story.world_id, limit=500)
            world_lore_items = await crud_lore_item.get_lore_items_by_world(db, world_id=story.world_id, limit=500)
        else:
            logger.warning(f"User {current_user.username} accessing act editor for story {story.id}, but world {story.world_id} not found or not owned by user.")
            story_world = None 

    return templates.TemplateResponse(
        "pages/act_editor_ui.html",
        {
            "request":request,"story":story,"act":act,"current_user":current_user,
            "project_name":settings.APP_PROJECT_NAME,
            "available_system_prompts":available_system_prompts_for_editor,
            "story_world": story_world,
            "world_characters": world_characters,
            "world_locations": world_locations,
            "world_lore_items": world_lore_items,
        }
    )

@router.get("/stories/{story_id}/acts/{act_id}/ai-review", response_class=HTMLResponse, name="ui_act_ai_review")
async def act_ai_review_ui(
    request: Request,
    story_id: int,
    act_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /stories/{story_id}/acts/{act_id}/ai-review."""
    logger.info(f"User '{current_user.username}' accessing AI Review page for Story ID: {story_id}, Act ID: {act_id}")

    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        logger.warning(f"AI Review page: Story {story_id} not found or not accessible by user {current_user.username}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible.")

    act = await crud_act.get_act(db, act_id=act_id) 
    if not act or act.story_id != story.id:
        logger.warning(f"AI Review page: Act {act_id} not found for story {story_id} for user {current_user.username}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found for this story.")

    logger.info(f"AI Review UI (views_story_act.py): Act ID {act.id}, Description length: {len(act.description) if act.description else 'None/Empty'}")
    logger.debug(f"AI Review UI (views_story_act.py): Act Description content (first 200 chars): '{act.description[:200] if act.description else ''}'")

    return templates.TemplateResponse(
        "pages/act_ai_review.html",
        {
            "request": request,
            "story": story,
            "act": act, 
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

# --- Scene UI Page Endpoints ---
@router.get("/stories/{story_id}/acts/{act_id}/scenes/new", response_class=HTMLResponse, name="ui_create_scene_form")
async def create_scene_ui_form(
    request: Request,
    story_id: int,
    act_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /stories/{story_id}/acts/{act_id}/scenes/new."""
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible.")
    act = await crud_act.get_act(db, act_id=act_id)
    if not act or act.story_id != story.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found for this story.")

    next_scene_number = await crud_scene.get_next_scene_number(db, act_id=act_id)

    user_system_prompts = await crud_prompt.get_prompts_by_user(db, user_id=current_user.id, prompt_type=PromptTypeEnum.SYSTEM, is_active=True)
    shared_system_prompts = await crud_prompt.get_shared_prompts(db, prompt_type=PromptTypeEnum.SYSTEM, is_active=True)
    combined_prompts_dict: Dict[int, ModelPrompt]={p.id:p for p in user_system_prompts}
    for p_shared in shared_system_prompts:
        if p_shared.id not in combined_prompts_dict:
            combined_prompts_dict[p_shared.id] = p_shared
    available_system_prompts_for_editor = sorted(list(combined_prompts_dict.values()), key=lambda p_sort: p_sort.title)

    return templates.TemplateResponse(
        "pages/scene_editor_ui.html",
        {
            "request":request, "scene":None, "act":act, "story":story,
            "current_user":current_user, "project_name":settings.APP_PROJECT_NAME,
            "suggested_scene_number":next_scene_number,
            "available_system_prompts": available_system_prompts_for_editor
        }
    )

@router.get("/scenes/{scene_id}/edit", response_class=HTMLResponse, name="ui_edit_scene_form")
async def edit_scene_ui_form(
    request: Request,
    scene_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /scenes/{scene_id}/edit."""
    logger.info(f"User {current_user.username} accessing edit form for Scene ID: {scene_id}")

    scene = await crud_scene.get_scene(db, scene_id=scene_id)
    if not scene:
        logger.warning(f"Scene ID {scene_id} not found for editing by user {current_user.username}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")

    if not scene.act:
        logger.error(f"Scene ID {scene.id} is orphaned (no parent act). Data integrity issue.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Scene data is inconsistent (missing parent act).")

    act = scene.act
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        logger.warning(f"User {current_user.username} attempted to edit scene ID {scene_id}, but does not own the parent story (Story ID {act.story_id}).")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this scene (story ownership).")

    user_system_prompts = await crud_prompt.get_prompts_by_user(db, user_id=current_user.id, prompt_type=PromptTypeEnum.SYSTEM, is_active=True)
    shared_system_prompts = await crud_prompt.get_shared_prompts(db, prompt_type=PromptTypeEnum.SYSTEM, is_active=True)
    combined_system_prompts_dict: Dict[int, ModelPrompt] = {p.id: p for p in user_system_prompts}
    for p_shared in shared_system_prompts:
        if p_shared.id not in combined_system_prompts_dict:
            combined_system_prompts_dict[p_shared.id] = p_shared
    available_system_prompts_for_editor = sorted(list(combined_system_prompts_dict.values()), key=lambda p_sort: p_sort.title)

    return templates.TemplateResponse(
        "pages/scene_editor_ui.html",
        {
            "request": request,
            "scene": scene,
            "act": act,
            "story": story,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "available_system_prompts": available_system_prompts_for_editor,
            "suggested_scene_number": scene.scene_number 
        }
    )

