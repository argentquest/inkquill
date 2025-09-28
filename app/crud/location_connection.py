# /ai_rag_story_app/app/crud/location_connection.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
import logging

from app.models.location import LocationConnection, Location
from app.schemas.location import LocationConnectionCreate, LocationConnectionUpdate

logger = logging.getLogger(__name__)

async def create_location_connection(
    db: AsyncSession, 
    connection_in: LocationConnectionCreate
) -> LocationConnection:
    """Create a new location connection."""
    
    # Validate that both locations exist and are in the same world
    from_location = await db.get(Location, connection_in.from_location_id)
    to_location = await db.get(Location, connection_in.to_location_id)
    
    if not from_location:
        raise ValueError(f"From location with ID {connection_in.from_location_id} not found")
    if not to_location:
        raise ValueError(f"To location with ID {connection_in.to_location_id} not found")
    if from_location.world_id != to_location.world_id:
        raise ValueError("Locations must be in the same world to be connected")
    if connection_in.from_location_id == connection_in.to_location_id:
        raise ValueError("A location cannot be connected to itself")
    
    db_connection = LocationConnection(**connection_in.model_dump())
    db.add(db_connection)
    await db.flush()
    await db.refresh(db_connection)
    
    logger.info(f"Created location connection from {connection_in.from_location_id} to {connection_in.to_location_id}")
    return db_connection

async def get_location_connection(
    db: AsyncSession, 
    from_location_id: int, 
    to_location_id: int
) -> Optional[LocationConnection]:
    """Get a specific location connection."""
    result = await db.execute(
        select(LocationConnection)
        .filter(
            LocationConnection.from_location_id == from_location_id,
            LocationConnection.to_location_id == to_location_id
        )
        .options(
            selectinload(LocationConnection.from_location),
            selectinload(LocationConnection.to_location)
        )
    )
    return result.scalars().first()

async def get_connections_for_location(
    db: AsyncSession, 
    location_id: int, 
    include_bidirectional_reverse: bool = True
) -> List[LocationConnection]:
    """Get all connections for a specific location.
    
    Args:
        location_id: The location to get connections for
        include_bidirectional_reverse: If True, includes bidirectional connections
                                     where this location is the 'to' location
    """
    query = select(LocationConnection).options(
        selectinload(LocationConnection.from_location),
        selectinload(LocationConnection.to_location)
    )
    
    if include_bidirectional_reverse:
        query = query.filter(
            ((LocationConnection.from_location_id == location_id) |
             ((LocationConnection.to_location_id == location_id) & 
              (LocationConnection.is_bidirectional == True)))
        )
    else:
        query = query.filter(LocationConnection.from_location_id == location_id)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_connections_for_world(
    db: AsyncSession, 
    world_id: int
) -> List[LocationConnection]:
    """Get all location connections within a world."""
    result = await db.execute(
        select(LocationConnection)
        .join(Location, LocationConnection.from_location_id == Location.id)
        .filter(Location.world_id == world_id)
        .options(
            selectinload(LocationConnection.from_location),
            selectinload(LocationConnection.to_location)
        )
    )
    return result.scalars().all()

async def update_location_connection(
    db: AsyncSession, 
    from_location_id: int,
    to_location_id: int,
    connection_in: LocationConnectionUpdate
) -> Optional[LocationConnection]:
    """Update an existing location connection."""
    db_connection = await get_location_connection(db, from_location_id, to_location_id)
    if not db_connection:
        return None
    
    update_data = connection_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_connection, key):
            setattr(db_connection, key, value)
    
    db.add(db_connection)
    await db.flush()
    await db.refresh(db_connection)
    
    logger.info(f"Updated location connection from {from_location_id} to {to_location_id}")
    return db_connection

async def delete_location_connection(
    db: AsyncSession, 
    from_location_id: int,
    to_location_id: int
) -> bool:
    """Delete a location connection."""
    db_connection = await get_location_connection(db, from_location_id, to_location_id)
    if not db_connection:
        return False
    
    await db.delete(db_connection)
    await db.flush()
    
    logger.info(f"Deleted location connection from {from_location_id} to {to_location_id}")
    return True

async def get_location_hierarchy(
    db: AsyncSession, 
    world_id: int
) -> List[Tuple[Location, List[Location]]]:
    """Get the full location hierarchy for a world.
    
    Returns a list of tuples: (parent_location, [child_locations])
    Root locations (no parent) have None as the parent.
    """
    # Get all locations in the world
    result = await db.execute(
        select(Location)
        .filter(Location.world_id == world_id)
        .options(selectinload(Location.child_locations))
        .order_by(Location.parent_location_id.nulls_first(), Location.name)
    )
    locations = result.scalars().all()
    
    # Group by parent
    hierarchy = []
    processed_ids = set()
    
    # First, process root locations (no parent)
    for location in locations:
        if location.parent_location_id is None:
            children = [child for child in locations if child.parent_location_id == location.id]
            hierarchy.append((location, children))
            processed_ids.add(location.id)
            processed_ids.update(child.id for child in children)
    
    # Then process any remaining locations that have parents
    for location in locations:
        if location.id not in processed_ids and location.parent_location_id is not None:
            children = [child for child in locations if child.parent_location_id == location.id]
            hierarchy.append((location, children))
    
    return hierarchy

async def get_location_path(
    db: AsyncSession,
    from_location_id: int,
    to_location_id: int,
    max_depth: int = 10
) -> Optional[List[LocationConnection]]:
    """Find a path between two locations using connections.
    
    This is a simple breadth-first search implementation.
    Returns None if no path exists.
    """
    if from_location_id == to_location_id:
        return []
    
    visited = set()
    queue = [(from_location_id, [])]
    
    while queue and len(queue[0][1]) < max_depth:
        current_location_id, path = queue.pop(0)
        
        if current_location_id in visited:
            continue
        visited.add(current_location_id)
        
        # Get all connections from current location
        connections = await get_connections_for_location(db, current_location_id, True)
        
        for connection in connections:
            next_location_id = None
            if connection.from_location_id == current_location_id:
                next_location_id = connection.to_location_id
            elif connection.is_bidirectional and connection.to_location_id == current_location_id:
                next_location_id = connection.from_location_id
            
            if next_location_id is None or next_location_id in visited:
                continue
                
            new_path = path + [connection]
            
            if next_location_id == to_location_id:
                return new_path
            
            queue.append((next_location_id, new_path))
    
    return None  # No path found