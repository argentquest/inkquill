"""Pydantic schemas for user."""

# /story_app/app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

# --- Background: Pydantic Schemas ---
# Pydantic is used for data validation and settings management using Python type annotations.
# In FastAPI, Pydantic models define the expected structure of request bodies (input)
# and the structure of response bodies (output).
# This ensures data consistency and provides automatic data validation and documentation.

# --- Base Schema ---
# A base schema can define common fields or configurations.
class UserBase(BaseModel):
    """
    Base Pydantic model for User, containing common fields.
    """
    # Define username constraints: required, min 3 chars, max 50 chars.
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for login")
    # Email is optional, but if provided, must be a valid email format.
    email: Optional[EmailStr] = Field(None, description="Optional user email address")
    # Optional display name with a maximum length.
    display_name: Optional[str] = Field(None, max_length=100, description="Optional display name")

# --- Schema for User Creation (Input) ---
# This model defines the fields required when a new user registers.
# It inherits from UserBase and adds the password field.
class UserCreate(UserBase):
    """
    Pydantic model for creating a new user (e.g., during registration).
    Password is optional to support anonymous users.
    """
    # Password is optional to support anonymous users
    password: Optional[str] = Field(None, min_length=8, description="User password (will be hashed), optional for anonymous users")
    # Terms of Service acceptance is required for new user registrations
    terms_accepted: Optional[bool] = Field(None, description="User must accept Terms of Service to register")

# --- Schema for User Update (Input) ---
# Defines optional fields that can be updated for an existing user.
class UserUpdate(BaseModel):
    """
    Pydantic model for updating user information. All fields are optional.
    """
    # All fields are optional, allowing partial updates.
    email: Optional[EmailStr] = None
    display_name: Optional[str] = Field(None, max_length=100)
    # Password can be updated, enforcing minimum length if provided.
    password: Optional[str] = Field(None, min_length=8, description="New password (if changing)")
    is_active: Optional[bool] = None

# --- Profile Update Schema ---
class UserProfileUpdate(BaseModel):
    """Schema for updating user profile information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    display_name: Optional[str] = Field(None, max_length=100, description="Display name")

# --- Password Change Schema ---
class UserPasswordChange(BaseModel):
    """Schema for changing user password"""
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Confirm new password")
    is_admin: Optional[bool] = None

# --- Schema for Reading/Returning User Data (Output) ---
# This model defines the fields that are safe to return in API responses.
# Crucially, it inherits from UserBase but *does not* include the password.
# It adds fields like 'id' and 'is_active' which are present in the database model.
class UserRead(UserBase):
    """
    Pydantic model for representing a user in API responses.
    Excludes sensitive information like the password hash.
    """
    id: int
    is_active: bool
    is_admin: Optional[bool] = False
    is_family_owner: bool = False
    created_at: datetime
    updated_at: datetime
    
    # New fields for token response
    access_token: Optional[str] = Field(None, description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: Optional[str] = Field(None, description="Type of the token (e.g., bearer)")

    model_config = ConfigDict(from_attributes=True)

class UserToken(BaseModel):
    """
    Schema for returning tokens after successful login or refresh.
    Matches the required fields from the migration document's Phase 3.1.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field("bearer", description="Type of the token")
    expires_in: int = Field(..., description="Access token expiry in seconds")

class UserTokenWithDetails(UserToken):
    """
    Includes user details along with the token. Useful for initial login response.
    """
    user: UserRead

    model_config = ConfigDict(from_attributes=True)
