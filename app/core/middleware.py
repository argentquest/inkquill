# /ai_rag_story_app/app/core/middleware.py
import uuid
import time
import json
from typing import Optional, Callable, Awaitable, Dict, Any, Set
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware 
# Removed: RequestResponseCall as it's causing ImportError
from starlette.requests import Request
from starlette.responses import Response
from contextvars import Token as ContextVarToken
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import request_id_var, user_identifier_var
from app.db.database import async_session_local
from app.crud.user_activity import create_user_activity
from app.schemas.user_activity import UserActivityCreate
from app.core import security
import logging

logger = logging.getLogger(__name__)

class LoggingContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]] # <<< MODIFIED type hint for call_next
    ) -> Response:
        
        request_id_context_token: Optional[ContextVarToken] = None
        user_identifier_context_token: Optional[ContextVarToken] = None
        
        current_request_id_value = "[no_request_id_set]" # Default if something goes wrong

        try:
            # --- Request ID Handling ---
            current_request_id_value = request.headers.get("X-Request-ID")
            if not current_request_id_value:
                current_request_id_value = str(uuid.uuid4())
            
            # Set the request_id in the context variable.
            request_id_context_token = request_id_var.set(current_request_id_value)
            request.state.request_id = current_request_id_value

            # --- User Identifier Handling (Default for HTTP) ---
            if user_identifier_var.get() == "[no_user_context]": 
                user_identifier_context_token = user_identifier_var.set("[anonymous_http]")
            
            response = await call_next(request)
            
            if response:
                 response.headers["X-Request-ID"] = current_request_id_value # Use the value that was set/used
            
            return response

        except Exception as e:
            # Log with the request ID if available, even on error
            logger.error(f"Error in LoggingContextMiddleware (ReqID: {current_request_id_value}): {e}", exc_info=True)
            raise # Re-raise the original exception to be handled by FastAPI's error handling
        finally:
            if request_id_context_token is not None:
                request_id_var.reset(request_id_context_token)
            if user_identifier_context_token is not None:
                user_identifier_var.reset(user_identifier_context_token)


class UserActivityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log all HTTP requests as user activities.
    This provides comprehensive audit trail and analytics capabilities.
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        # Configuration options
        self.exclude_paths: Set[str] = kwargs.get("exclude_paths", {
            "/docs", "/redoc", "/openapi.json", "/health", "/metrics",
            "/favicon.ico", "/static"
        })
        self.exclude_methods: Set[str] = kwargs.get("exclude_methods", {"OPTIONS"})
        self.log_request_body: bool = kwargs.get("log_request_body", False)
        self.log_response_body: bool = kwargs.get("log_response_body", False)
        self.max_body_size: int = kwargs.get("max_body_size", 1000)  # Max chars to log
        self.sensitive_fields: Set[str] = kwargs.get("sensitive_fields", {
            "password", "token", "secret", "api_key", "credit_card", "ssn"
        })
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Skip logging for excluded paths and methods
        if self._should_skip_logging(request):
            return await call_next(request)
        
        start_time = time.time()
        user_id = None
        user_agent = request.headers.get("user-agent", "")
        client_ip = self._get_client_ip(request)
        request_id = request_id_var.get("[no_request_id]")
        
        # Try to get user ID from authentication
        try:
            # Check cookie first (primary auth method in this app)
            token = request.cookies.get("access_token")
            if not token:
                # Check Authorization header as fallback
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
            
            if token:
                payload = await security.decode_access_token(token=token)
                if payload:
                    # The 'sub' field contains the username, not the user ID
                    # We need to look up the user to get their ID
                    username = payload.get("sub")
                    if username:
                        # Import here to avoid circular imports
                        from app.crud.user import get_user_by_username
                        async with async_session_local() as db:
                            user = await get_user_by_username(db, username=username)
                            if user:
                                user_id = user.id
        except Exception as e:
            logger.debug(f"Could not extract user from token: {e}")
        
        # Prepare request data
        request_data = None
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            request_data = await self._get_request_data(request)
        
        # Determine action type and category
        action_type, action_category = self._determine_action_type(request)
        
        response = None
        error_message = None
        error_type = None
        status_code = 500  # Default to error if exception occurs
        
        try:
            # Process the request
            response = await call_next(request)
            status_code = response.status_code
            
            # Log errors
            if status_code >= 400:
                error_type = "HTTP_ERROR"
                error_message = f"HTTP {status_code}"
                
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Prepare response data
            response_data = None
            if self.log_response_body and response and status_code < 400:
                response_data = {"status_code": status_code}
            
            # Create activity log
            try:
                async with async_session_local() as db:
                    activity = UserActivityCreate(
                        user_id=user_id,
                        action_type=action_type,
                        action_category=action_category,
                        action_details=self._get_action_details(request),
                        endpoint=str(request.url.path),
                        method=request.method,
                        status_code=status_code,
                        duration_ms=duration_ms,
                        ip_address=client_ip,
                        user_agent=user_agent[:500] if user_agent else None,  # Limit length
                        request_id=request_id,
                        request_data=request_data,
                        response_data=response_data,
                        error_message=error_message,
                        error_type=error_type
                    )
                    await create_user_activity(db, activity, request)
            except Exception as e:
                # Don't let logging errors break the application
                logger.error(f"Failed to log user activity: {e}", exc_info=True)
        
        return response
    
    def _should_skip_logging(self, request: Request) -> bool:
        """Check if this request should be skipped from logging."""
        # Skip excluded methods
        if request.method in self.exclude_methods:
            return True
        
        # Skip excluded paths
        path = str(request.url.path)
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check X-Forwarded-For header (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _get_request_data(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract and sanitize request data."""
        try:
            # Clone request body (it can only be read once)
            body = await request.body()
            
            # Try to parse as JSON
            if body:
                try:
                    data = json.loads(body)
                    # Sanitize sensitive fields
                    return self._sanitize_data(data)
                except json.JSONDecodeError:
                    # If not JSON, store as string (truncated)
                    body_str = body.decode("utf-8", errors="ignore")
                    return {"raw": body_str[:self.max_body_size]}
            
        except Exception as e:
            logger.debug(f"Could not extract request body: {e}")
        
        return None
    
    def _sanitize_data(self, data: Any) -> Any:
        """Remove sensitive fields from data."""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self._sanitize_data(value)
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data
    
    def _determine_action_type(self, request: Request) -> tuple[str, str]:
        """Determine the action type and category from the request."""
        path = str(request.url.path)
        method = request.method
        
        # Authentication endpoints
        if "/auth/" in path or "/login" in path or "/register" in path:
            return f"{method.lower()}_auth", "auth"
        
        # API endpoints by resource
        if "/api/" in path:
            parts = path.split("/")
            if len(parts) > 2:
                resource = parts[2]  # e.g., /api/stories/... -> stories
                return f"{method.lower()}_{resource}", resource
        
        # WebSocket endpoints
        if "/ws/" in path:
            return "websocket_connect", "websocket"
        
        # Default
        return f"{method.lower()}_request", "general"
    
    def _get_action_details(self, request: Request) -> str:
        """Generate human-readable action description."""
        path = str(request.url.path)
        method = request.method
        
        # Special cases for common endpoints
        if path == "/api/auth/login" and method == "POST":
            return "User login attempt"
        elif path == "/api/auth/register" and method == "POST":
            return "New user registration"
        elif path.startswith("/api/stories") and method == "POST":
            return "Created new story"
        elif path.startswith("/api/stories") and method == "GET":
            return "Retrieved stories"
        elif path.startswith("/api/worlds") and method == "POST":
            return "Created new world"
        
        # Generic description
        return f"{method} request to {path}"