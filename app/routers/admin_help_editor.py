# /ai_rag_story_app/app/routers/admin_help_editor.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import os
import glob
import datetime
from pathlib import Path
from typing import List, Dict

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/help-editor",
    tags=["admin-help-editor"],
    dependencies=[Depends(get_current_active_user)]
)

templates = Jinja2Templates(directory="app/templates")

HELP_FILES_DIR = Path("app/static/help")


def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Ensure the current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/", response_class=HTMLResponse, name="admin_help_editor")
async def help_editor_page(
    request: Request,
    current_user: User = Depends(get_admin_user)
):
    """Display the help file editor page for admins."""
    logger.info(f"Admin {current_user.username} accessing help editor")
    
    return templates.TemplateResponse(
        "pages/admin_help_editor.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )


@router.get("/files", response_model=List[Dict], name="admin_help_files_list")
async def list_help_files(
    current_user: User = Depends(get_admin_user)
):
    """Get list of all help files including versions."""
    try:
        files_data = {}
        
        # Get all HTML files in help directory
        help_files = glob.glob(str(HELP_FILES_DIR / "*.html"))
        
        for file_path in help_files:
            filename = os.path.basename(file_path)
            
            # Check if this is a versioned file
            if "_v2_" in filename:
                # Extract the original filename
                parts = filename.split("_v2_")
                original_name = parts[0] + ".html"
                
                # Extract user and date from version
                version_info = parts[1].replace(".html", "")
                version_parts = version_info.rsplit("_", 1)
                username = version_parts[0] if len(version_parts) > 1 else "unknown"
                date = version_parts[1] if len(version_parts) > 1 else "unknown"
                
                # Add to versions list
                if original_name not in files_data:
                    # Check if the original file actually exists
                    original_file_path = HELP_FILES_DIR / original_name
                    if original_file_path.exists():
                        files_data[original_name] = {
                            "name": original_name,
                            "path": original_name,
                            "is_original": True,
                            "versions": []
                        }
                    else:
                        # Create a placeholder entry for versioned files without originals
                        files_data[original_name] = {
                            "name": original_name,
                            "path": None,  # No original file exists
                            "is_original": False,
                            "versions": []
                        }
                
                files_data[original_name]["versions"].append({
                    "name": filename,
                    "path": filename,
                    "username": username,
                    "date": date,
                    "is_original": False
                })
            else:
                # This is an original file
                if filename not in files_data:
                    files_data[filename] = {
                        "name": filename,
                        "path": filename,
                        "is_original": True,
                        "versions": []
                    }
        
        # Convert to list and sort
        files_list = list(files_data.values())
        files_list.sort(key=lambda x: x["name"])
        
        # Sort versions by date (newest first)
        for file_info in files_list:
            file_info["versions"].sort(key=lambda x: x["date"], reverse=True)
        
        return files_list
        
    except Exception as e:
        logger.error(f"Error listing help files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list help files: {str(e)}"
        )


@router.get("/file/{filename:path}", response_model=Dict, name="admin_get_help_file")
async def get_help_file_content(
    filename: str,
    current_user: User = Depends(get_admin_user)
):
    """Get the content of a specific help file."""
    try:
        file_path = HELP_FILES_DIR / filename
        
        # Security check - ensure file is within help directory
        if not file_path.resolve().is_relative_to(HELP_FILES_DIR.resolve()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path"
            )
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Help file not found: {filename}"
            )
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "filename": filename,
            "content": content
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading help file {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read help file: {str(e)}"
        )


@router.post("/save", response_model=Dict, name="admin_save_help_file")
async def save_help_file(
    data: Dict,
    current_user: User = Depends(get_admin_user)
):
    """Save an edited help file with versioning."""
    try:
        original_filename = data.get("filename")
        content = data.get("content")
        
        if not original_filename or not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename and content are required"
            )
        
        # Extract base filename without extension
        base_name = original_filename.replace(".html", "")
        
        # Create version filename
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        version_filename = f"{base_name}_v2_{current_user.username}_{date_str}.html"
        
        # Save the versioned file
        version_path = HELP_FILES_DIR / version_filename
        with open(version_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Admin {current_user.username} saved version: {version_filename}")
        
        return {
            "success": True,
            "filename": version_filename,
            "message": f"File saved as {version_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving help file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save help file: {str(e)}"
        )


@router.post("/create", response_model=Dict, name="admin_create_help_file")
async def create_help_file(
    data: Dict,
    current_user: User = Depends(get_admin_user)
):
    """Create a new help file."""
    try:
        filename = data.get("filename")
        content = data.get("content")
        
        if not filename or not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename and content are required"
            )
        
        # Validate filename
        if not filename.endswith(".html"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename must end with .html"
            )
        
        # Security check - ensure filename is safe
        safe_filename = os.path.basename(filename)
        if safe_filename != filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        # Check if file already exists
        file_path = HELP_FILES_DIR / safe_filename
        if file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="File already exists"
            )
        
        # Create the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Admin {current_user.username} created new help file: {safe_filename}")
        
        return {
            "success": True,
            "filename": safe_filename,
            "message": f"File {safe_filename} created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating help file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create help file: {str(e)}"
        )