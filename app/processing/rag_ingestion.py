# /ai_rag_story_app/app/processing/rag_ingestion.py

import os
import uuid
import logging
import shutil
import tempfile
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession
from app.core.config import settings
from app.db.database import async_session_local
from app.services.azure_ai_search_service import AzureAISearchService
from app.services.embedding_service import generate_embeddings
from app.processing.text_extraction import extract_text_from_file_path
from app.processing.chunking import chunk_text_fixed_size_with_overlap
from app.crud import document as crud_document
from app.crud import job_status as crud_job_status
from app.models.uploaded_document import DocumentStatus, SourceElementTypeEnum
from app.models.job_status import JobStateEnum

logger = logging.getLogger(__name__)

class RAGIngestionError(Exception):
    pass

async def process_uploaded_document_task(
    job_id: str,
    db_document_id: int,
    file_path_on_disk: str,
):
    """Process an uploaded document for RAG indexing"""
    logger.info(f"JOB_ID: {job_id} - Starting document processing for DB doc ID: {db_document_id}")
    search_service_instance: Optional[AzureAISearchService] = None
    
    async with async_session_local() as db:
        try:
            # Update job status to running
            await crud_job_status.update_job_status(db, job_id, JobStateEnum.RUNNING, "Processing document...")
            
            # Get document record
            document = await crud_document.get_document_record(db, db_document_id)
            if not document:
                raise RAGIngestionError(f"Document with ID {db_document_id} not found")
            
            # Initialize Azure AI Search
            if not settings.AZURE_AI_SEARCH_ENDPOINT or not settings.AZURE_AI_SEARCH_API_KEY:
                raise RAGIngestionError("Azure AI Search service configuration is missing.")
            
            search_service_instance = AzureAISearchService(
                endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT),
                api_key=settings.AZURE_AI_SEARCH_API_KEY,
                index_name=settings.AZURE_AI_SEARCH_INDEX_NAME
            )
            
            if not search_service_instance.search_client:
                raise RAGIngestionError("Failed to initialize Azure AI Search client.")
            
            # Extract text from file
            await crud_document.update_document_status(db, db_document_id, DocumentStatus.PROCESSING_TEXT)
            extracted_text = await extract_text_from_file_path(file_path_on_disk, document.filename)
            
            if not extracted_text or extracted_text.isspace():
                raise RAGIngestionError("No text could be extracted from the document")
            
            logger.info(f"JOB_ID: {job_id} - Extracted {len(extracted_text)} characters from document")
            
            # Upload to blob storage if configured
            if settings.AZURE_STORAGE_CONNECTION_STRING or settings.AZURE_STORAGE_ACCOUNT_NAME:
                logger.info(f"JOB_ID: {job_id} - Uploading to blob: {document.blob_storage_path}")
                
                if settings.AZURE_STORAGE_CONNECTION_STRING:
                    from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
                    blob_service_client = AsyncBlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
                elif settings.AZURE_STORAGE_ACCOUNT_NAME:
                    from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
                    from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
                    account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
                    credential = AsyncDefaultAzureCredential()
                    blob_service_client = AsyncBlobServiceClient(account_url=account_url, credential=credential)
                
                async with blob_service_client:
                    blob_client = blob_service_client.get_blob_client(
                        container=settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS,
                        blob=document.blob_storage_path
                    )
                    # Upload original file
                    with open(file_path_on_disk, 'rb') as file_data:
                        await blob_client.upload_blob(file_data, overwrite=True)
                    
                    # Also upload extracted text
                    text_blob_path = document.blob_storage_path + ".extracted.txt"
                    text_blob_client = blob_service_client.get_blob_client(
                        container=settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS,
                        blob=text_blob_path
                    )
                    await text_blob_client.upload_blob(extracted_text.encode('utf-8'), overwrite=True)
                
                logger.info(f"JOB_ID: {job_id} - Successfully uploaded to blob storage")
            
            # Chunk the text
            await crud_document.update_document_status(db, db_document_id, DocumentStatus.CHUNKING)
            text_chunks = chunk_text_fixed_size_with_overlap(
                extracted_text, 
                settings.DEFAULT_CHUNK_SIZE_TOKENS, 
                settings.DEFAULT_CHUNK_OVERLAP_TOKENS
            )
            
            if not text_chunks:
                raise RAGIngestionError("No chunks created from extracted text")
            
            logger.info(f"JOB_ID: {job_id} - Created {len(text_chunks)} text chunks")
            
            # Generate embeddings
            await crud_document.update_document_status(db, db_document_id, DocumentStatus.GENERATING_EMBEDDINGS)
            chunk_embeddings = await generate_embeddings(text_chunks, user_id=document.user_id)
            
            if not chunk_embeddings or len(chunk_embeddings) != len(text_chunks):
                raise RAGIngestionError("Failed to generate embeddings for all chunks")
            
            # Prepare documents for search index
            docs_for_search_index = []
            for i, chunk_text in enumerate(text_chunks):
                docs_for_search_index.append({
                    "id": f"doc{db_document_id}_chunk{i}_{uuid.uuid4().hex[:8]}",
                    "document_id": str(db_document_id),
                    "user_id": str(document.user_id),
                    "source_filename": document.filename,
                    "chunk_text": chunk_text,
                    "chunk_text_vector": chunk_embeddings[i],
                    "uploaded_at": datetime.utcnow().isoformat() + "Z",
                    "world_id": str(document.world_id) if document.world_id else None,
                    "element_type": "uploaded_document",
                    "source_element_id": str(db_document_id)
                })
            
            # Upload to search index
            await crud_document.update_document_status(db, db_document_id, DocumentStatus.INDEXING)
            upload_results = await search_service_instance.upload_documents_async(docs_for_search_index)
            succeeded_count = sum(1 for r in upload_results if r.succeeded)
            
            if succeeded_count == len(docs_for_search_index):
                await crud_document.update_document_status(db, db_document_id, DocumentStatus.COMPLETED)
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.COMPLETED, 
                    f"Successfully processed {len(text_chunks)} chunks")
                logger.info(f"JOB_ID: {job_id} - Successfully completed document processing")
            else:
                raise RAGIngestionError(f"Partial indexing success: {succeeded_count}/{len(docs_for_search_index)} chunks")
            
        except Exception as e:
            error_message = f"Error processing document: {str(e)[:500]}"
            logger.error(f"JOB_ID: {job_id} - {error_message}", exc_info=True)
            
            try:
                await crud_document.update_document_status(db, db_document_id, DocumentStatus.ERROR, error_message)
                await crud_job_status.update_job_status(db, job_id, JobStateEnum.FAILED, error_message)
            except Exception as update_error:
                logger.error(f"JOB_ID: {job_id} - Failed to update error status: {update_error}")
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(file_path_on_disk):
                    temp_dir = os.path.dirname(file_path_on_disk)
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info(f"JOB_ID: {job_id} - Cleaned up temporary file")
            except Exception as cleanup_error:
                logger.warning(f"JOB_ID: {job_id} - Failed to cleanup temp file: {cleanup_error}")
            
            # Close search service
            if search_service_instance:
                await search_service_instance.close_async_clients()

async def process_generated_text_for_rag(
    db: AsyncSession, # --- FIX: Accept the db session as the first argument ---
    db_document_id: int,
    generated_text_content: str,
    original_filename: str,
    blob_storage_path: str,
    user_id_for_index: int,
    world_id_for_index: int,
    element_type_for_index_str: str,
    source_id_for_index: str
):
    logger.info(f"RAG Processing (Generated Text): Starting for DB doc ID: {db_document_id}, Element: {element_type_for_index_str} ID: {source_id_for_index}")
    search_service_instance: Optional[AzureAISearchService] = None
    
    # --- FIX: We no longer create a new session here, we use the one passed in ---
    # async with async_session_local() as db:
    try:
        if not settings.AZURE_AI_SEARCH_ENDPOINT or not settings.AZURE_AI_SEARCH_API_KEY:
            raise RAGIngestionError("Azure AI Search service configuration is missing.")
        search_service_instance = AzureAISearchService(
            endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT),
            api_key=settings.AZURE_AI_SEARCH_API_KEY,
            index_name=settings.AZURE_AI_SEARCH_INDEX_NAME
        )
        if not search_service_instance.search_client:
            raise RAGIngestionError("Failed to initialize Azure AI Search client.")

        if settings.AZURE_STORAGE_CONNECTION_STRING or settings.AZURE_STORAGE_ACCOUNT_NAME:
            logger.info(f"RAG GEN (ID {db_document_id}): Uploading content to Blob: {settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS}/{blob_storage_path}")
            if settings.AZURE_STORAGE_CONNECTION_STRING:
                from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
                blob_service_client_for_upload_async = AsyncBlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
            elif settings.AZURE_STORAGE_ACCOUNT_NAME:
                from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
                from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
                account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
                credential_for_upload_async = AsyncDefaultAzureCredential()
                blob_service_client_for_upload_async = AsyncBlobServiceClient(account_url=account_url, credential=credential_for_upload_async)
            
            if blob_service_client_for_upload_async:
                async with blob_service_client_for_upload_async:
                    blob_client = blob_service_client_for_upload_async.get_blob_client(container=settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS, blob=blob_storage_path)
                    await blob_client.upload_blob(generated_text_content.encode('utf-8'), overwrite=True)
                logger.info(f"RAG GEN (ID {db_document_id}): Generated text content successfully uploaded to blob.")
        else:
            logger.warning(f"RAG GEN (ID {db_document_id}): Azure Storage not configured. Skipping blob upload.")

        await crud_document.update_document_status(db, db_document_id, DocumentStatus.CHUNKING)
        if not generated_text_content or generated_text_content.isspace():
            raise RAGIngestionError("Generated text content for RAG is empty.")
        
        text_chunks = chunk_text_fixed_size_with_overlap(generated_text_content, settings.DEFAULT_CHUNK_SIZE_TOKENS, settings.DEFAULT_CHUNK_OVERLAP_TOKENS)
        if not text_chunks: raise RAGIngestionError("No chunks created from generated text.")

        await crud_document.update_document_status(db, db_document_id, DocumentStatus.GENERATING_EMBEDDINGS)
        chunk_embeddings = await generate_embeddings(text_chunks, user_id=user_id_for_index)
        if not chunk_embeddings or len(chunk_embeddings) != len(text_chunks):
            raise RAGIngestionError("Failed to generate embeddings for all chunks of generated text.")

        docs_for_search_index = []
        for i, chunk_text in enumerate(text_chunks):
            docs_for_search_index.append({
                "id": f"gen_doc{db_document_id}_chunk{i}_{uuid.uuid4().hex[:8]}", "document_id": str(db_document_id),
                "user_id": str(user_id_for_index), "source_filename": original_filename,
                "chunk_text": chunk_text, "chunk_text_vector": chunk_embeddings[i],
                "uploaded_at": datetime.utcnow().isoformat() + "Z",
                "world_id": str(world_id_for_index), "element_type": element_type_for_index_str,
                "source_element_id": str(source_id_for_index)
            })

        await crud_document.update_document_status(db, db_document_id, DocumentStatus.INDEXING)
        upload_results = await search_service_instance.upload_documents_async(docs_for_search_index)
        succeeded_count = sum(1 for r in upload_results if r.succeeded)

        if succeeded_count == len(docs_for_search_index):
            await crud_document.update_document_status(db, db_document_id, DocumentStatus.COMPLETED)
        else:
            raise RAGIngestionError(f"Partial success: Indexed {succeeded_count}/{len(docs_for_search_index)} generated text chunks.")

        logger.info(f"RAG GEN (ID {db_document_id}): Indexing complete. Succeeded: {succeeded_count}")

    except Exception as e:
        error_message = f"Error processing generated text for RAG: {str(e)[:500]}"
        logger.error(f"RAG GEN (ID {db_document_id}): {error_message}", exc_info=True)
        # Use the passed-in session to update status
        await crud_document.update_document_status(db, db_document_id, DocumentStatus.ERROR, error_message)
    finally:
        if search_service_instance: await search_service_instance.close_async_clients()