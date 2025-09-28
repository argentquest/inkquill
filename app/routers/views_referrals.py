"""
View routes for referral analytics dashboard.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.deps import get_current_active_user, get_current_user
from app.models.user import User
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/ui/referrals", response_class=HTMLResponse, name="ui_referrals")
async def referrals_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Display referral analytics dashboard."""
    return templates.TemplateResponse(
        "pages/referrals.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": "AI Story App"
        }
    )

@router.get("/ui/referrals/intro", response_class=HTMLResponse, name="ui_referrals_intro")
async def referrals_intro(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Display referral introduction and guide page."""
    return templates.TemplateResponse(
        "pages/referral_intro.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": "AI Story App"
        }
    )