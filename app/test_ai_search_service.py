# test_ai_search_service.py
# Standalone test script specifically for Azure AI Search service.
# - Verifies connectivity by getting index statistics.
# - Tests basic document operations (upload, get, delete) on the specified index.
# Loads configuration from a .env file or system environment variables.
# Logs output to a timestamped file (e.g., test_ai_search_YYYY-MM-DD_HH-MM-SS.log).

import os
import asyncio
import uuid # For generating unique document IDs for testing
from typing import Optional
import logging
from datetime import datetime, timezone # Added timezone for uploaded_at
from dotenv import load_dotenv

# Azure SDK Imports
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
# from azure.search.documents.indexes.models import IndexStatistics # Removed problematic import
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

# --- Setup Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
current_time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file_name = f'test_ai_search_{current_time_str}.log'
file_handler = logging.FileHandler(log_file_name, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# --- Load Environment Variables from .env file ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
logger.info(f"Attempting to load .env file from: {dotenv_path}")
if os.path.exists(dotenv_path):
    loaded_from_env_file = load_dotenv(dotenv_path=dotenv_path, override=True)
    if loaded_from_env_file:
        logger.info(f"Successfully loaded variables from: {dotenv_path}")
    else:
        logger.warning(f".env file found at {dotenv_path}, but no variables were loaded.")
else:
    logger.info(f".env file not found. Relying on system environment variables or script defaults.")

# --- Configuration Loading for Azure AI Search ---
logger.info("--- Loading Azure AI Search Configuration ---")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_SERVICE_ENDPOINT", "AI_SEARCH_ENDPOINT_NOT_SET_IN_ENV")
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY", "AI_SEARCH_API_KEY_NOT_SET_IN_ENV")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME", "rag-app-content-index") # Your target RAG index

# For dummy document vector - adjust dimension based on your index schema
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "3072"))


def print_loaded_configuration():
    """Prints the loaded configuration values for AI Search."""
    logger.info("\n--- Loaded Configuration Values (test_ai_search_service.py) ---")
    logger.info(f"AZURE_AI_SEARCH_ENDPOINT: {AZURE_AI_SEARCH_ENDPOINT}")
    logger.info(f"AZURE_AI_SEARCH_API_KEY: {'********' if AZURE_AI_SEARCH_API_KEY and not AZURE_AI_SEARCH_API_KEY.endswith('_NOT_SET_IN_ENV') else AZURE_AI_SEARCH_API_KEY}")
    logger.info(f"AZURE_AI_SEARCH_INDEX_NAME: {AZURE_AI_SEARCH_INDEX_NAME}")
    logger.info(f"EMBEDDING_DIMENSION (for dummy vector): {EMBEDDING_DIMENSION}")
    logger.info(f"LOG_FILE_NAME: {log_file_name}")
    logger.info("---------------------------------")

async def test_get_index_statistics():
    """Tests basic connectivity by getting statistics for the specified index."""
    logger.info("\n--- Testing Azure AI Search: Get Index Statistics ---")

    if any(val.endswith("_NOT_SET_IN_ENV") for val in [AZURE_AI_SEARCH_ENDPOINT, AZURE_AI_SEARCH_API_KEY, AZURE_AI_SEARCH_INDEX_NAME]):
        logger.warning("WARNING: Azure AI Search configuration uses placeholders. Skipping get index statistics test.")
        logger.info("--- Get Index Statistics Test Skipped ---")
        return False

    search_index_client = None
    success = False
    try:
        logger.info(f"Attempting to connect to Endpoint: {AZURE_AI_SEARCH_ENDPOINT}")
        logger.info(f"Target Index Name: {AZURE_AI_SEARCH_INDEX_NAME}")

        search_credential = AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)
        search_index_client = SearchIndexClient(endpoint=AZURE_AI_SEARCH_ENDPOINT, credential=search_credential)

        logger.info(f"Attempting to get statistics for index '{AZURE_AI_SEARCH_INDEX_NAME}'...")
        index_stats = await search_index_client.get_index_statistics(index_name=AZURE_AI_SEARCH_INDEX_NAME)
        
        # The get_index_statistics method returns an object that might behave like a dict
        # or have attributes. We try to access them robustly.
        doc_count = getattr(index_stats, 'document_count', None)
        if doc_count is None and isinstance(index_stats, dict): # Fallback for dict-like objects
            doc_count = index_stats.get('document_count', 'N/A')
        
        storage_size = getattr(index_stats, 'storage_size', None)
        if storage_size is None and isinstance(index_stats, dict): # Fallback for dict-like objects
            storage_size = index_stats.get('storage_size', 'N/A')

        logger.info(f"SUCCESS: Retrieved stats for index '{AZURE_AI_SEARCH_INDEX_NAME}'.")
        logger.info(f"  Document Count: {doc_count if doc_count is not None else 'N/A'}")
        logger.info(f"  Storage Size (bytes): {storage_size if storage_size is not None else 'N/A'}")
        
        if doc_count == 'N/A' or storage_size == 'N/A':
            logger.warning("Could not reliably access document_count or storage_size. Stats object structure might have changed.")
            logger.info(f"Raw stats object type: {type(index_stats)}")
            logger.info(f"Raw stats object content: {index_stats}") # Log raw object for inspection
        
        success = True
        logger.info("--- Get Index Statistics Test Complete ---")

    except ResourceNotFoundError:
        logger.error(f"FAILURE: Index '{AZURE_AI_SEARCH_INDEX_NAME}' not found at '{AZURE_AI_SEARCH_ENDPOINT}'.")
        logger.info("   Please ensure the index has been created with the schema from 'azure_ai_search_schema_json_v1'.")
    except TypeError as te: 
        logger.error(f"FAILURE: TypeError during get index statistics. This might indicate an SDK version mismatch or incorrect parameter name. Error: {te}")
        logger.info("   Parameter used was 'index_name'. If this fails, try 'name'. Check SDK documentation for your installed version.")
    except HttpResponseError as e_http:
        logger.error(f"FAILURE: HTTP error during get index statistics. Status: {e_http.status_code}. Error: {e_http.message}")
        if hasattr(e_http, "reason"): logger.error(f"   Reason: {e_http.reason}")
    except Exception as e:
        logger.error(f"FAILURE: Error during get index statistics. Error: {type(e).__name__}: {e}")
    finally:
        if search_index_client:
            await search_index_client.close()
        if not success:
            logger.info("--- Get Index Statistics Test Failed ---")
        return success

async def test_ai_search_document_operations():
    """Tests basic document operations (upload, get, delete) on the Azure AI Search index."""
    logger.info("\n--- Testing Azure AI Search: Document Operations (Upload, Get, Delete) ---")

    if any(val.endswith("_NOT_SET_IN_ENV") for val in [AZURE_AI_SEARCH_ENDPOINT, AZURE_AI_SEARCH_API_KEY, AZURE_AI_SEARCH_INDEX_NAME]):
        logger.warning("WARNING: Azure AI Search configuration uses placeholders. Skipping document operations test.")
        logger.info("--- Document Operations Test Skipped ---")
        return False

    search_client = None
    test_doc_id = f"maintest-doc-{uuid.uuid4()}" 
    dummy_document = {
        "id": test_doc_id,
        "document_id": "test_parent_doc_001", 
        "user_id": "test_user_ai_search",     
        "source_filename": "test_ai_search_operations.txt",
        "chunk_text": "This is a test document chunk uploaded by maintest_sk_logic.py for Azure AI Search testing.",
        "chunk_text_vector": [0.01] * EMBEDDING_DIMENSION, 
        "uploaded_at": datetime.now(timezone.utc).isoformat(), 
        "tags": ["test", "maintest"],
    }
    success = False

    try:
        logger.info(f"Initializing SearchClient for index '{AZURE_AI_SEARCH_INDEX_NAME}' at endpoint '{AZURE_AI_SEARCH_ENDPOINT}'.")
        search_credential = AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)
        search_client = SearchClient(
            endpoint=AZURE_AI_SEARCH_ENDPOINT,
            index_name=AZURE_AI_SEARCH_INDEX_NAME,
            credential=search_credential
        )

        logger.info(f"Attempting to upload test document with id: {test_doc_id}")
        upload_results = await search_client.upload_documents(documents=[dummy_document])
        if not upload_results[0].succeeded:
            error_detail = upload_results[0].error_message if hasattr(upload_results[0], 'error_message') and upload_results[0].error_message else (upload_results[0].error.message if hasattr(upload_results[0], 'error') and upload_results[0].error else "Unknown upload error.")
            status_code_detail = f"(Status: {upload_results[0].status_code})" if hasattr(upload_results[0], 'status_code') and upload_results[0].status_code else ""
            raise Exception(f"Failed to upload test document '{upload_results[0].key}': {error_detail} {status_code_detail}")
        logger.info("SUCCESS: Test document uploaded.")
        
        await asyncio.sleep(2) 

        logger.info(f"Attempting to retrieve test document by id: {test_doc_id}")
        retrieved_doc = await search_client.get_document(key=test_doc_id)
        assert retrieved_doc is not None, f"Failed to retrieve uploaded test document by ID '{test_doc_id}'."
        assert retrieved_doc["chunk_text"] == dummy_document["chunk_text"], "Retrieved document content mismatch."
        logger.info("SUCCESS: Test document retrieved and content verified.")

        search_text_query = "test document chunk maintest_sk_logic.py" 
        logger.info(f"Attempting simple keyword search for text: '{search_text_query}'")
        search_results = await search_client.search(search_text=search_text_query, select=["id", "chunk_text"])
        
        found_in_search = False
        async for result in search_results:
            logger.info(f"  Search result found: id='{result['id']}', text='{result['chunk_text'][:50]}...'")
            if result["id"] == test_doc_id:
                found_in_search = True
                break
        assert found_in_search, f"Uploaded test document '{test_doc_id}' not found via keyword search for '{search_text_query}'."
        logger.info("SUCCESS: Test document found via simple keyword search.")
        success = True
        logger.info("--- Document Operations Test Complete ---")

    except ResourceNotFoundError:
        logger.error(f"FAILURE: Index '{AZURE_AI_SEARCH_INDEX_NAME}' not found at '{AZURE_AI_SEARCH_ENDPOINT}'.")
        logger.info("   Please ensure the index has been created with the schema from 'azure_ai_search_schema_json_v1'.")
    except HttpResponseError as e_http:
        logger.error(f"FAILURE: HTTP error during Azure AI Search document operations. Status: {e_http.status_code}. Error: {e_http.message}")
        if hasattr(e_http, "reason"): logger.error(f"   Reason: {e_http.reason}")
    except Exception as e:
        logger.error(f"FAILURE: Error during Azure AI Search document operations. Error: {type(e).__name__}: {e}")
    finally:
        if search_client and test_doc_id: 
            try:
                logger.info(f"Attempting to delete test document: {test_doc_id}")
                await search_client.delete_documents(documents=[{"id": test_doc_id}])
                logger.info("SUCCESS: Test document deleted from search index.")
            except ResourceNotFoundError:
                logger.info(f"Test document '{test_doc_id}' not found for deletion (might have failed to upload or already deleted).")
            except Exception as e_del:
                logger.error(f"ERROR deleting test document '{test_doc_id}' from search index: {e_del}")
        
        if search_client:
            await search_client.close()
        if not success: 
             logger.info("--- Document Operations Test Failed ---")
        return success


async def main():
    """Runs all Azure AI Search specific tests."""
    logger.info(f"Starting test_ai_search_service.py script... Log file: {log_file_name}")
    print_loaded_configuration()
    
    stats_success = await test_get_index_statistics()
    if stats_success: 
        await test_ai_search_document_operations()
    else:
        logger.warning("Skipping document operations test due to failure in getting index statistics.")
        
    logger.info("test_ai_search_service.py script finished.")

if __name__ == "__main__":
    asyncio.run(main())
