"""SQLAlchemy models for act associations."""

# /story_app/app/models/act_associations.py

from sqlalchemy import Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from typing import List, Dict, Any, TYPE_CHECKING

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .act import Act
    from .character import Character
    from .location import Location
    from .lore_item import LoreItem

class ActCharacterAssociation(Base):
    """SQLAlchemy model for act character association."""
    __tablename__ = "act_character_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    act_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("acts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    character_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # JSON array of role names
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Optional notes about this association
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    act: Mapped["Act"] = relationship("Act", back_populates="character_associations")
    character: Mapped["Character"] = relationship("Character", back_populates="act_associations")

    def __repr__(self):
        return f"<ActCharacterAssociation(act_id={self.act_id}, character_id={self.character_id}, roles={self.roles})>"


class ActLocationAssociation(Base):
    """SQLAlchemy model for act location association."""
    __tablename__ = "act_location_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    act_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("acts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    location_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # JSON array of role names
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Optional notes about this association
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    act: Mapped["Act"] = relationship("Act", back_populates="location_associations")
    location: Mapped["Location"] = relationship("Location", back_populates="act_associations")

    def __repr__(self):
        return f"<ActLocationAssociation(act_id={self.act_id}, location_id={self.location_id}, roles={self.roles})>"


class ActLoreItemAssociation(Base):
    """SQLAlchemy model for act lore item association."""
    __tablename__ = "act_lore_item_associations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    act_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("acts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    lore_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lore_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # JSON array of role names
    roles: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    
    # Optional notes about this association
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    act: Mapped["Act"] = relationship("Act", back_populates="lore_item_associations")
    lore_item: Mapped["LoreItem"] = relationship("LoreItem", back_populates="act_associations")

    def __repr__(self):
        return f"<ActLoreItemAssociation(act_id={self.act_id}, lore_item_id={self.lore_item_id}, roles={self.roles})>"
