from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db_session, get_current_user_with_anonymous_support
from app.core import security as core_security 
from app.crud import user as crud_user
from typing import Optional, Dict, Any
import logging
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/billing", response_class=HTMLResponse, name="ui_billing_dashboard")
async def billing_dashboard(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Render the billing dashboard page"""
    if not current_user:
        logger.info("Anonymous user accessing demo billing page.")
        # Show demo billing information for anonymous users
        demo_billing_data = {
            "total_tokens_used": 45230,
            "total_cost": 12.45,
            "current_month_tokens": 8420,
            "current_month_cost": 2.35,
            "plan_name": "Free Trial",
            "plan_tokens_limit": 50000,
            "plan_monthly_cost": 0.00,
            "usage_percentage": 85,
            "days_remaining": 14
        }
        
        return templates.TemplateResponse(
            "pages/billing_dashboard.html",
            {
                "request": request,
                "current_user": current_user,
                "page_title": "Demo Billing Dashboard",
                "billing_data": demo_billing_data,
                "is_demo": True
            }
        )
    
    return templates.TemplateResponse(
        "pages/billing_dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "page_title": "Billing Dashboard",
            "is_demo": False
        }
    )