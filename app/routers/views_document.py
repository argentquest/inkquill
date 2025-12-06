# /ai_rag_story_app/app/routers/views_document.py

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.crud import document as crud_document
from app.crud import world as crud_world
# <<< MODIFICATION: Import the Pydantic schema >>>
from app.schemas.document import UploadedDocumentRead
from app.schemas.base import ApiResponse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ui/documents",
    tags=["ui-document-views"],
    dependencies=[Depends(get_current_active_user)]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse, name="ui_document_manager")
async def document_manager_ui(
    request: Request,
    world_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Document manager UI - supports world_id as query parameter"""
    return await _document_manager_core(request, world_id, db, current_user)

@router.get("/world/{world_id}", response_class=HTMLResponse, name="ui_document_manager_for_world")
async def document_manager_for_world_ui(
    request: Request,
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Document manager UI - world_id as path parameter"""
    return await _document_manager_core(request, world_id, db, current_user)

@router.get("/world_id={world_id}", response_class=HTMLResponse, name="ui_document_manager_malformed_url")
async def document_manager_malformed_url(
    request: Request,
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Document manager UI - handles malformed URLs like /documents/world_id=152"""
    logger.warning(f"Handling malformed document manager URL for world_id={world_id}. This should be fixed in the URL generation.")
    return await _document_manager_core(request, world_id, db, current_user)

async def _document_manager_core(
    request: Request,
    world_id: Optional[int],
    db: AsyncSession,
    current_user: User
):
    logger.info(f"User {current_user.username} accessing document management page. World ID: {world_id}")
    documents_from_db = []
    available_worlds = []
    try:
        if world_id:
            # If world_id is provided, show only documents for that world
            documents_from_db = await crud_document.get_documents_by_world(db, world_id=world_id)
            logger.info(f"Found {len(documents_from_db)} document records for world {world_id}.")
        else:
            # Otherwise, show all documents for the user
            documents_from_db = await crud_document.get_documents_by_user(db, user_id=current_user.id)
            logger.info(f"Found {len(documents_from_db)} document records for user {current_user.username}.")
        
        available_worlds = await crud_world.get_worlds_by_user(db, user_id=current_user.id)
        logger.info(f"Found {len(available_worlds)} worlds for user {current_user.username} for document association.")
        
        # If no worlds exist and no specific world_id provided, user can't upload documents
        if not available_worlds and not world_id:
            logger.warning(f"User {current_user.username} accessed document manager but has no worlds created")

    except Exception as e:
        logger.error(f"Error fetching documents or worlds for user {current_user.username}: {e}", exc_info=True)

    # Pass DB models directly to template since they have world relationships loaded
    # Converting to Pydantic schemas loses the SQLAlchemy relationships
    documents_for_template = documents_from_db

    return templates.TemplateResponse(
        "pages/document_manager.html",
        {
            "request": request,
            "documents": documents_for_template, # Pass the DB objects with relationships
            "available_worlds": available_worlds,
            "selected_world_id": world_id,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "has_worlds": bool(available_worlds)
        }
    )