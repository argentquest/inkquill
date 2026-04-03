"""Database CRUD helpers for document."""

# /story_app/app/crud/document.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete 
from sqlalchemy.orm import selectinload 
from typing import List, Optional
from datetime import datetime, timezone
import logging
from fastapi import BackgroundTasks 

from app.models.uploaded_document import UploadedDocument, DocumentStatus, SourceElementTypeEnum
from app.schemas.document import UploadedDocumentCreate, UploadedDocumentUpdate 
logger = logging.getLogger(__name__)

async def create_document_record_from_schema(
    db: AsyncSession, 
    document_in: UploadedDocumentCreate
) -> UploadedDocument:
    """Create document record from schema."""
    logger.info(f"Creating document record from schema for filename: '{document_in.filename}', "
                f"type: {document_in.source_element_type.value if document_in.source_element_type else 'N/A'}, "
                f"world_id: {document_in.world_id}")
    
    db_document = UploadedDocument(**document_in.model_dump())
    
    db.add(db_document)
    try:
        await db.commit()
        await db.refresh(db_document) 
        
        logger.info(f"Document record ID {db_document.id} ('{db_document.filename}') created successfully from schema.")
        logger.debug(f"After refresh - ID: {db_document.id}, UploadedAt: {db_document.uploaded_at}, UpdatedAt: {db_document.updated_at}, Status: {db_document.status.value if db_document.status else 'N/A'}")

        if db_document.updated_at is None:
            if db_document.uploaded_at is not None:
                logger.warning(f"updated_at for doc ID {db_document.id} was None after refresh. Setting to uploaded_at value ({db_document.uploaded_at}) for Pydantic model.")
                db_document.updated_at = db_document.uploaded_at
            else:
                logger.error(f"CRITICAL: Both uploaded_at and updated_at are None for doc ID {db_document.id} after refresh. Setting updated_at to current time for Pydantic model.")
                db_document.updated_at = datetime.now(timezone.utc) 

        if hasattr(UploadedDocument, 'owner') and not hasattr(db_document, '_sa_owner_id'): 
             await db.refresh(db_document, attribute_names=['owner'])
        if hasattr(UploadedDocument, 'world') and db_document.world_id and not hasattr(db_document, '_sa_world_id'):
             await db.refresh(db_document, attribute_names=['world'])
        
        return db_document
    except Exception as e_commit:
        await db.rollback()
        logger.error(f"Error committing new document record from schema for '{document_in.filename}': {e_commit}", exc_info=True)
        raise

async def get_document_record(db: AsyncSession, document_id: int) -> Optional[UploadedDocument]:
    """Return document record."""
    logger.debug(f"Fetching document record with ID: {document_id}")
    result = await db.execute(
        select(UploadedDocument)
        .filter(UploadedDocument.id == document_id)
        .options(selectinload(UploadedDocument.owner), selectinload(UploadedDocument.world))
    )
    return result.scalars().first()

async def get_document_record_for_user(
    db: AsyncSession, document_id: int, user_id: int
) -> Optional[UploadedDocument]:
    """Return document record for user."""
    logger.debug(f"Fetching document record ID: {document_id} for user ID: {user_id}")
    result = await db.execute(
        select(UploadedDocument)
        .filter(UploadedDocument.id == document_id, UploadedDocument.user_id == user_id)
        .options(selectinload(UploadedDocument.owner), selectinload(UploadedDocument.world))
    )
    return result.scalars().first()

async def get_documents_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[UploadedDocument]:
    """Return documents by user."""
    logger.debug(f"Fetching document records for user ID: {user_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(UploadedDocument)
        .filter(UploadedDocument.user_id == user_id)
        .options(selectinload(UploadedDocument.world)) 
        .order_by(UploadedDocument.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_documents_by_world(
    db: AsyncSession,
    world_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[UploadedDocument]:
    """Get all documents associated with a specific world."""
    logger.info(f"Fetching documents for world ID: {world_id} (skip={skip}, limit={limit})")
    result = await db.execute(
        select(UploadedDocument)
        .filter(
            UploadedDocument.world_id == world_id,
            UploadedDocument.source_element_type == SourceElementTypeEnum.USER_UPLOADED
        )
        .options(selectinload(UploadedDocument.owner), selectinload(UploadedDocument.world))
        .order_by(UploadedDocument.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()
    logger.info(f"Found {len(documents)} documents for world ID: {world_id}")
    return documents

async def update_document_status(
    db: AsyncSession,
    document_id: int,
    new_status: DocumentStatus,
    error_message: Optional[str] = None
) -> Optional[UploadedDocument]:
    """Update document status."""
    logger.info(f"Updating status for document ID {document_id} to {new_status.value}. Error: '{error_message if error_message else 'None'}'")
    db_document = await get_document_record(db, document_id=document_id)
    if not db_document:
        logger.warning(f"Attempted to update status for non-existent document ID {document_id}")
        return None

    db_document.status = new_status 
    db_document.error_message = error_message if new_status == DocumentStatus.ERROR else None
    if new_status == DocumentStatus.COMPLETED or new_status == DocumentStatus.ERROR:
        db_document.processed_at = datetime.now(timezone.utc) 
    elif db_document.processed_at and new_status not in [DocumentStatus.COMPLETED, DocumentStatus.ERROR]:
        if db_document.status not in [
            DocumentStatus.PROCESSING_TEXT, DocumentStatus.CHUNKING, 
            DocumentStatus.PREPARING_CONTEXT, DocumentStatus.STORING_CONTEXT, 
            DocumentStatus.PENDING, DocumentStatus.UPLOADED
        ]:
             db_document.processed_at = None
    db.add(db_document)
    try:
        await db.commit()
        await db.refresh(db_document)
        logger.info(f"Document ID {document_id} status updated to {db_document.status.value if db_document.status else 'N/A'}.")
        return db_document
    except Exception as e_commit:
        await db.rollback()
        logger.error(f"Error committing status update for doc ID {document_id}: {e_commit}", exc_info=True)
        raise

async def delete_document_record_and_blob( 
    db: AsyncSession, 
    document_id: int, 
    user_id: int,
    background_tasks: Optional[BackgroundTasks] = None 
) -> Optional[UploadedDocument]:
    """Delete document record and blob."""
    logger.info(f"User ID {user_id} attempting delete of doc record ID: {document_id} and its blob.")
    db_document = await get_document_record_for_user(db, document_id=document_id, user_id=user_id)
    if not db_document: 
        logger.warning(f"Doc record ID {document_id} not found/owned by user ID {user_id} for deletion."); return None
    blob_path_to_delete = db_document.blob_storage_path
    await db.delete(db_document)
    try:
        await db.commit()
        logger.info(f"Document record ID {document_id} deleted from database.")
        if background_tasks and blob_path_to_delete:
            from app.services.storage_service import delete_blob
            container_name = "documents"
            background_tasks.add_task(delete_blob, container_name=container_name, blob_name=blob_path_to_delete)
            background_tasks.add_task(
                delete_blob,
                container_name=container_name,
                blob_name=f"{blob_path_to_delete}.extracted.txt",
            )
            logger.info(f"Scheduled blob deletion for: {blob_path_to_delete} in container {container_name}")
        elif blob_path_to_delete:
            logger.warning(f"BackgroundTasks not provided for doc ID {document_id}. Blob '{blob_path_to_delete}' not scheduled for deletion by this func.")
        return db_document 
    except Exception as e: 
        await db.rollback(); logger.error(f"Error during DB deletion of doc record ID {document_id}: {e}", exc_info=True); raise

async def delete_generated_document_records(
    db: AsyncSession, 
    source_element_type: SourceElementTypeEnum, 
    source_element_id: int,
    world_id: int,
    user_id: int,
    background_tasks: Optional[BackgroundTasks] = None
) -> int:
    """Delete generated document records."""
    logger.info(f"Deleting generated doc records for {source_element_type.value} ID: {source_element_id}, World: {world_id}, User: {user_id}")
    query_conditions = [UploadedDocument.source_element_type == source_element_type, UploadedDocument.world_id == world_id, UploadedDocument.user_id == user_id]
    if source_element_type == SourceElementTypeEnum.CHARACTER_LORE: query_conditions.append(UploadedDocument.source_character_id == source_element_id)
    elif source_element_type == SourceElementTypeEnum.LOCATION_LORE: query_conditions.append(UploadedDocument.source_location_id == source_element_id)
    elif source_element_type == SourceElementTypeEnum.LORE_ITEM_LORE: query_conditions.append(UploadedDocument.source_lore_item_id == source_element_id)
    else: logger.error(f"Invalid source_element_type '{source_element_type}'"); return 0
    stmt_select = select(UploadedDocument).where(*query_conditions); result_select = await db.execute(stmt_select); records_to_delete = result_select.scalars().all()
    if not records_to_delete: logger.info(f"No generated doc records found for {source_element_type.value} ID: {source_element_id}"); return 0
    blob_paths_to_delete = [rec.blob_storage_path for rec in records_to_delete if rec.blob_storage_path]; record_ids_to_delete = [rec.id for rec in records_to_delete if rec.id is not None]
    if not record_ids_to_delete: logger.info("No valid record IDs to delete"); return 0
    stmt_delete = delete(UploadedDocument).where(UploadedDocument.id.in_(record_ids_to_delete))
    try:
        result_delete = await db.execute(stmt_delete); await db.commit(); deleted_db_count = result_delete.rowcount
        logger.info(f"Deleted {deleted_db_count} generated doc DB records for {source_element_type.value} ID: {source_element_id}.")
        if background_tasks and blob_paths_to_delete:
            from app.services.storage_service import delete_blob
            container_for_generated = "documents"
            for blob_path in blob_paths_to_delete: background_tasks.add_task(delete_blob, container_name=container_for_generated, blob_name=blob_path)
            logger.info(f"Scheduled deletion for {len(blob_paths_to_delete)} blobs.")
        elif blob_paths_to_delete: logger.warning(f"BackgroundTasks not provided. {len(blob_paths_to_delete)} blobs not scheduled for deletion here.")
        return deleted_db_count
    except Exception as e: await db.rollback(); logger.error(f"Error deleting generated doc records for {source_element_type.value} ID: {source_element_id}: {e}", exc_info=True); raise

