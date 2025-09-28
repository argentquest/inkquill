# /ai_rag_story_app/app/models/world_collaborator.py

from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, TYPE_CHECKING
from enum import Enum

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .world import World
    from .user import User

class CollaboratorRole(str, Enum):
    """Roles that collaborators can have in a world"""
    CONTRIBUTOR = "contributor"
    MODERATOR = "moderator"
    CO_OWNER = "co_owner"

class CollaboratorStatus(str, Enum):
    """Status of a collaboration invitation/membership"""
    PENDING = "pending"
    ACTIVE = "active"
    DECLINED = "declined"
    REMOVED = "removed"

class WorldCollaborator(Base):
    """
    Represents a user's collaboration relationship with a world.
    Tracks permissions, role, and status.
    """
    __tablename__ = "world_collaborators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    world_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("worlds.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Role and status
    role: Mapped[CollaboratorRole] = mapped_column(
        String(50), 
        nullable=False, 
        default=CollaboratorRole.CONTRIBUTOR
    )
    status: Mapped[CollaboratorStatus] = mapped_column(
        String(20), 
        nullable=False, 
        default=CollaboratorStatus.PENDING
    )
    
    # Invitation tracking
    invited_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    invited_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    joined_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # Granular permissions override (JSON for flexibility)
    permissions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # --- Relationships ---
    world: Mapped["World"] = relationship("World", back_populates="collaborators")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    invited_by: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[invited_by_user_id]
    )

    # --- Unique constraint ---
    __table_args__ = (
        sqlalchemy.UniqueConstraint('world_id', 'user_id', name='uq_world_collaborator'),
    )

    def has_permission(self, permission: str) -> bool:
        """
        Check if this collaborator has a specific permission.
        Permissions can be overridden in the permissions JSON field.
        """
        if self.status != CollaboratorStatus.ACTIVE:
            return False
            
        # Check permissions override first
        if self.permissions and permission in self.permissions:
            return self.permissions[permission]
            
        # Default permissions based on role
        default_permissions = {
            CollaboratorRole.CONTRIBUTOR: {
                'create_stories': True,
                'create_characters': True,
                'create_locations': True,
                'create_lore_items': True,
                'edit_own_content': True,
                'edit_others_content': False,
                'delete_own_content': True,
                'delete_others_content': False,
                'manage_collaborators': False,
                'change_world_settings': False
            },
            CollaboratorRole.MODERATOR: {
                'create_stories': True,
                'create_characters': True,
                'create_locations': True,
                'create_lore_items': True,
                'edit_own_content': True,
                'edit_others_content': True,
                'delete_own_content': True,
                'delete_others_content': True,
                'manage_collaborators': True,
                'change_world_settings': False
            },
            CollaboratorRole.CO_OWNER: {
                'create_stories': True,
                'create_characters': True,
                'create_locations': True,
                'create_lore_items': True,
                'edit_own_content': True,
                'edit_others_content': True,
                'delete_own_content': True,
                'delete_others_content': True,
                'manage_collaborators': True,
                'change_world_settings': True
            }
        }
        
        role_permissions = default_permissions.get(self.role, {})
        return role_permissions.get(permission, False)

    def __repr__(self):
        return f"<WorldCollaborator(world_id={self.world_id}, user_id={self.user_id}, role='{self.role}', status='{self.status}')>"