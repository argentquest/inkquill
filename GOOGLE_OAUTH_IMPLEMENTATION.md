# Google OAuth Implementation Plan for AI Storytelling Assistant

## Overview
This document outlines the implementation of Google OAuth authentication using `python-social-auth`, designed to support multiple OAuth providers in the future while starting with Google as the primary provider.

## Architecture Decisions Summary
Based on our planning discussion:
- **Library**: `python-social-auth` for multi-provider support
- **Database**: Extend existing users table with OAuth fields
- **User Flow**: Separate accounts for same email, automatic account creation
- **Session**: Reuse existing session management system
- **UI**: Google sign-in on both login and registration pages

## Phase 1: Initial Setup

### 1.1 Google Cloud Console Configuration
```
1. Create new project (or use existing):
   - Go to https://console.cloud.google.com
   - Create new project: "AI-Storytelling-OAuth"

2. Enable Google+ API:
   - Navigate to "APIs & Services" > "Enable APIs"
   - Search for "Google+ API" and enable it

3. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Configure consent screen first:
     * App name: "AI Storytelling Assistant"
     * User support email: your-support@email.com
     * App logo: Upload your logo
     * Authorized domains: yourdomain.com
     * Scopes: email, profile, openid

4. Create OAuth client:
   - Application type: Web application
   - Name: "AI Storytelling Web Client"
   - Authorized JavaScript origins:
     * http://localhost:8000 (development)
     * https://yourdomain.com (production)
   - Authorized redirect URIs:
     * http://localhost:8000/auth/google/callback
     * https://yourdomain.com/auth/google/callback

5. Save credentials:
   - Download JSON file
   - Note Client ID and Client Secret
```

### 1.2 Environment Configuration
```bash
# Add to .env file
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
SOCIAL_AUTH_REDIRECT_IS_HTTPS=true  # for production
SOCIAL_AUTH_LOGIN_REDIRECT_URL=/dashboard
SOCIAL_AUTH_LOGIN_ERROR_URL=/login
SOCIAL_AUTH_NEW_USER_REDIRECT_URL=/welcome
```

### 1.3 Dependencies Installation
```bash
# Add to requirements.txt
social-auth-app-fastapi==1.0.0
social-auth-core==4.5.0
python-jose[cryptography]==3.3.0
```

## Phase 2: Database Schema Updates

### 2.1 User Table Modifications
```sql
-- Add OAuth fields to users table
ALTER TABLE users 
ADD COLUMN auth_provider VARCHAR(50) DEFAULT 'local',
ADD COLUMN provider_id VARCHAR(255) UNIQUE,
ADD COLUMN provider_data JSONB DEFAULT '{}',
ADD COLUMN profile_picture_url VARCHAR(500);

-- Create index for faster OAuth lookups
CREATE INDEX idx_users_provider_id ON users(provider_id);
CREATE INDEX idx_users_auth_provider ON users(auth_provider);
```

### 2.2 Update User Model
```python
# app/models/user.py
class User(Base):
    # ... existing fields ...
    
    # OAuth fields
    auth_provider = Column(String(50), default='local')
    provider_id = Column(String(255), unique=True, nullable=True)
    provider_data = Column(JSON, default={})
    profile_picture_url = Column(String(500), nullable=True)
    
    @property
    def is_oauth_user(self):
        return self.auth_provider != 'local'
    
    @property
    def can_set_password(self):
        return True  # All users can set password
```

## Phase 3: Backend Implementation

### 3.1 Social Auth Configuration
```python
# app/core/social_auth_config.py
from social_core.backends.google import GoogleOAuth2
from social_core.backends.oauth import BaseOAuth2
from fastapi import FastAPI
from social_auth_app_fastapi.models import init_social
from social_auth_app_fastapi.routes import social_auth_routes

SOCIAL_AUTH_PROVIDERS = {
    'google': {
        'class': GoogleOAuth2,
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
        'scope': ['email', 'profile'],
    }
}

def configure_social_auth(app: FastAPI):
    """Configure social auth for the FastAPI app"""
    init_social(app, SOCIAL_AUTH_PROVIDERS)
    app.include_router(social_auth_routes, prefix='/auth')
```

### 3.2 OAuth Routes
```python
# app/routers/oauth.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from social_auth_app_fastapi.utils import do_auth, do_complete

router = APIRouter(prefix="/auth", tags=["oauth"])

@router.get("/{provider}")
async def social_auth(provider: str, request: Request):
    """Initiate OAuth flow"""
    if provider not in SOCIAL_AUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return await do_auth(request, provider)

@router.get("/{provider}/callback")
async def social_auth_callback(
    provider: str, 
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle OAuth callback"""
    try:
        result = await do_complete(request, provider)
        user_data = result.get('user_data')
        
        # Check if user exists with this provider_id
        existing_user = await user_service.get_by_provider_id(
            db, provider, user_data['id']
        )
        
        if existing_user:
            # Login existing user
            await auth_service.create_session(request, existing_user)
            return RedirectResponse(url="/dashboard")
        
        # Check if email already exists (different account)
        email_user = await user_service.get_by_email(db, user_data['email'])
        
        if not email_user:
            # Create new user
            new_user = await create_oauth_user(db, provider, user_data)
            await auth_service.create_session(request, new_user)
            return RedirectResponse(url="/welcome")
        
        # Email exists but different account - create separate account
        new_user = await create_oauth_user_with_modified_email(
            db, provider, user_data
        )
        await auth_service.create_session(request, new_user)
        return RedirectResponse(url="/welcome?account=duplicate")
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return RedirectResponse(url="/login?error=oauth_failed")
```

### 3.3 User Creation Service
```python
# app/services/oauth_service.py
async def create_oauth_user(
    db: AsyncSession,
    provider: str,
    user_data: dict
) -> User:
    """Create a new user from OAuth data"""
    user = User(
        email=user_data['email'],
        username=generate_username_from_email(user_data['email']),
        full_name=user_data.get('name', ''),
        auth_provider=provider,
        provider_id=user_data['id'],
        provider_data=user_data,
        profile_picture_url=user_data.get('picture'),
        is_active=True,
        email_verified=True  # OAuth emails are pre-verified
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Log the OAuth registration
    await log_user_event(db, user.id, "oauth_registration", {
        "provider": provider
    })
    
    return user

async def create_oauth_user_with_modified_email(
    db: AsyncSession,
    provider: str,
    user_data: dict
) -> User:
    """Create OAuth user when email already exists"""
    # Modify email to make it unique
    base_email = user_data['email']
    modified_email = f"{provider}.{base_email}"
    
    user_data['original_email'] = base_email
    user_data['email'] = modified_email
    
    return await create_oauth_user(db, provider, user_data)
```

## Phase 4: Frontend Implementation

### 4.1 Google Sign-In Button Component
```html
<!-- app/templates/partials/_google_signin_button.html -->
<a href="{{ url_for('social_auth', provider='google') }}" 
   class="btn btn-outline-primary d-flex align-items-center justify-content-center w-100 mb-3">
    <svg class="me-2" width="18" height="18" viewBox="0 0 18 18">
        <!-- Google Logo SVG -->
        <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"/>
        <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.18L12.05 13.56c-.806.54-1.837.86-3.05.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9 18z"/>
        <path fill="#FBBC04" d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71s.102-1.17.282-1.71V4.958H.957C.347 6.173 0 7.548 0 9s.348 2.827.957 4.042l3.007-2.332z"/>
        <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/>
    </svg>
    Continue with Google
</a>
```

### 4.2 Updated Login Page
```html
<!-- app/templates/pages/login.html -->
<div class="card-body">
    <h4 class="card-title text-center mb-4">Sign In</h4>
    
    <!-- Google Sign In -->
    <div class="oauth-section">
        {% include 'partials/_google_signin_button.html' %}
        
        <div class="divider-text">
            <span class="px-3 bg-white text-muted">OR</span>
        </div>
    </div>
    
    <!-- Traditional Login Form -->
    <form method="post" action="{{ url_for('ui_login_post') }}">
        <!-- ... existing form fields ... -->
    </form>
</div>
```

### 4.3 Updated Registration Page
```html
<!-- app/templates/pages/register.html -->
<div class="card-body">
    <h4 class="card-title text-center mb-4">Create Account</h4>
    
    <!-- Google Sign Up -->
    <div class="oauth-section">
        {% include 'partials/_google_signin_button.html' %}
        
        <div class="divider-text">
            <span class="px-3 bg-white text-muted">OR</span>
        </div>
    </div>
    
    <!-- Traditional Registration Form -->
    <form method="post" action="{{ url_for('ui_register_post') }}">
        <!-- ... existing form fields ... -->
    </form>
</div>
```

### 4.4 Welcome Modal for New OAuth Users
```javascript
// app/static/js/oauth-welcome.js
function showOAuthWelcomeModal() {
    const urlParams = new URLSearchParams(window.location.search);
    const isNewOAuthUser = urlParams.get('welcome') === 'oauth';
    const isDuplicateAccount = urlParams.get('account') === 'duplicate';
    
    if (isNewOAuthUser || isDuplicateAccount) {
        const modal = new bootstrap.Modal(document.getElementById('oauthWelcomeModal'));
        
        if (isDuplicateAccount) {
            document.getElementById('welcomeMessage').innerHTML = 
                'An account with this email already exists. We\'ve created a new account for you with Google sign-in.';
        }
        
        modal.show();
        
        // Start tutorial after modal is closed
        modal._element.addEventListener('hidden.bs.modal', function() {
            if (window.startTutorial) {
                window.startTutorial();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', showOAuthWelcomeModal);
```

## Phase 5: Account Management Features

### 5.1 Allow OAuth Users to Set Password
```python
# app/routers/account_settings.py
@router.post("/set-password")
async def set_password_for_oauth_user(
    request: PasswordSetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Allow OAuth users to set a password"""
    if current_user.password_hash:
        raise HTTPException(
            status_code=400,
            detail="Password already set"
        )
    
    # Set the password
    current_user.password_hash = get_password_hash(request.password)
    await db.commit()
    
    # Send confirmation email
    await send_password_set_confirmation(current_user.email)
    
    return {"message": "Password set successfully"}
```

### 5.2 Account Settings UI Updates
```html
<!-- app/templates/pages/account_settings.html -->
{% if current_user.is_oauth_user and not current_user.password_hash %}
<div class="card mb-4">
    <div class="card-header">
        <h5>Set Password</h5>
    </div>
    <div class="card-body">
        <p>You signed up with {{ current_user.auth_provider|title }}. 
           You can set a password to also sign in with email.</p>
        <button class="btn btn-primary" data-bs-toggle="modal" 
                data-bs-target="#setPasswordModal">
            Set Password
        </button>
    </div>
</div>
{% endif %}

<!-- Display auth method -->
<div class="card mb-4">
    <div class="card-header">
        <h5>Sign-in Methods</h5>
    </div>
    <div class="card-body">
        <div class="d-flex align-items-center mb-2">
            {% if current_user.auth_provider == 'google' %}
                <img src="/static/img/google-icon.svg" width="20" class="me-2">
                Google Account
            {% endif %}
            {% if current_user.password_hash %}
                <i class="fas fa-envelope me-2"></i>
                Email & Password
            {% endif %}
        </div>
    </div>
</div>
```

## Phase 6: Testing Plan

### 6.1 Test Scenarios
```python
# tests/test_oauth_flow.py
async def test_google_oauth_new_user():
    """Test creating new user via Google OAuth"""
    # Mock Google OAuth response
    # Verify user creation
    # Check welcome redirect

async def test_google_oauth_existing_user():
    """Test login for existing OAuth user"""
    # Create user with Google provider_id
    # Mock OAuth callback
    # Verify login success

async def test_google_oauth_duplicate_email():
    """Test OAuth with existing email account"""
    # Create regular user
    # Attempt Google OAuth with same email
    # Verify separate account creation

async def test_oauth_user_set_password():
    """Test OAuth user setting password"""
    # Create OAuth user
    # Set password
    # Verify can login both ways
```

### 6.2 Security Testing
- CSRF protection on OAuth endpoints
- State parameter validation
- Redirect URI validation
- Session fixation prevention

## Phase 7: Deployment

### 7.1 Feature Flags
```python
# app/core/feature_flags.py
FEATURE_FLAGS = {
    'oauth_enabled': os.getenv('OAUTH_ENABLED', 'false') == 'true',
    'google_oauth': os.getenv('GOOGLE_OAUTH_ENABLED', 'true') == 'true',
    'facebook_oauth': os.getenv('FACEBOOK_OAUTH_ENABLED', 'false') == 'true',
}
```

### 7.2 Gradual Rollout
1. **Stage 1**: Enable for internal testing only
2. **Stage 2**: Enable for 10% of new users
3. **Stage 3**: Enable for all new users
4. **Stage 4**: Show option to existing users

### 7.3 Monitoring
```python
# Track OAuth metrics
- OAuth registration success rate
- OAuth login success rate  
- Provider usage distribution
- Duplicate email handling
- Password set rate for OAuth users
```

## Phase 8: Future Provider Support

### 8.1 Adding New Providers
To add a new OAuth provider (e.g., GitHub):

1. Add provider configuration:
```python
SOCIAL_AUTH_PROVIDERS['github'] = {
    'class': GitHubOAuth2,
    'client_id': settings.GITHUB_CLIENT_ID,
    'client_secret': settings.GITHUB_CLIENT_SECRET,
    'scope': ['user:email'],
}
```

2. Add button to UI:
```html
{% include 'partials/_github_signin_button.html' %}
```

3. No other code changes needed!

### 8.2 Provider-Specific Considerations
- **Apple**: Requires special handling for email privacy
- **Microsoft**: Different scopes for personal vs work accounts
- **Discord**: Popular with gaming/creative communities
- **GitHub**: Great for technical users

## Appendix: Troubleshooting

### Common Issues
1. **Redirect URI mismatch**: Ensure exact match in Google Console
2. **CSRF errors**: Check HTTPS settings in production
3. **Email conflicts**: Monitor duplicate account creation
4. **Session issues**: Verify cookie settings

### Debug Mode
```python
# Enable detailed OAuth logging
SOCIAL_AUTH_DEBUG = True
SOCIAL_AUTH_RAISE_EXCEPTIONS = True
```

## Security Considerations

1. **State Parameter**: Automatically handled by python-social-auth
2. **PKCE**: Not required for server-side flow but can be enabled
3. **Token Storage**: Tokens not stored, only provider_id
4. **Redirect Validation**: Whitelist allowed redirect URLs
5. **Rate Limiting**: Apply same limits as regular login

## Privacy & Compliance

1. Update Privacy Policy to include:
   - Google data collection
   - Profile picture storage
   - OAuth data retention

2. GDPR Considerations:
   - Clear consent for data collection
   - Right to disconnect OAuth
   - Data portability

3. User Communication:
   - Clear explanation of data usage
   - Option to delete OAuth data
   - Transparent account linking

This implementation provides a robust, secure, and user-friendly OAuth integration that can easily expand to support additional providers in the future.