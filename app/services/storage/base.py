"""Base storage interface for blog media."""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Dict, Any, Tuple
from pathlib import Path


class StorageProvider(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    async def upload(
        self, 
        file_data: BinaryIO, 
        filename: str, 
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file to storage.
        
        Args:
            file_data: Binary file data
            filename: Unique filename
            content_type: MIME type of the file
            metadata: Optional metadata to store with the file
            
        Returns:
            URL or path to access the uploaded file
        """
        pass
    
    @abstractmethod
    async def download(self, file_path: str) -> Tuple[bytes, str]:
        """
        Download a file from storage.
        
        Args:
            file_path: Path or key of the file to download
            
        Returns:
            Tuple of (file_data, content_type)
        """
        pass
    
    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path or key of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.
        
        Args:
            file_path: Path or key of the file to check
            
        Returns:
            True if file exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """
        Get a URL to access the file.
        
        Args:
            file_path: Path or key of the file
            expires_in: Optional expiration time in seconds for signed URLs
            
        Returns:
            URL to access the file
        """
        pass
    
    @abstractmethod
    async def list_files(self, prefix: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
        """
        List files in storage.
        
        Args:
            prefix: Optional prefix to filter files
            limit: Maximum number of files to return
            
        Returns:
            List of file metadata dictionaries
        """
        pass