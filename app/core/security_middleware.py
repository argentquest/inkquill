"""Core application helpers for security middleware."""

# Security middleware to prevent iframe embedding and other security vulnerabilities
import logging
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Prevents iframe embedding attacks and other security vulnerabilities.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent iframe embedding from external sites
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # Content Security Policy to block unauthorized iframes and scripts
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.quilljs.com "
            "https://stackpath.bootstrapcdn.com https://cdn.tabler.io "
            "https://www.googletagmanager.com https://www.google-analytics.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.quilljs.com "
            "https://stackpath.bootstrapcdn.com https://cdn.tabler.io; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
            "https://stackpath.bootstrapcdn.com https://cdn.tabler.io; "
            "connect-src 'self' https: "
            "https://www.google-analytics.com https://analytics.google.com "
            "https://www.googletagmanager.com; "
            "media-src 'self' https: blob:; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'self'; "
            "frame-src 'self' https: data: blob:; "
            "child-src 'self' https: data: blob:"
        )
        
        # Only add upgrade-insecure-requests in production (when HTTPS is available)
        # Check if we're in development mode (localhost or 127.0.0.1)
        is_development = (
            str(request.url.hostname) in ['localhost', '127.0.0.1'] or
            os.getenv('APP_ENV', '').lower() in ['development', 'dev'] or
            os.getenv('ENVIRONMENT', '').lower() in ['development', 'dev']
        )
        
        if not is_development:
            csp_policy += "; upgrade-insecure-requests"
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Additional security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=(), "
            "usb=(), magnetometer=(), accelerometer=(), gyroscope=()"
        )
        
        # Log security violations if any
        if "bedpage" in str(response.body).lower() if hasattr(response, 'body') else False:
            logger.critical(f"SECURITY ALERT: Detected malicious content in response for {request.url}")
        
        return response