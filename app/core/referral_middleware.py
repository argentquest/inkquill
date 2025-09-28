"""
Middleware for tracking referral links.
"""
import logging
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from urllib.parse import parse_qs

from app.core.deps import get_db_session
from app.services.referral_service import referral_service
from app.services.anonymous_user_service import anonymous_user_service
from app.utils.bot_detection import is_bot_request, get_bot_info

logger = logging.getLogger(__name__)

REFERRAL_COOKIE_NAME = "ref_code"
REFERRAL_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days


class ReferralTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track referral links and set cookies."""
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is a bot request
        if is_bot_request(request):
            bot_info = get_bot_info(request)
            logger.info(f"Bot detected in referral middleware: {bot_info['bot_name']} - adding cache headers")
            
            # Get response and add cache headers for bots
            response = await call_next(request)
            
            # Add cache headers to reduce bot re-fetching
            response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=3600"  # 1 hour
            response.headers["Expires"] = "Mon, 01 Jan 2025 00:00:00 GMT"
            response.headers["ETag"] = f'"{hash(str(request.url))}"'
            
            return response
        
        # Check for referral parameter in query string
        ref_code = request.query_params.get("ref")
        
        logger.info(f"🔍 MIDDLEWARE DEBUG: Processing request {request.url}")
        logger.info(f"🔍 MIDDLEWARE DEBUG: Query params: {dict(request.query_params)}")
        logger.info(f"🔍 MIDDLEWARE DEBUG: Referral code from URL: {ref_code}")
        
        if ref_code:
            # Store in request state for later use
            request.state.referral_code = ref_code
            
            # Get response first
            response = await call_next(request)
            
            # Set referral cookie
            response.set_cookie(
                key=REFERRAL_COOKIE_NAME,
                value=ref_code,
                max_age=REFERRAL_COOKIE_MAX_AGE,
                httponly=False,  # Changed to False so JavaScript can access it
                secure=request.url.scheme == "https",
                samesite="lax"
            )
            
            logger.info(f"Set referral cookie for code: {ref_code}")
            
            # Track the referral immediately
            logger.info(f"🔍 MIDDLEWARE DEBUG: Attempting to track referral for code: {ref_code}")
            try:
                # Get IP and user agent
                ip_address = request.client.host
                if request.headers.get("X-Forwarded-For"):
                    ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
                
                user_agent = request.headers.get("User-Agent", "")
                
                # Track the referral visit
                async for db in get_db_session():
                    try:
                        referrer_user_id = int(ref_code)
                        logger.info(f"🔍 MIDDLEWARE DEBUG: Calling track_referral_visit with referrer_user_id: {referrer_user_id}")
                        
                        result = await referral_service.track_referral_visit(
                            db=db,
                            referrer_user_id=referrer_user_id,
                            referred_user_id=None,  # Anonymous user
                            anonymous_session_id=f"middleware_{ip_address}_{referrer_user_id}",
                            source_platform="web",
                            source_content_type="direct_link",
                            source_content_id=None,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            referral_url=str(request.url)
                        )
                        
                        logger.info(f"🔍 MIDDLEWARE DEBUG: Track result: {result}")
                        
                        if result:
                            logger.info(f"🔍 MIDDLEWARE DEBUG: Successfully tracked referral {result.id}")
                        else:
                            logger.warning(f"🔍 MIDDLEWARE DEBUG: Failed to track referral")
                            
                    except ValueError:
                        logger.error(f"🔍 MIDDLEWARE DEBUG: Invalid referral code: {ref_code}")
                    except Exception as e:
                        logger.error(f"🔍 MIDDLEWARE DEBUG: Error tracking referral: {e}")
                    break
                        
            except Exception as e:
                logger.error(f"🔍 MIDDLEWARE DEBUG: Exception during referral tracking: {e}")
            
        else:
            # Check for existing referral cookie
            ref_cookie = request.cookies.get(REFERRAL_COOKIE_NAME)
            if ref_cookie:
                request.state.referral_code = ref_cookie
                logger.debug(f"Found existing referral cookie: {ref_cookie}")
            
            response = await call_next(request)
        
        return response


async def track_referral_from_request(
    request: Request,
    user_id: Optional[int] = None,
    anonymous_session_id: Optional[str] = None
) -> bool:
    """Track a referral from the current request."""
    try:
        # Get referral code from request state or cookie
        ref_code = getattr(request.state, "referral_code", None)
        if not ref_code:
            ref_code = request.cookies.get(REFERRAL_COOKIE_NAME)
        
        if not ref_code:
            return False
        
        # Try to parse referral code as user ID
        try:
            referrer_user_id = int(ref_code)
        except ValueError:
            logger.warning(f"Invalid referral code: {ref_code}")
            return False
        
        # Don't allow self-referrals
        if user_id and user_id == referrer_user_id:
            logger.warning(f"Self-referral attempt by user {user_id}")
            return False
        
        # Get source information from headers/URL
        source_platform = None
        referer = request.headers.get("referer", "")
        
        # Detect social platforms from referer
        if "facebook.com" in referer:
            source_platform = "facebook"
        elif "twitter.com" in referer or "t.co" in referer:
            source_platform = "twitter"
        elif "linkedin.com" in referer:
            source_platform = "linkedin"
        elif "reddit.com" in referer:
            source_platform = "reddit"
        elif "whatsapp.com" in referer:
            source_platform = "whatsapp"
        
        # Get content info from URL path
        source_content_type = None
        source_content_id = None
        
        path = str(request.url.path)
        if "/story/" in path:
            source_content_type = "story"
            # Extract story ID from path
            parts = path.split("/story/")
            if len(parts) > 1:
                source_content_id = parts[1].split("/")[0]
        elif "/world/" in path:
            source_content_type = "world"
            parts = path.split("/world/")
            if len(parts) > 1:
                source_content_id = parts[1].split("/")[0]
        elif "/image/" in path:
            source_content_type = "image"
        
        # Get IP and user agent
        ip_address = request.client.host
        if request.headers.get("X-Forwarded-For"):
            ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
        
        user_agent = request.headers.get("User-Agent", "")
        
        # Track the referral
        async for db in get_db_session():
            result = await referral_service.track_referral_visit(
                db=db,
                referrer_user_id=referrer_user_id,
                referred_user_id=user_id,
                anonymous_session_id=anonymous_session_id,
                source_platform=source_platform,
                source_content_type=source_content_type,
                source_content_id=source_content_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referral_url=str(request.url)
            )
            
            return result is not None
        
        return False
        
    except Exception as e:
        logger.error(f"Error tracking referral: {e}")
        return False