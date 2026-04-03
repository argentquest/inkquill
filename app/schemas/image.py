"""Pydantic schemas for image."""

# /story_app/app/schemas/image.py
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime
import uuid

from app.core.storage_deps import build_storage_url

class GeneratedImageRead(BaseModel):
    """
    Pydantic model for representing a GeneratedImage in API responses.
    """
    id: int
    image_uuid: uuid.UUID
    blob_path: str
    prompt: str
    revised_prompt: Optional[str] = None
    created_at: datetime

    @computed_field
    @property
    def url(self) -> Optional[str]:
        """
        Computes the full public URL for the blob.
        """
        return build_storage_url("generated-images", self.blob_path)

    class Config:
        from_attributes = True

