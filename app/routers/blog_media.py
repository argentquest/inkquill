"""Blog media management API endpoints."""
import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image, ImageOps
import io

from app.core.deps import get_db_session, get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/media", tags=["blog-media"])

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


async def upload_to_azure_blob(
    file_data: bytes,
    filename: str,
    content_type: str,
    user_id: int,
    metadata: Optional[Dict[str, str]] = None
) -> str:
    """Upload file to Azure Blob Storage and return the blob URL."""
    from azure.storage.blob.aio import BlobServiceClient
    from azure.storage.blob import ContentSettings
    
    # Create blob path with date organization
    date_path = datetime.now().strftime("%Y/%m/%d")
    blob_name = f"{date_path}/{filename}"
    
    # Upload to Azure blob storage
    container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_BLOG_MEDIA
    
    if settings.AZURE_STORAGE_CONNECTION_STRING:
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    else:
        account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        from azure.identity.aio import DefaultAzureCredential
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
    
    try:
        async with blob_service_client:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            content_settings = ContentSettings(content_type=content_type)
            
            # Prepare blob metadata
            blob_metadata = metadata or {}
            blob_metadata.update({
                'user_id': str(user_id),
                'original_filename': filename.split('_', 1)[-1] if '_' in filename else filename,
                'upload_time': datetime.now().isoformat()
            })
            
            await blob_client.upload_blob(
                file_data,
                content_settings=content_settings,
                metadata=blob_metadata,
                overwrite=True
            )
            
            # Return the blob URL
            blob_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{blob_name}"
            logger.info(f"File uploaded to Azure Blob: {blob_url}")
            return blob_url
            
    except Exception as e:
        logger.error(f"Error uploading to Azure Blob: {e}")
        raise


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
    db: AsyncSession = Depends(get_db_session)
):
    """Upload a media file to Azure Blob Storage."""
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
                    
                    aspect_url = await upload_to_azure_blob(
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
        
        # Prepare metadata
        metadata = {
            "alt_text": alt_text or "",
            "caption": caption or "",
            "file_type": file_type,
            "original_filename": file.filename or "unnamed"
        }
        
        # Upload to Azure Blob Storage
        blob_url = await upload_to_azure_blob(
            file_data=content,
            filename=filename,
            content_type=file.content_type,
            user_id=current_user.id,
            metadata=metadata
        )
        
        # Return media info
        media_info = {
            "id": str(uuid.uuid4()),  # In a real system, this would be from database
            "filename": filename,
            "original_filename": file.filename,
            "url": blob_url,
            "file_type": file_type,
            "content_type": file.content_type,
            "file_size": file_size,
            "alt_text": alt_text,
            "caption": caption,
            "uploaded_by": current_user.id,
            "created_at": datetime.now().isoformat()
        }
        
        # Add image-specific info
        if image_info:
            media_info.update({
                "width": image_info["width"],
                "height": image_info["height"],
                "format": image_info["format"],
                "aspect_ratio_urls": aspect_ratio_urls
            })
        
        logger.info(f"User {current_user.id} uploaded media to Azure Blob: {filename}")
        
        return {
            "message": "File uploaded successfully to Azure Blob Storage",
            "media": media_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading media to Azure Blob: {e}")
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
    db: AsyncSession = Depends(get_db_session)
):
    """List uploaded media files."""
    try:
        # In a real implementation, this would query a database
        # For now, we'll list files from the upload directory
        media_files = []
        
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file() and not file_path.name.startswith("thumb_"):
                    # Extract user ID from filename
                    if file_path.name.startswith(f"{current_user.id}_"):
                        stat = file_path.stat()
                        
                        # Determine content type from extension
                        ext = file_path.suffix.lower()
                        content_type = {
                            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                            '.png': 'image/png', '.gif': 'image/gif',
                            '.webp': 'image/webp', '.mp4': 'video/mp4',
                            '.webm': 'video/webm', '.mp3': 'audio/mp3',
                            '.wav': 'audio/wav'
                        }.get(ext, 'application/octet-stream')
                        
                        file_type_detected = get_file_type(content_type)
                        
                        # Filter by file type if specified
                        if file_type and file_type_detected != file_type:
                            continue
                        
                        # Check for thumbnail
                        thumbnail_path = UPLOAD_DIR / f"thumb_{file_path.name}"
                        thumbnail_url = f"/static/uploads/blog/thumb_{file_path.name}" if thumbnail_path.exists() else None
                        
                        media_files.append({
                            "filename": file_path.name,
                            "url": f"/static/uploads/blog/{file_path.name}",
                            "thumbnail_url": thumbnail_url,
                            "file_type": file_type_detected,
                            "content_type": content_type,
                            "file_size": stat.st_size,
                            "created_at": stat.st_ctime
                        })
        
        # Sort by creation time (newest first)
        media_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total = len(media_files)
        media_files = media_files[skip:skip + limit]
        
        return media_files
        
    except Exception as e:
        logger.error(f"Error listing media files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list media files"
        )


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    filename: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a media file."""
    try:
        # Validate that the file belongs to the current user
        if not filename.startswith(f"{current_user.id}_"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own files"
            )
        
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Delete main file
        os.unlink(file_path)
        
        # Delete thumbnail if it exists
        thumbnail_path = UPLOAD_DIR / f"thumb_{filename}"
        if thumbnail_path.exists():
            os.unlink(thumbnail_path)
        
        logger.info(f"User {current_user.id} deleted media: {filename}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media file {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete media file"
        )


@router.get("/info/{filename}", response_model=ApiResponse)
async def get_media_info(
    filename: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get information about a media file."""
    try:
        file_path = UPLOAD_DIR / filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Validate that the file belongs to the current user or is publicly accessible
        if not filename.startswith(f"{current_user.id}_") and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        stat = file_path.stat()
        
        # Determine content type
        ext = file_path.suffix.lower()
        content_type = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
            '.png': 'image/png', '.gif': 'image/gif',
            '.webp': 'image/webp', '.mp4': 'video/mp4',
            '.webm': 'video/webm', '.mp3': 'audio/mp3',
            '.wav': 'audio/wav'
        }.get(ext, 'application/octet-stream')
        
        file_type = get_file_type(content_type)
        
        info = {
            "filename": filename,
            "url": f"/static/uploads/blog/{filename}",
            "file_type": file_type,
            "content_type": content_type,
            "file_size": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime
        }
        
        # Add image-specific info
        if file_type == "image":
            image_info = await validate_image(file_path)
            if image_info["is_valid"]:
                info.update({
                    "width": image_info.get("width"),
                    "height": image_info.get("height"),
                    "format": image_info.get("format")
                })
            
            # Check for thumbnail
            thumbnail_path = UPLOAD_DIR / f"thumb_{filename}"
            if thumbnail_path.exists():
                info["thumbnail_url"] = f"/static/uploads/blog/thumb_{filename}"
        
        return info
        
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
    db: AsyncSession = Depends(get_db_session)
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
                result = await upload_media(file, None, None, current_user, db)
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "media": result["media"]
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process bulk upload"
        )