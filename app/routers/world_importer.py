# /ai_rag_story_app/app/routers/world_importer.py

import logging
import tempfile
import shutil
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from fastapi import HTTPException, status

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.processing.importer_jobs import create_world_and_extract_elements_from_document_task, import_world_from_book_task
from app.crud import job_status as crud_job_status
from app.models.job_status import JobTypeEnum
from app.schemas.general import JobSubmissionResponse
from app.schemas.job_status import JobStatusRead

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/worlds", 
    tags=["world-importer"],
    dependencies=[Depends(get_current_active_user)]
)

class BookTitleImportRequest(BaseModel):
    book_title: str
    model_config_id: Optional[int] = None

class WorldImportResponse(BaseModel):
    message: str
    world_id: Optional[int] = None
    world_name: Optional[str] = None
    error: Optional[str] = None

@router.post(
    "/import-from-book-title", 
    response_model=JobSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED, 
    summary="Generate and import a world definition based on a book title."
)
async def import_world_from_book_api(
    request_data: BookTitleImportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    book_title = request_data.book_title
    logger.info(f"User '{current_user.username}' submitted request to import world from book: '{book_title}'")

    try:
        job_id = str(uuid.uuid4())
        await crud_job_status.create_job(
            db=db,
            job_id=job_id,
            user_id=current_user.id,
            job_type=JobTypeEnum.WORLD_IMPORT_FROM_TITLE,
            status_message=f"Job initiated to import world from title: '{book_title}'."
        )

        background_tasks.add_task(
            import_world_from_book_task,
            job_id=job_id,
            book_title=book_title,
            user_id=current_user.id,
            model_config_id=request_data.model_config_id
        )

        # --- BEGIN FIX: Updated user-facing message ---
        return JobSubmissionResponse(
            message=f"Import job for '{book_title}' has been started. This process typically takes 5-10 minutes depending on the complexity of the book and current system load. Please keep this browser tab open until the import completes. You can check the progress below or visit the 'My Worlds' page to see your newly generated world when finished.",
            job_id=job_id
        )
        # --- END FIX ---
    except Exception as e:
        await db.rollback() # Rollback job creation if task scheduling fails
        logger.error(f"Failed to initiate world import job for title '{book_title}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not start world import job.")


@router.post("/import/create-from-document", response_model=JobSubmissionResponse, status_code=status.HTTP_202_ACCEPTED, name="create_world_from_document_api")
async def create_world_from_document_api(
    background_tasks: BackgroundTasks,
    world_name: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    logger.info(f"User '{current_user.username}' submitted document '{file.filename}' to create new world '{world_name}'.")

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename cannot be empty.")
    if not any(file.filename.lower().endswith(ext) for ext in ['.pdf', '.docx', '.txt']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Allowed: PDF, DOCX, TXT.")

    temp_dir = tempfile.mkdtemp(prefix="world_doc_upload_")
    safe_filename = "".join(c if c.isalnum() or c in ['.', '-', '_'] else '_' for c in file.filename)
    if not safe_filename: safe_filename = "uploaded_file"
    temp_file_path = os.path.join(temp_dir, safe_filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File '{file.filename}' saved temporarily to '{temp_file_path}' for world creation.")

        job_id = str(uuid.uuid4())
        await crud_job_status.create_job(
            db=db,
            job_id=job_id,
            user_id=current_user.id,
            job_type=JobTypeEnum.WORLD_EXTRACTION_FROM_DOC,
            status_message=f"Job initiated for world '{world_name}' from document '{file.filename}'."
        )

        background_tasks.add_task(
            create_world_and_extract_elements_from_document_task,
            job_id=job_id,
            world_name=world_name,
            user_id=current_user.id,
            temp_file_path=temp_file_path,
            original_filename=file.filename,
            model_config_id=None  # Hardcoded to use GPT-4.1 Mini in the task
        )

        # --- BEGIN FIX: Updated user-facing message ---
        return JobSubmissionResponse(
            message=f"Analysis of '{file.filename}' has been started using GPT-4.1 Mini for optimal element extraction. This process typically takes 10-20 minutes depending on the document size, complexity, and current system load. Please keep this browser tab open until the import completes. You can check the progress below or visit the 'My Worlds' page to see your newly generated world '{world_name}' when finished.",
            job_id=job_id
        )
        # --- END FIX ---
    except Exception as e:
        await db.rollback() # Rollback job creation if task scheduling fails
        logger.error(f"Error handling file upload for world creation from document: {e}", exc_info=True)
        if os.path.exists(temp_file_path):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to start world creation process.")

@router.get("/import/job-status/{job_id}", response_model=JobStatusRead, name="get_job_status")
async def get_job_status_api(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    db_job = await crud_job_status.get_job_by_job_id(db, job_id=job_id, user_id=current_user.id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found or you do not have permission to view it.")
    return db_job