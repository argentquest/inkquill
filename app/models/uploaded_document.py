"""SQLAlchemy models for uploaded document."""

# /story_app/app/models/uploaded_document.py

from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
import enum # Use standard Python enum for status values

# --- Core Application Imports ---
from app.db.database import Base

# --- Type Checking Imports ---
if TYPE_CHECKING:
    from .user import User
    from .world import World
    from .character import Character
    from .location import Location
    from .lore_item import LoreItem

class DocumentStatus(str, enum.Enum):
    """SQLAlchemy model for document status."""
    UPLOADED = "UPLOADED"
    PENDING = "PENDING"
    PROCESSING_TEXT = "PROCESSING_TEXT"
    CHUNKING = "CHUNKING"
    PREPARING_CONTEXT = "PREPARING_CONTEXT"
    STORING_CONTEXT = "STORING_CONTEXT"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class SourceElementTypeEnum(str, enum.Enum):
    """SQLAlchemy model for source element type enum."""
    USER_UPLOADED = "USER_UPLOADED"
    CHARACTER_LORE = "CHARACTER_LORE"
    LOCATION_LORE = "LOCATION_LORE"
    LORE_ITEM_LORE = "LORE_ITEM_LORE"

class UploadedDocument(Base):
    """SQLAlchemy model for uploaded document."""
    __tablename__ = "uploaded_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    blob_storage_path: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        SQLAlchemyEnum(DocumentStatus, name="document_status_enum", create_type=False),
        nullable=False, default=DocumentStatus.UPLOADED, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # uploaded_at effectively serves as the creation timestamp for this record
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # --- ADDED updated_at field ---
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # --- END ADDED updated_at field ---

    processed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    world_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("storytelling_worlds.id", ondelete="SET NULL"),
        nullable=True, 
        index=True
    )
    source_element_type: Mapped[Optional[SourceElementTypeEnum]] = mapped_column(
        SQLAlchemyEnum(SourceElementTypeEnum, name="source_element_type_enum", create_type=True),
        nullable=True,
        index=True
    )
    source_character_id: Mapped[Optional[int]] = mapped_column(ForeignKey("storytelling_characters.id", ondelete="SET NULL"), nullable=True, index=True)
    source_location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("storytelling_locations.id", ondelete="SET NULL"), nullable=True, index=True)
    source_lore_item_id: Mapped[Optional[int]] = mapped_column(ForeignKey("storytelling_lore_items.id", ondelete="SET NULL"), nullable=True, index=True)

    # --- Relationships ---
    owner: Mapped["User"] = relationship("User", back_populates="uploaded_documents")
    world: Mapped[Optional["World"]] = relationship("World")
    source_character: Mapped[Optional["Character"]] = relationship("Character")
    source_location: Mapped[Optional["Location"]] = relationship("Location")
    source_lore_item: Mapped[Optional["LoreItem"]] = relationship("LoreItem")

    def __repr__(self):
        status_value = self.status.value if isinstance(self.status, enum.Enum) else self.status
        source_type_val = self.source_element_type.value if self.source_element_type else SourceElementTypeEnum.USER_UPLOADED.value
        return (f"<UploadedDocument(id={self.id}, fn='{self.filename}', uid={self.user_id}, "
                f"status='{status_value}', type='{source_type_val}', uploaded='{self.uploaded_at}')>")

