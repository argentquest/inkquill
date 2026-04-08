# Frontend Shared Architecture Document

## 1. Overview

The Frontend Shared layer provides cross-cutting infrastructure consumed by all application surfaces (Storytelling, CareCircle, Chatbot). It establishes the foundational shell, authentication, state management, routing, and platform behavior that every app-specific surface inherits.

### Key Characteristics
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom design tokens
- **State Management**: React Context + TanStack Query
- **Testing**: Playwright E2E tests

### Accuracy Review
- Reviewed against:
  - `frontendv1/app/layout.tsx`
  - `frontendv1/components/providers/app-providers.tsx`
  - `frontendv1/components/platform/platform-context.ts`
  - `frontendv1/components/shell/**`
  - `frontendv1/lib/apps/**`
- This document is broadly accurate for the active shared shell.
- The most important confirmed shared behaviors in the repository today are:
  - route-based app/surface resolution
  - session bootstrap
  - balance loading
  - maintenance loading/gating
  - theme persistence
  - cookie consent persistence
  - global notification/toast presentation
- The retired shared `/app` shell still appears in compatibility redirects, but the active product direction is app-specific surfaces such as `/storytelling`, `/care-circle-family`, `/care-circle-patient`, and `/chatbot`.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Frontend Shared Layer                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Root Layout (app/layout.tsx)                  │   │
│  │                                                                      │   │
│  │  <html>                                                              │   │
│  │    <body>                                                            │   │
│  │      <AppProviders>  ← Session, Balance, Maintenance, Theme          │   │
│  │        <AppShellResolver>  ← Route → Surface → Context Resolution    │   │
│  │          {children}  ← App-specific surfaces render here             │   │
│  │        </AppShellResolver>                                           │   │
│  │      </AppProviders>                                                 │   │
│  │    </body>                                                           │   │
│  │  </html>                                                             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        AppProviders (providers/app-providers.tsx)    │   │
│  │                                                                      │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  ┌──────────┐ │   │
│  │  │ Session     │  │ Balance      │  │ Maintenance   │  │ Theme    │ │   │
│  │  │ Provider    │  │ Provider     │  │ Provider      │  │ Provider │ │   │
│  │  │             │  │              │  │               │  │          │ │   │
│  │  │ - user      │  │ - balance    │  │ - enabled     │  │ - mode   │ │   │
│  │  │ - loading   │  │ - loading    │  │ - message     │  │ - toggle │ │   │
│  │  │ - refresh   │  │ - refresh    │  │ - refresh     │  │          │ │   │
│  │  └─────────────┘  └──────────────┘  └───────────────┘  └──────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        AppShell (shell/app-shell.tsx)                │   │
│  │                                                                      │   │
│  │  ┌────────────────────────────────────────────────────────────────┐  │   │
│  │  │ TopNav                                                         │  │   │
│  │  │  - Logo, Navigation Links, User Menu, Theme Toggle             │  │   │
│  │  ├────────────────────────────────────────────────────────────────┤  │   │
│  │  │ Breadcrumbs (optional)                                         │  │   │
│  │  ├────────────────────────────────────────────────────────────────┤  │   │
│  │  │ MaintenanceBanner (conditional)                                │  │   │
│  │  ├────────────────────────────────────────────────────────────────┤  │   │
│  │  │ Main Content Area ({children})                                 │  │   │
│  │  ├────────────────────────────────────────────────────────────────┤  │   │
│  │  │ Footer                                                         │  │   │
│  │  │  - Links, Copyright, Cookie Consent                           │  │   │
│  │  └────────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Platform Layer                                │   │
│  │                                                                      │   │
│  │  ┌───────────────────┐  ┌────────────────────┐  ┌─────────────────┐ │   │
│  │  │ PlatformContext   │  │ AppShellResolver   │  │ AppRouteLanding │ │   │
│  │  │                   │  │                    │  │                 │ │   │
│  │  │ - surface_id      │  │ - resolve surface  │  │ - surface info  │ │   │
│  │  │ - app_id          │  │ - apply shell      │  │ - auth gating   │ │   │
│  │  │ - owner_scope     │  │ - render landing   │  │ - navigation    │ │   │
│  │  │ - memberships     │  │                    │  │                 │ │   │
│  │  └───────────────────┘  └────────────────────┘  └─────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        UI Component Library                          │   │
│  │                                                                      │   │
│  │  Button, TextField, PasswordField, Form, Dialog, Drawer, DataTable,  │   │
│  │  LoadingState, ErrorState, EmptyState, AlertBanner, ToastCenter,     │   │
│  │  Skeleton, StatCard, AccountSummaryPanel, SettingsFormSection,       │   │
│  │  GoogleSignInButton, InlineValidationMessage, ConfirmationModal      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        API Client Layer (lib/api.ts)                 │   │
│  │                                                                      │   │
│  │  - apiGet<T>(path) → Promise<ApiEnvelope<T>>                         │   │
│  │  - apiPostJson<TResponse, TBody>(path, body)                         │   │
│  │  - apiPutJson<TResponse, TBody>(path, body)                          │   │
│  │  - apiPostForm<TResponse>(path, formData)                            │   │
│  │                                                                      │   │
│  │  Shared fetchers:                                                    │   │
│  │  - fetchSession(), fetchBalance(), fetchMaintenanceStatus()          │   │
│  │  - fetchBillingDashboard(), fetchReferralStats()                     │   │
│  │  - loginUser(), registerUser(), logoutUser()                         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Type Definitions (lib/types.ts)               │   │
│  │                                                                      │   │
│  │  - SessionUser, BalanceState, MaintenanceState                       │   │
│  │  - ApiEnvelope<T>, PlatformSurfaceId, PlatformCurrentContext         │   │
│  │  - AppMembership, BillingDashboard, ReferralStats                    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Route Structure (Shared)

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | `page.tsx` | Public landing page |
| `/about` | `about/page.tsx` | About page |
| `/help` | `help/page.tsx` | Help center |
| `/privacy` | `privacy/page.tsx` | Privacy policy |
| `/terms` | `terms/page.tsx` | Terms of service |
| `/access-denied` | `access-denied/page.tsx` | Access denied page |
| `/auth/login` | `auth/login/page.tsx` | Login form |
| `/auth/register` | `auth/register/page.tsx` | Registration form |
| `/auth/forgot-password` | `auth/forgot-password/page.tsx` | Password reset request |
| `/auth/reset-password` | `auth/reset-password/page.tsx` | Password reset confirm |
| `/app/*` | Legacy routes | Bridge to app-specific surfaces |

---

## 4. Data Model (Shared Types)

```typescript
// API Response Envelope
interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  errors?: ApiError[];
}

interface ApiError {
  code?: string;
  message: string;
  detail?: string;
}

// Session State
interface SessionUser {
  id: number;
  username: string;
  email: string;
  displayName?: string;
  isActive: boolean;
  isAdmin: boolean;
  createdAt: string;
}

interface SessionState {
  status: 'authenticated' | 'unauthenticated' | 'loading';
  user: SessionUser | null;
}

// Balance State
interface BalanceState {
  balance: number;
  currency: string;
  error: string | null;
}

// Maintenance State
interface MaintenanceState {
  enabled: boolean;
  message: string | null;
  updated_at: string | null;
  end_time: string | null;
}

// Platform Types
type PlatformSurfaceId = 
  | 'storytelling'
  | 'care-circle-family'
  | 'care-circle-patient'
  | 'chatbot'
  | 'legacy-app'
  | 'public';

type OwnerScope = 'user' | 'family' | 'patient' | 'none';

interface PlatformCurrentContext {
  surface_id: PlatformSurfaceId;
  app_id: string | null;
  requires_auth: boolean;
  owner_scope: OwnerScope;
  title: string;
  description: string;
  memberships: AppMembership[];
}

interface AppMembership {
  surface_id: PlatformSurfaceId;
  granted: boolean;
  reason: string | null;
}

// Billing Dashboard
interface BillingDashboard {
  account: UserAccount;
  recentTransactions: UserTransaction[];
  availablePackages: CreditPackage[];
}

// Referral Types
interface ReferralStats {
  totalReferrals: number;
  convertedReferrals: number;
  totalRewards: number;
  referralCode: string;
}

interface ReferralHistoryResponse {
  referrals: ReferralRecord[];
  total: number;
}

interface ReferralRewardsResponse {
  rewards: RewardRecord[];
  total: number;
}
```

---

## 5. API Endpoints Consumed (Shared)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/me` | Optional | Get current user session |
| GET | `/api/v1/billing/balance` | Optional | Get user balance |
| GET | `/api/v1/maintenance/status` | None | Get maintenance state |
| POST | `/api/v1/auth/login` | None | User login |
| POST | `/api/v1/auth/register` | None | User registration |
| POST | `/api/v1/auth/logout` | User | User logout |
| POST | `/api/v1/auth/password-reset/request` | None | Request password reset |
| POST | `/api/v1/auth/password-reset/confirm` | None | Confirm password reset |
| GET | `/api/v1/billing/dashboard` | User | Billing dashboard data |
| GET | `/api/v1/referrals/stats` | User | Referral statistics |
| GET | `/api/v1/referrals/history` | User | Referral history |
| GET | `/api/v1/referrals/rewards` | User | Referral rewards |
| PUT | `/api/v1/users/me` | User | Update user profile |

---

## 6. Component Architecture

### 6.1 Shell Components

| Component | File | Purpose |
|-----------|------|---------|
| `AppShell` | `shell/app-shell.tsx` | Main layout wrapper with nav, content, footer |
| `TopNav` | `shell/top-nav.tsx` | Top navigation bar |
| `Footer` | `shell/footer.tsx` | Site footer |
| `Breadcrumbs` | `shell/breadcrumbs.tsx` | Navigation breadcrumbs |
| `PageHeader` | `shell/page-header.tsx` | Page header with title, description, action |
| `UserMenu` | `shell/user-menu.tsx` | User dropdown menu |
| `ThemeToggle` | `shell/theme-toggle.tsx` | Light/dark theme toggle |
| `CoinBalanceBadge` | `shell/coin-balance-badge.tsx` | Display user coin balance |

### 6.2 State & Gating Components

| Component | File | Purpose |
|-----------|------|---------|
| `AppShellGuard` | `shell/app-shell-guard.tsx` | Auth + maintenance gating wrapper |
| `MaintenanceGate` | `shell/maintenance-gate.tsx` | Show maintenance message when enabled |
| `MaintenanceBanner` | `shell/maintenance-banner.tsx` | Banner showing maintenance status |
| `CookieConsentBanner` | `shell/cookie-consent-banner.tsx` | GDPR cookie consent |

### 6.3 Platform Components

| Component | File | Purpose |
|-----------|------|---------|
| `AppShellResolver` | `platform/app-shell-resolver.tsx` | Resolves route to surface context |
| `AppRouteLanding` | `platform/platform-route-landing.tsx` | Surface landing page header |
| `PlatformAppGate` | `platform/platform-app-gate.tsx` | Auth gating per app surface |
| `PlatformContext` | `platform/platform-context.ts` | Surface resolution logic |
| `OwnerScopeBadge` | `platform/owner-scope-badge.tsx` | Visual owner scope indicator |
| `RealtimeStatusIndicator` | `platform/realtime-status-indicator.tsx` | Real-time connection status |

### 6.4 UI Component Library

| Component | File | Purpose |
|-----------|------|---------|
| `Button` | `ui/button.tsx` | Styled button component |
| `TextField` | `ui/text-field.tsx` | Text input field |
| `PasswordField` | `ui/password-field.tsx` | Password input with toggle |
| `Form` | `ui/form.tsx` | Form wrapper with validation |
| `Dialog` | `ui/dialog.tsx` | Modal dialog |
| `Drawer` | `ui/drawer-panel.tsx` | Slide-out drawer |
| `DataTable` | `ui/data-table.tsx` | Data table with sorting |
| `LoadingState` | `ui/loading-state.tsx` | Loading spinner + message |
| `ErrorState` | `ui/error-state.tsx` | Error display with retry |
| `EmptyState` | `ui/empty-state.tsx` | Empty state illustration |
| `AlertBanner` | `ui/alert-banner.tsx` | Alert/notification banner |
| `ToastCenter` | `ui/toast-center.tsx` | Toast notification container |
| `Skeleton` | `ui/skeleton.tsx` | Loading skeleton |
| `StatCard` | `ui/stat-card.tsx` | Statistics display card |
| `AccountSummaryPanel` | `ui/account-summary-panel.tsx` | Account summary display |
| `SettingsFormSection` | `ui/settings-form-section.tsx` | Settings form section |
| `GoogleSignInButton` | `ui/google-signin-button.tsx` | Google OAuth button |
| `InlineValidationMessage` | `ui/inline-validation-message.tsx` | Field validation message |
| `ConfirmationModal` | `ui/confirmation-modal.tsx` | Confirmation dialog |

---

## 7. Provider Architecture

### 7.1 AppProviders

The `AppProviders` component wraps the entire application and provides:

```typescript
interface AppProvidersProps {
  children: React.ReactNode;
}

// Internal providers:
// - SessionProvider: Manages user authentication state
// - BalanceProvider: Manages user coin balance
// - MaintenanceProvider: Manages maintenance mode state
// - ThemeProvider: Manages light/dark theme
// - QueryClientProvider: TanStack Query client
// - NotificationProvider: Toast/notification system
```

### 7.2 Session Provider Flow

```
1. App mounts → SessionProvider fetches /api/v1/users/me
2. If 200 → status = 'authenticated', user = response.data
3. If 401 → status = 'unauthenticated', user = null
4. If error → status = 'unauthenticated', user = null
5. Session refreshes on route change or explicit call
```

### 7.3 Balance Provider Flow

```
1. If authenticated → fetch /api/v1/billing/balance
2. Store balance, currency, error
3. Refresh on interval or explicit call
4. If unauthenticated → balance = 0
```

### 7.4 Maintenance Provider Flow

```
1. Fetch /api/v1/maintenance/status on mount
2. If enabled → show MaintenanceGate
3. Refresh on interval (every 60s)
4. Cache with staleTime for performance
```

---

## 8. Unit Tests

### 8.1 Existing Tests
- **Playwright E2E**: `tests/e2e/sprint-common-platform.spec.ts`
- **Playwright E2E**: `tests/e2e/sprint1-shell.spec.ts`
- **Playwright E2E**: `tests/e2e/sprint2-auth.spec.ts`
- **Playwright E2E**: `tests/e2e/sprint3-framework.spec.ts`

### 8.2 Recommended Unit Tests (Missing)

```typescript
// components/platform/__tests__/platform-context.test.ts
describe('PlatformContext', () => {
  it('resolves storytelling surface for /storytelling paths');
  it('resolves care-circle-family surface for /care-circle-family paths');
  it('resolves care-circle-patient surface for /care-circle-patient paths');
  it('resolves chatbot surface for /chatbot paths');
  it('resolves public surface for unknown paths');
  it('builds memberships with auth required for authenticated surfaces');
  it('grants patient surface access without auth');
});

// components/shell/__tests__/maintenance-gate.test.tsx
describe('MaintenanceGate', () => {
  it('shows children when maintenance is disabled');
  it('shows maintenance message when enabled');
  it('shows end time when provided');
});

// lib/__tests__/api.test.ts
describe('API client functions', () => {
  it('apiGet returns parsed JSON on success');
  it('apiGet throws on non-OK response');
  it('apiPostJson sends correct headers and body');
  it('apiPostForm sends form-encoded data');
  it('buildErrorMessage extracts detail from various response shapes');
});

// components/providers/__tests__/app-providers.test.tsx
describe('AppProviders', () => {
  it('renders children');
  it('provides session context');
  it('provides balance context');
  it('provides maintenance context');
});
```

---

## 9. Integration Tests

### 9.1 Playwright E2E Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Shell Loading | Visit root → Check layout | Shell renders with nav, footer |
| Auth Flow | Visit login → Submit credentials → Redirect | User authenticated, session active |
| Maintenance Mode | Enable maintenance → Visit any page | Maintenance gate shown |
| Theme Toggle | Toggle theme → Check UI | Theme changes persist |
| Balance Display | Login → Check header | Coin balance visible |
| Cookie Consent | Visit site → Accept cookies | Banner dismissed, cookie set |

---

## 10. Suggestions and Improvements

### 10.1 Immediate Improvements
1. **Add Error Boundary**: Wrap `AppShellResolver` with React Error Boundary for graceful error handling.
2. **Implement Toast Notifications**: Complete `ToastCenter` implementation with actual toast rendering.
3. **Add Loading Transitions**: Implement route transition loading indicators.
4. **Implement Google OAuth**: Complete Google sign-in flow with proper token handling.

### 10.2 Architecture Improvements
1. **Extract API Client Class**: Replace functional API calls with a class-based client for better testability and dependency injection.
2. **Add Request Interceptor**: Implement automatic token refresh on 401 responses.
3. **Implement Response Caching**: Use TanStack Query's built-in caching more aggressively for shared data.
4. **Add Analytics Integration**: Integrate analytics (PostHog, Plausible) at the shared layer.

### 10.3 Testing Improvements
1. **Add Component Unit Tests**: Use Vitest + React Testing Library for all shared components.
2. **Add API Mock Tests**: Use MSW for consistent API mocking in tests.
3. **Add Accessibility Tests**: Integrate axe-core into Playwright tests.
4. **Add Performance Tests**: Use Playwright performance tracing for critical paths.

### 10.4 Performance Improvements
1. **Implement Route Prefetching**: Use Next.js `prefetch` for common navigation targets.
2. **Optimize Bundle Size**: Analyze and reduce bundle size with `@next/bundle-analyzer`.
3. **Implement Code Splitting**: Lazy-load heavy components (charts, editors).
4. **Use React Server Components**: Move data fetching to server components where possible.

### 10.5 Security Considerations
1. **CSRF Protection**: Ensure CSRF tokens are properly handled for state-changing requests.
2. **XSS Prevention**: Sanitize all user-generated content before rendering.
3. **Secure Cookie Handling**: Ensure cookies are set with proper flags (HttpOnly, Secure, SameSite).
4. **Content Security Policy**: Implement CSP headers for additional XSS protection.

### 10.6 Developer Experience
1. **Add Storybook**: Document all UI components with interactive stories.
2. **Add ESLint Rules**: Enforce consistent patterns for API calls and state management.
3. **Add TypeScript Strict Mode**: Enable all strict TypeScript options.
4. **Add Pre-commit Hooks**: Run linting and type checking before commits.
