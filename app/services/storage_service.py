"""Service helpers for storage service."""

import logging

from app.core.storage_deps import build_storage_url, resolve_storage_path

logger = logging.getLogger(__name__)


async def delete_blob(container_name: str, blob_name: str) -> None:
    """Delete blob."""
    file_path = resolve_storage_path(container_name, blob_name)
    logger.info("STORAGE: deleting '%s'", file_path)
    if file_path.exists():
        file_path.unlink()


async def save_blob(
    container_name: str,
    blob_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """Provide service support for save blob."""
    del content_type
    file_path = resolve_storage_path(container_name, blob_name)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)
    logger.info("STORAGE: saved %s bytes to '%s'", len(data), file_path)
    return build_storage_url(container_name, blob_name) or ""

