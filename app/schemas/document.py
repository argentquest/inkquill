# /ai_rag_story_app/app/schemas/document.py

from pydantic import BaseModel, Field, computed_field
from typing import Optional, List
from datetime import datetime
import enum
import logging

from app.models.uploaded_document import DocumentStatus, SourceElementTypeEnum
from app.core.config import settings

logger = logging.getLogger(__name__)

class UploadedDocumentBase(BaseModel):
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
    user_id: int

class UploadedDocumentUpdate(BaseModel):
    filename: Optional[str] = Field(None, max_length=255)
    content_type: Optional[str] = Field(None, max_length=100)
    blob_storage_path: Optional[str] = Field(None, max_length=1024)
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = Field(None)
    processed_at: Optional[datetime] = None
    world_id: Optional[int] = None

class UploadedDocumentRead(UploadedDocumentBase):
    id: int
    user_id: int 
    uploaded_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    @computed_field
    @property
    def blob_url(self) -> Optional[str]:
        account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS
        
        # <<< MODIFICATION: Add logging to debug why this might fail >>>
        if not account_name:
            logger.warning("Could not generate blob_url: AZURE_STORAGE_ACCOUNT_NAME is not set in settings.")
        if not container_name:
            logger.warning("Could not generate blob_url: AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS is not set.")
        if not self.blob_storage_path:
            logger.debug(f"Document ID {self.id} has no blob_storage_path, so blob_url is null.")
        # <<< END MODIFICATION >>>

        if account_name and container_name and self.blob_storage_path:
            return f"https://{account_name}.blob.core.windows.net/{container_name}/{self.blob_storage_path}"
        return None

    class Config:
        from_attributes = True 
        use_enum_values = True 