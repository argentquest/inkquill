# /ai_rag_story_app/app/services/azure_blob_service.py

import logging
from typing import Optional

from azure.core.exceptions import ResourceNotFoundError
from app.core.config import settings

logger = logging.getLogger(__name__)

async def delete_blob(container_name: str, blob_name: str):
    """
    Asynchronously deletes a single blob from the specified container.
    """
    logger.info(f"BLOB_SERVICE: Attempting to delete blob '{blob_name}' from container '{container_name}'.")
    
    blob_service_client_async = None
    credential_for_storage_async = None
    
    try:
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            from azure.storage.blob.aio import BlobServiceClient
            blob_service_client_async = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME:
            from azure.identity.aio import DefaultAzureCredential
            from azure.storage.blob.aio import BlobServiceClient
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential_for_storage_async = DefaultAzureCredential()
            blob_service_client_async = BlobServiceClient(account_url=account_url, credential=credential_for_storage_async)
        else:
            logger.error("BLOB_SERVICE: Azure Storage not configured for blob deletion. Cannot proceed.")
            return

        async with blob_service_client_async:
            blob_client = blob_service_client_async.get_blob_client(container=container_name, blob=blob_name)
            await blob_client.delete_blob(delete_snapshots="include")
            logger.info(f"BLOB_SERVICE: Successfully deleted blob '{blob_name}' from container '{container_name}'.")

    except ResourceNotFoundError:
        logger.warning(f"BLOB_SERVICE: Blob '{blob_name}' not found in container '{container_name}' for deletion. It might have been already deleted.")
    except Exception as e:
        logger.error(f"BLOB_SERVICE: Error deleting blob '{blob_name}': {e}", exc_info=True)
    finally:
        if credential_for_storage_async:
            await credential_for_storage_async.close()