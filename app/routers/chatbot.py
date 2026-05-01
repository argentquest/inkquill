"""API router for standalone chatbot sessions."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.chatbot import (
    ChatbotSessionCreate,
    ChatbotSessionUpdate,
    ChatbotSendMessageRequest,
)
from app.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


def _service(db: AsyncSession) -> ChatbotService:
    return ChatbotService(db)


@router.post("/sessions", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: ChatbotSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    svc = _service(db)
    session = await svc.create_session(current_user.id, payload)
    return ApiResponse.success_response(data=session.model_dump())


@router.get("/sessions", response_model=ApiResponse)
async def list_sessions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    svc = _service(db)
    sessions = await svc.list_sessions(current_user.id)
    return ApiResponse.success_response(data=[s.model_dump() for s in sessions])


@router.get("/sessions/{session_id}", response_model=ApiResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    svc = _service(db)
    session = await svc.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return ApiResponse.success_response(data=session.model_dump())


@router.put("/sessions/{session_id}", response_model=ApiResponse)
async def rename_session(
    session_id: int,
    payload: ChatbotSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    from app.crud import chatbot as chatbot_crud
    session = await chatbot_crud.get_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    updated = await chatbot_crud.update_session_title(db, session, payload.title)
    from app.schemas.chatbot import ChatbotSessionRead
    return ApiResponse.success_response(data=ChatbotSessionRead.model_validate(updated).model_dump())


@router.delete("/sessions/{session_id}", response_model=ApiResponse)
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    svc = _service(db)
    deleted = await svc.delete_session(session_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return ApiResponse.success_response(data={"deleted": True})


@router.post("/sessions/{session_id}/messages", response_model=ApiResponse)
async def send_message(
    session_id: int,
    payload: ChatbotSendMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    svc = _service(db)
    try:
        result = await svc.send_message(session_id, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("send_message failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )
    return ApiResponse.success_response(data=result.model_dump())
