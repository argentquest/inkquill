# /ai_rag_story_app/app/services/azure_ai_search_service.py
import logging
from typing import List, Dict, Any, Optional

from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError, ServiceRequestError, ResourceNotFoundError, HttpResponseError
)
# Ensure these are the ASYNC versions
from azure.search.documents.aio import SearchClient 
from azure.search.documents.indexes.aio import SearchIndexClient

logger = logging.getLogger(__name__)

class AzureAISearchService:
    def __init__(self, endpoint: Optional[str], api_key: Optional[str], index_name: str):
        self.endpoint: Optional[str] = endpoint
        self.api_key: Optional[str] = api_key
        self.index_name: str = index_name

        self.search_client: Optional[SearchClient] = None # This will be the async client
        self.index_client: Optional[SearchIndexClient] = None # This will be the async client
        self.credential: Optional[AzureKeyCredential] = None

        if not self.endpoint or not self.api_key or not self.index_name:
            logger.error(f"AzureAISearchService __init__: Insufficient config. Endpoint: '{self.endpoint}', API Key Set: {bool(self.api_key)}, Index: '{self.index_name}'")
            self._clear_clients() # Ensure clients are None if config is bad
            return

        try:
            logger.info(f"AzureAISearchService: Initializing async clients for endpoint: '{self.endpoint}', index: '{self.index_name}'")
            self.credential = AzureKeyCredential(self.api_key)
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=self.credential
            )
            self.index_client = SearchIndexClient(
                endpoint=self.endpoint,
                credential=self.credential
            )
            logger.info(f"AzureAISearchService: Async clients configured for index: '{self.index_name}'.")
            # Initial connectivity test (optional, can be deferred to first operation)
            # async def _verify_connection():
            #     if self.index_client: await self.index_client.get_index(self.index_name)
            # try: asyncio.run(_verify_connection()) logger.info("Verified index access.")
            # except Exception as ve: logger.warning(f"Could not verify index access during init: {ve}")
            
        except Exception as e:
            logger.error(f"AzureAISearchService: Unexpected error initializing clients: {e}", exc_info=True)
            self._clear_clients()

    def _clear_clients(self):
        self.search_client = None
        self.index_client = None
        # self.credential = None # Credential can be kept if re-init is attempted

    async def close_async_clients(self): # <<< CORRECT METHOD NAME
        logger.info("AzureAISearchService: Attempting to close async clients.")
        closed_search = False
        closed_index = False
        if self.search_client:
            try:
                await self.search_client.close()
                closed_search = True
            except Exception as e:
                logger.error(f"AzureAISearchService: Error closing async search_client: {e}", exc_info=True)
        if self.index_client:
            try:
                await self.index_client.close()
                closed_index = True
            except Exception as e:
                logger.error(f"AzureAISearchService: Error closing async index_client: {e}", exc_info=True)
        
        self._clear_clients() # Nullify after attempting close
        if closed_search and closed_index:
            logger.info("AzureAISearchService: Async clients closed successfully.")
        else:
            logger.warning("AzureAISearchService: One or more async clients might not have closed cleanly.")


    def get_search_client(self) -> Optional[SearchClient]: # Synchronous getter for the async client instance
        # This method is mainly for checking if the client attribute is set.
        # Actual operations should use async methods.
        if not self.search_client:
            logger.warning("AzureAISearchService: Search client (async instance) accessed via sync getter but is not available.")
        return self.search_client

    async def perform_search_async(self, query_text: str, top_k: int = 5, **kwargs) -> List[Dict[str, Any]]:
        if not self.search_client:
            raise ConnectionError("Async Search client unavailable. Check service initialization.")
        try:
            results = await self.search_client.search(search_text=query_text, top=top_k, include_total_count=True, **kwargs)
            documents = []
            async for doc in results:
                documents.append(dict(doc))
            count_val = "N/A"
            try: count_val = await results.get_count() # get_count is async
            except AttributeError: logger.warning("get_count() not available on results object for this search type.")
            
            logger.info(f"Search returned {len(documents)} of ~{count_val} total documents.")
            return documents
        except Exception as e:
            logger.error(f"Unexpected error during async search: {e}", exc_info=True)
            raise

    async def upload_documents_async(self, documents: List[Dict[str, Any]]) -> List[Any]:
        if not self.search_client:
            raise ConnectionError("Async Search client unavailable for upload.")
        if not documents: return []
        try:
            result_objects = await self.search_client.upload_documents(documents=documents)
            succeeded_count = sum(1 for r in result_objects if r.succeeded)
            if succeeded_count < len(documents):
                logger.warning(f"AzureAISearchService: {len(documents) - succeeded_count} documents failed to upload.")
                for i, r_item in enumerate(result_objects):
                    if not r_item.succeeded:
                        doc_key_info = r_item.key if hasattr(r_item, 'key') else f"input_idx_{i}"
                        error_msg = getattr(r_item.error, 'message', "Unknown upload error") if r_item.error else "Unknown upload error"
                        status_code_info = f"(Status: {r_item.status_code})" if hasattr(r_item, 'status_code') else ""
                        logger.error(f"  Upload fail for doc '{doc_key_info}': {error_msg} {status_code_info}")
            logger.info(f"AzureAISearchService: Uploaded {succeeded_count}/{len(documents)} documents asynchronously.")
            return result_objects
        except Exception as e:
            logger.error(f"Unexpected error uploading documents asynchronously: {e}", exc_info=True)
            raise

    async def delete_documents_by_filter_async(self, filter_string: str) -> bool: # <<< CORRECT METHOD NAME
        if not self.search_client:
            logger.error("AzureAISearchService: Async Search client not available for delete_documents_by_filter_async.")
            return False
        
        if not filter_string:
            logger.warning("AzureAISearchService: delete_documents_by_filter_async called with an empty filter. No deletion performed.")
            return True # No error, but nothing to do.

        try:
            key_field_name = "id" # Assuming 'id' is your key field based on aisearch.json
            logger.info(f"AzureAISearchService: Finding documents with filter: '{filter_string}' for deletion (key field: '{key_field_name}').")
            
            # The SearchClient might not have key_field_name directly. It's part of the index definition.
            # We know our key field is 'id' from the schema.
            
            search_results = await self.search_client.search(search_text="*", filter=filter_string, select=[key_field_name])
            
            documents_to_delete = []
            async for result in search_results:
                if key_field_name in result:
                    documents_to_delete.append({key_field_name: result[key_field_name]})
                else:
                    logger.warning(f"AzureAISearchService: Document found by filter but key field '{key_field_name}' missing in result: {result}")

            if not documents_to_delete:
                logger.info(f"AzureAISearchService: No documents found matching filter '{filter_string}' for deletion.")
                return True

            logger.info(f"AzureAISearchService: Found {len(documents_to_delete)} documents to delete. Submitting delete request.")
            delete_results = await self.search_client.delete_documents(documents=documents_to_delete)
            
            all_succeeded = True
            for i, result_item in enumerate(delete_results):
                if not result_item.succeeded:
                    all_succeeded = False
                    doc_key_info = documents_to_delete[i].get(key_field_name, f"unknown_key_at_index_{i}")
                    error_msg = getattr(result_item.error, 'message', "Unknown delete error") if result_item.error else "Unknown delete error"
                    status_code_info = f"(Status: {result_item.status_code})" if hasattr(result_item, 'status_code') else ""
                    logger.error(f"AzureAISearchService: Failed to delete document '{doc_key_info}': {error_msg} {status_code_info}")
            
            if all_succeeded:
                logger.info(f"AzureAISearchService: Successfully submitted deletion for {len(documents_to_delete)} documents with filter: {filter_string}")
            else:
                logger.warning(f"AzureAISearchService: Some documents failed to delete for filter: {filter_string}.")
            return all_succeeded

        except HttpResponseError as e_http:
            logger.error(f"AzureAISearchService: HTTP error during deletion by filter '{filter_string}'. Status: {e_http.status_code}. Error: {e_http.message}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"AzureAISearchService: Unexpected error during deletion by filter '{filter_string}': {e}", exc_info=True)
            return False

    # Synchronous upload_documents - kept for potential existing sync calls
    def upload_documents(self, documents: List[Dict[str, Any]]) -> List[Any]:
        logger.warning("AzureAISearchService: Synchronous 'upload_documents' called. Prefer 'upload_documents_async'.")
        if not self.search_client:
             raise ConnectionError("Search client unavailable. Check service initialization.")
        try:
            # Note: This directly calls the sync method on what is now an async client.
            # This might not work as expected if the underlying transport is strictly async.
            # For robust sync operations, a separate sync client instance would be better.
            # However, the SDK might handle this gracefully for simple cases.
            # The azure-search-documents client objects are typically distinct for sync/async.
            # Re-initializing a sync client here or having two instances (sync/async) would be safer.
            # For now, this reflects previous structure but with a warning.
            
            # To make this truly work synchronously if self.search_client is async:
            # return asyncio.run(self.search_client.upload_documents(documents=documents))
            # But that's bad practice to call asyncio.run from within an async app.
            # The best is to make the caller async. If not possible, use a sync SearchClient.
            # For now, this line below will likely cause issues if self.search_client is async.
            # We should assume callers will use upload_documents_async.
            logger.error("AzureAISearchService: Attempted to use synchronous upload_documents with an async client. This is not supported. Use upload_documents_async.")
            raise NotImplementedError("Synchronous upload_documents is not correctly implemented with an async client.")
            # return self.search_client.upload_documents(documents=documents) # This line is problematic
        except Exception as e:
             logger.error(f"Error in synchronous upload_documents: {e}", exc_info=True)
             raise