"""API routes for views admin maintenance."""

# /story_app/app/routers/views_admin_maintenance.py

from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Optional

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.core.config import settings
from app.services.email_service import EmailService
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ui/admin",
    tags=["admin-ui-maintenance"],
    dependencies=[Depends(get_current_active_user)]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/maintenance", response_class=HTMLResponse, name="admin_maintenance_page")
async def admin_maintenance_page(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Admin maintenance control page"""
    
    # Check if user has admin privileges
    if not current_user or not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.username if current_user else 'unknown'} attempted to access maintenance admin page")
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "page_title": "Access Denied",
                "message": "Admin access required to view this page."
            }
        )
    
    logger.info(f"Admin user {current_user.username} accessing maintenance control page")
    
    return templates.TemplateResponse(
        "pages/admin_maintenance.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )


@router.post("/test-email")
async def test_email(
    request: Request,
    test_email: str = Form(...),
    email_type: str = Form(default="test"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Send a test email to verify email configuration"""
    
    # Check if user has admin privileges
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        email_service = EmailService()
        
        if email_type == "welcome":
            success = await email_service.send_welcome_email(
                user_email=test_email,
                user_name="Test User",
                is_test=True
            )
        elif email_type == "password_reset":
            success = await email_service.send_password_reset_email(
                user_email=test_email,
                user_name="Test User",
                reset_token="test-token-123",
                is_test=False  # Test real production mode
            )
        elif email_type == "story_completion":
            success = await email_service.send_story_completion_email(
                user_email=test_email,
                user_name="Test User",
                story_title="Test Story",
                milestone_type="completion",
                story_url="#",
                is_test=True
            )
        elif email_type == "maintenance":
            success = await email_service.send_maintenance_email(
                user_email=test_email,
                user_name="Test User",
                maintenance_title="Test Maintenance",
                maintenance_message="This is a test maintenance notification",
                start_time="Now",
                end_time="In 30 minutes",
                is_test=True
            )
        else:  # test email
            success = await email_service.send_test_email(
                test_email=test_email,
                is_test=True
            )
        
        if success:
            logger.info(f"Admin {current_user.username} sent test email of type '{email_type}' to {test_email}")
            return JSONResponse({
                "success": True,
                "message": f"Test {email_type} email sent successfully to {test_email}"
            })
        else:
            logger.error(f"Failed to send test email of type '{email_type}' to {test_email}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Failed to send test email. Check server logs for details."
                }
            )
    
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error sending test email: {str(e)}"
            }
        )


@router.get("/user-email", response_class=HTMLResponse, name="admin_user_email_page")
async def admin_user_email_page(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Admin page for sending emails to specific users"""
    
    # Check if user has admin privileges
    if not current_user or not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.username if current_user else 'unknown'} attempted to access user email admin page")
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "page_title": "Access Denied",
                "message": "Admin access required to view this page."
            }
        )
    
    logger.info(f"Admin user {current_user.username} accessing user email page")
    
    return templates.TemplateResponse(
        "pages/admin_user_email.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "page_title": "Send User Email - Admin"
        }
    )


@router.get("/api/users")
async def get_users_list(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get list of users for admin user email interface"""
    
    # Check if user has admin privileges
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Get all users with basic info
        result = await db.execute(
            select(User.id, User.username, User.email, User.full_name, User.is_active, User.created_at)
            .order_by(User.username)
        )
        users = result.all()
        
        users_list = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ]
        
        return JSONResponse({
            "success": True,
            "users": users_list,
            "total": len(users_list)
        })
    
    except Exception as e:
        logger.error(f"Error fetching users list: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error fetching users: {str(e)}"
            }
        )


@router.post("/send-user-email")
async def send_user_email(
    request: Request,
    user_id: int = Form(...),
    email_type: str = Form(...),
    custom_subject: Optional[str] = Form(None),
    custom_message: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Send email to a specific user"""
    
    # Check if user has admin privileges
    if not current_user or not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Get the target user
        result = await db.execute(select(User).where(User.id == user_id))
        target_user = result.scalar_one_or_none()
        
        if not target_user:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": "User not found"
                }
            )
        
        email_service = EmailService()
        success = False
        
        if email_type == "welcome":
            success = await email_service.send_welcome_email(
                user_email=target_user.email,
                user_name=target_user.full_name or target_user.username
            )
        elif email_type == "maintenance":
            maintenance_title = custom_subject or "Scheduled System Maintenance"
            maintenance_message = custom_message or "We will be performing scheduled maintenance to improve our services."
            success = await email_service.send_maintenance_email(
                user_email=target_user.email,
                user_name=target_user.full_name or target_user.username,
                maintenance_title=maintenance_title,
                maintenance_message=maintenance_message,
                start_time="Soon",
                end_time="Within the next hour"
            )
        elif email_type == "custom":
            # For custom emails, we'll use the test template with custom content
            success = await email_service.send_test_email(
                test_email=target_user.email,
                custom_subject=custom_subject,
                custom_message=custom_message
            )
        
        if success:
            logger.info(f"Admin {current_user.username} sent {email_type} email to user {target_user.username} ({target_user.email})")
            return JSONResponse({
                "success": True,
                "message": f"Email sent successfully to {target_user.username} ({target_user.email})"
            })
        else:
            logger.error(f"Failed to send {email_type} email to user {target_user.username}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Failed to send email. Check server logs for details."
                }
            )
    
    except Exception as e:
        logger.error(f"Error sending user email: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error sending email: {str(e)}"
            }
        )


@router.get("/image-jobs", response_class=HTMLResponse, name="admin_image_jobs_page")
async def admin_image_jobs_page(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Admin image generation jobs monitoring page"""
    
    # Check if user has admin privileges
    if not current_user or not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.username if current_user else 'unknown'} attempted to access image jobs admin page")
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "page_title": "Access Denied",
                "message": "Admin access required to view this page."
            }
        )
    
    logger.info(f"Admin user {current_user.username} accessing image jobs monitoring page")
    
    return templates.TemplateResponse(
        "pages/admin_image_jobs.html",
        {
            "request": request,
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "page_title": "Image Generation Jobs - Admin"
        }
    )
