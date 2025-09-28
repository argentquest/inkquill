# /ai_rag_story_app/app/routers/oauth.py

import logging
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from app.core.deps import get_db_session
from app.core.config import settings
from app.core.oauth_config import oauth
from app.core.security import create_access_token
from app.services.oauth_service import get_or_create_oauth_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["oauth"])

@router.get("/google", name="google_login")
async def google_login(request: Request):
    """Initiate Google OAuth flow"""
    if not settings.GOOGLE_OAUTH_ENABLED:
        raise HTTPException(status_code=404, detail="Google OAuth is not enabled")
    
    # Determine redirect URI based on environment
    redirect_uri = request.url_for('google_callback')
    if settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS and redirect_uri.startswith('http://'):
        redirect_uri = redirect_uri.replace('http://', 'https://', 1)
    
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle Google OAuth callback"""
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from token
        user_info = token.get('userinfo')
        if not user_info:
            # If userinfo not in token, fetch it
            resp = await oauth.google.get('userinfo', token=token)
            user_info = resp.json()
        
        logger.info(f"OAuth user info: {user_info}")
        
        # Get or create user
        user = await get_or_create_oauth_user(db, 'google', user_info)
        
        # Create JWT token (using username like regular login)
        access_token = create_access_token(
            data={"sub": user.username, "type": "access"},
            expires_delta=timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Check if this is a new user
        if user.created_at == user.updated_at:  # Newly created
            redirect_url = f"{settings.SOCIAL_AUTH_NEW_USER_REDIRECT_URL}?welcome=oauth"
        else:
            redirect_url = settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL
            
        # Create response with appropriate redirect
        response = RedirectResponse(url=redirect_url)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/"  # Add path to ensure cookie is available everywhere
        )
        
        return response
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        return RedirectResponse(url=f"{settings.SOCIAL_AUTH_LOGIN_ERROR_URL}?error=oauth_failed")