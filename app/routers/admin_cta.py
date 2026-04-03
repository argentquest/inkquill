"""API routes for admin cta."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db_session
from app.crud import cta_content as crud_cta
from app.models.cta_content import CTAPosition
from app.models.user import User
from app.schemas.base import ApiResponse


router = APIRouter()


class CTAFeature(BaseModel):
    """Response or helper model for c t a feature."""
    icon: str
    text: str
    color: Optional[str] = "#10B981"


class CTACreateRequest(BaseModel):
    """Response or helper model for c t a create request."""
    title: str
    subtitle: Optional[str] = None
    content: Optional[str] = None
    position: str
    style: str = "gradient"
    background_color: Optional[str] = None
    text_color: str = "#FFFFFF"
    icon_class: Optional[str] = None
    features: Optional[List[CTAFeature]] = None
    primary_button_text: Optional[str] = None
    primary_button_url: Optional[str] = None
    primary_button_icon: Optional[str] = None
    secondary_button_text: Optional[str] = None
    secondary_button_url: Optional[str] = None
    secondary_button_icon: Optional[str] = None
    show_for_anonymous: bool = True
    show_for_authenticated: bool = True
    show_for_admin: bool = True
    campaign_name: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    sort_order: int = 0


class CTAUpdateRequest(BaseModel):
    """Response or helper model for c t a update request."""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    position: Optional[str] = None
    style: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    icon_class: Optional[str] = None
    features: Optional[List[CTAFeature]] = None
    primary_button_text: Optional[str] = None
    primary_button_url: Optional[str] = None
    primary_button_icon: Optional[str] = None
    secondary_button_text: Optional[str] = None
    secondary_button_url: Optional[str] = None
    secondary_button_icon: Optional[str] = None
    show_for_anonymous: Optional[bool] = None
    show_for_authenticated: Optional[bool] = None
    show_for_admin: Optional[bool] = None
    campaign_name: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


def _require_admin(current_user: User) -> None:
    """Provide internal router support for require admin."""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage CTA content",
        )


def _parse_position(position: Optional[str]) -> Optional[CTAPosition]:
    """Provide internal router support for parse position."""
    if position is None:
        return None
    try:
        return CTAPosition(position)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid position value: {position}",
        ) from exc


def _normalize_features(features: Optional[List[CTAFeature]]) -> Optional[List[dict]]:
    """Provide internal router support for normalize features."""
    if not features:
        return None
    return [feature.model_dump() for feature in features]


@router.get("/admin/cta-content", response_model=ApiResponse)
async def get_all_ctas(
    position: Optional[str] = Query(None, description="Filter by position"),
    include_inactive: bool = Query(False, description="Include inactive CTAs"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle GET /admin/cta-content."""
    _require_admin(current_user)
    position_enum = _parse_position(position)
    ctas = await crud_cta.get_all_ctas(
        db=db,
        position=position_enum,
        include_inactive=include_inactive,
    )
    return ApiResponse.success_response([cta.to_dict() for cta in ctas])


@router.get("/admin/cta-content/{cta_id}", response_model=ApiResponse)
async def get_cta_by_id(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle GET /admin/cta-content/{cta_id}."""
    _require_admin(current_user)
    cta = await crud_cta.get_cta_by_id(db, cta_id)
    if not cta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CTA not found")
    return ApiResponse.success_response(cta.to_dict())


@router.post("/admin/cta-content", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_cta(
    request: CTACreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle POST /admin/cta-content."""
    _require_admin(current_user)
    position = _parse_position(request.position)
    if position is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Position is required")
    if not request.style or not request.style.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Style is required")

    cta = await crud_cta.create_cta_content(
        db=db,
        title=request.title,
        subtitle=request.subtitle,
        content=request.content,
        position=position,
        style=request.style,
        background_color=request.background_color,
        text_color=request.text_color,
        icon_class=request.icon_class,
        features=_normalize_features(request.features),
        primary_button_text=request.primary_button_text,
        primary_button_url=request.primary_button_url,
        primary_button_icon=request.primary_button_icon,
        secondary_button_text=request.secondary_button_text,
        secondary_button_url=request.secondary_button_url,
        secondary_button_icon=request.secondary_button_icon,
        show_for_anonymous=request.show_for_anonymous,
        show_for_authenticated=request.show_for_authenticated,
        show_for_admin=request.show_for_admin,
        campaign_name=request.campaign_name,
        utm_source=request.utm_source,
        utm_medium=request.utm_medium,
        utm_campaign=request.utm_campaign,
        sort_order=request.sort_order,
    )
    return ApiResponse.success_response({"message": "CTA created successfully", "id": cta.id})


@router.put("/admin/cta-content/{cta_id}", response_model=ApiResponse)
async def update_cta(
    cta_id: int,
    request: CTAUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle PUT /admin/cta-content/{cta_id}."""
    _require_admin(current_user)
    update_data = {}
    for field, value in request.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        if field == "position":
            update_data[field] = _parse_position(value)
        elif field == "style":
            if value.strip():
                update_data[field] = value
        elif field == "features":
            update_data[field] = _normalize_features(value)
        else:
            update_data[field] = value

    cta = await crud_cta.update_cta_content(db, cta_id, **update_data)
    if not cta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CTA not found")
    return ApiResponse.success_response({"message": "CTA updated successfully", "id": cta.id})


@router.post("/admin/cta-content/{cta_id}/toggle-active", response_model=ApiResponse)
async def toggle_cta_active(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle POST /admin/cta-content/{cta_id}/toggle-active."""
    _require_admin(current_user)
    cta = await crud_cta.toggle_cta_active_status(db, cta_id)
    if not cta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CTA not found")
    return ApiResponse.success_response(
        {
            "message": f"CTA {'activated' if cta.is_active else 'deactivated'} successfully",
            "is_active": cta.is_active,
        }
    )


@router.get("/admin/debug/user-info", response_model=ApiResponse)
async def debug_user_info(current_user: User = Depends(get_current_user)):
    """Handle GET /admin/debug/user-info."""
    if not current_user:
        return ApiResponse.success_response({"error": "No user authenticated", "user": None})
    return ApiResponse.success_response(
        {
            "user_id": current_user.id,
            "username": current_user.username,
            "is_admin": getattr(current_user, "is_admin", None),
            "is_active": getattr(current_user, "is_active", None),
            "user_type": type(current_user).__name__,
        }
    )


@router.delete("/admin/cta-content/{cta_id}", response_model=ApiResponse)
async def delete_cta(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle DELETE /admin/cta-content/{cta_id}."""
    _require_admin(current_user)
    success = await crud_cta.delete_cta_content(db, cta_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CTA not found")
    return ApiResponse.success_response({"message": "CTA deleted successfully"})


@router.post("/admin/cta-content/create-default", response_model=ApiResponse)
async def create_default_cta(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Handle POST /admin/cta-content/create-default."""
    _require_admin(current_user)
    cta = await crud_cta.create_default_home_cta(db)
    return ApiResponse.success_response({"message": "Default CTA created successfully", "id": cta.id})
