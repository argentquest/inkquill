# /ai_rag_story_app/app/core/azure_deps.py

from fastapi import HTTPException, status
from typing import Optional, AsyncGenerator
import logging

from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

from app.core.config import settings

logger = logging.getLogger(__name__)

async def get_blob_service_client() -> AsyncGenerator[BlobServiceClient, None]:
    """
    FastAPI dependency that provides an authenticated Azure BlobServiceClient.

    It tries to authenticate using a connection string first, then falls back
    to DefaultAzureCredential (suitable for Managed Identity in production or
    local developer logins via Azure CLI).

    Yields:
        BlobServiceClient: The authenticated async blob service client.

    Raises:
        HTTPException: If storage is not configured or authentication fails.
    """
    if not (settings.AZURE_STORAGE_CONNECTION_STRING or settings.AZURE_STORAGE_ACCOUNT_NAME):
        logger.error("Azure Storage dependency error: Neither AZURE_STORAGE_CONNECTION_STRING nor AZURE_STORAGE_ACCOUNT_NAME is configured.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage service is not configured on the server."
        )

    blob_service_client: Optional[BlobServiceClient] = None
    credential_for_storage: Optional[DefaultAzureCredential] = None

    try:
        if settings.AZURE_STORAGE_CONNECTION_STRING and not settings.AZURE_STORAGE_CONNECTION_STRING.endswith("_NOT_SET_IN_ENV"):
            logger.debug("Attempting to connect to Azure Storage using Connection String.")
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME and not settings.AZURE_STORAGE_ACCOUNT_NAME.endswith("_NOT_SET_IN_ENV"):
            logger.debug(f"Attempting to connect to Azure Storage Account '{settings.AZURE_STORAGE_ACCOUNT_NAME}' using DefaultAzureCredential.")
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential_for_storage = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(account_url=account_url, credential=credential_for_storage)
        
        if not blob_service_client:
            # This case should be caught by the initial check, but as a safeguard:
            raise HTTPException(status_code=503, detail="Could not initialize storage client.")

        yield blob_service_client

    except ClientAuthenticationError as e:
        logger.error(f"Azure authentication failed for blob storage: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Storage service authentication failed.")
    except Exception as e:
        logger.error(f"An unexpected error occurred with the storage service dependency: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred with the storage service.")
    finally:
        if blob_service_client:
            await blob_service_client.close()
            logger.debug("Blob service client closed by dependency.")
        if credential_for_storage:
            await credential_for_storage.close()
            logger.debug("DefaultAzureCredential for blob storage closed by dependency.")