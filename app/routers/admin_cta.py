# Admin CTA Content Management API
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from app.core.deps import get_db_session
from app.models.user import User
from app.models.cta_content import CTAContent, CTAPosition, CTAStyle
from app.crud import cta_content as crud_cta
from app.core.deps import get_current_user
import json

router = APIRouter()

class CTAFeature(BaseModel):
    icon: str
    text: str
    color: Optional[str] = "#10B981"

class CTACreateRequest(BaseModel):
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

@router.get("/admin/cta-content")
async def get_all_ctas(
    position: Optional[str] = Query(None, description="Filter by position"),
    include_inactive: bool = Query(False, description="Include inactive CTAs"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get all CTAs for admin management (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view CTA content"
        )
    
    # Build query
    query = select(CTAContent)
    filters = []
    
    # Filter by position if specified
    if position:
        try:
            position_enum = CTAPosition(position)
            filters.append(CTAContent.position == position_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid position: {position}"
            )
    
    # Filter by active status if needed
    if not include_inactive:
        filters.append(CTAContent.is_active == True)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by position, then sort_order, then created_at
    query = query.order_by(
        CTAContent.position, 
        CTAContent.sort_order.asc().nulls_last(), 
        CTAContent.created_at.desc()
    )
    
    result = await db.execute(query)
    ctas = result.scalars().all()
    
    # Convert to dict format for JSON response
    return [cta.to_dict() for cta in ctas]

@router.get("/admin/cta-content/{cta_id}")
async def get_cta_by_id(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific CTA by ID (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view CTA content"
        )
    
    cta = await crud_cta.get_cta_by_id(db, cta_id)
    if not cta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTA not found"
        )
    
    return cta.to_dict()

@router.post("/admin/cta-content", status_code=status.HTTP_201_CREATED)
async def create_cta(
    request: CTACreateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new CTA content (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create CTA content"
        )
    
    try:
        # Validate and convert string position to enum
        if not request.position or not request.position.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position is required"
            )
        position = CTAPosition(request.position)
        
        # Validate style
        if not request.style or not request.style.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Style is required"
            )
        
        # Convert features to list of dicts - handle both Pydantic models and plain dicts
        features = None
        if request.features:
            features = [
                f.dict() if hasattr(f, 'dict') else f 
                for f in request.features
            ]
        
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
            features=features,
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
            sort_order=request.sort_order
        )
        
        return {"message": "CTA created successfully", "id": cta.id}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid position value: {request.position}"
        )

@router.get("/admin/cta-content")
async def get_all_ctas(
    position: Optional[str] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get all CTA content (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view CTA content"
        )
    
    position_enum = None
    if position:
        try:
            position_enum = CTAPosition(position)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid position value: {position}"
            )
    
    ctas = await crud_cta.get_all_ctas(
        db=db,
        position=position_enum,
        include_inactive=include_inactive
    )
    
    return [cta.to_dict() for cta in ctas]

@router.get("/admin/cta-content/{cta_id}")
async def get_cta_by_id(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific CTA by ID (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view CTA content"
        )
    
    cta = await crud_cta.get_cta_by_id(db, cta_id)
    if not cta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTA not found"
        )
    
    return cta.to_dict()

@router.put("/admin/cta-content/{cta_id}")
async def update_cta(
    cta_id: int,
    request: CTAUpdateRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Update a CTA content (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update CTA content"
        )
    
    # Prepare update data
    update_data = {}
    for field, value in request.dict(exclude_unset=True).items():
        if value is not None:
            if field == "position":
                if value:  # Don't update if empty
                    try:
                        update_data[field] = CTAPosition(value)
                    except ValueError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid position value: {value}"
                        )
            elif field == "style":
                # Handle style enum - don't update if empty string
                if value and value.strip():
                    update_data[field] = value
            elif field == "features":
                # Handle features - they could be dicts or Pydantic models
                if value:
                    update_data[field] = [
                        f.dict() if hasattr(f, 'dict') else f 
                        for f in value
                    ]
                else:
                    update_data[field] = value
            else:
                # For other fields, skip empty strings that could cause enum errors
                if isinstance(value, str) and not value.strip() and field in ['position', 'style']:
                    continue
                update_data[field] = value
    
    cta = await crud_cta.update_cta_content(db, cta_id, **update_data)
    if not cta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTA not found"
        )
    
    return {"message": "CTA updated successfully", "id": cta.id}

@router.post("/admin/cta-content/{cta_id}/toggle-active")
async def toggle_cta_active(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Toggle the active status of a CTA (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can toggle CTA status"
        )
    
    cta = await crud_cta.toggle_cta_active_status(db, cta_id)
    if not cta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTA not found"
        )
    
    return {
        "message": f"CTA {'activated' if cta.is_active else 'deactivated'} successfully",
        "is_active": cta.is_active
    }

@router.get("/admin/debug/user-info")
async def debug_user_info(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Debug endpoint to check current user info"""
    if not current_user:
        return {"error": "No user authenticated", "user": None}
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "is_admin": getattr(current_user, 'is_admin', 'ATTRIBUTE_NOT_FOUND'),
        "is_active": getattr(current_user, 'is_active', 'ATTRIBUTE_NOT_FOUND'),
        "user_type": type(current_user).__name__
    }

@router.delete("/admin/cta-content/{cta_id}")
async def delete_cta(
    cta_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a CTA content (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete CTA content"
        )
    
    success = await crud_cta.delete_cta_content(db, cta_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CTA not found"
        )
    
    return {"message": "CTA deleted successfully"}

@router.post("/admin/cta-content/create-default")
async def create_default_cta(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create the default home page CTA (Admin only)"""
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create default CTA content"
        )
    
    try:
        cta = await crud_cta.create_default_home_cta(db)
        return {"message": "Default CTA created successfully", "id": cta.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating default CTA: {str(e)}"
        )