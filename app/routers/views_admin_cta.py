"""API routes for views admin cta."""

# Admin CTA Manager View Router
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db_session
from app.models.user import User
from app.core.deps import get_current_user
from app.core.config import settings
from app.core.template_filters import setup_secure_templates

router = APIRouter(prefix="/ui/admin", tags=["Admin CTA Views"])

# Create templates instance with security filters
templates = setup_secure_templates()

@router.get("/cta-manager", response_class=HTMLResponse, name="ui_admin_cta_manager")
async def admin_cta_manager(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Admin CTA Manager page"""
    
    # Check if user is admin
    if not current_user or not getattr(current_user, 'is_admin', False):
        # Redirect to login or show error
        return templates.TemplateResponse(
            "pages/error.html",
            {
                "request": request,
                "error_title": "Access Denied",
                "error_message": "You must be an administrator to access this page.",
                "current_user": current_user
            }
        )
    
    return templates.TemplateResponse(
        "pages/admin_cta_manager.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )