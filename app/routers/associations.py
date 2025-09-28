# /app/routers/associations.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.story_associations import StoryCharacterAssociation, StoryLocationAssociation, StoryLoreItemAssociation
from app.models.act_associations import ActCharacterAssociation, ActLocationAssociation, ActLoreItemAssociation
from app.models.scene_associations import SceneCharacterAssociation, SceneLocationAssociation, SceneLoreItemAssociation
from app.schemas.story_associations import (
    StoryCharacterAssociationCreate, StoryCharacterAssociationRead, StoryCharacterAssociationUpdate,
    StoryLocationAssociationCreate, StoryLocationAssociationRead, StoryLocationAssociationUpdate,
    StoryLoreItemAssociationCreate, StoryLoreItemAssociationRead, StoryLoreItemAssociationUpdate
)
from app.schemas.act_associations import (
    ActCharacterAssociationCreate, ActCharacterAssociationRead, ActCharacterAssociationUpdate,
    ActLocationAssociationCreate, ActLocationAssociationRead, ActLocationAssociationUpdate,
    ActLoreItemAssociationCreate, ActLoreItemAssociationRead, ActLoreItemAssociationUpdate
)
from app.schemas.scene_associations import (
    SceneCharacterAssociationCreate, SceneCharacterAssociationRead, SceneCharacterAssociationUpdate,
    SceneLocationAssociationCreate, SceneLocationAssociationRead, SceneLocationAssociationUpdate,
    SceneLoreItemAssociationCreate, SceneLoreItemAssociationRead, SceneLoreItemAssociationUpdate
)
from app.crud import story as crud_story, act as crud_act, scene as crud_scene, character as crud_character, location as crud_location, lore_item as crud_lore_item
from app.core.role_config import get_predefined_roles, validate_role, normalize_role

router = APIRouter(
    prefix="/associations",
    tags=["associations"],
    dependencies=[Depends(get_current_active_user)]
)

# === ROLE SUGGESTIONS ===

@router.get("/roles/{container_type}/{element_type}")
async def get_role_suggestions(
    container_type: str,
    element_type: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get predefined role suggestions for a specific element and container type."""
    valid_container_types = ["story", "act", "scene"]
    valid_element_types = ["character", "location", "lore_item"]
    
    if container_type not in valid_container_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid container type. Must be one of: {valid_container_types}"
        )
    
    if element_type not in valid_element_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid element type. Must be one of: {valid_element_types}"
        )
    
    roles = get_predefined_roles(element_type, container_type)
    
    return {
        "container_type": container_type,
        "element_type": element_type,
        "predefined_roles": roles,
        "allow_custom": True,
        "max_custom_roles": 5
    }

# === STORY ASSOCIATIONS ===

@router.post("/story/{story_id}/character/{character_id}", response_model=StoryCharacterAssociationRead)
async def create_story_character_association(
    story_id: int,
    character_id: int,
    association_data: StoryCharacterAssociationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create an association between a story and character with roles."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Verify character belongs to same world
    character = await crud_character.get_character(db, character_id=character_id)
    if not character or character.world_id != story.world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not in same world")
    
    # Check if association already exists
    from sqlalchemy import select
    result = await db.execute(
        select(StoryCharacterAssociation).filter(
            StoryCharacterAssociation.story_id == story_id,
            StoryCharacterAssociation.character_id == character_id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Association already exists")
    
    # Validate roles
    if association_data.roles:
        validated_roles = []
        for role in association_data.roles:
            if validate_role(role):
                validated_roles.append(normalize_role(role))
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Invalid role: '{role}'. Roles must be 2-50 characters and contain only letters, numbers, spaces, hyphens, and apostrophes."
                )
        association_data.roles = validated_roles
    
    # Create association
    db_association = StoryCharacterAssociation(
        story_id=story_id,
        character_id=character_id,
        roles=association_data.roles,
        notes=association_data.notes
    )
    db.add(db_association)
    await db.commit()
    await db.refresh(db_association)
    
    return StoryCharacterAssociationRead.from_orm(db_association)

@router.get("/story/{story_id}/characters", response_model=List[StoryCharacterAssociationRead])
async def get_story_character_associations(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all character associations for a story."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(StoryCharacterAssociation)
        .filter(StoryCharacterAssociation.story_id == story_id)
        .options(selectinload(StoryCharacterAssociation.character))
    )
    associations = result.scalars().all()
    
    return [StoryCharacterAssociationRead.from_orm(assoc) for assoc in associations]

@router.put("/story/{story_id}/character/{character_id}", response_model=StoryCharacterAssociationRead)
async def update_story_character_association(
    story_id: int,
    character_id: int,
    association_update: StoryCharacterAssociationUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update roles and notes for a story-character association."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Find association
    from sqlalchemy import select
    result = await db.execute(
        select(StoryCharacterAssociation).filter(
            StoryCharacterAssociation.story_id == story_id,
            StoryCharacterAssociation.character_id == character_id
        )
    )
    association = result.scalars().first()
    
    if not association:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")
    
    # Update association
    if association_update.roles is not None:
        association.roles = association_update.roles
    if association_update.notes is not None:
        association.notes = association_update.notes
    
    await db.commit()
    await db.refresh(association)
    
    return StoryCharacterAssociationRead.from_orm(association)

@router.delete("/story/{story_id}/character/{character_id}")
async def delete_story_character_association(
    story_id: int,
    character_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Remove association between story and character."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Find and delete association
    from sqlalchemy import select
    result = await db.execute(
        select(StoryCharacterAssociation).filter(
            StoryCharacterAssociation.story_id == story_id,
            StoryCharacterAssociation.character_id == character_id
        )
    )
    association = result.scalars().first()
    
    if not association:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")
    
    await db.delete(association)
    await db.commit()
    
    return {"message": "Association deleted successfully"}

# === SIMILAR ENDPOINTS FOR LOCATIONS AND LORE ITEMS ===
# I'll add the location and lore item endpoints following the same pattern

@router.post("/story/{story_id}/location/{location_id}", response_model=StoryLocationAssociationRead)
async def create_story_location_association(
    story_id: int,
    location_id: int,
    association_data: StoryLocationAssociationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create an association between a story and location with roles."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Verify location belongs to same world
    location = await crud_location.get_location(db, location_id=location_id)
    if not location or location.world_id != story.world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found or not in same world")
    
    # Check if association already exists
    from sqlalchemy import select
    result = await db.execute(
        select(StoryLocationAssociation).filter(
            StoryLocationAssociation.story_id == story_id,
            StoryLocationAssociation.location_id == location_id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Association already exists")
    
    # Create association
    db_association = StoryLocationAssociation(
        story_id=story_id,
        location_id=location_id,
        roles=association_data.roles,
        notes=association_data.notes
    )
    db.add(db_association)
    await db.commit()
    await db.refresh(db_association)
    
    return StoryLocationAssociationRead.from_orm(db_association)

# === GET ALL ASSOCIATIONS FOR A STORY ===
@router.get("/story/{story_id}/all")
async def get_all_story_associations(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all associations for a story (characters, locations, lore items)."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # Get all association types
    char_result = await db.execute(
        select(StoryCharacterAssociation)
        .filter(StoryCharacterAssociation.story_id == story_id)
        .options(selectinload(StoryCharacterAssociation.character))
    )
    
    loc_result = await db.execute(
        select(StoryLocationAssociation)
        .filter(StoryLocationAssociation.story_id == story_id)
        .options(selectinload(StoryLocationAssociation.location))
    )
    
    lore_result = await db.execute(
        select(StoryLoreItemAssociation)
        .filter(StoryLoreItemAssociation.story_id == story_id)
        .options(selectinload(StoryLoreItemAssociation.lore_item))
    )
    
    return {
        "characters": [StoryCharacterAssociationRead.from_orm(assoc) for assoc in char_result.scalars().all()],
        "locations": [StoryLocationAssociationRead.from_orm(assoc) for assoc in loc_result.scalars().all()],
        "lore_items": [StoryLoreItemAssociationRead.from_orm(assoc) for assoc in lore_result.scalars().all()]
    }

# === ACT ASSOCIATIONS ===

@router.post("/act/{act_id}/character/{character_id}", response_model=ActCharacterAssociationRead)
async def create_act_character_association(
    act_id: int,
    character_id: int,
    association_data: ActCharacterAssociationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create an association between an act and character with roles."""
    # Verify act ownership (through story ownership)
    act = await crud_act.get_act(db, act_id=act_id)
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Verify character belongs to same world
    character = await crud_character.get_character(db, character_id=character_id)
    if not character or character.world_id != story.world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not in same world")
    
    # Check if association already exists
    from sqlalchemy import select
    result = await db.execute(
        select(ActCharacterAssociation).filter(
            ActCharacterAssociation.act_id == act_id,
            ActCharacterAssociation.character_id == character_id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Association already exists")
    
    # Create association
    db_association = ActCharacterAssociation(
        act_id=act_id,
        character_id=character_id,
        roles=association_data.roles,
        notes=association_data.notes
    )
    db.add(db_association)
    await db.commit()
    await db.refresh(db_association)
    
    return ActCharacterAssociationRead.from_orm(db_association)

@router.get("/act/{act_id}/all")
async def get_all_act_associations(
    act_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all associations for an act (characters, locations, lore items)."""
    # Verify act ownership (through story ownership)
    act = await crud_act.get_act(db, act_id=act_id)
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    # Get all association types
    char_result = await db.execute(
        select(ActCharacterAssociation)
        .filter(ActCharacterAssociation.act_id == act_id)
        .options(selectinload(ActCharacterAssociation.character))
    )
    
    loc_result = await db.execute(
        select(ActLocationAssociation)
        .filter(ActLocationAssociation.act_id == act_id)
        .options(selectinload(ActLocationAssociation.location))
    )
    
    lore_result = await db.execute(
        select(ActLoreItemAssociation)
        .filter(ActLoreItemAssociation.act_id == act_id)
        .options(selectinload(ActLoreItemAssociation.lore_item))
    )
    
    return {
        "characters": [ActCharacterAssociationRead.from_orm(assoc) for assoc in char_result.scalars().all()],
        "locations": [ActLocationAssociationRead.from_orm(assoc) for assoc in loc_result.scalars().all()],
        "lore_items": [ActLoreItemAssociationRead.from_orm(assoc) for assoc in lore_result.scalars().all()]
    }

@router.get("/scene/{scene_id}/all")
async def get_all_scene_associations(
    scene_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all associations for a scene (characters, locations, lore items)."""
    # Verify scene ownership (through act -> story ownership)
    scene = await crud_scene.get_scene(db, scene_id=scene_id)
    if not scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
    
    act = await crud_act.get_act(db, act_id=scene.act_id)
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Get all association types
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    char_result = await db.execute(
        select(SceneCharacterAssociation)
        .filter(SceneCharacterAssociation.scene_id == scene_id)
        .options(selectinload(SceneCharacterAssociation.character))
    )
    
    loc_result = await db.execute(
        select(SceneLocationAssociation)
        .filter(SceneLocationAssociation.scene_id == scene_id)
        .options(selectinload(SceneLocationAssociation.location))
    )
    
    lore_result = await db.execute(
        select(SceneLoreItemAssociation)
        .filter(SceneLoreItemAssociation.scene_id == scene_id)
        .options(selectinload(SceneLoreItemAssociation.lore_item))
    )
    
    return {
        "characters": [SceneCharacterAssociationRead.from_orm(assoc) for assoc in char_result.scalars().all()],
        "locations": [SceneLocationAssociationRead.from_orm(assoc) for assoc in loc_result.scalars().all()],
        "lore_items": [SceneLoreItemAssociationRead.from_orm(assoc) for assoc in lore_result.scalars().all()]
    }

# === LOCATION ASSOCIATIONS ===

@router.post("/act/{act_id}/location/{location_id}", response_model=ActLocationAssociationRead)
async def create_act_location_association(
    act_id: int,
    location_id: int,
    association_data: ActLocationAssociationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create an association between an act and location with roles."""
    # Verify act ownership (through story ownership)
    act = await crud_act.get_act(db, act_id=act_id)
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Verify location belongs to same world
    location = await crud_location.get_location(db, location_id=location_id)
    if not location or location.world_id != story.world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found or not in same world")
    
    # Check if association already exists
    from sqlalchemy import select
    result = await db.execute(
        select(ActLocationAssociation).filter(
            ActLocationAssociation.act_id == act_id,
            ActLocationAssociation.location_id == location_id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Association already exists")
    
    # Create association
    db_association = ActLocationAssociation(
        act_id=act_id,
        location_id=location_id,
        roles=association_data.roles,
        notes=association_data.notes
    )
    db.add(db_association)
    await db.commit()
    await db.refresh(db_association)
    
    return ActLocationAssociationRead.from_orm(db_association)

@router.post("/story/{story_id}/lore_item/{lore_item_id}", response_model=StoryLoreItemAssociationRead)
async def create_story_lore_item_association(
    story_id: int,
    lore_item_id: int,
    association_data: StoryLoreItemAssociationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create an association between a story and lore item with roles."""
    # Verify story ownership
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Verify lore item belongs to same world
    lore_item = await crud_lore_item.get_lore_item(db, lore_item_id=lore_item_id)
    if not lore_item or lore_item.world_id != story.world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lore item not found or not in same world")
    
    # Check if association already exists
    from sqlalchemy import select
    result = await db.execute(
        select(StoryLoreItemAssociation).filter(
            StoryLoreItemAssociation.story_id == story_id,
            StoryLoreItemAssociation.lore_item_id == lore_item_id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Association already exists")
    
    # Create association
    db_association = StoryLoreItemAssociation(
        story_id=story_id,
        lore_item_id=lore_item_id,
        roles=association_data.roles,
        notes=association_data.notes
    )
    db.add(db_association)
    await db.commit()
    await db.refresh(db_association)
    
    return StoryLoreItemAssociationRead.from_orm(db_association)

# === LORE ITEM ASSOCIATIONS ===

@router.post("/act/{act_id}/lore_item/{lore_item_id}", response_model=ActLoreItemAssociationRead)
async def create_act_lore_item_association(
    act_id: int,
    lore_item_id: int,
    association_data: ActLoreItemAssociationCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create an association between an act and lore item with roles."""
    # Verify act ownership (through story ownership)
    act = await crud_act.get_act(db, act_id=act_id)
    if not act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    
    story = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Verify lore item belongs to same world
    lore_item = await crud_lore_item.get_lore_item(db, lore_item_id=lore_item_id)
    if not lore_item or lore_item.world_id != story.world_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lore item not found or not in same world")
    
    # Check if association already exists
    from sqlalchemy import select
    result = await db.execute(
        select(ActLoreItemAssociation).filter(
            ActLoreItemAssociation.act_id == act_id,
            ActLoreItemAssociation.lore_item_id == lore_item_id
        )
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Association already exists")
    
    # Create association
    db_association = ActLoreItemAssociation(
        act_id=act_id,
        lore_item_id=lore_item_id,
        roles=association_data.roles,
        notes=association_data.notes
    )
    db.add(db_association)
    await db.commit()
    await db.refresh(db_association)
    
    return ActLoreItemAssociationRead.from_orm(db_association)

# === SINGLE ASSOCIATION RETRIEVAL ===

@router.get("/{container_type}/{container_id}/{element_type}/{element_id}")
async def get_single_association(
    container_type: str,
    container_id: int,
    element_type: str,
    element_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific association between a container and element."""
    from sqlalchemy import select
    
    # Validate types
    valid_container_types = ["story", "act", "scene"]
    valid_element_types = ["character", "location", "lore_item"]
    
    if container_type not in valid_container_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid container type. Must be one of: {valid_container_types}"
        )
    
    if element_type not in valid_element_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid element type. Must be one of: {valid_element_types}"
        )
    
    # Map to association models
    association_model = None
    if container_type == "story":
        if element_type == "character":
            association_model = StoryCharacterAssociation
        elif element_type == "location":
            association_model = StoryLocationAssociation
        elif element_type == "lore_item":
            association_model = StoryLoreItemAssociation
    elif container_type == "act":
        if element_type == "character":
            association_model = ActCharacterAssociation
        elif element_type == "location":
            association_model = ActLocationAssociation
        elif element_type == "lore_item":
            association_model = ActLoreItemAssociation
    elif container_type == "scene":
        if element_type == "character":
            association_model = SceneCharacterAssociation
        elif element_type == "location":
            association_model = SceneLocationAssociation
        elif element_type == "lore_item":
            association_model = SceneLoreItemAssociation
    
    if not association_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid container/element type combination"
        )
    
    # Verify ownership
    if container_type == "story":
        container = await crud_story.get_story_for_user(db, story_id=container_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "act":
        act = await crud_act.get_act(db, act_id=container_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "scene":
        scene = await crud_scene.get_scene(db, scene_id=container_id)
        if not scene:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
        act = await crud_act.get_act(db, act_id=scene.act_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Get the association
    query = select(association_model).filter(
        getattr(association_model, f"{container_type}_id") == container_id,
        getattr(association_model, f"{element_type}_id") == element_id
    )
    
    result = await db.execute(query)
    association = result.scalars().first()
    
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Association between {container_type} {container_id} and {element_type} {element_id} not found"
        )
    
    return {
        "container_type": container_type,
        "container_id": container_id,
        "element_type": element_type,
        "element_id": element_id,
        "roles": association.roles or [],
        "notes": association.notes,
        "created_at": association.created_at,
        "updated_at": association.updated_at
    }

# === UPDATE ASSOCIATION ===

@router.put("/{container_type}/{container_id}/{element_type}/{element_id}")
async def update_association(
    container_type: str,
    container_id: int,
    element_type: str,
    element_id: int,
    association_data: dict,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing association between a container and element."""
    from sqlalchemy import select
    
    # Validate types
    valid_container_types = ["story", "act", "scene"]
    valid_element_types = ["character", "location", "lore_item"]
    
    if container_type not in valid_container_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid container type. Must be one of: {valid_container_types}"
        )
    
    if element_type not in valid_element_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid element type. Must be one of: {valid_element_types}"
        )
    
    # Map to association models
    association_model = None
    if container_type == "story":
        if element_type == "character":
            association_model = StoryCharacterAssociation
        elif element_type == "location":
            association_model = StoryLocationAssociation
        elif element_type == "lore_item":
            association_model = StoryLoreItemAssociation
    elif container_type == "act":
        if element_type == "character":
            association_model = ActCharacterAssociation
        elif element_type == "location":
            association_model = ActLocationAssociation
        elif element_type == "lore_item":
            association_model = ActLoreItemAssociation
    elif container_type == "scene":
        if element_type == "character":
            association_model = SceneCharacterAssociation
        elif element_type == "location":
            association_model = SceneLocationAssociation
        elif element_type == "lore_item":
            association_model = SceneLoreItemAssociation
    
    if not association_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid container/element type combination"
        )
    
    # Verify ownership
    if container_type == "story":
        container = await crud_story.get_story_for_user(db, story_id=container_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "act":
        act = await crud_act.get_act(db, act_id=container_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "scene":
        scene = await crud_scene.get_scene(db, scene_id=container_id)
        if not scene:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
        act = await crud_act.get_act(db, act_id=scene.act_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Get the existing association
    query = select(association_model).filter(
        getattr(association_model, f"{container_type}_id") == container_id,
        getattr(association_model, f"{element_type}_id") == element_id
    )
    
    result = await db.execute(query)
    association = result.scalars().first()
    
    if not association:
        # If association doesn't exist, create it
        association = association_model(
            **{
                f"{container_type}_id": container_id,
                f"{element_type}_id": element_id,
                "roles": association_data.get("roles", []),
                "notes": association_data.get("notes")
            }
        )
        db.add(association)
    else:
        # Update existing association
        association.roles = association_data.get("roles", association.roles)
        association.notes = association_data.get("notes", association.notes)
    
    await db.commit()
    await db.refresh(association)
    
    return {
        "container_type": container_type,
        "container_id": container_id,
        "element_type": element_type,
        "element_id": element_id,
        "roles": association.roles or [],
        "notes": association.notes,
        "created_at": association.created_at,
        "updated_at": association.updated_at
    }

# === BULK ASSOCIATION OPERATIONS ===

@router.post("/bulk/{container_type}/{container_id}")
async def create_bulk_associations(
    container_type: str,
    container_id: int,
    associations_data: list[dict],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create multiple associations in bulk."""
    # Validate container type
    valid_container_types = ["story", "act", "scene"]
    if container_type not in valid_container_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid container type. Must be one of: {valid_container_types}"
        )
    
    # Verify container ownership
    if container_type == "story":
        container = await crud_story.get_story_for_user(db, story_id=container_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "act":
        act = await crud_act.get_act(db, act_id=container_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "scene":
        scene = await crud_scene.get_scene(db, scene_id=container_id)
        if not scene:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
        act = await crud_act.get_act(db, act_id=scene.act_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    results = []
    
    for assoc_data in associations_data:
        element_type = assoc_data.get("element_type")
        element_id = assoc_data.get("element_id")
        roles = assoc_data.get("roles", [])
        
        if not element_type or not element_id:
            continue
            
        # Validate element type
        valid_element_types = ["character", "location", "lore_item"]
        if element_type not in valid_element_types:
            continue
            
        try:
            # Use the existing PUT endpoint logic
            response_data = await update_association(
                container_type=container_type,
                container_id=container_id,
                element_type=element_type,
                element_id=element_id,
                association_data={"roles": roles, "notes": None},
                db=db,
                current_user=current_user
            )
            results.append(response_data)
        except Exception as e:
            # Log error but continue with other associations
            print(f"Error creating association for {element_type} {element_id}: {e}")
            
    return {
        "message": f"Processed {len(results)} associations",
        "associations": results
    }

# === GENERIC DELETE ASSOCIATION ENDPOINT ===

@router.delete("/{container_type}/{container_id}/{element_type}/{element_id}")
async def delete_association(
    container_type: str,
    container_id: int,
    element_type: str,
    element_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an association between a container (story/act/scene) and an element (character/location/lore_item)."""
    # Validate types
    valid_container_types = ["story", "act", "scene"]
    valid_element_types = ["character", "location", "lore_item"]
    
    if container_type not in valid_container_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid container type. Must be one of: {valid_container_types}"
        )
    
    if element_type not in valid_element_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid element type. Must be one of: {valid_element_types}"
        )
    
    # Verify container ownership
    if container_type == "story":
        container = await crud_story.get_story_for_user(db, story_id=container_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "act":
        act = await crud_act.get_act(db, act_id=container_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    elif container_type == "scene":
        scene = await crud_scene.get_scene(db, scene_id=container_id)
        if not scene:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
        act = await crud_act.get_act(db, act_id=scene.act_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
        container = await crud_story.get_story_for_user(db, story_id=act.story_id, user_id=current_user.id)
        if not container:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    
    # Determine association model
    association_model_map = {
        "story": {
            "character": StoryCharacterAssociation,
            "location": StoryLocationAssociation,
            "lore_item": StoryLoreItemAssociation
        },
        "act": {
            "character": ActCharacterAssociation,
            "location": ActLocationAssociation,
            "lore_item": ActLoreItemAssociation
        },
        "scene": {
            "character": SceneCharacterAssociation,
            "location": SceneLocationAssociation,
            "lore_item": SceneLoreItemAssociation
        }
    }
    
    association_model = association_model_map[container_type][element_type]
    
    # Find and delete association
    from sqlalchemy import select
    
    query = select(association_model).filter(
        getattr(association_model, f"{container_type}_id") == container_id,
        getattr(association_model, f"{element_type}_id") == element_id
    )
    
    result = await db.execute(query)
    association = result.scalars().first()
    
    if not association:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")
    
    await db.delete(association)
    await db.commit()
    
    return {"message": "Association removed successfully"}