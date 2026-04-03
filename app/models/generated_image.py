"""SQLAlchemy models for generated image."""

# /story_app/app/models/generated_image.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
import uuid

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User

class GeneratedImage(Base):
    """
    SQLAlchemy ORM Model to store metadata for every AI-generated image.
    This enables versioning and a gallery for each world element.
    """
    __tablename__ = "generated_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, nullable=False, default=uuid.uuid4, index=True)
    blob_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    revised_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    element_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., 'character', 'scene'
    associated_element_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Image generation metadata
    aspect_ratio: Mapped[Optional[str]] = mapped_column(String(10), nullable=True) # e.g., '16x9', '5x4', '1x1'
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- Relationships ---
    owner: Mapped["User"] = relationship("User")

    __table_args__ = (
        sqlalchemy.Index('ix_generated_images_element_type_assoc_id', 'element_type', 'associated_element_id'),
    )

    @property
    def blob_url(self) -> str:
        """Convert blob_path to a public URL."""
        from app.core.storage_deps import build_storage_url

        return build_storage_url("generated-images", self.blob_path) or ""

    def __repr__(self):
        return f"<GeneratedImage(id={self.id}, uuid='{self.image_uuid}', element='{self.element_type}:{self.associated_element_id}')>"

