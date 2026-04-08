"""Pydantic schemas for document."""

# /story_app/app/schemas/document.py

from pydantic import BaseModel, Field, computed_field, ConfigDict
from typing import Optional, List
from datetime import datetime
import enum
import logging

from app.models.uploaded_document import DocumentStatus, SourceElementTypeEnum
from app.core.storage_deps import build_storage_url

logger = logging.getLogger(__name__)

class UploadedDocumentBase(BaseModel):
    """Pydantic schema for uploaded document base."""
    filename: str = Field(..., max_length=255)
    content_type: Optional[str] = Field(None, max_length=100)
    blob_storage_path: Optional[str] = Field(None, max_length=1024)
    status: DocumentStatus = Field(default=DocumentStatus.UPLOADED)
    error_message: Optional[str] = None
    world_id: Optional[int] = None
    source_element_type: Optional[SourceElementTypeEnum] = Field(default=SourceElementTypeEnum.USER_UPLOADED)
    source_character_id: Optional[int] = None
    source_location_id: Optional[int] = None
    source_lore_item_id: Optional[int] = None

class UploadedDocumentCreate(UploadedDocumentBase):
    """Pydantic schema for uploaded document create."""
    user_id: int

class UploadedDocumentUpdate(BaseModel):
    """Pydantic schema for uploaded document update."""
    filename: Optional[str] = Field(None, max_length=255)
    content_type: Optional[str] = Field(None, max_length=100)
    blob_storage_path: Optional[str] = Field(None, max_length=1024)
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = Field(None)
    processed_at: Optional[datetime] = None
    world_id: Optional[int] = None

class UploadedDocumentRead(UploadedDocumentBase):
    """Pydantic schema for uploaded document read."""
    id: int
    user_id: int 
    uploaded_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    @computed_field
    @property
    def blob_url(self) -> Optional[str]:
        if not self.blob_storage_path:
            logger.debug(f"Document ID {self.id} has no blob_storage_path, so blob_url is null.")
            return None
        return build_storage_url("documents", self.blob_storage_path)

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

