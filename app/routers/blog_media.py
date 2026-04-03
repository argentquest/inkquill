"""Blog media management API endpoints."""
import logging
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from PIL import Image, ImageOps
import io

from app.core.deps import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.base import ApiResponse
from app.services.storage.local_storage import LocalStorageProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/media", tags=["blog-media"])
UPLOAD_DIR = Path(settings.LOCAL_STORAGE_BASE_PATH) / settings.LOCAL_STORAGE_BLOG_MEDIA_PATH
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Configuration
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg"}
ALLOWED_AUDIO_TYPES = {"audio/mp3", "audio/wav", "audio/ogg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB for images


def get_file_type(content_type: str) -> str:
    """Determine file type from content type."""
    if content_type in ALLOWED_IMAGE_TYPES:
        return "image"
    elif content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    elif content_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    else:
        return "document"


def generate_filename(original_filename: str, user_id: int, suffix: str = "") -> str:
    """Generate a unique filename."""
    file_extension = Path(original_filename).suffix.lower()
    unique_id = str(uuid.uuid4())
    suffix_str = f"_{suffix}" if suffix else ""
    return f"{user_id}_{unique_id}{suffix_str}{file_extension}"


def generate_aspect_ratio_versions(image_data: bytes, aspect_ratios: Dict[str, tuple]) -> Dict[str, bytes]:
    """
    Generate multiple aspect ratio versions of an image.
    
    Args:
        image_data: Original image bytes
        aspect_ratios: Dict of {name: (width, height)} for each version
    
    Returns:
        Dict of {aspect_name: processed_image_bytes}
    """
    try:
        original_img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary (for JPEG output)
        if original_img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparency
            background = Image.new('RGB', original_img.size, (255, 255, 255))
            if original_img.mode == 'P':
                original_img = original_img.convert('RGBA')
            background.paste(original_img, mask=original_img.split()[-1] if original_img.mode == 'RGBA' else None)
            original_img = background
        elif original_img.mode != 'RGB':
            original_img = original_img.convert('RGB')
        
        versions = {}
        
        for aspect_name, (target_width, target_height) in aspect_ratios.items():
            # Calculate aspect ratios
            target_aspect = target_width / target_height
            original_aspect = original_img.width / original_img.height
            
            # Create a copy for processing
            img = original_img.copy()
            
            if original_aspect > target_aspect:
                # Original is wider - crop width
                new_width = int(original_img.height * target_aspect)
                left = (original_img.width - new_width) // 2
                img = img.crop((left, 0, left + new_width, original_img.height))
            elif original_aspect < target_aspect:
                # Original is taller - crop height
                new_height = int(original_img.width / target_aspect)
                top = (original_img.height - new_height) // 2
                img = img.crop((0, top, original_img.width, top + new_height))
            
            # Resize to target dimensions
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Apply auto-orientation
            img = ImageOps.exif_transpose(img)
            
            # Convert to bytes (JPEG format for optimization)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=85, optimize=True)
            versions[aspect_name] = img_bytes.getvalue()
        
        return versions
        
    except Exception as e:
        logger.error(f"Error generating aspect ratio versions: {e}")
        raise


def _serialize_media_entry(
    *,
    storage_path: str,
    url: str,
    file_type: str,
    content_type: str,
    file_size: int,
    original_filename: Optional[str] = None,
    alt_text: Optional[str] = None,
    caption: Optional[str] = None,
    uploaded_by: Optional[int] = None,
    created_at: Optional[str] = None,
    thumbnail_url: Optional[str] = None,
    image_info: Optional[Dict[str, Any]] = None,
    aspect_ratio_urls: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Provide internal router support for serialize media entry."""
    entry = {
        "id": str(uuid.uuid4()),
        "filename": Path(storage_path).name,
        "storage_path": storage_path,
        "original_filename": original_filename or Path(storage_path).name,
        "url": url,
        "file_type": file_type,
        "content_type": content_type,
        "file_size": file_size,
        "alt_text": alt_text,
        "caption": caption,
        "uploaded_by": uploaded_by,
        "created_at": created_at or datetime.now().isoformat(),
    }
    if thumbnail_url:
        entry["thumbnail_url"] = thumbnail_url
    if image_info:
        entry.update(image_info)
    if aspect_ratio_urls:
        entry["aspect_ratio_urls"] = aspect_ratio_urls
    return entry


async def upload_to_local_storage(
    file_data: bytes,
    filename: str,
    content_type: str,
    user_id: int,
    metadata: Optional[Dict[str, str]] = None
) -> tuple[str, str]:
    """Upload file to local storage and return relative path plus public URL."""
    provider = LocalStorageProvider(str(UPLOAD_DIR))
    blob_metadata = metadata or {}
    blob_metadata.update({
        'user_id': str(user_id),
        'original_filename': filename.split('_', 1)[-1] if '_' in filename else filename,
        'upload_time': datetime.now().isoformat()
    })
    relative_path = await provider.upload(
        file_data=io.BytesIO(file_data),
        filename=filename,
        content_type=content_type,
        metadata=blob_metadata
    )
    url = await provider.get_url(relative_path)
    logger.info(f"File uploaded to local storage: {url}")
    return relative_path, url


async def validate_image(file_path: Path) -> Dict[str, Any]:
    """Validate and get image information."""
    try:
        with Image.open(file_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode,
                "is_valid": True
            }
    except Exception as e:
        logger.error(f"Error validating image {file_path}: {e}")
        return {"is_valid": False, "error": str(e)}


async def create_thumbnail(image_path: Path, thumbnail_path: Path, size: tuple = (300, 300)) -> bool:
    """Create a thumbnail for an image."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background
            
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=85, optimize=True)
            return True
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return False


@router.post("/upload", response_model=ApiResponse)
async def upload_media(
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
):
    """Upload a media file to local storage."""
    try:
        # Validate file type
        if not file.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to determine file type"
            )
        
        file_type = get_file_type(file.content_type)
        
        # Check file size
        content = await file.read()
        file_size = len(content)
        
        max_size = MAX_IMAGE_SIZE if file_type == "image" else MAX_FILE_SIZE
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Validate image if it's an image file and generate aspect ratio versions
        image_info = None
        aspect_ratio_urls = {}
        
        metadata = {
            "alt_text": alt_text or "",
            "caption": caption or "",
            "file_type": file_type,
            "original_filename": file.filename or "unnamed"
        }

        if file_type == "image":
            try:
                # Validate image using PIL
                img = Image.open(io.BytesIO(content))
                image_info = {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format
                }
                img.verify()  # Verify image integrity
                
                # Generate aspect ratio versions
                aspect_ratios = {
                    "16x9": (1920, 1080),    # Featured/hero images
                    "5x4": (1280, 1024),     # Content images
                    "1x1": (1080, 1080)      # Thumbnails/square
                }
                
                aspect_versions = generate_aspect_ratio_versions(content, aspect_ratios)
                
                # Upload each aspect ratio version
                base_filename = Path(file.filename or "unnamed").stem
                file_extension = ".jpg"  # Always save as JPEG for optimization
                
                for aspect_name, aspect_data in aspect_versions.items():
                    aspect_filename = generate_filename(
                        f"{base_filename}_{aspect_name}{file_extension}", 
                        current_user.id, 
                        aspect_name
                    )
                    
                    _, aspect_url = await upload_to_local_storage(
                        file_data=aspect_data,
                        filename=aspect_filename,
                        content_type="image/jpeg",
                        user_id=current_user.id,
                        metadata={
                            **metadata,
                            "aspect_ratio": aspect_name,
                            "is_processed_version": True
                        }
                    )
                    
                    aspect_ratio_urls[aspect_name] = aspect_url
                    
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid image file: {str(e)}"
                )
        
        # Generate unique filename
        filename = generate_filename(file.filename or "unnamed", current_user.id)
        
        storage_path, blob_url = await upload_to_local_storage(
            file_data=content,
            filename=filename,
            content_type=file.content_type,
            user_id=current_user.id,
            metadata=metadata
        )
        
        # Return media info
        media_info = _serialize_media_entry(
            storage_path=storage_path,
            url=blob_url,
            file_type=file_type,
            content_type=file.content_type,
            file_size=file_size,
            original_filename=file.filename,
            alt_text=alt_text,
            caption=caption,
            uploaded_by=current_user.id,
            image_info=image_info,
            aspect_ratio_urls=aspect_ratio_urls if image_info else None,
        )
        
        logger.info(f"User {current_user.id} uploaded media to local storage: {filename}")
        
        return ApiResponse.success_response(data={
            "message": "File uploaded successfully",
            "media": media_info
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading media to local storage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload media file"
        )


@router.get("/list", response_model=ApiResponse)
async def list_media(
    file_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
):
    """List uploaded media files."""
    try:
        # In a real implementation, this would query a database
        # For now, we'll list files from the upload directory
        media_files = []
        provider = LocalStorageProvider(str(UPLOAD_DIR))

        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.rglob("*"):
                if file_path.is_file() and not file_path.name.endswith(".meta") and not file_path.name.startswith("thumb_"):
                    if not file_path.name.startswith(f"{current_user.id}_"):
                        continue

                    stat = file_path.stat()
                    relative_path = str(file_path.relative_to(UPLOAD_DIR)).replace("\\", "/")
                    ext = file_path.suffix.lower()
                    content_type = {
                        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                        '.png': 'image/png', '.gif': 'image/gif',
                        '.webp': 'image/webp', '.mp4': 'video/mp4',
                        '.webm': 'video/webm', '.mp3': 'audio/mp3',
                        '.wav': 'audio/wav'
                    }.get(ext, 'application/octet-stream')
                    file_type_detected = get_file_type(content_type)

                    if file_type and file_type_detected != file_type:
                        continue

                    media_files.append(
                        _serialize_media_entry(
                            storage_path=relative_path,
                            url=await provider.get_url(relative_path),
                            file_type=file_type_detected,
                            content_type=content_type,
                            file_size=stat.st_size,
                            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        )
                    )
        
        # Sort by creation time (newest first)
        media_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total = len(media_files)
        media_files = media_files[skip:skip + limit]
        
        return ApiResponse.success_response(data=media_files)
        
    except Exception as e:
        logger.error(f"Error listing media files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list media files"
        )


@router.delete("/{file_path:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a media file."""
    try:
        # Validate that the file belongs to the current user
        normalized_path = file_path.replace("\\", "/")
        if not Path(normalized_path).name.startswith(f"{current_user.id}_"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own files"
            )
        
        resolved_path = UPLOAD_DIR / normalized_path
        if not resolved_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete main file
        os.unlink(resolved_path)
        
        # Delete thumbnail if it exists
        thumbnail_path = resolved_path.parent / f"thumb_{resolved_path.name}"
        if thumbnail_path.exists():
            os.unlink(thumbnail_path)

        metadata_path = resolved_path.with_suffix(resolved_path.suffix + ".meta")
        if metadata_path.exists():
            os.unlink(metadata_path)
        
        logger.info(f"User {current_user.id} deleted media: {normalized_path}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete media file"
        )


@router.get("/info/{file_path:path}", response_model=ApiResponse)
async def get_media_info(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get information about a media file."""
    try:
        normalized_path = file_path.replace("\\", "/")
        resolved_path = UPLOAD_DIR / normalized_path
        if not resolved_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Validate that the file belongs to the current user or is publicly accessible
        if not Path(normalized_path).name.startswith(f"{current_user.id}_") and not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        stat = resolved_path.stat()
        
        # Determine content type
        ext = resolved_path.suffix.lower()
        content_type = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif',
            '.webp': 'image/webp', '.mp4': 'video/mp4',
            '.webm': 'video/webm', '.mp3': 'audio/mp3',
            '.wav': 'audio/wav'
        }.get(ext, 'application/octet-stream')
        
        file_type = get_file_type(content_type)
        
        provider = LocalStorageProvider(str(UPLOAD_DIR))
        info = _serialize_media_entry(
            storage_path=normalized_path,
            url=await provider.get_url(normalized_path),
            file_type=file_type,
            content_type=content_type,
            file_size=stat.st_size,
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
        )
        info["modified_at"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Add image-specific info
        if file_type == "image":
            image_info = await validate_image(resolved_path)
            if image_info["is_valid"]:
                info.update({
                    "width": image_info.get("width"),
                    "height": image_info.get("height"),
                    "format": image_info.get("format")
                })
            
            # Check for thumbnail
            thumbnail_path = resolved_path.parent / f"thumb_{resolved_path.name}"
            if thumbnail_path.exists():
                info["thumbnail_url"] = await provider.get_url(
                    str(thumbnail_path.relative_to(UPLOAD_DIR)).replace("\\", "/")
                )
        
        return ApiResponse.success_response(data=info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting media info for {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get media information"
        )


@router.post("/bulk-upload", response_model=ApiResponse)
async def bulk_upload_media(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
):
    """Upload multiple media files at once."""
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files can be uploaded at once"
            )
        
        results = []
        for file in files:
            try:
                # Process each file individually
                # This is a simplified version - in practice you'd want to optimize this
                result = await upload_media(file, None, None, current_user)
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "media": result.data["media"]
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return ApiResponse.success_response(data=results)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process bulk upload"
        )

