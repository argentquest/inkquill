"""Azure Blob Storage provider for blog media."""
import logging
from typing import BinaryIO, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import io

from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.blob import BlobSasPermissions, generate_blob_sas

from app.services.storage.base import StorageProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureBlobStorageProvider(StorageProvider):
    """Azure Blob Storage provider."""
    
    def __init__(self, container_name: str = None):
        """
        Initialize Azure Blob Storage provider.
        
        Args:
            container_name: Name of the blob container
        """
        self.container_name = container_name or settings.AZURE_STORAGE_CONTAINER_NAME_FOR_BLOG_MEDIA
        self.blob_service_client = None
        self.container_client = None
        self.credential = None
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = None  # Will be extracted from connection string if available
        
        logger.info(f"AzureBlobStorageProvider initialized for container: {self.container_name}")
    
    async def _ensure_client(self):
        """Ensure blob service client is initialized."""
        if self.blob_service_client is None:
            if settings.AZURE_STORAGE_CONNECTION_STRING:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    settings.AZURE_STORAGE_CONNECTION_STRING
                )
                # Extract account key from connection string for SAS generation
                parts = settings.AZURE_STORAGE_CONNECTION_STRING.split(';')
                for part in parts:
                    if part.startswith('AccountKey='):
                        self.account_key = part.split('=', 1)[1]
            elif self.account_name:
                account_url = f"https://{self.account_name}.blob.core.windows.net"
                self.credential = DefaultAzureCredential()
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url, 
                    credential=self.credential
                )
            else:
                raise ValueError("Azure Storage not configured. Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME")
            
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Ensure container exists
            try:
                await self.container_client.get_container_properties()
            except ResourceNotFoundError:
                logger.info(f"Creating container: {self.container_name}")
                await self.container_client.create_container(public_access="blob")
    
    def _get_blob_url(self, blob_name: str) -> str:
        """Get the public URL for a blob."""
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
    
    async def upload(
        self, 
        file_data: BinaryIO, 
        filename: str, 
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload a file to Azure Blob Storage."""
        try:
            await self._ensure_client()
            
            # Create blob path with date organization
            date_path = datetime.now().strftime("%Y/%m/%d")
            blob_name = f"{date_path}/{filename}"
            
            # Prepare metadata
            blob_metadata = metadata or {}
            blob_metadata['original_filename'] = filename
            blob_metadata['upload_time'] = datetime.now().isoformat()
            
            # Upload blob
            blob_client = self.container_client.get_blob_client(blob_name)
            
            # Read file data into memory (for seeking support)
            if hasattr(file_data, 'read'):
                data = file_data.read()
            else:
                data = file_data
            
            await blob_client.upload_blob(
                data,
                content_type=content_type,
                metadata=blob_metadata,
                overwrite=True
            )
            
            logger.info(f"File uploaded successfully to Azure Blob: {blob_name}")
            return blob_name
            
        except Exception as e:
            logger.error(f"Error uploading file {filename} to Azure Blob: {e}")
            raise
        finally:
            if self.credential:
                await self.credential.close()
    
    async def download(self, file_path: str) -> Tuple[bytes, str]:
        """Download a file from Azure Blob Storage."""
        try:
            await self._ensure_client()
            
            blob_client = self.container_client.get_blob_client(file_path)
            
            # Download blob
            download_stream = await blob_client.download_blob()
            data = await download_stream.readall()
            
            # Get properties for content type
            properties = await blob_client.get_blob_properties()
            content_type = properties.content_settings.content_type or 'application/octet-stream'
            
            return data, content_type
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            logger.error(f"Error downloading file {file_path} from Azure Blob: {e}")
            raise
        finally:
            if self.credential:
                await self.credential.close()
    
    async def delete(self, file_path: str) -> bool:
        """Delete a file from Azure Blob Storage."""
        try:
            await self._ensure_client()
            
            blob_client = self.container_client.get_blob_client(file_path)
            await blob_client.delete_blob()
            
            logger.info(f"Blob deleted: {file_path}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error deleting blob {file_path}: {e}")
            return False
        finally:
            if self.credential:
                await self.credential.close()
    
    async def exists(self, file_path: str) -> bool:
        """Check if a file exists in Azure Blob Storage."""
        try:
            await self._ensure_client()
            
            blob_client = self.container_client.get_blob_client(file_path)
            return await blob_client.exists()
            
        except Exception as e:
            logger.error(f"Error checking blob existence {file_path}: {e}")
            return False
        finally:
            if self.credential:
                await self.credential.close()
    
    async def get_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL to access the file."""
        try:
            if expires_in and self.account_key:
                # Generate SAS token for temporary access
                sas_token = generate_blob_sas(
                    account_name=self.account_name,
                    container_name=self.container_name,
                    blob_name=file_path,
                    account_key=self.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(seconds=expires_in)
                )
                return f"{self._get_blob_url(file_path)}?{sas_token}"
            else:
                # Return public URL
                return self._get_blob_url(file_path)
                
        except Exception as e:
            logger.error(f"Error generating URL for blob {file_path}: {e}")
            raise
    
    async def list_files(self, prefix: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
        """List files in Azure Blob Storage."""
        try:
            await self._ensure_client()
            
            files = []
            count = 0
            
            # List blobs with optional prefix
            async for blob in self.container_client.list_blobs(name_starts_with=prefix):
                if count >= limit:
                    break
                
                file_info = {
                    'path': blob.name,
                    'name': blob.name.split('/')[-1],
                    'size': blob.size,
                    'modified': blob.last_modified.isoformat(),
                    'url': self._get_blob_url(blob.name),
                    'content_type': blob.content_settings.content_type if blob.content_settings else 'application/octet-stream',
                    'metadata': blob.metadata
                }
                
                files.append(file_info)
                count += 1
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing blobs with prefix {prefix}: {e}")
            return []
        finally:
            if self.credential:
                await self.credential.close()
    
    async def close(self):
        """Close the Azure clients."""
        if self.blob_service_client:
            await self.blob_service_client.close()
        if self.credential:
            await self.credential.close()