# /ai_rag_story_app/app/schemas/image.py
from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime
import uuid

from app.core.config import settings

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
        account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
        if account_name and container_name and self.blob_path:
            return f"https://{account_name}.blob.core.windows.net/{container_name}/{self.blob_path}"
        return None

    class Config:
        from_attributes = True