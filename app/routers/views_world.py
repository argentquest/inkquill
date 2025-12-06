# /ai_rag_story_app/app/routers/views_world.py

from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any, Union, Type
import asyncio

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user, get_current_user_with_anonymous_support
from app.core import security as core_security 
from app.crud import user as crud_user
from app.core.azure_deps import get_blob_service_client
from azure.storage.blob.aio import BlobServiceClient
from app.models.user import User
from app.models.world import World as ModelWorld
from app.models.story import Story as ModelStory
from app.models.act import Act as ModelAct
from app.models.character import Character as ModelCharacter
from app.models.location import Location as ModelLocation
from app.models.lore_item import LoreItem as ModelLoreItem, LoreItemCategoryEnum
from app.models.uploaded_document import UploadedDocument as ModelUploadedDocument
from app.schemas.character import CharacterRead, CharacterGeneratorInput, CharacterGeneratorResult
from app.schemas.base import ApiResponse
from app.schemas.location import LocationRead
from app.schemas.lore_item import LoreItemRead
from app.schemas.world import WorldRead
from app.schemas.document import UploadedDocumentRead
from app.crud import world as crud_world, story as crud_story, act as crud_act, scene as crud_scene, character as crud_character, location as crud_location, lore_item as crud_lore_item, document as crud_document
from app.services.character_generator_service import character_generator_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ui/worlds", 
    tags=["ui-world-elements-views"]
)

templates = Jinja2Templates(directory="app/templates")

# --- HELPER FUNCTIONS ---


async def _check_and_get_image_url(blob_service_client: BlobServiceClient, blob_path: Optional[str]) -> Optional[str]:
    """Safely constructs a public URL for a blob if it exists."""
    if not blob_path:
        return None
    try:
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        if await blob_client.exists():
            return blob_client.url
    except Exception as e:
        logger.warning(f"Could not check for blob '{blob_path}' due to error: {e}")
    return None

async def get_world_for_ui_and_verify_ownership(
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> ModelWorld:
    """Dependency to fetch and verify world ownership for UI routes."""
    db_world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not db_world:
        logger.warning(f"UI: World ID {world_id} not found or not accessible by user '{current_user.username}'.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World not found or you do not have permission to access it."
        )
    return db_world

async def _enrich_elements_with_image_urls(
    elements: List[Union[ModelWorld, ModelCharacter, ModelLocation, ModelLoreItem]],
    schema: Type[Union[WorldRead, CharacterRead, LocationRead, LoreItemRead]],
    blob_service_client: BlobServiceClient
) -> List[Union[WorldRead, CharacterRead, LocationRead, LoreItemRead]]:
    """
    Takes a list of ORM elements, converts them to Pydantic schemas,
    and populates the image_url for each.
    """
    enriched_list = []
    for element in elements:
        element_read = schema.from_orm(element)
        path_to_check = None
        if hasattr(element, 'current_image') and element.current_image and element.current_image.blob_path:
            path_to_check = element.current_image.blob_path
        elif hasattr(element, 'image_blob_path'):
            path_to_check = element.image_blob_path
        
        element_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        enriched_list.append(element_read)
    return enriched_list


# --- WORLD VIEWS ---

@router.get("/", response_class=HTMLResponse, name="ui_list_worlds")
async def list_worlds_ui(
    request: Request, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    if current_user:
        logger.info(f"User '{current_user.username}' accessing list of their worlds.")
        worlds_db = await crud_world.get_worlds_by_user(db, user_id=current_user.id)
        worlds_for_template = await _enrich_elements_with_image_urls(worlds_db, WorldRead, blob_service_client)
    else:
        logger.info("Anonymous user accessing demo worlds.")
        # For anonymous users, show sample/demo worlds
        worlds_for_template = [
            {
                "id": 1,
                "name": "Middle-earth",
                "description": "A fantasy world created by J.R.R. Tolkien featuring hobbits, elves, dwarves, and humans.",
                "image_url": None,
                "user_id": None,
                "is_demo": True
            },
            {
                "id": 2,
                "name": "Westeros",
                "description": "The primary setting of George R.R. Martin's A Song of Ice and Fire series.",
                "image_url": None,
                "user_id": None,
                "is_demo": True
            },
            {
                "id": 3,
                "name": "Hogwarts",
                "description": "The magical school from J.K. Rowling's Harry Potter series.",
                "image_url": None,
                "user_id": None,
                "is_demo": True
            }
        ]
    
    return templates.TemplateResponse(
        "pages/world_list.html", 
        {"request": request, "worlds": worlds_for_template, "current_user": current_user}
    )

@router.get("/new", response_class=HTMLResponse, name="ui_create_world_form")
async def create_world_ui_form(request: Request):
    return templates.TemplateResponse(
        "pages/world_form.html", 
        {"request": request, "world": None, "form_action_url": request.url_for('create_new_world')}
    )

@router.get("/import-from-book", response_class=HTMLResponse, name="ui_import_world_from_book_form")
async def import_world_from_book_ui_form(request: Request):
    return templates.TemplateResponse("pages/import_from_book.html", {"request": request})

@router.get("/create-from-document", response_class=HTMLResponse, name="ui_create_world_from_document_form")
async def create_world_from_document_ui_form(request: Request):
    return templates.TemplateResponse("pages/create_from_document.html", {"request": request})

@router.get("/generator/world", response_class=HTMLResponse, name="ui_world_builder_wizard")
async def world_builder_wizard_ui(request: Request):
    """World Builder Wizard page"""
    return templates.TemplateResponse("pages/world_builder.html", {"request": request})

@router.get("/{world_id}", response_class=HTMLResponse, name="ui_world_detail")
async def world_detail_ui(
    request: Request, 
    db_world: ModelWorld = Depends(get_world_for_ui_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    characters_db, locations_db, lore_items_db, documents_db, stories_in_world = await asyncio.gather(
        crud_character.get_characters_by_world(db, world_id=db_world.id, limit=settings.MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT),
        crud_location.get_locations_by_world(db, world_id=db_world.id, limit=settings.MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT),
        crud_lore_item.get_lore_items_by_world(db, world_id=db_world.id, limit=settings.MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT),
        crud_document.get_documents_by_world(db, world_id=db_world.id, limit=settings.MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT),
        crud_story.get_stories_by_world_id(db, world_id=db_world.id, user_id=current_user.id, limit=10)
    )

    world_characters, world_locations, world_lore_items = await asyncio.gather(
        _enrich_elements_with_image_urls(characters_db, CharacterRead, blob_service_client),
        _enrich_elements_with_image_urls(locations_db, LocationRead, blob_service_client),
        _enrich_elements_with_image_urls(lore_items_db, LoreItemRead, blob_service_client)
    )
    
    # Convert documents to read schema
    world_documents = [UploadedDocumentRead.from_orm(doc) for doc in documents_db]
    
    return templates.TemplateResponse(
        "pages/world_detail.html", 
        {
            "request": request, "world": db_world, "world_characters": world_characters, 
            "world_locations": world_locations, "world_lore_items": world_lore_items, 
            "world_documents": world_documents,
            "stories_in_world": stories_in_world, "current_user": current_user, 
        }
    )


@router.get("/{world_id}/edit", response_class=HTMLResponse, name="ui_edit_world_form")
async def edit_world_ui_form(
    request: Request, 
    db_world: ModelWorld = Depends(get_world_for_ui_and_verify_ownership),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    path_to_check = db_world.current_image.blob_path if db_world.current_image else db_world.image_blob_path
    image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/world_form.html", 
        {
            "request": request, "world": db_world, 
            "form_action_url": request.url_for('update_existing_world', world_id=db_world.id),
            "image_url": image_url
        }
    )

# --- CHARACTER VIEWS ---

@router.get("/{world_id}/characters", response_class=HTMLResponse, name="ui_list_characters_for_world")
async def list_characters_for_world_ui(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    characters_db = await crud_character.get_characters_by_world(db, world_id=db_world.id, limit=100)
    world_characters = await _enrich_elements_with_image_urls(characters_db, CharacterRead, blob_service_client)
    return templates.TemplateResponse(
        "pages/character_list_for_world.html", 
        {"request": request, "world": db_world, "characters": world_characters}
    )

@router.get("/{world_id}/characters/new", response_class=HTMLResponse, name="ui_create_character_for_world_form")
async def create_character_for_world_ui_form(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user)
):
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    return templates.TemplateResponse(
        "pages/character_form.html", 
        {"request": request, "world": db_world, "character": None, "form_action_url": request.url_for('create_new_character_for_world', world_id=db_world.id)}
    )

@router.get("/{world_id}/characters/{character_id}", response_class=HTMLResponse, name="ui_view_character")
async def view_character_ui(
    request: Request,
    world_id: int,
    character_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """View a specific character details."""
    db_character = await crud_character.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    
    db_world = await get_world_for_ui_and_verify_ownership(db_character.world_id, db, current_user)
    
    # Get character with image URL
    character_read = CharacterRead.from_orm(db_character)
    path_to_check = db_character.current_image.blob_path if db_character.current_image else db_character.image_blob_path
    character_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/character_detail.html",
        {
            "request": request,
            "world": db_world,
            "character": character_read
        }
    )

@router.get("/characters/{character_id}/edit", response_class=HTMLResponse, name="ui_edit_character_form")
async def edit_character_ui_form(
    request: Request, 
    character_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    db_character = await crud_character.get_character(db, character_id=character_id)
    if not db_character: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    
    db_world = await get_world_for_ui_and_verify_ownership(db_character.world_id, db, current_user) 
    
    path_to_check = db_character.current_image.blob_path if db_character.current_image else db_character.image_blob_path
    image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/character_form.html", 
        {
            "request": request, "world": db_world, "character": db_character, 
            "form_action_url": request.url_for('update_existing_character', character_id=db_character.id),
            "image_url": image_url
        }
    )


# --- LOCATION VIEWS ---

@router.get("/{world_id}/locations", response_class=HTMLResponse, name="ui_list_locations_for_world")
async def list_locations_for_world_ui(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    from app.crud import location_connection as crud_location_connection
    
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    locations_db = await crud_location.get_locations_by_world(db, world_id=db_world.id, limit=100)
    locations_for_template = await _enrich_elements_with_image_urls(locations_db, LocationRead, blob_service_client)
        
    connections = await crud_location_connection.get_connections_for_world(db, world_id=db_world.id)
    
    location_connections = {loc.id: [] for loc in locations_for_template}
    for connection in connections:
        if connection.from_location_id in location_connections:
            location_connections[connection.from_location_id].append({
                'location': connection.to_location, 'path_description': connection.path_description, 'is_bidirectional': connection.is_bidirectional
            })
        if connection.is_bidirectional and connection.to_location_id in location_connections:
            location_connections[connection.to_location_id].append({
                'location': connection.from_location, 'path_description': connection.reverse_path_description or connection.path_description, 'is_bidirectional': connection.is_bidirectional
            })
    
    return templates.TemplateResponse(
        "pages/location_list_for_world.html", 
        {"request": request, "world": db_world, "locations": locations_for_template, "location_connections": location_connections}
    )

@router.get("/{world_id}/locations/new", response_class=HTMLResponse, name="ui_create_location_for_world_form")
async def create_location_for_world_ui_form(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user)
):
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    return templates.TemplateResponse(
        "pages/location_form.html", 
        {"request": request, "world": db_world, "location": None, "form_action_url": request.url_for('create_new_location_for_world', world_id=db_world.id)}
    )

@router.get("/{world_id}/locations/{location_id}", response_class=HTMLResponse, name="ui_view_location")
async def view_location_ui(
    request: Request,
    world_id: int,
    location_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """View a specific location details."""
    db_location = await crud_location.get_location(db, location_id=location_id)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    
    db_world = await get_world_for_ui_and_verify_ownership(db_location.world_id, db, current_user)
    
    # Get location with image URL
    location_read = LocationRead.from_orm(db_location)
    path_to_check = db_location.current_image.blob_path if db_location.current_image else db_location.image_blob_path
    location_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/location_detail.html",
        {
            "request": request,
            "world": db_world,
            "location": location_read
        }
    )

@router.get("/locations/{location_id}/edit", response_class=HTMLResponse, name="ui_edit_location_form")
async def edit_location_ui_form(
    request: Request, 
    location_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    db_location = await crud_location.get_location(db, location_id=location_id)
    if not db_location: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
        
    db_world = await get_world_for_ui_and_verify_ownership(db_location.world_id, db, current_user)
    path_to_check = db_location.current_image.blob_path if db_location.current_image else db_location.image_blob_path
    image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/location_form.html", 
        {
            "request": request, "world": db_world, "location": db_location, 
            "form_action_url": request.url_for('update_existing_location', location_id=db_location.id),
            "image_url": image_url
        }
    )

@router.get("/{world_id}/map", response_class=HTMLResponse, name="ui_world_map")
async def world_map_ui(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user)
):
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    return templates.TemplateResponse("pages/world_map.html", {"request": request, "world": db_world})

# --- LORE ITEM VIEWS ---

@router.get("/{world_id}/lore-items", response_class=HTMLResponse, name="ui_list_lore_items_for_world")
async def list_lore_items_for_world_ui(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    lore_items_db = await crud_lore_item.get_lore_items_by_world(db, world_id=db_world.id, limit=100)
    world_lore_items = await _enrich_elements_with_image_urls(lore_items_db, LoreItemRead, blob_service_client)
    categories_for_filter = [cat for cat in LoreItemCategoryEnum]
    return templates.TemplateResponse(
        "pages/lore_item_list_for_world.html", 
        {"request": request, "world": db_world, "lore_items": world_lore_items, "categories_for_filter": categories_for_filter}
    )

@router.get("/{world_id}/lore-items/new", response_class=HTMLResponse, name="ui_create_lore_item_for_world_form")
async def create_lore_item_for_world_ui_form(
    request: Request, 
    world_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user)
):
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    categories = [cat for cat in LoreItemCategoryEnum]
    return templates.TemplateResponse(
        "pages/lore_item_form.html", 
        {"request": request, "world": db_world, "lore_item": None, "categories": categories, "form_action_url": request.url_for('create_new_lore_item_for_world', world_id=db_world.id)}
    )

@router.get("/{world_id}/lore-items/{lore_item_id}", response_class=HTMLResponse, name="ui_view_lore_item")
async def view_lore_item_ui(
    request: Request,
    world_id: int,
    lore_item_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """View a specific lore item details."""
    db_lore_item = await crud_lore_item.get_lore_item(db, lore_item_id=lore_item_id)
    if not db_lore_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lore item not found")
    
    db_world = await get_world_for_ui_and_verify_ownership(db_lore_item.world_id, db, current_user)
    
    # Get lore item with image URL
    lore_item_read = LoreItemRead.from_orm(db_lore_item)
    path_to_check = db_lore_item.current_image.blob_path if db_lore_item.current_image else db_lore_item.image_blob_path
    lore_item_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/lore_item_detail.html",
        {
            "request": request,
            "world": db_world,
            "lore_item": lore_item_read
        }
    )

@router.get("/lore-items/{lore_item_id}/edit", response_class=HTMLResponse, name="ui_edit_lore_item_form")
async def edit_lore_item_ui_form(
    request: Request, 
    lore_item_id: int, 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    db_lore_item = await crud_lore_item.get_lore_item(db, lore_item_id=lore_item_id)
    if not db_lore_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lore item not found")
    
    db_world = await get_world_for_ui_and_verify_ownership(db_lore_item.world_id, db, current_user)
    categories = [cat for cat in LoreItemCategoryEnum]
    
    path_to_check = db_lore_item.current_image.blob_path if db_lore_item.current_image else db_lore_item.image_blob_path
    image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    
    return templates.TemplateResponse(
        "pages/lore_item_form.html", 
        {
            "request": request, "world": db_world, "lore_item": db_lore_item, "categories": categories, 
            "form_action_url": request.url_for('update_existing_lore_item', lore_item_id=db_lore_item.id),
            "image_url": image_url
        }
    )

# --- WORLD HIERARCHY VIEW ---

@router.get("/{world_id}/hierarchy", response_class=HTMLResponse, name="ui_world_hierarchy")
async def world_hierarchy_ui(
    request: Request, 
    world_id: int, 
    story_id: Optional[int] = Query(None, description="Optional story ID to filter hierarchy to specific story"),
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user),
    blob_service_client=Depends(get_blob_service_client)
):
    """
    Display the hierarchical tree view of world elements organized by Stories and Acts
    with role-based associations.
    If story_id is provided, only show that specific story.
    """
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    # Fetch stories with acts and scenes preloaded - either all for the world or just the specific story
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    if story_id:
        # Verify the story belongs to this world and user, and load with acts/scenes
        story_result = await db.execute(
            select(ModelStory)
            .filter(ModelStory.id == story_id, ModelStory.user_id == current_user.id, ModelStory.world_id == db_world.id)
            .options(selectinload(ModelStory.acts).selectinload(ModelAct.scenes))
        )
        specific_story = story_result.scalars().first()
        if not specific_story:
            raise HTTPException(status_code=404, detail="Story not found or not in this world")
        stories_db = [specific_story]
    else:
        # Load all stories for this world with acts and scenes preloaded
        stories_result = await db.execute(
            select(ModelStory)
            .filter(ModelStory.world_id == db_world.id, ModelStory.user_id == current_user.id)
            .options(selectinload(ModelStory.acts).selectinload(ModelAct.scenes))
            .order_by(ModelStory.created_at.desc())
        )
        stories_db = stories_result.scalars().all()
    
    # Fetch all world elements
    characters_db = await crud_character.get_characters_by_world(db, world_id=db_world.id, limit=1000)
    locations_db = await crud_location.get_locations_by_world(db, world_id=db_world.id, limit=1000)
    lore_items_db = await crud_lore_item.get_lore_items_by_world(db, world_id=db_world.id, limit=1000)
    
    # Enrich elements with image URLs
    world_characters = await _enrich_elements_with_image_urls(characters_db, CharacterRead, blob_service_client)
    world_locations = await _enrich_elements_with_image_urls(locations_db, LocationRead, blob_service_client)
    world_lore_items = await _enrich_elements_with_image_urls(lore_items_db, LoreItemRead, blob_service_client)
    
    # Fetch associations for all stories and acts
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
    from app.models.act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
    
    # Get all story associations
    story_associations = {}
    for story in stories_db:
        story_char_result = await db.execute(
            select(StoryCharacterAssociation)
            .filter(StoryCharacterAssociation.story_id == story.id)
            .options(selectinload(StoryCharacterAssociation.character))
        )
        story_loc_result = await db.execute(
            select(StoryLocationAssociation)
            .filter(StoryLocationAssociation.story_id == story.id)
            .options(selectinload(StoryLocationAssociation.location))
        )
        story_lore_result = await db.execute(
            select(StoryLoreItemAssociation)
            .filter(StoryLoreItemAssociation.story_id == story.id)
            .options(selectinload(StoryLoreItemAssociation.lore_item))
        )
        
        story_associations[story.id] = {
            'characters': story_char_result.scalars().all(),
            'locations': story_loc_result.scalars().all(),
            'lore_items': story_lore_result.scalars().all()
        }
    
    # Get all act associations
    act_associations = {}
    for story in stories_db:
        for act in story.acts:
            act_char_result = await db.execute(
                select(ActCharacterAssociation)
                .filter(ActCharacterAssociation.act_id == act.id)
                .options(selectinload(ActCharacterAssociation.character))
            )
            act_loc_result = await db.execute(
                select(ActLocationAssociation)
                .filter(ActLocationAssociation.act_id == act.id)
                .options(selectinload(ActLocationAssociation.location))
            )
            act_lore_result = await db.execute(
                select(ActLoreItemAssociation)
                .filter(ActLoreItemAssociation.act_id == act.id)
                .options(selectinload(ActLoreItemAssociation.lore_item))
            )
            
            act_associations[act.id] = {
                'characters': act_char_result.scalars().all(),
                'locations': act_loc_result.scalars().all(), 
                'lore_items': act_lore_result.scalars().all()
            }
    
    # Get all scene associations
    from app.models.scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation
    scene_associations = {}
    for story in stories_db:
        for act in story.acts:
            for scene in act.scenes:
                scene_char_result = await db.execute(
                    select(SceneCharacterAssociation)
                    .filter(SceneCharacterAssociation.scene_id == scene.id)
                    .options(selectinload(SceneCharacterAssociation.character))
                )
                scene_loc_result = await db.execute(
                    select(SceneLocationAssociation)
                    .filter(SceneLocationAssociation.scene_id == scene.id)
                    .options(selectinload(SceneLocationAssociation.location))
                )
                scene_lore_result = await db.execute(
                    select(SceneLoreItemAssociation)
                    .filter(SceneLoreItemAssociation.scene_id == scene.id)
                    .options(selectinload(SceneLoreItemAssociation.lore_item))
                )
                
                scene_associations[scene.id] = {
                    'characters': scene_char_result.scalars().all(),
                    'locations': scene_loc_result.scalars().all(),
                    'lore_items': scene_lore_result.scalars().all()
                }
    
    return templates.TemplateResponse(
        "pages/world_hierarchy.html", 
        {
            "request": request, 
            "world": db_world, 
            "stories": stories_db,
            "characters": world_characters,
            "locations": world_locations,
            "lore_items": world_lore_items,
            "story_associations": story_associations,
            "act_associations": act_associations,
            "scene_associations": scene_associations,
            "filtered_story_id": story_id,
            "is_story_filtered": story_id is not None
        }
    )

# --- CHARACTER GENERATOR ENDPOINTS ---

@router.get("/{world_id}/generator/character", response_class=HTMLResponse, name="ui_character_generator")
async def character_generator_ui(
    request: Request,
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Character generator wizard page"""
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    # Get generator data
    generator_data = {
        "personality_traits": sorted(character_generator_service.get_personality_traits()),
        "core_motivations": sorted(character_generator_service.get_core_motivations()),
        "relationship_dynamics": sorted(character_generator_service.get_relationship_dynamics()),
        "physical_attributes": character_generator_service.get_physical_attributes(),
        "available_genres": sorted(character_generator_service.get_available_genres()),
        "professions": sorted(character_generator_service.get_professions()),
        "age_categories": character_generator_service.get_age_categories()  # Keep logical order for ages
    }
    
    return templates.TemplateResponse(
        "pages/character_generator.html",
        {
            "request": request,
            "world": db_world,
            **generator_data
        }
    )

@router.get("/{world_id}/api/generator/character/genre-questions/{genre}")
async def get_genre_questions(
    world_id: int,
    genre: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get questions for a specific genre"""
    await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    questions = character_generator_service.get_genre_questions(genre)
    return {"questions": questions}

@router.post("/{world_id}/api/generator/character/random")
async def generate_random_character(
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Generate random character data"""
    db_world = await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    try:
        random_data = character_generator_service.generate_random_character_data(db_world)
        return random_data.dict()
    except Exception as e:
        logger.error(f"Failed to generate random character: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate random character")

@router.post("/{world_id}/api/generator/character/create")
async def create_generated_character(
    request: Request,
    world_id: int,
    character_input: CharacterGeneratorInput,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create character from generator input"""
    await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    try:
        character = await character_generator_service.create_character_from_input(
            db, world_id, character_input, current_user.id, background_tasks
        )
        
        result = CharacterGeneratorResult(
            success=True,
            character=CharacterRead.from_orm(character),
            redirect_url=str(request.url_for('ui_edit_character_form', character_id=character.id))
        )
        return result.dict()
        
    except Exception as e:
        logger.error(f"Failed to create generated character: {e}")
        return CharacterGeneratorResult(
            success=False,
            error=str(e)
        ).dict()

@router.get("/{world_id}/api/generator/character/professions")
async def get_professions(
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get available professions for character generator"""
    await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    professions = character_generator_service.get_professions()
    return {"professions": professions}

@router.get("/{world_id}/api/generator/character/age-categories")
async def get_age_categories(
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get available age categories for character generator"""
    await get_world_for_ui_and_verify_ownership(world_id, db, current_user)
    
    age_categories = character_generator_service.get_age_categories()
    return {"age_categories": age_categories}