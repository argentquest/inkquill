"""Core application helpers for oauth config."""

# /story_app/app/core/oauth_config.py

from authlib.integrations.starlette_client import OAuth
from app.core.config import settings

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
oauth.register(
    name='google',
    client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
    client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
