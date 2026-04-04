from pathlib import Path

import pytest
from sqlalchemy import select

from app.models.job_status import JobStateEnum, JobStatus, JobTypeEnum
from app.models.uploaded_document import DocumentStatus, UploadedDocument


pytestmark = pytest.mark.integration


def test_document_upload_processing_download_and_delete(client, register_and_login, run_db, app_instance):
    register_and_login("docflow")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Document Flow World",
            "description": "World for document integration tests",
            "short_description": "Document world",
            "is_free_chat_enabled": False,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    upload_response = client.post(
        "/api/v1/documents/upload",
        data={"world_id": str(world_id)},
        files={
            "file": (
                "integration_notes.txt",
                b"Line one of integration context.\nLine two of integration context.\n",
                "text/plain",
            )
        },
    )
    assert upload_response.status_code == 202, upload_response.text
    upload_body = upload_response.json()
    assert upload_body["success"] is True
    job_id = upload_body["data"]["job_id"]

    def fetch_document_and_job(session):
        async def _inner():
            document = (
                await session.execute(
                    select(UploadedDocument).where(UploadedDocument.filename == "integration_notes.txt")
                )
            ).scalar_one()
            job = (
                await session.execute(select(JobStatus).where(JobStatus.job_id == job_id))
            ).scalar_one()
            return {
                "document_id": document.id,
                "blob_storage_path": document.blob_storage_path,
                "document_status": document.status,
                "processed_at": document.processed_at,
                "job_type": job.job_type,
                "job_state": job.state,
                "job_message": job.status_message,
                "job_result": job.result_message,
            }

        return _inner()

    state = run_db(fetch_document_and_job)
    document_id = state["document_id"]
    blob_storage_path = state["blob_storage_path"]

    assert state["document_status"] == DocumentStatus.COMPLETED
    assert state["processed_at"] is not None
    assert state["job_type"] == JobTypeEnum.DOCUMENT_CONTEXT_PROCESSING
    assert state["job_state"] == JobStateEnum.COMPLETED
    assert "Document processing complete" in (state["job_message"] or "")
    assert "direct context" in (state["job_result"] or "")

    storage_root = app_instance.state.test_storage_root / "uploads" / "documents"
    stored_document = storage_root / blob_storage_path
    extracted_document = storage_root / f"{blob_storage_path}.extracted.txt"

    assert stored_document.exists()
    assert extracted_document.exists()
    assert "integration context" in extracted_document.read_text(encoding="utf-8")

    download_response = client.get(f"/api/v1/documents/download/{document_id}")
    assert download_response.status_code == 200, download_response.text
    assert download_response.headers["content-type"].startswith("text/plain")
    assert "integration_notes.txt" in download_response.headers["content-disposition"]
    assert b"Line one of integration context." in download_response.content

    delete_response = client.delete(f"/api/v1/documents/{document_id}")
    assert delete_response.status_code == 204, delete_response.text

    def fetch_deleted_document(session):
        async def _inner():
            return (
                await session.execute(select(UploadedDocument).where(UploadedDocument.id == document_id))
            ).scalar_one_or_none()

        return _inner()

    assert run_db(fetch_deleted_document) is None
    assert not stored_document.exists()
    assert not extracted_document.exists()
