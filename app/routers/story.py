# /ai_rag_story_app/app/routers/story.py

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
import sqlalchemy
from typing import List, Dict, Optional 
import logging
import re 
import uuid 
from pydantic import BaseModel
from html import escape 

# --- Azure SDK Imports ---
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings 
from azure.core.exceptions import AzureError, ResourceNotFoundError as AzureResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.core.azure_deps import get_blob_service_client 
from app.services.email_service import get_email_service
from app.models.user import User
from app.models.story import Story 
from app.models.published_story import PublishedStory
from app.schemas import story as schema_story
from app.crud import story as crud_story
from app.crud import act as crud_act
from app.crud import scene as crud_scene
from app.crud import character as crud_character
from app.crud import location as crud_location
from app.crud import lore_item as crud_lore_item 
from app.core.config import settings 

logger = logging.getLogger(__name__)

async def check_story_completion_milestone(db: AsyncSession, story_id: int) -> bool:
    """
    Check if a story has reached a completion milestone.
    Returns True if the story appears to be complete (has acts with substantial content).
    """
    try:
        # Get all acts for the story
        acts = await crud_act.get_acts_by_story(db, story_id=story_id, limit=1000)
        
        if not acts:
            return False
        
        # Check if story has at least one act with substantial content
        total_word_count = 0
        acts_with_content = 0
        
        for act in acts:
            # Count words in act description
            if act.description:
                total_word_count += len(act.description.split())
            
            # Get scenes for this act
            scenes = await crud_scene.get_scenes_by_act(db, act.id, limit=1000)
            act_has_content = False
            
            for scene in scenes:
                if scene.content:
                    scene_word_count = len(scene.content.split())
                    total_word_count += scene_word_count
                    if scene_word_count > 50:  # Scene has substantial content
                        act_has_content = True
                        
            if act_has_content:
                acts_with_content += 1
        
        # Consider story complete if:
        # - Has at least 1 act with substantial content
        # - Total word count is over 500 words
        # - OR has 3+ acts with any content
        is_complete = (
            (acts_with_content >= 1 and total_word_count >= 500) or
            (len(acts) >= 3 and total_word_count >= 200)
        )
        
        logger.info(f"Story {story_id} completion check: {acts_with_content} acts with content, {total_word_count} total words, {len(acts)} total acts -> Complete: {is_complete}")
        return is_complete
        
    except Exception as e:
        logger.error(f"Error checking story completion for story {story_id}: {e}")
        return False

router = APIRouter(
    prefix="/stories", 
    tags=["stories"],
    dependencies=[Depends(get_current_active_user)]
)

def sanitize_filename(name: str) -> str:
    """Removes or replaces characters not suitable for filenames."""
    name = str(name) 
    name = re.sub(r'[^\w\s.-]', '', name).strip() 
    name = re.sub(r'[-\s]+', '-', name) 
    return name if name else "untitled_story"

# --- Pydantic Response Model for the Publish Endpoint ---
class StoryPublishRequest(BaseModel):
    visibility: str = "public"  # "public" or "private"
    description: Optional[str] = None

class StoryPublishResponse(BaseModel): 
    message: str
    published_url: Optional[str] = None
    filename: Optional[str] = None
    status: str = "published"

# --- API Endpoint Definitions ---

@router.post("/", response_model=schema_story.StoryRead, status_code=status.HTTP_201_CREATED, name="create_new_story", summary="Create a new story for the authenticated user.")
async def create_new_story(
    story: schema_story.StoryCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' (ID: {current_user.id}) creating new story: '{story.title}' (type: {story.story_type})")
    try:
        from app.crud import world as crud_world
        from app.schemas.world import WorldCreate
        
        # If creating an advanced story and no world_id is provided (or world_id is None/0), create a generic world first
        if story.story_type == 'advanced' and (story.world_id is None or story.world_id == 0):
            logger.info(f"Creating generic world for advanced story for user '{current_user.username}'")
            
            # Create a generic world with "Untitled World by [username]" naming
            world_name = f"Untitled World by {current_user.username}"
            world_data = WorldCreate(
                name=world_name,
                description="A generic world created for your advanced story. You can customize this world later.",
                short_description="Generic world for advanced storytelling",
                is_free_chat_enabled=False
            )
            
            created_world = await crud_world.create_world(db=db, world_in=world_data, user_id=current_user.id)
            logger.info(f"Generic world '{created_world.name}' (ID: {created_world.id}) created for story")
            
            # Update the story to use the newly created world
            story.world_id = created_world.id
        elif story.world_id is not None:
            # Validate that the provided world exists and belongs to the user
            existing_world = await crud_world.get_world_for_user(db=db, world_id=story.world_id, user_id=current_user.id)
            if not existing_world:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"World with ID {story.world_id} not found or you don't have access to it."
                )
            logger.info(f"Using existing world '{existing_world.name}' (ID: {existing_world.id}) for story")
        
        created_story = await crud_story.create_story(db=db, story=story, user_id=current_user.id)
        await db.commit()
        await db.refresh(created_story)
        logger.info(f"Story '{created_story.title}' (ID: {created_story.id}) created successfully for user ID: {current_user.id} with world_id: {created_story.world_id}")
        return created_story
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating story '{story.title}' for user '{current_user.username}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the story."
        )

@router.get("/", response_model=List[schema_story.StoryRead], name="list_user_stories", summary="List all stories for the authenticated user.")
async def list_user_stories(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination."),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return."),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' listing their stories (skip: {skip}, limit: {limit}).")
    stories = await crud_story.get_stories_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    logger.info(f"Found {len(stories)} stories for user '{current_user.username}'.")
    return stories

@router.get("/{story_id}", response_model=schema_story.StoryRead, name="get_single_story", summary="Get a specific story by ID.")
async def get_single_story(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' requesting story ID: {story_id}")
    db_story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if db_story is None:
        logger.warning(f"Story ID {story_id} not found or not accessible for user '{current_user.username}'.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or not accessible by the current user."
        )
    return db_story

@router.put("/{story_id}", response_model=schema_story.StoryRead, name="update_existing_story", summary="Update an existing story.")
async def update_existing_story(
    story_id: int,
    story_update: schema_story.StoryUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    email_service = Depends(get_email_service)
):
    # Capture username before try block to avoid lazy loading issues in exception handler
    username = current_user.username
    logger.info(f"User '{username}' attempting to update story ID: {story_id} with data: {story_update.model_dump(exclude_unset=True)}")
    try:
        updated_story = await crud_story.update_story(
            db=db, story_id=story_id, story_update=story_update, user_id=current_user.id
        )
        if updated_story is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible for update.")
        await db.commit()
        await db.refresh(updated_story)
        logger.info(f"Story ID {story_id} updated successfully by user '{username}'.")
        
        # Check if story has reached completion milestone
        if current_user.email:
            try:
                is_complete = await check_story_completion_milestone(db, story_id)
                if is_complete:
                    # Check if we've already sent a completion email for this story
                    # For now, we'll send the email - in the future, we could track sent emails
                    story_url = f"{settings.APP_URL}/ui/stories/{story_id}"
                    
                    email_sent = await email_service.send_story_completion_email(
                        user_email=current_user.email,
                        user_name=current_user.display_name or current_user.username,
                        story_title=updated_story.title or "Untitled Story",
                        milestone_type="completion",
                        story_url=story_url
                    )
                    
                    if email_sent:
                        logger.info(f"Story completion email sent successfully to {current_user.email} for story {story_id}")
                    else:
                        logger.warning(f"Failed to send story completion email to {current_user.email} for story {story_id}")
                        
            except Exception as e:
                logger.error(f"Error checking/sending story completion email: {e}")
                # Don't fail the update operation if email fails
        
        return updated_story
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating story ID {story_id} for user '{username}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the story."
        )

@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_story", summary="Delete an existing story.")
async def delete_existing_story(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    # Capture username before try block to avoid lazy loading issues in exception handler
    username = current_user.username
    logger.info(f"User '{username}' attempting to delete story ID: {story_id}")
    try:
        deleted_story = await crud_story.delete_story(db=db, story_id=story_id, user_id=current_user.id)
        if deleted_story is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible for deletion.")
        await db.commit()
        logger.info(f"Story ID {story_id} and its associated data deleted successfully by user '{username}'.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting story ID {story_id} for user '{username}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the story."
        )

# --- NEW PUBLISH STORY ENDPOINT ---
@router.post("/{story_id}/publish", response_model=StoryPublishResponse, name="publish_story_to_html", summary="Compile story acts into an HTML file and upload it.")
async def publish_story_to_html(
    story_id: int,
    request: StoryPublishRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    email_service = Depends(get_email_service)
):
    logger.info(f"User '{current_user.username}' attempting to publish story ID: {story_id}")
    logger.info(f"Publish request data: visibility={request.visibility}, description={request.description}")

    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible")

    acts = await crud_act.get_acts_by_story(db, story_id=story.id, limit=1000)
    if not acts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This story has no acts to publish.")

    html_parts = []
    html_parts.append(f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>{story.title.strip() if story.title else 'Untitled Story'}</title>")
    html_parts.append("<style>")
    html_parts.append("body{font-family: Georgia, serif; margin: 2em; line-height: 1.8; max-width: 800px; margin: 2em auto;}")
    html_parts.append("h1, h2, h3 {color: #333; font-family: 'Arial', sans-serif;}")
    html_parts.append("h1 {text-align: center; border-bottom: 2px solid #333; padding-bottom: 0.5em;}")
    html_parts.append("h2 {margin-top: 2em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em;}")
    html_parts.append("h3 {margin-top: 1.5em; font-style: italic; color: #666;}")
    html_parts.append(".story-description {font-style: italic; text-align: center; margin: 1.5em 0; color: #666;}")
    html_parts.append(".writer-intent {font-style: italic; color: #666; margin: 1em 0; padding: 0.5em; background: #f9f9f9; border-left: 3px solid #ccc;}")
    html_parts.append(".scene-content {margin: 1em 0; text-align: justify;}")
    html_parts.append(".act-section {margin: 2em 0;}")
    html_parts.append(".world-elements-section {margin: 2em 0; padding: 1em; background: #f9f9f9; border-radius: 5px;}")
    html_parts.append(".act-elements {margin: 1em 0; padding: 0.5em; background: #f0f0f0; border-radius: 3px; font-size: 0.9em;}")
    html_parts.append(".scene-elements {margin: 0.5em 0; padding: 0.5em; background: #e8e8e8; border-radius: 3px; font-size: 0.85em;}")
    html_parts.append("hr {margin: 2em 0; border: none; border-top: 2px solid #333;}")
    html_parts.append(".story-image {width: 256px; height: 256px; object-fit: cover; border-radius: 8px; margin: 1em auto; display: block; box-shadow: 0 2px 8px rgba(0,0,0,0.15);}")
    html_parts.append(".act-image {width: 256px; height: 256px; object-fit: cover; border-radius: 8px; margin: 1em 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15); float: right; margin-left: 1em;}")
    html_parts.append(".scene-image {width: 256px; height: 256px; object-fit: cover; border-radius: 8px; margin: 1em 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15); float: left; margin-right: 1em;}")
    html_parts.append(".clearfix::after {content: ''; display: table; clear: both;}")
    html_parts.append("</style>")
    html_parts.append(f"</head><body><article><h1>{escape(story.title.strip() if story.title else 'Untitled Story')}</h1>")
    
    if story.short_description:
        html_parts.append(f"<div class='story-description'>{escape(story.short_description.strip())}</div>")
    
    # Add story AI summary if it exists
    if story.ai_summary:
        html_parts.append(f"<div class='writer-intent'><strong>AI Summary:</strong> {story.ai_summary.strip()}</div>")
    
    # Add story image if available
    if hasattr(story, 'image_url') and story.image_url:
        html_parts.append(f"<img src='{escape(story.image_url)}' alt='Story image' class='story-image'>")
    
    # Get story-level associations
    from app.models.story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
    from app.models.act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
    from app.models.scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation
    from app.models.character import Character
    from app.models.location import Location
    from app.models.lore_item import LoreItem
    from sqlalchemy import select
    
    # Story-level character associations
    story_chars_result = await db.execute(
        select(StoryCharacterAssociation, Character)
        .join(Character)
        .where(StoryCharacterAssociation.story_id == story.id)
    )
    story_characters = [{
        "character": char, 
        "roles": assoc.roles
    } for assoc, char in story_chars_result.fetchall()]
    
    # Story-level location associations
    story_locs_result = await db.execute(
        select(StoryLocationAssociation, Location)
        .join(Location)
        .where(StoryLocationAssociation.story_id == story.id)
    )
    story_locations = [{
        "location": loc, 
        "roles": assoc.roles
    } for assoc, loc in story_locs_result.fetchall()]
    
    # Story-level lore item associations
    story_lore_result = await db.execute(
        select(StoryLoreItemAssociation, LoreItem)
        .join(LoreItem)
        .where(StoryLoreItemAssociation.story_id == story.id)
    )
    story_lore_items = [{
        "lore_item": lore, 
        "roles": assoc.roles
    } for assoc, lore in story_lore_result.fetchall()]
    
    # Add story-level world elements section
    if story_characters or story_locations or story_lore_items:
        html_parts.append("<div class='world-elements-section'>")
        html_parts.append("<h2>Story Elements</h2>")
        
        if story_characters:
            html_parts.append("<h3>Characters</h3>")
            for char_data in story_characters:
                char = char_data["character"]
                roles = char_data["roles"]
                roles_text = ", ".join(roles) if roles else "No specific role"
                html_parts.append(f"<p><strong>{escape(char.name)}</strong> - {escape(roles_text)}</p>")
        
        if story_locations:
            html_parts.append("<h3>Locations</h3>")
            for loc_data in story_locations:
                loc = loc_data["location"]
                roles = loc_data["roles"]
                roles_text = ", ".join(roles) if roles else "No specific significance"
                html_parts.append(f"<p><strong>{escape(loc.name)}</strong> - {escape(roles_text)}</p>")
        
        if story_lore_items:
            html_parts.append("<h3>Lore Items</h3>")
            for lore_data in story_lore_items:
                lore = lore_data["lore_item"]
                roles = lore_data["roles"]
                roles_text = ", ".join(roles) if roles else "No specific relevance"
                html_parts.append(f"<p><strong>{escape(lore.title)}</strong> - {escape(roles_text)}</p>")
        
        html_parts.append("</div>")
    
    # Include acts and their scenes
    for act in acts:
        html_parts.append(f"<div class='act-section clearfix'><hr><h2>Act {act.act_number}: {escape(act.title.strip() if act.title else 'Untitled Act')}</h2>")
        
        # Add act image if available
        if hasattr(act, 'image_url') and act.image_url:
            html_parts.append(f"<img src='{escape(act.image_url)}' alt='Act {act.act_number} image' class='act-image'>")
        
        # Add act description if it exists
        if act.description:
            html_parts.append(f"<div class='act-content'>{act.description}</div>")
        
        # Add act writer's summary if it exists
        if act.act_summary:
            html_parts.append(f"<div class='writer-intent'><strong>Writer's Intent:</strong> {act.act_summary.strip()}</div>")
        
        # Add act AI summary if it exists
        if act.ai_summary:
            html_parts.append(f"<div class='writer-intent'><strong>AI Summary:</strong> {act.ai_summary.strip()}</div>")
        
        # Get act-level associations
        act_chars_result = await db.execute(
            select(ActCharacterAssociation, Character)
            .join(Character)
            .where(ActCharacterAssociation.act_id == act.id)
        )
        act_characters = [{
            "character": char, 
            "roles": assoc.roles
        } for assoc, char in act_chars_result.fetchall()]
        
        act_locs_result = await db.execute(
            select(ActLocationAssociation, Location)
            .join(Location)
            .where(ActLocationAssociation.act_id == act.id)
        )
        act_locations = [{
            "location": loc, 
            "roles": assoc.roles
        } for assoc, loc in act_locs_result.fetchall()]
        
        act_lore_result = await db.execute(
            select(ActLoreItemAssociation, LoreItem)
            .join(LoreItem)
            .where(ActLoreItemAssociation.act_id == act.id)
        )
        act_lore_items = [{
            "lore_item": lore, 
            "roles": assoc.roles
        } for assoc, lore in act_lore_result.fetchall()]
        
        # Add act-level elements if any exist
        if act_characters or act_locations or act_lore_items:
            html_parts.append("<div class='act-elements'>")
            html_parts.append("<h4>Act Elements:</h4>")
            
            elements_list = []
            for char_data in act_characters:
                char = char_data["character"]
                roles = char_data["roles"]
                roles_text = f" ({', '.join(roles)})" if roles else ""
                elements_list.append(f"<strong>{escape(char.name)}</strong>{escape(roles_text)}")
            
            for loc_data in act_locations:
                loc = loc_data["location"]
                roles = loc_data["roles"]
                roles_text = f" ({', '.join(roles)})" if roles else ""
                elements_list.append(f"<strong>{escape(loc.name)}</strong>{escape(roles_text)}")
            
            for lore_data in act_lore_items:
                lore = lore_data["lore_item"]
                roles = lore_data["roles"]
                roles_text = f" ({', '.join(roles)})" if roles else ""
                elements_list.append(f"<strong>{escape(lore.title)}</strong>{escape(roles_text)}")
            
            if elements_list:
                html_parts.append(f"<p>{', '.join(elements_list)}</p>")
            
            html_parts.append("</div>")
        
        # Get scenes for this act
        scenes = await crud_scene.get_scenes_by_act(db, act.id, limit=1000)
        
        if scenes:
            for scene in scenes:
                html_parts.append(f"<div class='clearfix'><h3>Scene {scene.scene_number}: {escape(scene.title.strip() if scene.title else 'Untitled Scene')}</h3>")
                
                # Add scene image if available
                if hasattr(scene, 'image_url') and scene.image_url:
                    html_parts.append(f"<img src='{escape(scene.image_url)}' alt='Scene {scene.scene_number} image' class='scene-image'>")
                
                # Get scene-level associations
                scene_chars_result = await db.execute(
                    select(SceneCharacterAssociation, Character)
                    .join(Character)
                    .where(SceneCharacterAssociation.scene_id == scene.id)
                )
                scene_characters = [{
                    "character": char, 
                    "roles": assoc.roles
                } for assoc, char in scene_chars_result.fetchall()]
                
                scene_locs_result = await db.execute(
                    select(SceneLocationAssociation, Location)
                    .join(Location)
                    .where(SceneLocationAssociation.scene_id == scene.id)
                )
                scene_locations = [{
                    "location": loc, 
                    "roles": assoc.roles
                } for assoc, loc in scene_locs_result.fetchall()]
                
                scene_lore_result = await db.execute(
                    select(SceneLoreItemAssociation, LoreItem)
                    .join(LoreItem)
                    .where(SceneLoreItemAssociation.scene_id == scene.id)
                )
                scene_lore_items = [{
                    "lore_item": lore, 
                    "roles": assoc.roles
                } for assoc, lore in scene_lore_result.fetchall()]
                
                # Add scene-level elements if any exist
                if scene_characters or scene_locations or scene_lore_items:
                    html_parts.append("<div class='scene-elements'>")
                    html_parts.append("<h5>Scene Elements:</h5>")
                    
                    elements_list = []
                    for char_data in scene_characters:
                        char = char_data["character"]
                        roles = char_data["roles"]
                        roles_text = f" ({', '.join(roles)})" if roles else ""
                        elements_list.append(f"<strong>{escape(char.name)}</strong>{escape(roles_text)}")
                    
                    for loc_data in scene_locations:
                        loc = loc_data["location"]
                        roles = loc_data["roles"]
                        roles_text = f" ({', '.join(roles)})" if roles else ""
                        elements_list.append(f"<strong>{escape(loc.name)}</strong>{escape(roles_text)}")
                    
                    for lore_data in scene_lore_items:
                        lore = lore_data["lore_item"]
                        roles = lore_data["roles"]
                        roles_text = f" ({', '.join(roles)})" if roles else ""
                        elements_list.append(f"<strong>{escape(lore.title)}</strong>{escape(roles_text)}")
                    
                    if elements_list:
                        html_parts.append(f"<p>{', '.join(elements_list)}</p>")
                    
                    html_parts.append("</div>")
                
                # Add writer intent (summary) in italics if it exists
                if scene.summary:
                    html_parts.append(f"<div class='writer-intent'><strong>Writer's Intent:</strong> {scene.summary.strip()}</div>")
                
                # Add AI summary if it exists
                if scene.ai_summary:
                    html_parts.append(f"<div class='writer-intent'><strong>AI Summary:</strong> {scene.ai_summary.strip()}</div>")
                
                # Add scene content
                if scene.content:
                    html_parts.append(f"<div class='scene-content'>{scene.content}</div>")
                else:
                    html_parts.append("<div class='scene-content'><em>No content written for this scene yet.</em></div>")
                    
                html_parts.append("</div>")  # Close scene div
        else:
            html_parts.append("<p><em>No scenes have been written for this act yet.</em></p>")
        
        html_parts.append("</div>")
    
    html_parts.append("</article></body></html>")
    full_html_content = "".join(html_parts)

    sanitized_title = sanitize_filename(story.title if story.title else "story")
    # Use a deterministic filename based on story ID to allow overwriting
    html_filename = f"story_{story.id}_{sanitized_title}.html"
    
    logger.info(f"Generated filename for published story: {html_filename}")

    blob_service_client = None
    credential_for_storage = None
    published_blob_url = None
    container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_PUBLISHED_STORIES

    try:
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME:
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential_for_storage = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(account_url=account_url, credential=credential_for_storage)
        else:
            raise HTTPException(status_code=500, detail="Azure Storage not configured for publishing.")

        async with blob_service_client:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=html_filename)
            blob_content_settings = ContentSettings(content_type='text/html; charset=utf-8') 
            await blob_client.upload_blob(full_html_content.encode('utf-8'), content_settings=blob_content_settings, overwrite=True)
            published_blob_url = blob_client.url
            logger.info(f"Story ID {story_id} published successfully. URL: {published_blob_url}")
            
    except AzureResourceNotFoundError: 
        logger.error(f"Azure Storage container '{container_name}' not found for publishing.", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Publishing container '{container_name}' not found.")
    except AzureError as azure_ex:
        logger.error(f"AzureError during publishing story ID {story_id}: {azure_ex}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to publish due to an Azure storage error.")
    except Exception as e:
        logger.error(f"Unexpected error publishing story ID {story_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during publishing.")
    finally:
        if credential_for_storage:
            await credential_for_storage.close()
            
    if not published_blob_url: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to obtain published URL after upload.")

    # Save or update published story metadata in database
    try:
        # Calculate word count from actual story content (excluding HTML tags)
        story_text_parts = []
        if story.short_description:
            story_text_parts.append(story.short_description)
        for act in acts:
            if act.description:
                story_text_parts.append(act.description)
            # Get scenes for word count
            scenes = await crud_scene.get_scenes_by_act(db, act.id, limit=1000)
            for scene in scenes:
                if scene.summary:
                    story_text_parts.append(scene.summary)
                if scene.content:
                    story_text_parts.append(scene.content)
        
        # Calculate word count from actual text content
        all_text = " ".join(story_text_parts)
        word_count = len(all_text.split())
        
        # Check if already published
        existing_published = await db.execute(
            sqlalchemy.select(PublishedStory).where(PublishedStory.story_id == story_id)
        )
        existing = existing_published.scalar_one_or_none()
        
        if existing:
            # Update existing published story
            existing.published_url = published_blob_url
            existing.filename = html_filename
            existing.title = story.title or "Untitled Story"
            existing.description = request.description or story.short_description
            existing.word_count = word_count
            existing.is_public = (request.visibility == "public")
            existing.updated_at = func.now()
            db.add(existing)
        else:
            # Create new published story record
            published_story = PublishedStory(
                story_id=story_id,
                user_id=current_user.id,
                published_url=published_blob_url,
                filename=html_filename,
                title=story.title or "Untitled Story",
                description=request.description or story.short_description,
                word_count=word_count,
                is_public=(request.visibility == "public")
            )
            db.add(published_story)
        
        await db.commit()
        logger.info(f"Published story metadata saved for story ID {story_id}")
        
        # Send story publication email notification
        if current_user.email:
            try:
                # Get the published story ID from the existing record or the newly created one
                if existing:
                    published_story_id = existing.id
                else:
                    # Need to refresh to get the ID of the newly created published story
                    await db.refresh(published_story)
                    published_story_id = published_story.id
                
                # Use the application's published story viewer URL
                story_url = f"{settings.APP_URL}/published/story/{published_story_id}"
                
                email_sent = await email_service.send_story_completion_email(
                    user_email=current_user.email,
                    user_name=current_user.display_name or current_user.username,
                    story_title=story.title or "Untitled Story",
                    milestone_type="published",
                    story_url=story_url
                )
                
                if email_sent:
                    logger.info(f"Story publication email sent successfully to {current_user.email}")
                else:
                    logger.warning(f"Failed to send story publication email to {current_user.email}")
                    
            except Exception as e:
                logger.error(f"Error sending story publication email: {e}")
                # Don't fail the publish operation if email fails
                
    except Exception as e:
        logger.error(f"Failed to save published story metadata: {e}")
        # Don't fail the whole publish operation if metadata save fails
        
    return StoryPublishResponse(
        message="Story published successfully!",
        published_url=published_blob_url,
        filename=html_filename,
        status="published"
    )


# --- Image Management Endpoints ---

@router.get("/{story_id}/images")
async def list_story_images(
    story_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """Get all generated images for a story"""
    
    # Get story and verify ownership
    story = await crud_story.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Check if user owns the story or its world
    from app.crud import world as crud_world
    world = await crud_world.get_world(db, story.world_id)
    if not world or world.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all generated images for this story
    from app.models.generated_image import GeneratedImage
    from sqlalchemy import select
    
    result = await db.execute(
        select(GeneratedImage)
        .where(GeneratedImage.element_type == "story")
        .where(GeneratedImage.associated_element_id == story_id)
        .order_by(GeneratedImage.created_at.desc())
    )
    images = result.scalars().all()
    
    # Build response with image URLs
    image_list = []
    for image in images:
        image_url = None
        if image.blob_path:
            # Construct Azure blob URL
            container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
            if settings.AZURE_STORAGE_ACCOUNT_NAME:
                image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{image.blob_path}"
        
        image_list.append({
            "id": image.id,
            "url": image_url,
            "prompt": image.prompt,
            "revised_prompt": image.revised_prompt,
            "created_at": image.created_at.isoformat(),
            "is_current": story.current_image_id == image.id
        })
    
    return image_list


@router.post("/{story_id}/set-current-image/{image_id}")
async def set_current_story_image(
    story_id: int,
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Set the current image for a story"""
    
    # Get story and verify ownership
    story = await crud_story.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Check if user owns the story or its world
    from app.crud import world as crud_world
    world = await crud_world.get_world(db, story.world_id)
    if not world or world.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify the image exists and belongs to this story
    from app.models.generated_image import GeneratedImage
    from sqlalchemy import select
    
    result = await db.execute(
        select(GeneratedImage)
        .where(GeneratedImage.id == image_id)
        .where(GeneratedImage.element_type == "story")
        .where(GeneratedImage.associated_element_id == story_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Update story's current image
    story.current_image_id = image_id
    story.image_blob_path = image.blob_path
    
    await db.commit()
    
    # Build image URL for response
    image_url = None
    if image.blob_path:
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
        if settings.AZURE_STORAGE_ACCOUNT_NAME:
            image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{image.blob_path}"
    
    return {
        "message": "Current image updated successfully",
        "image_id": image_id,
        "image_url": image_url
    }

# --- Story Upgrade Endpoint ---

class StoryUpgradeRequest(BaseModel):
    """Request model for upgrading a Basic Story to Advanced"""
    world_id: Optional[int] = None  # If None, creates new world

@router.post("/{story_id}/upgrade", response_model=schema_story.StoryRead)
async def upgrade_story_to_advanced(
    story_id: int,
    upgrade_request: StoryUpgradeRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upgrade a Basic Story to an Advanced Story with full world-building features.
    
    This endpoint:
    - Converts story_type from 'basic' to 'advanced'
    - Associates with existing world or creates new world
    - Preserves all story content (acts, scenes)
    - Enables full world-building features
    """
    from app.services.story_service import story_service
    
    try:
        upgraded_story = await story_service.upgrade_story_to_advanced(
            db=db,
            story_id=story_id,
            user=current_user,
            world_id=upgrade_request.world_id
        )
        
        return upgraded_story
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to upgrade story {story_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upgrade story"
        )