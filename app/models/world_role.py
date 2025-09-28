# /ai_rag_story_app/app/models/world_role.py

from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .world import World
    from .user import User

class WorldRole(Base):
    __tablename__ = "world_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # For predefined roles (world_id is None) vs custom roles (world_id is set)
    world_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("worlds.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Track who created custom roles
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Predefined roles have is_predefined=True, custom roles have is_predefined=False
    is_predefined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    world: Mapped[Optional["World"]] = relationship("World", back_populates="custom_roles")
    created_by: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self):
        world_info = f"world_id={self.world_id}" if self.world_id else "predefined"
        return f"<WorldRole(id={self.id}, name='{self.name}', {world_info})>"