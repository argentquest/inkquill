"""API routes for views admin billing."""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin/billing", response_class=HTMLResponse, name="ui_admin_billing_dashboard")
async def admin_billing_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Render the admin billing dashboard page"""
    if not current_user:
        # Redirect to login if not authenticated
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "page_title": "Login Required",
                "message": "Please log in to access the admin billing dashboard."
            }
        )
    
    if not current_user.is_admin:
        # Show access denied for non-admin users
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "page_title": "Access Denied",
                "message": "Admin access required to view this page."
            }
        )
    
    return templates.TemplateResponse(
        "pages/admin_billing_dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "page_title": "Admin Billing Dashboard"
        }
    )