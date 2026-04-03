"""Service helpers for mixins."""

# /story_app/app/services/mixins.py

from typing import Optional
from sqlalchemy.orm import Session
from app.models.world import World
from app.models.user import User


class ShadowWorldMixin:
    """
    Mixin for handling shadow world operations in the Basic/Advanced story system.
    Shadow worlds are hidden worlds automatically created for Basic Stories.
    """
    
    def create_shadow_world(
        self, 
        db: Session, 
        user: User, 
        story_title: str
    ) -> World:
        """
        Create a shadow world for a Basic Story.
        
        Args:
            db: Database session
            user: User who owns the story
            story_title: Title of the Basic Story
            
        Returns:
            Created shadow world
        """
        world_name = f"{story_title} World"
        
        shadow_world = World(
            name=world_name,
            description=f"Auto-generated world for the story '{story_title}'",
            short_description=f"World for {story_title}",
            user_id=user.id,
            is_shadow=True,  # Mark as shadow world
            is_free_chat_enabled=False
        )
        
        db.add(shadow_world)
        db.commit()
        db.refresh(shadow_world)
        
        return shadow_world
    
    def reveal_shadow_world(
        self, 
        db: Session, 
        world: World, 
        new_name: Optional[str] = None
    ) -> World:
        """
        Convert a shadow world to a regular world (when upgrading story to Advanced).
        
        Args:
            db: Database session
            world: The shadow world to reveal
            new_name: Optional new name for the world
            
        Returns:
            Updated world (no longer shadow)
        """
        if not world.is_shadow:
            raise ValueError("World is not a shadow world")
            
        # Update world properties
        world.is_shadow = False
        
        if new_name:
            world.name = new_name
            
        # Update description to remove auto-generated text
        if world.description and "Auto-generated world" in world.description:
            world.description = ""
            
        db.commit()
        db.refresh(world)
        
        return world
    
    def get_visible_worlds(self, db: Session, user_id: int) -> list[World]:
        """
        Get all non-shadow worlds for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of visible (non-shadow) worlds
        """
        return db.query(World).filter(
            World.user_id == user_id,
            World.is_shadow == False
        ).order_by(World.updated_at.desc()).all()
    
    def count_visible_worlds(self, db: Session, user_id: int) -> int:
        """
        Count non-shadow worlds for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Count of visible worlds
        """
        return db.query(World).filter(
            World.user_id == user_id,
            World.is_shadow == False
        ).count()
