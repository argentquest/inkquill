"""Core application helpers for storage deps."""

import logging
from pathlib import Path
from typing import AsyncGenerator, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def resolve_storage_subpath(container_name: str) -> str:
    """Resolve storage subpath."""
    container_map = {
        "documents": settings.LOCAL_STORAGE_DOCUMENTS_PATH,
        "published-stories": settings.LOCAL_STORAGE_PUBLISHED_STORIES_PATH,
        "generated-images": settings.LOCAL_STORAGE_GENERATED_IMAGES_PATH,
        "blogs": settings.LOCAL_STORAGE_BLOG_MEDIA_PATH,
    }
    return container_map.get(container_name, container_name)


def resolve_storage_path(container_name: str, blob_name: str) -> Path:
    """Resolve storage path."""
    return Path(settings.LOCAL_STORAGE_BASE_PATH) / resolve_storage_subpath(container_name) / blob_name


def build_storage_url(container_name: str, blob_name: Optional[str]) -> Optional[str]:
    """Build storage url."""
    if not blob_name:
        return None
    subpath = resolve_storage_subpath(container_name)
    return f"/runtime/data/uploads/{subpath}/{blob_name}".replace("\\", "/")


class LocalDownloadStream:
    """Class for local download stream."""
    def __init__(self, path: Path):
        self._path = path

    async def readall(self) -> bytes:
        return self._path.read_bytes()


class LocalBlobClient:
    """Class for local blob client."""
    def __init__(self, container: str, blob: str):
        self.container = container
        self.blob = blob
        self.path = resolve_storage_path(container, blob)
        self.url = build_storage_url(container, blob) or ""

    async def exists(self) -> bool:
        return self.path.exists()

    async def download_blob(self) -> LocalDownloadStream:
        if not self.path.exists():
            raise FileNotFoundError(f"Blob not found: {self.container}/{self.blob}")
        return LocalDownloadStream(self.path)

    async def upload_blob(self, data: bytes, overwrite: bool = True, content_settings=None) -> None:
        if self.path.exists() and not overwrite:
            raise FileExistsError(f"Blob already exists: {self.container}/{self.blob}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(data)

    async def delete_blob(self, delete_snapshots: Optional[str] = None) -> None:
        if self.path.exists():
            self.path.unlink()

    async def get_blob_properties(self):
        class _ContentSettings:
            content_type = "application/octet-stream"

        class _Properties:
            content_settings = _ContentSettings()

        return _Properties()


class LocalContainerClient:
    """Class for local container client."""
    def __init__(self, container: str):
        self.container = container
        self.path = Path(settings.LOCAL_STORAGE_BASE_PATH) / resolve_storage_subpath(container)

    async def exists(self) -> bool:
        return self.path.exists()

    async def create_container(self, public_access: Optional[str] = None) -> None:
        self.path.mkdir(parents=True, exist_ok=True)

    def get_blob_client(self, blob: str) -> LocalBlobClient:
        return LocalBlobClient(self.container, blob)


class LocalStorageClient:
    """Class for local storage client."""
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_blob(self, container: str, name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        blob_client = self.get_blob_client(container=container, blob=name)
        await blob_client.upload_blob(data, overwrite=True)
        logger.info("LocalStorageClient: saved %s bytes to %s", len(data), blob_client.path)
        return blob_client.url

    async def delete_blob(self, container: str, name: str) -> None:
        blob_client = self.get_blob_client(container=container, blob=name)
        await blob_client.delete_blob()

    async def close(self) -> None:
        return None

    def get_blob_client(self, container: str, blob: str) -> LocalBlobClient:
        return LocalBlobClient(container, blob)

    def get_container_client(self, container: str) -> LocalContainerClient:
        return LocalContainerClient(container)


async def get_storage_client() -> AsyncGenerator[LocalStorageClient, None]:
    """Return storage client."""
    client = LocalStorageClient(base_path=settings.LOCAL_STORAGE_BASE_PATH)
    try:
        yield client
    finally:
        await client.close()


async def get_blob_service_client() -> AsyncGenerator[LocalStorageClient, None]:
    """Return blob service client."""
    async for client in get_storage_client():
        yield client

