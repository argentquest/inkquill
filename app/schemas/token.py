"""Pydantic schemas for token."""

# /story_app/app/schemas/token.py

from pydantic import BaseModel
from typing import Optional

# --- Background: Pydantic Schemas for Tokens ---
# This file defines the Pydantic models related to authentication tokens (JWTs).
# These schemas are used:
#   - To define the structure of the response when a user successfully logs in (returning an access token).
#   - Potentially, to validate the payload data contained within a decoded JWT.

class Token(BaseModel):
    """
    Pydantic model representing the access token returned upon successful login.
    """
    # The JWT access token string itself.
    access_token: str
    # The type of token, typically "bearer" for JWTs used in Authorization headers.
    token_type: str = "bearer" # Default to "bearer" as per OAuth2 standard

class TokenPayload(BaseModel):
    """
    Pydantic model representing the expected data structure within the JWT payload.
    This can be used internally (e.g., in security.py) to validate the decoded token's content.
    """
    # The 'subject' of the token, typically the user identifier (e.g., username or user ID).
    # Marked as Optional because the validation might happen after checking if 'sub' exists.
    sub: Optional[str] = None
    # You could add other standard or custom claims here if needed, e.g.:
    # exp: Optional[int] = None # Expiration time (handled during decoding)
    # iat: Optional[int] = None # Issued at time
    # iss: Optional[str] = None # Issuer
    # aud: Optional[str] = None # Audience
