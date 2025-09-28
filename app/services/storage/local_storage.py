"""Local file system storage provider for blog media."""
import os
import logging
from typing import BinaryIO, Optional, Dict, Any, Tuple
from pathlib import Path
import aiofiles
import aiofiles.os
from datetime import datetime
import mimetypes

from app.services.storage.base import StorageProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class LocalStorageProvider(StorageProvider):
    """Local file system storage provider."""
    
    def __init__(self, base_path: str = "app/static/uploads/blog"):
        """
        Initialize local storage provider.
        
        Args:
            base_path: Base directory for storing files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorageProvider initialized with base path: {self.base_path}")
    
    def _get_full_path(self, file_path: str) -> Path:
        """Get full file path."""
        return self.base_path / file_path
    
    def _get_relative_path(self, full_path: Path) -> str:
        """Get relative path from full path."""
        return str(full_path.relative_to(self.base_path))
    
    def _get_public_url(self, file_path: str) -> str:
        """Get public URL for the file."""
        # Assuming static files are served from /static/
        relative_to_static = Path("uploads/blog") / file_path
        return f"/static/{relative_to_static.as_posix()}"
    
    async def upload(
        self, 
        file_data: BinaryIO, 
        filename: str, 
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload a file to local storage."""
        try:
            # Create subdirectories based on date for organization
            date_path = datetime.now().strftime("%Y/%m/%d")
            upload_dir = self.base_path / date_path
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            file_path = upload_dir / filename
            
            # Write file
            async with aiofiles.open(file_path, 'wb') as f:
                # Read chunks to handle large files
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = file_data.read(chunk_size)
                    if not chunk:
                        break
                    await f.write(chunk)
            
            # Save metadata if provided
            if metadata:
                metadata_path = file_path.with_suffix(file_path.suffix + '.meta')
                metadata['content_type'] = content_type
                metadata['upload_time'] = datetime.now().isoformat()
                
                import json
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata))
            
            relative_path = f"{date_path}/{filename}"
            logger.info(f"File uploaded successfully to: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Error uploading file {filename}: {e}")
            raise
    
    async def download(self, file_path: str) -> Tuple[bytes, str]:
        """Download a file from local storage."""
        try:
            full_path = self._get_full_path(file_path)
            
            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file
            async with aiofiles.open(full_path, 'rb') as f:
                data = await f.read()
            
            # Get content type
            content_type, _ = mimetypes.guess_type(str(full_path))
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Try to get content type from metadata
            metadata_path = full_path.with_suffix(full_path.suffix + '.meta')
            if metadata_path.exists():
                import json
                async with aiofiles.open(metadata_path, 'r') as f:
                    metadata = json.loads(await f.read())
                    content_type = metadata.get('content_type', content_type)
            
            return data, content_type
            
        except Exception as e:
            logger.error(f"Error downloading file {file_path}: {e}")
            raise
    
    async def delete(self, file_path: str) -> bool:
        """Delete a file from local storage."""
        try:
            full_path = self._get_full_path(file_path)
            
            if full_path.exists():
                await aiofiles.os.remove(full_path)
                
                # Also remove metadata file if exists
                metadata_path = full_path.with_suffix(full_path.suffix + '.meta')
                if metadata_path.exists():
                    await aiofiles.os.remove(metadata_path)
                
                logger.info(f"File deleted: {file_path}")
                return True
            
            logger.warning(f"File not found for deletion: {file_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    async def exists(self, file_path: str) -> bool:
        """Check if a file exists in local storage."""
        try:
            full_path = self._get_full_path(file_path)
            return full_path.exists()
        except Exception as e:
            logger.error(f"Error checking file existence {file_path}: {e}")
            return False
    
    async def get_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL to access the file."""
        # For local storage, we ignore expires_in since we can't create signed URLs
        return self._get_public_url(file_path)
    
    async def list_files(self, prefix: Optional[str] = None, limit: int = 100) -> list[Dict[str, Any]]:
        """List files in local storage."""
        try:
            files = []
            count = 0
            
            search_path = self.base_path
            if prefix:
                search_path = self.base_path / prefix
            
            # Walk through directory
            for root, dirs, filenames in os.walk(search_path):
                for filename in filenames:
                    # Skip metadata files
                    if filename.endswith('.meta'):
                        continue
                    
                    if count >= limit:
                        break
                    
                    full_path = Path(root) / filename
                    relative_path = self._get_relative_path(full_path)
                    
                    # Get file stats
                    stat = full_path.stat()
                    
                    file_info = {
                        'path': relative_path,
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'url': self._get_public_url(relative_path)
                    }
                    
                    # Try to get metadata
                    metadata_path = full_path.with_suffix(full_path.suffix + '.meta')
                    if metadata_path.exists():
                        import json
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            file_info['content_type'] = metadata.get('content_type', 'application/octet-stream')
                            file_info['metadata'] = metadata
                    
                    files.append(file_info)
                    count += 1
                
                if count >= limit:
                    break
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing files with prefix {prefix}: {e}")
            return []