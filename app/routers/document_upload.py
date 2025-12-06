# /ai_rag_story_app/app/routers/document_upload.py

from fastapi import (
    APIRouter, Depends, UploadFile, File, Form, 
    HTTPException, BackgroundTasks, status
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional 
import shutil
import tempfile
import os
import uuid 
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User as ModelUser
from app.schemas.document import UploadedDocumentCreate, UploadedDocumentRead
from app.schemas.base import ApiResponse
from app.models.uploaded_document import DocumentStatus, SourceElementTypeEnum
from app.crud import document as crud_document_db
from app.core.config import settings

# --- MODIFIED IMPORT ---
from app.processing.rag_ingestion import process_uploaded_document_task

from app.models.job_status import JobTypeEnum
from app.crud import job_status as crud_job_status
from app.schemas.general import JobSubmissionResponse

logger = logging.getLogger(__name__)

router = APIRouter() 

MAX_FILE_SIZE_MB = getattr(settings, 'MAX_DOCUMENT_UPLOAD_SIZE_MB', 50) 
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = [
    "application/pdf", "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword" 
]
ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx"] 


@router.post(
    "/upload", 
    response_model=ApiResponse,
    status_code=status.HTTP_202_ACCEPTED,
    # <<< MODIFICATION: Added name attribute to match the template's url_for call >>>
    name="upload_document_for_rag",
    # <<< END MODIFICATION >>>
    summary="Upload a document for RAG processing.",
    description="Accepts a file, creates a database record, and schedules a background job for RAG indexing. Returns a job_id for tracking."
)
async def handle_document_upload_for_rag(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="The document file (PDF, TXT, DOCX)."),
    world_id: int = Form(..., description="Required ID of the World to associate this document with."),
    current_user: ModelUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not file.filename:
        logger.warning(f"User '{current_user.username}' attempted upload with no filename.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename cannot be empty.")
    
    # Validate that the world exists and belongs to the user
    from app.crud import world as crud_world
    world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not world:
        logger.warning(f"User '{current_user.username}' attempted upload to invalid or inaccessible world ID: {world_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid world ID or you don't have access to this world.")
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        logger.warning(f"User '{current_user.username}' attempted upload with invalid file type: {file_extension}. Allowed: {ALLOWED_EXTENSIONS}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"File type {file_extension} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"User '{current_user.username}' uploaded file '{file.filename}' with potentially mismatched MIME type: {file.content_type}. Proceeding based on extension.")

    temp_dir = tempfile.mkdtemp(prefix="doc_upload_")
    safe_filename = "".join(c if c.isalnum() or c in ['.', '-', '_'] else '_' for c in file.filename)
    if not safe_filename: safe_filename = "uploaded_file"
    temp_file_path = os.path.join(temp_dir, safe_filename)
    
    file_size = 0
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(temp_file_path)
        if file_size == 0:
            logger.warning(f"User '{current_user.username}' uploaded an empty file: {file.filename}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
        if file_size > MAX_FILE_SIZE_BYTES:
            logger.warning(f"User '{current_user.username}' uploaded file '{file.filename}' too large: {file_size} bytes.")
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File size {file_size / (1024*1024):.2f}MB exceeds limit of {MAX_FILE_SIZE_MB}MB.")
        
        logger.info(f"User '{current_user.username}' uploaded file '{file.filename}' (size: {file_size} bytes), saved temporarily to '{temp_file_path}'. World ID: {world_id}")

        tentative_blob_name = f"user_uploads/{current_user.id}/{uuid.uuid4()}_{safe_filename}"

        doc_create_payload = UploadedDocumentCreate(
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            blob_storage_path=tentative_blob_name, 
            status=DocumentStatus.PENDING,
            user_id=current_user.id,
            world_id=world_id,
            source_element_type=SourceElementTypeEnum.USER_UPLOADED,
        )
        db_document = await crud_document_db.create_document_record_from_schema(db, doc_create_payload)
        
        job_id = str(uuid.uuid4())
        await crud_job_status.create_job(
            db=db,
            job_id=job_id,
            user_id=current_user.id,
            job_type=JobTypeEnum.DOCUMENT_RAG_PROCESSING,
            status_message=f"Job initiated for document '{db_document.filename}'."
        )

        background_tasks.add_task(
            process_uploaded_document_task,
            job_id=job_id,
            db_document_id=db_document.id,
            file_path_on_disk=temp_file_path
        )
        logger.info(f"Scheduled RAG processing job {job_id} for document ID {db_document.id} ('{db_document.filename}') for user '{current_user.username}'.")
        
        return JobSubmissionResponse(
            message=f"Document '{db_document.filename}' accepted. Processing started.",
            job_id=job_id
        )

    except HTTPException: 
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as e:
        logger.error(f"Error during document upload by '{current_user.username}' for file '{file.filename}': {e}", exc_info=True)
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initiate document processing.")


@router.get(
    "/download/{document_id}",
    name="download_document",
    summary="Download a document"
)
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Download a document file."""
    from fastapi.responses import StreamingResponse
    from app.core.azure_deps import get_blob_service_client
    import mimetypes
    
    # Get document record
    document = await crud_document_db.get_document_record_for_user(db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or you don't have permission to access it"
        )
    
    try:
        # Get blob service client
        from azure.storage.blob import BlobServiceClient
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME:
            from azure.identity import DefaultAzureCredential
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Azure Storage not configured")
        
        # Get blob client
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=document.blob_storage_path)
        
        # Check if blob exists
        if not blob_client.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found in storage")
        
        # Download blob
        download_stream = blob_client.download_blob()
        
        # Determine content type
        content_type = document.content_type or mimetypes.guess_type(document.filename)[0] or "application/octet-stream"
        
        # Return streaming response
        return StreamingResponse(
            download_stream.chunks(),
            media_type=content_type,
            headers={
                "Content-Disposition": f'inline; filename="{document.filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document {document_id}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to download document")


@router.delete(
    "/{document_id}",
    name="delete_document",
    summary="Delete a document",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Delete a document and its associated blob storage."""
    # Get document record and verify ownership
    document = await crud_document_db.get_document_record_for_user(db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or you don't have permission to delete it"
        )
    
    try:
        # Delete document record and blob
        await crud_document_db.delete_document_record_and_blob(db, document_id, current_user.id)
        logger.info(f"User '{current_user.username}' successfully deleted document {document_id} ('{document.filename}')")
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id} for user '{current_user.username}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting document"
        )