"""Background processing helpers for document processing."""

import logging
import os
import shutil
from pathlib import Path

from app.core.config import settings
from app.crud import document as crud_document
from app.crud import job_status as crud_job_status
from app.db import database as db_database
from app.models.job_status import JobStateEnum
from app.models.uploaded_document import DocumentStatus
from app.processing.text_extraction import extract_text_from_file_path

logger = logging.getLogger(__name__)


def _save_to_local_storage(blob_path: str, data: bytes) -> None:
    """Handle save to local storage."""
    destination = Path(settings.LOCAL_STORAGE_BASE_PATH) / settings.LOCAL_STORAGE_DOCUMENTS_PATH / blob_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)


async def process_uploaded_document_task(job_id: str, db_document_id: int, file_path_on_disk: str) -> None:
    """Process uploaded document task."""
    async with db_database.async_session_local() as db:
        try:
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Extracting document text...")
            document = await crud_document.get_document_record(db, db_document_id)
            if not document:
                raise ValueError(f"Document with ID {db_document_id} not found")

            await crud_document.update_document_status(db, db_document_id, DocumentStatus.PROCESSING_TEXT)
            extracted_text = await extract_text_from_file_path(file_path_on_disk, document.filename)
            if not extracted_text or extracted_text.isspace():
                raise ValueError("No text could be extracted from the document")

            await crud_document.update_document_status(db, db_document_id, DocumentStatus.COMPLETED)

            if document.blob_storage_path:
                with open(file_path_on_disk, "rb") as handle:
                    _save_to_local_storage(document.blob_storage_path, handle.read())
                _save_to_local_storage(
                    document.blob_storage_path + ".extracted.txt",
                    extracted_text.encode("utf-8"),
                )

            await crud_job_status.update_job_status(
                db,
                job_id,
                JobStateEnum.COMPLETED,
                "Document processing complete.",
                result_message=f"Extracted {len(extracted_text)} characters of direct context.",
            )
            logger.info("Processed uploaded document %s without retrieval indexing", db_document_id)
        except Exception as exc:
            error_message = f"Error processing document: {str(exc)[:500]}"
            logger.error(error_message, exc_info=True)
            await crud_document.update_document_status(db, db_document_id, DocumentStatus.ERROR, error_message)
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.FAILED, error_message)
        finally:
            try:
                if os.path.exists(file_path_on_disk):
                    shutil.rmtree(os.path.dirname(file_path_on_disk), ignore_errors=True)
            except Exception as cleanup_error:
                logger.warning("Failed to clean up temp document processing path: %s", cleanup_error)

