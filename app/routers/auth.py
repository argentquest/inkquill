# /ai_rag_story_app/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import RedirectResponse 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone 
from pydantic import BaseModel 
import logging
import secrets
import uuid 

# --- Core Application Imports ---
from app.schemas import user as schema_user
from app.schemas.base import ApiResponse
from app.crud import user as crud_user
from app.core import security 
from app.core.deps import get_db_session, get_current_active_user 
from app.core.config import settings
from app.models.user import User
from app.services.email_service import EmailService
from app.services.referral_service import referral_service
from app.core.referral_middleware import REFERRAL_COOKIE_NAME 

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Password reset schemas
class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, name="register_new_user", summary="Register a new user account.")
async def register_new_user(user_in: schema_user.UserCreate, response: Response, request: Request, db: AsyncSession = Depends(get_db_session)):
    logger.info(f"Attempting registration for username: {user_in.username}, email: {user_in.email}")
    
    # Validate Terms of Service acceptance
    if not user_in.terms_accepted:
        logger.warning(f"Registration failed: User '{user_in.username}' did not accept Terms of Service.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must accept the Terms of Service to create an account.")
    
    existing_user_by_username = await crud_user.get_user_by_username(db, username=user_in.username)
    if existing_user_by_username:
        logger.warning(f"Registration failed: Username '{user_in.username}' already registered.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered.")
    if user_in.email:
        existing_user_by_email = await crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_by_email:
            logger.warning(f"Registration failed: Email '{user_in.email}' already registered.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    try:
        created_user = await crud_user.create_user(db=db, user=user_in)
        await db.commit()
        await db.refresh(created_user)
        logger.info(f"User '{created_user.username}' registered successfully with ID: {created_user.id} (Terms of Service accepted)")
        
        # Automatically log in the newly registered user
        access_token_expires = timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": created_user.username, "type": "access"},
            expires_delta=access_token_expires
        )
        response.set_cookie(
            key="access_token", 
            value=access_token, 
            httponly=True, 
            max_age=int(access_token_expires.total_seconds()), 
            expires=access_token_expires,
            samesite="Lax",
            secure=settings.APP_ENV.lower() == "production",
            path="/"
        )
        logger.info(f"User '{created_user.username}' automatically logged in after registration. Access token cookie set.")
        
        # Handle referral conversion if user came from a referral link
        try:
            # Check for referral cookie or state
            ref_code = getattr(request.state, 'referral_code', None)
            if not ref_code:
                ref_code = request.cookies.get(REFERRAL_COOKIE_NAME)
            
            if ref_code:
                logger.info(f"User '{created_user.username}' registered with referral code: {ref_code}")
                
                # Create anonymous session ID to match the middleware tracking
                ip_address = request.client.host
                if request.headers.get("X-Forwarded-For"):
                    ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
                
                anonymous_session_id = f"middleware_{ip_address}_{ref_code}"
                
                # Convert anonymous referral to registered user referral
                conversion_success = await referral_service.convert_anonymous_referral(
                    db=db,
                    anonymous_session_id=anonymous_session_id,
                    registered_user_id=created_user.id
                )
                
                if conversion_success:
                    logger.info(f"Successfully converted referral for user '{created_user.username}' from referrer {ref_code}")
                else:
                    logger.warning(f"Failed to convert referral for user '{created_user.username}' with code {ref_code}")
            else:
                logger.info(f"User '{created_user.username}' registered without referral code")
                
        except Exception as referral_error:
            logger.error(f"Error handling referral conversion for user '{created_user.username}': {referral_error}")
            # Don't fail registration if referral processing fails
        
        # Send welcome email
        if created_user.email:
            try:
                email_service = EmailService()
                await email_service.send_welcome_email(
                    to_email=created_user.email,
                    username=created_user.username,
                    display_name=created_user.display_name or created_user.username
                )
                logger.info(f"Welcome email sent to {created_user.email}")
            except Exception as email_error:
                logger.error(f"Failed to send welcome email to {created_user.email}: {email_error}")
                # Don't fail registration if email fails
        
        return ApiResponse.success_response(data=created_user)
    except Exception as e:
        await db.rollback() 
        logger.error(f"Error during user registration for '{user_in.username}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during user registration.")

@router.post("/login", name="login_for_access_token", summary="Login for existing user, sets HttpOnly access token cookie.")
async def login_for_access_token(response: Response, db: AsyncSession = Depends(get_db_session), form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for username: {form_data.username}")
    user = await crud_user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed for username: {form_data.username} - Incorrect username or password.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        logger.warning(f"Login failed for username: {form_data.username} - Inactive user account.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account.")
    
    access_token_expires = timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "type": "access"},
        expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=int(access_token_expires.total_seconds()), 
        expires=access_token_expires,
        samesite="Lax",
        secure=settings.APP_ENV.lower() == "production",
        path="/"
    )
    logger.info(f"User '{user.username}' logged in successfully. Access token cookie set.")
    return {"message": "Login successful. Token set in cookie."}


# --- FIX: LOGOUT ENDPOINT IS REMOVED FROM HERE ---


# --- Endpoint to get a WebSocket ticket ---
class WSTicketResponse(BaseModel): 
    ticket: str
    expires_at: datetime 

@router.get("/ws-ticket", response_model=WSTicketResponse, name="get_websocket_ticket", summary="Get a short-lived ticket for WebSocket authentication.")
async def get_websocket_ticket(
    current_user: User = Depends(get_current_active_user) 
):
    """
    Provides a short-lived JWT to be used as a ticket for authenticating
    WebSocket connections.
    """
    logger.info(f"User '{current_user.username}' requesting WebSocket ticket.")
    
    ticket_expires_delta = timedelta(seconds=300) # 5 minutes
    
    ticket_jwt = security.create_access_token(
        data={"sub": current_user.username, "type": "ws-ticket"}, 
        expires_delta=ticket_expires_delta
    )
    expires_at = datetime.now(timezone.utc) + ticket_expires_delta
    logger.info(f"WebSocket ticket generated for user '{current_user.username}', expires at {expires_at.isoformat()} (in {ticket_expires_delta.total_seconds()} seconds)")
    return WSTicketResponse(ticket=ticket_jwt, expires_at=expires_at)


# --- Impersonation endpoints (admin only) ---
class ImpersonateRequest(BaseModel):
    username: str


@router.post("/impersonate", name="impersonate_user", summary="Admin: Impersonate another user")
async def impersonate_user(
    response: Response,
    request: ImpersonateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Allows admin users to impersonate another user by creating a special token.
    The token will contain both the admin's identity and the impersonated user's identity.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to impersonate")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can impersonate other users"
        )
    
    # Get the user to impersonate
    target_user = await crud_user.get_user_by_username(db, username=request.username)
    if not target_user:
        logger.warning(f"Admin '{current_user.username}' tried to impersonate non-existent user '{request.username}'")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{request.username}' not found"
        )
    
    if not target_user.is_active:
        logger.warning(f"Admin '{current_user.username}' tried to impersonate inactive user '{request.username}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot impersonate inactive users"
        )
    
    # Create impersonation token with both admin and target user info
    access_token_expires = timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={
            "sub": target_user.username,
            "type": "access",
            "impersonator": current_user.username,  # Track who is impersonating
            "is_impersonating": True
        },
        expires_delta=access_token_expires
    )
    
    # Set the impersonation token as cookie
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=int(access_token_expires.total_seconds()), 
        expires=access_token_expires,
        samesite="Lax",
        secure=settings.APP_ENV.lower() == "production",
        path="/"
    )
    
    logger.info(f"Admin '{current_user.username}' is now impersonating user '{target_user.username}'")
    return {
        "message": f"Now impersonating user '{target_user.username}'",
        "impersonating": target_user.username,
        "admin": current_user.username
    }


@router.post("/stop-impersonation", name="stop_impersonation", summary="Admin: Stop impersonating")
async def stop_impersonation(
    response: Response,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
    request: Request = None
):
    """
    Stops impersonation and returns to the admin's original session.
    """
    # Get the token to check if we're impersonating
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No active session"
        )
    
    # Decode token to check impersonation status
    payload = await security.decode_access_token(token)
    if not payload or not payload.get("is_impersonating"):
        logger.warning(f"User '{current_user.username}' tried to stop impersonation but wasn't impersonating")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not currently impersonating"
        )
    
    admin_username = payload.get("impersonator")
    if not admin_username:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid impersonation token"
        )
    
    # Get the admin user
    admin_user = await crud_user.get_user_by_username(db, username=admin_username)
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin user not found"
        )
    
    # Create new token for the admin user (not impersonating)
    access_token_expires = timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": admin_user.username, "type": "access"},
        expires_delta=access_token_expires
    )
    
    # Set the normal token as cookie
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True, 
        max_age=int(access_token_expires.total_seconds()), 
        expires=access_token_expires,
        samesite="Lax",
        secure=settings.APP_ENV.lower() == "production",
        path="/"
    )
    
    logger.info(f"Admin '{admin_user.username}' stopped impersonating user '{current_user.username}'")
    return {
        "message": "Impersonation stopped",
        "current_user": admin_user.username
    }


# --- Password Reset Endpoints ---

@router.post("/password-reset/request", name="request_password_reset", summary="Request password reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Request a password reset email for the given email address.
    """
    logger.info(f"Password reset requested for email: {request.email}")
    
    # Check if user exists
    user = await crud_user.get_user_by_email(db, email=request.email)
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {request.email}")
        # Return success anyway to prevent email enumeration
        return {"message": "If an account with this email exists, a password reset link has been sent."}
    
    if not user.is_active:
        logger.warning(f"Password reset requested for inactive user: {request.email}")
        # Return success anyway to prevent account status enumeration
        return {"message": "If an account with this email exists, a password reset link has been sent."}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)  # 24 hour expiry
    
    # Update user with reset token
    user.reset_token = reset_token
    user.reset_token_expires = reset_token_expires
    await db.commit()
    
    # Send password reset email
    try:
        email_service = EmailService()
        reset_url = f"{settings.APP_URL}/auth/password-reset/confirm?token={reset_token}"
        
        await email_service.send_password_reset_email(
            user_email=user.email,
            user_name=user.display_name or user.username,
            reset_token=reset_token
        )
        logger.info(f"Password reset email sent to {user.email}")
    except Exception as email_error:
        logger.error(f"Failed to send password reset email to {user.email}: {email_error}")
        # Don't expose email sending errors to user
    
    return {"message": "If an account with this email exists, a password reset link has been sent."}


@router.post("/password-reset/confirm", name="confirm_password_reset", summary="Confirm password reset")
async def confirm_password_reset(
    reset_request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Confirm password reset with token and set new password.
    """
    logger.info(f"Password reset confirmation attempted with token: {reset_request.token[:8]}...")
    
    # Find user by reset token
    user = await crud_user.get_user_by_reset_token(db, reset_token=reset_request.token)
    if not user:
        logger.warning(f"Invalid reset token used: {reset_request.token[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
        logger.warning(f"Expired reset token used for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    if len(reset_request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Update password and clear reset token
    user.hashed_password = security.get_password_hash(reset_request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    await db.commit()
    
    logger.info(f"Password successfully reset for user: {user.email}")
    return {"message": "Password has been successfully reset. You can now log in with your new password."}


# --- WebSocket Authentication ---

@router.post("/ws-ticket", summary="Generate WebSocket authentication ticket")
async def create_websocket_ticket(
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a temporary ticket for WebSocket authentication.
    This ticket can be used to authenticate WebSocket connections.
    """
    try:
        # Generate a temporary ticket that expires in 5 minutes
        ticket_expires = timedelta(minutes=5)
        ticket = security.create_access_token(
            data={"sub": current_user.username, "type": "websocket"},
            expires_delta=ticket_expires
        )
        
        logger.info(f"WebSocket ticket generated for user: {current_user.username}")
        return {"ticket": ticket, "expires_in": int(ticket_expires.total_seconds())}
        
    except Exception as e:
        logger.error(f"Error generating WebSocket ticket for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate WebSocket ticket"
        )