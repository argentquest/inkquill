# /ai_rag_story_app/app/routers/location_connection.py

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.world import World as ModelWorld
from app.models.location import LocationConnection as ModelLocationConnection
from app.schemas.base import ApiResponse
from app.schemas.location import (
    LocationConnectionCreate, 
    LocationConnectionRead, 
    LocationConnectionUpdate,
    LocationConnectionWithLocations
)
from app.crud import location_connection as crud_location_connection
from app.crud import world as crud_world
from app.crud import location as crud_location

from .world import get_world_and_verify_ownership as get_world_dependency

logger = logging.getLogger(__name__)

router_world_location_connections = APIRouter(
    prefix="/worlds/{world_id}/location-connections",
    tags=["world-location-connections"],
    dependencies=[Depends(get_current_active_user)]
)

router_location_connections = APIRouter(
    prefix="/location-connections",
    tags=["location-connections"],
    dependencies=[Depends(get_current_active_user)]
)

@router_world_location_connections.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_location_connection_for_world(
    world_id: int,
    connection_in: LocationConnectionCreate,
    db_world: ModelWorld = Depends(get_world_dependency),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new location connection within a world."""
    logger.info(f"User '{current_user.username}' creating location connection in world {db_world.id}")
    
    try:
        # Validate that both locations belong to this world
        from_location = await crud_location.get_location(db, connection_in.from_location_id)
        to_location = await crud_location.get_location(db, connection_in.to_location_id)
        
        if not from_location or from_location.world_id != world_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"From location {connection_in.from_location_id} not found in world {world_id}"
            )
        
        if not to_location or to_location.world_id != world_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"To location {connection_in.to_location_id} not found in world {world_id}"
            )
        
        # Check if connection already exists
        existing_connection = await crud_location_connection.get_location_connection(
            db, connection_in.from_location_id, connection_in.to_location_id
        )
        if existing_connection:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Connection already exists between these locations"
            )
        
        created_connection = await crud_location_connection.create_location_connection(db, connection_in)
        await db.commit()
        await db.refresh(created_connection)
        return created_connection
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating location connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the location connection."
        )

@router_world_location_connections.get("/", response_model=ApiResponse)
async def list_location_connections_for_world(
    world_id: int,
    db_world: ModelWorld = Depends(get_world_dependency),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all location connections within a world."""
    logger.info(f"User '{current_user.username}' listing location connections for world {db_world.id}")
    
    connections = await crud_location_connection.get_connections_for_world(db, db_world.id)
    return connections

@router_location_connections.get("/{from_location_id}/{to_location_id}", response_model=ApiResponse)
async def get_location_connection(
    from_location_id: int = Path(..., description="ID of the source location"),
    to_location_id: int = Path(..., description="ID of the destination location"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific location connection."""
    connection = await crud_location_connection.get_location_connection(db, from_location_id, to_location_id)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location connection not found"
        )
    
    # Verify user has access to this connection's world
    from_location = await crud_location.get_location(db, from_location_id)
    if not from_location or not from_location.world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source location not found")
    
    if from_location.world.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this location connection"
        )
    
    return connection

@router_location_connections.put("/{from_location_id}/{to_location_id}", response_model=ApiResponse)
async def update_location_connection(
    connection_in: LocationConnectionUpdate,
    from_location_id: int = Path(..., description="ID of the source location"),
    to_location_id: int = Path(..., description="ID of the destination location"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing location connection."""
    # Verify user has access to this connection's world
    from_location = await crud_location.get_location(db, from_location_id)
    if not from_location or not from_location.world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source location not found")
    
    if from_location.world.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this location connection"
        )
    
    try:
        updated_connection = await crud_location_connection.update_location_connection(
            db, from_location_id, to_location_id, connection_in
        )
        if not updated_connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location connection not found"
            )
        
        await db.commit()
        await db.refresh(updated_connection)
        return updated_connection
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating location connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the location connection."
        )

@router_location_connections.delete("/{from_location_id}/{to_location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location_connection(
    from_location_id: int = Path(..., description="ID of the source location"),
    to_location_id: int = Path(..., description="ID of the destination location"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a location connection."""
    # Verify user has access to this connection's world
    from_location = await crud_location.get_location(db, from_location_id)
    if not from_location or not from_location.world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source location not found")
    
    if from_location.world.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this location connection"
        )
    
    try:
        success = await crud_location_connection.delete_location_connection(
            db, from_location_id, to_location_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location connection not found"
            )
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting location connection: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the location connection."
        )

# Additional endpoints for advanced features

@router_world_location_connections.get("/location/{location_id}", response_model=ApiResponse)
async def get_connections_for_location(
    world_id: int,
    location_id: int,
    include_bidirectional: bool = Query(True, description="Include bidirectional connections where this location is the destination"),
    db_world: ModelWorld = Depends(get_world_dependency),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all connections for a specific location."""
    # Verify location belongs to this world
    location = await crud_location.get_location(db, location_id)
    if not location or location.world_id != world_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found in this world"
        )
    
    connections = await crud_location_connection.get_connections_for_location(
        db, location_id, include_bidirectional
    )
    return connections

@router_world_location_connections.get("/hierarchy", response_model=ApiResponse)
async def get_world_location_hierarchy(
    world_id: int,
    db_world: ModelWorld = Depends(get_world_dependency),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get the hierarchical structure of locations in a world."""
    hierarchy = await crud_location_connection.get_location_hierarchy(db, db_world.id)
    
    # Convert to a more readable format
    result = []
    for parent, children in hierarchy:
        result.append({
            "parent": {
                "id": parent.id if parent else None,
                "name": parent.name if parent else "Root",
                "scale": parent.scale.value if parent and parent.scale else None
            },
            "children": [
                {
                    "id": child.id,
                    "name": child.name,
                    "scale": child.scale.value if child.scale else None
                }
                for child in children
            ]
        })
    
    return result