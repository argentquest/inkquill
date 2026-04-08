# Backend Shared Architecture Document

## 1. Overview

The Backend Shared layer provides cross-cutting services consumed by all application domains (Storytelling, CareCircle, Chatbot). It establishes foundational infrastructure for authentication, billing, referrals, email notifications, storage, and AI model management.

### Key Characteristics
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (async via SQLAlchemy)
- **ORM**: SQLAlchemy 2.0 (async)
- **Architecture**: Service → CRUD → Model layers
- **Testing**: pytest (unit + integration)

### Accuracy Review
- Reviewed against shared backend routers and dependencies, including:
  - `app/routers/auth.py`
  - `app/routers/billing.py`
  - `app/routers/referrals.py`
  - `app/routers/maintenance.py`
  - `app/routers/users.py`
  - `app/core/deps.py`
- This document is directionally accurate, but the repository does not implement one monolithic "shared layer" module. Shared behavior is distributed across routers, models, dependencies, and service helpers.
- Authentication, billing, referrals, maintenance, and current-user profile APIs are all active surfaces consumed by `frontendv1`.
- When the document describes a single service boundary, prefer the actual router + dependency + model files as the source of truth for exact request/response contracts.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Backend Shared Layer                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Authentication Services                       │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │   │
│  │  │ Security        │  │ OAuth           │  │ Anonymous User       │  │   │
│  │  │                 │  │                 │  │ Service              │  │   │
│  │  │ - Password hash │  │ - Google OAuth  │  │                      │  │   │
│  │  │ - JWT tokens    │  │ - Token exchange│  │ - Create anon user   │  │   │
│  │  │ - Token verify  │  │ - User mapping  │  │ - Session tracking   │  │   │
│  │  │ - WS tickets    │  │ - State mgmt    │  │ - Balance init       │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Billing Services                              │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │   │
│  │  │ BillingService  │  │ Billing CRUD    │  │ Cost Tracker         │  │   │
│  │  │                 │  │                 │  │                      │  │   │
│  │  │ - Check balance │  │ - Account CRUD  │  │ - Start AI call      │  │   │
│  │  │ - Deduct AI cost│  │ - Transaction   │  │ - Finish AI call     │  │   │
│  │  │ - Add credits   │  │ - Packages      │  │ - Get recent calls   │  │   │
│  │  │ - Charge fixed  │  │                 │  │ - Daily summary      │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Referral Services                             │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │   │
│  │  │ ReferralService │  │ Referral Models │  │ Referral Middleware  │  │   │
│  │  │                 │  │                 │  │                      │  │   │
│  │  │ - Track visit   │  │ - Referral      │  │ - Detect ref param   │  │   │
│  │  │ - Convert anon  │  │ - ReferralReward│  │ - Set cookie         │  │   │
│  │  │ - Track action  │  │ - ReferralLimit │  │ - Pass to request    │  │   │
│  │  │ - Award rewards │  │                 │  │                      │  │   │
│  │  │ - Get stats     │  │                 │  │                      │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Email Services                                │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │   │
│  │  │ EmailService    │  │ Jinja2 Templates│  │ SMTP Config          │  │   │
│  │  │                 │  │                 │  │                      │  │   │
│  │  │ - Welcome       │  │ - welcome.html  │  │ - IONOS SMTP         │  │   │
│  │  │ - Password reset│  │ - password_     │  │ - TLS encryption     │  │   │
│  │  │ - Story complete│  │   reset.html    │  │ - Test mode          │  │   │
│  │  │ - Maintenance   │  │ - story_        │  │ - Debug logging      │  │   │
│  │  │ - Test email    │  │   completion    │  │                      │  │   │
│  │  │                 │  │ - maintenance   │  │                      │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Storage Services                              │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │   │
│  │  │ StorageService  │  │ LocalStorage    │  │ Image Providers      │  │   │
│  │  │ (abstract)      │  │                 │  │                      │  │   │
│  │  │                 │  │ - File upload   │  │ - BaseProvider       │  │   │
│  │  │ - upload        │  │ - File download │  │ - Dalle3Provider     │  │   │
│  │  │ - download      │  │ - File delete   │  │ - RunpodProvider     │  │   │
│  │  │ - delete        │  │ - Path resolve  │  │                      │  │   │
│  │  │ - exists        │  │                 │  │                      │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        AI Model Services                             │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐  │   │
│  │  │ AI Model Cache  │  │ AI Client       │  │ Semantic Kernel      │  │   │
│  │  │                 │  │ Factory           │  │                      │  │   │
│  │  │ - Load from DB  │  │                 │  │ - Kernel instance    │  │   │
│  │  │ - Get default   │  │ - Create client │  │ - Plugin setup       │  │   │
│  │  │ - Get by name   │  │ - Model routing │  │ - Function registry  │  │   │
│  │  │ - Cache mgmt    │  │ - Fallback      │  │                      │  │   │
│  │  └─────────────────┘  └─────────────────┘  └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Core Dependencies                             │   │
│  │                                                                      │   │
│  │  - get_db_session: AsyncSession dependency                           │   │
│  │  - get_current_user: User authentication dependency                  │   │
│  │  - get_current_active_user: Active user check                        │   │
│  │  - get_current_user_with_anonymous_support: Anonymous user support   │   │
│  │  - get_current_user_from_ws_ticket: WebSocket auth                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. API Endpoints (Shared)

### 3.1 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | None | Register new user |
| POST | `/api/v1/auth/login` | None | Login for access token |
| POST | `/api/v1/auth/token` | None | Get access/refresh tokens (SPA) |
| POST | `/api/v1/auth/refresh` | None | Refresh access token |
| POST | `/api/v1/auth/logout` | User | Logout user |
| GET | `/api/v1/auth/ws-ticket` | User | Get WebSocket ticket |
| POST | `/api/v1/auth/impersonate` | Admin | Admin impersonate user |
| POST | `/api/v1/auth/stop-impersonation` | User | Stop impersonation |
| POST | `/api/v1/auth/password-reset/request` | None | Request password reset |
| POST | `/api/v1/auth/password-reset/confirm` | None | Confirm password reset |
| GET | `/api/v1/auth/google` | None | Google OAuth redirect |
| GET | `/api/v1/auth/google/callback` | None | Google OAuth callback |

### 3.2 Billing

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/billing/account` | User | Get user account |
| GET | `/api/v1/billing/balance` | Optional | Get user balance |
| GET | `/api/v1/billing/transactions` | User | Get transaction history |
| GET | `/api/v1/billing/packages` | None | Get credit packages |
| POST | `/api/v1/billing/add-credits` | User | Add credits |
| GET | `/api/v1/billing/dashboard` | User | Billing dashboard |
| GET | `/api/v1/billing/balance-check/{amount}` | User | Check sufficient balance |
| GET | `/api/v1/billing/ai-costs/recent` | User | Recent AI costs |
| GET | `/api/v1/billing/ai-costs/last` | User | Last AI call info |

### 3.3 Referrals

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/referrals/stats` | User | Get referral stats |
| GET | `/api/v1/referrals/history` | User | Get referral history |
| GET | `/api/v1/referrals/rewards` | User | Get referral rewards |
| POST | `/api/v1/referrals/track` | Optional | Track referral visit |

### 3.4 Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/me` | User | Get current user |
| PUT | `/api/v1/users/me` | User | Update current user |
| GET | `/api/v1/users/me/activities` | User | Get user activities |

### 3.5 Maintenance

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/maintenance/status` | None | Get maintenance status |
| POST | `/api/v1/maintenance/status` | Admin | Update maintenance status |

---

## 4. Data Model (Shared)

### 4.1 User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    reset_token: Mapped[Optional[str]] = mapped_column(String(255))
    reset_token_expires: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))
    referral_count: Mapped[int] = mapped_column(Integer, default=0)
    referred_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.2 Billing Models

```python
class UserAccount(Base):
    __tablename__ = "user_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=50.0)
    total_spent: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    total_credits_added: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=0)
    currency: Mapped[str] = mapped_column(String(10), default="Coins")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class UserTransaction(Base):
    __tablename__ = "user_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_account_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id"))
    transaction_type: Mapped[str] = mapped_column(Enum(TransactionType))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    description: Mapped[Optional[str]] = mapped_column(Text)
    ai_cost_log_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_cost_logs.id"))
    credit_package_id: Mapped[Optional[int]] = mapped_column(ForeignKey("credit_packages.id"))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class CreditPackage(Base):
    __tablename__ = "credit_packages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    price_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    bonus_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
```

### 4.3 Referral Models

```python
class Referral(Base):
    __tablename__ = "referrals"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    referred_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    anonymous_session_id: Mapped[Optional[str]] = mapped_column(String(255))
    referral_code: Mapped[str] = mapped_column(String(50))
    source_platform: Mapped[Optional[str]] = mapped_column(String(50))
    source_content_type: Mapped[Optional[str]] = mapped_column(String(50))
    source_content_id: Mapped[Optional[str]] = mapped_column(String(100))
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    referral_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_converted: Mapped[bool] = mapped_column(Boolean, default=False)
    converted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))
    has_created_story: Mapped[bool] = mapped_column(Boolean, default=False)
    has_published_story: Mapped[bool] = mapped_column(Boolean, default=False)
    first_story_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))
    first_publish_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ReferralReward(Base):
    __tablename__ = "referral_rewards"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referral_id: Mapped[int] = mapped_column(ForeignKey("referrals.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reward_type: Mapped[str] = mapped_column(String(50))
    coin_amount: Mapped[int] = mapped_column(Integer)
    awarded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ReferralLimit(Base):
    __tablename__ = "referral_limits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    total_coins_earned: Mapped[int] = mapped_column(Integer, default=0)
    visit_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    registration_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    story_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
    publish_rewards_count: Mapped[int] = mapped_column(Integer, default=0)
```

### 4.4 AI Cost Log Model

```python
class AICallLog(Base):
    __tablename__ = "ai_cost_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    model_name: Mapped[str] = mapped_column(String(100))
    call_type: Mapped[str] = mapped_column(String(50))
    prompt_tokens: Mapped[int] = mapped_column(Integer)
    completion_tokens: Mapped[int] = mapped_column(Integer)
    total_tokens: Mapped[int] = mapped_column(Integer)
    calculated_cost_usd: Mapped[float] = mapped_column(Float)
    response_text: Mapped[Optional[str]] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    context: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 4.5 Refresh Token Model

```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

---

## 5. Service Architecture

### 5.1 BillingService

```python
class BillingService:
    async def check_sufficient_balance(db, user_id, required_amount) -> bool
    async def deduct_ai_cost(db, user_id, model_name, ai_cost_log_id) -> bool
    async def add_credits(db, user_id, credit_package_id, payment_reference) -> Dict
    async def get_user_balance(db, user_id) -> Decimal
    async def get_or_create_anonymous_user_balance(db, user_id, is_anonymous) -> Decimal
    async def add_referral_reward(db, user_id, amount, description) -> bool
    async def charge_fixed_amount(db, user_id, amount, description, service_type) -> bool
```

### 5.2 ReferralService

```python
class ReferralService:
    async def track_referral_visit(db, referrer_user_id, ...) -> Optional[Referral]
    async def convert_anonymous_referral(db, anonymous_session_id, registered_user_id) -> bool
    async def track_referral_action(db, user_id, action) -> bool
    async def _try_award_reward(db, referral, reward_type) -> bool
    async def get_user_referral_stats(db, user_id) -> Dict[str, Any]
```

### 5.3 EmailService

```python
class EmailService:
    async def send_email(to_email, subject, template_name, context, to_name) -> bool
    async def send_welcome_email(user_email, user_name, is_test) -> bool
    async def send_password_reset_email(user_email, user_name, reset_token, is_test) -> bool
    async def send_story_completion_email(user_email, user_name, story_title, ...) -> bool
    async def send_maintenance_email(user_email, user_name, maintenance_title, ...) -> bool
    async def send_test_email(test_email, custom_subject, custom_message, is_test) -> bool
    def test_email_configuration(test_email) -> Dict[str, Any]
```

### 5.4 AnonymousUserService

```python
class AnonymousUserService:
    async def get_or_create_anonymous_user(request, db) -> User
    def _get_client_ip(request) -> str
    def _create_anonymous_username() -> str
```

### 5.5 CostTrackerService

```python
class CostTrackerService:
    async def start_ai_call(user_id, operation_type, model_name, context) -> AICallLog
    async def finish_ai_call(cost_log_id, response_text, success, error_message) -> AICallLog
    async def get_recent_ai_calls(db, user_id, limit) -> List[AICallLog]
    async def get_daily_ai_cost_summary(db, user_id) -> Tuple[int, float, int]
```

---

## 6. Core Dependencies

### 6.1 Database Session

```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 6.2 Authentication Dependencies

```python
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    # Extract token from cookie or Authorization header
    # Decode and validate token
    # Return user or None

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    # Raise 401 if user is None
    # Raise 400 if user is inactive
    # Return user

async def get_current_user_with_anonymous_support(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    # Try authenticated user first
    # Fall back to anonymous user if cookie present
```

### 6.3 WebSocket Authentication

```python
async def get_current_user_from_ws_ticket(
    websocket: WebSocket,
    ticket: str,
    db: AsyncSession = Depends(get_db_session)
) -> User:
    # Decode ticket JWT
    # Look up user by username
    # Return user or raise WebSocketDisconnect
```

---

## 7. Unit Tests

### 7.1 Existing Tests

| Test File | Coverage |
|-----------|----------|
| `tests/unit/shared/test_auth_router_unit.py` | Auth router unit tests |
| `tests/unit/shared/test_billing_referrals_maintenance_unit.py` | Billing, referrals, maintenance |
| `tests/unit/shared/test_bottom10_router_coverage_unit.py` | Low-coverage router tests |
| `tests/unit/shared/test_coverage_push_60_unit.py` | Coverage push tests |
| `tests/unit/shared/test_dashboard_and_model_catalog_unit.py` | Dashboard, model catalog |
| `tests/integration/shared/test_auth_users_integration.py` | Auth + users integration |
| `tests/integration/shared/test_billing_referrals_integration.py` | Billing + referrals integration |
| `tests/integration/shared/test_remaining_backend_endpoints.py` | Remaining endpoints |

### 7.2 Test Coverage Summary

| Area | Unit Tests | Integration Tests |
|------|------------|-------------------|
| Auth Router | ✅ | ✅ |
| Users CRUD | ✅ | ✅ |
| Billing | ✅ | ✅ |
| Referrals | ✅ | ✅ |
| Maintenance | ✅ | Partial |
| OAuth | Partial | Partial |
| Anonymous User | Partial | Partial |
| Email Service | ❌ | ❌ |
| Storage Service | ❌ | ❌ |
| AI Model Cache | ❌ | ❌ |

### 7.3 Recommended Additional Tests

```python
# tests/unit/shared/test_email_service_unit.py
def test_send_welcome_email_renders_template():
def test_send_password_reset_email_includes_reset_url():
def test_test_mode_redirects_to_test_email():
def test_smtp_connection_error_returns_false():

# tests/unit/shared/test_storage_service_unit.py
def test_local_storage_upload_creates_file():
def test_local_storage_delete_removes_file():
def test_local_storage_exists_returns_true_for_existing():

# tests/unit/shared/test_anonymous_user_service_unit.py
def test_get_or_create_anonymous_user_creates_new():
def test_get_or_create_anonymous_user_returns_existing():
def test_create_anonymous_username_is_unique():

# tests/unit/shared/test_cost_tracker_unit.py
def test_start_ai_call_creates_log():
def test_finish_ai_call_updates_log():
def test_get_daily_ai_cost_summary_aggregates():
```

---

## 8. Integration Tests

### 8.1 Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| User Registration | POST /auth/register → Verify user | User created, logged in, welcome email sent |
| User Login | POST /auth/login → Verify token | Access token returned in cookie |
| Token Refresh | POST /auth/refresh → Verify new token | New access token returned |
| Balance Check | GET /billing/balance → Verify balance | Balance returned (or 0 for anonymous) |
| Referral Tracking | POST /referrals/track → Verify referral | Referral created, reward awarded |
| Maintenance Status | GET /maintenance/status → Verify status | Status returned |
| Password Reset | POST /auth/password-reset/request → Verify email | Reset email sent |

---

## 9. Suggestions and Improvements

### 9.1 Immediate Improvements
1. **Add Email Service Tests**: Test email rendering, SMTP connection, and error handling.
2. **Add Storage Service Tests**: Test file upload, download, delete, and existence checks.
3. **Implement OAuth Integration Tests**: Test full Google OAuth flow.
4. **Add Anonymous User Tests**: Test anonymous user creation and balance initialization.

### 9.2 Architecture Improvements
1. **Add Payment Gateway Integration**: Integrate Stripe for real payment processing.
2. **Implement Email Queue**: Use Celery/Redis for async email sending.
3. **Add Storage Abstraction**: Support S3, GCS, and Azure Blob Storage.
4. **Implement Rate Limiting**: Add rate limiting for auth endpoints and referral tracking.

### 9.3 Testing Improvements
1. **Add Mock SMTP Server**: Use aiosmtpd for email testing.
2. **Add Mock Storage**: Use pyfakefs for file system testing.
3. **Add Load Tests**: Test billing and referral services under load.
4. **Add Chaos Tests**: Test graceful degradation when external services fail.

### 9.4 Performance Improvements
1. **Cache User Lookups**: Cache user objects by ID and username.
2. **Batch Transaction Creation**: Batch transaction inserts for bulk operations.
3. **Optimize Referral Queries**: Add indexes for referral lookups.
4. **Use Connection Pooling**: Optimize database connection pool settings.

### 9.5 Security Considerations
1. **Rotate JWT Secrets**: Implement JWT secret rotation.
2. **Add CSRF Protection**: Add CSRF tokens for state-changing requests.
3. **Encrypt Sensitive Data**: Encrypt refresh tokens and payment references.
4. **Add Audit Logging**: Log all billing and referral transactions.

### 9.6 Scalability Considerations
1. **Horizontal Service Scaling**: Deploy shared services independently.
2. **Database Read Replicas**: Route read queries to replicas.
3. **Redis Caching**: Cache frequently accessed data (balances, user profiles).
4. **Message Queue**: Use message queue for async operations (emails, referrals).

### 9.7 Future Feature Ideas
1. **Subscription Billing**: Implement recurring subscription billing.
2. **Multi-Currency Support**: Support multiple currencies for billing.
3. **Referral Tiers**: Implement tiered referral rewards.
4. **Email Templates Admin**: Admin UI for managing email templates.
5. **Storage Analytics**: Track storage usage and costs.
6. **AI Model Marketplace**: Allow users to select and pay for different AI models.
