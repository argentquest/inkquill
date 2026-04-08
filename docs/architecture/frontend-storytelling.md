# Frontend Storytelling Architecture Document

## 1. Overview

The Storytelling frontend is the primary creative authoring surface for the platform. It provides user-owned routes for account management, billing, referrals, onboarding, and (future) story creation. The storytelling app inherits the shared platform contract and resolves authenticated users into an app-specific account surface.

### Key Characteristics
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom design tokens
- **State Management**: React useState + useEffect (local state), migrating to TanStack Query
- **Testing**: Playwright E2E tests (pending)
- **Current Status**: Shell and account/billing/onboarding routes implemented; story creation routes pending

### Accuracy Review
- Reviewed against:
  - `frontendv1/app/storytelling/**`
  - `frontendv1/lib/api.ts`
- The current implementation status is:
  - implemented shells/routes for account, profile edit, billing, referrals, and onboarding
  - no full story/world authoring route tree yet inside `frontendv1`
- This file is accurate when treated as a staged architecture document, not a claim that story authoring UI is already complete in the current frontend workspace.
- The account/billing/referrals/onboarding routes are real and active; deeper storytelling creation flows remain planned work.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Storytelling Frontend                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    Storytelling Layout (layout.tsx)                  │   │
│  │                                                                      │   │
│  │  - Inherits from root layout                                         │   │
│  │  - AppShellResolver wraps children                                   │   │
│  │  - Surface ID: "storytelling"                                        │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│            ┌────────────────────┼────────────────────┐                      │
│            ▼                    ▼                    ▼                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐       │
│  │  /storytelling  │  │ /storytelling/  │  │ /storytelling/       │       │
│  │  (page.tsx)     │  │ account/        │  │ billing/             │       │
│  │                 │  │                 │  │                      │       │
│  │  Landing page   │  │ Account shell   │  │ Billing dashboard    │       │
│  │  with CTA to    │  │ with summary    │  │ with transactions    │       │
│  │  chatbot        │  │ and nav links   │  │ and packages         │       │
│  └─────────────────┘  └────────┬────────┘  └──────────┬───────────┘       │
│                                │                       │                   │
│            ┌───────────────────┼───────────────────────┤                   │
│            ▼                   ▼                       ▼                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐       │
│  │ /storytelling/  │  │ /storytelling/  │  │ /storytelling/       │       │
│  │ referrals/      │  │ onboarding/     │  │ account/edit/        │       │
│  │                 │  │                 │  │                      │       │
│  │ Referrals       │  │ Onboarding      │  │ Profile edit form    │       │
│  │ dashboard       │  │ interview       │  │                      │       │
│  │ (pending)       │  │ preview +       │  │                      │       │
│  │                 │  │ insights        │  │                      │       │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘       │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Shared Platform Integration                   │   │
│  │                                                                      │   │
│  │  - Surface ID: "storytelling"                                        │   │
│  │  - Owner Scope: "user"                                               │   │
│  │  - Requires Auth: true                                               │   │
│  │  - App Shell: Inherited from shared AppShell                         │   │
│  │  - Session: Checked via AppProviders                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        API Client Layer (lib/api.ts)                 │   │
│  │                                                                      │   │
│  │  - fetchBillingDashboard()                                           │   │
│  │  - fetchInterviewQuestions(id)                                       │   │
│  │  - fetchInterviewStatus(id)                                          │   │
│  │  - fetchUserInsights()                                               │   │
│  │  - updateCurrentUserProfile(input)                                   │   │
│  │  - fetchReferralStats(), fetchReferralHistory(), fetchReferralRewards│   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Future Story Creation Routes                  │   │
│  │                                                                      │   │
│  │  - /storytelling/stories (list)                                      │   │
│  │  - /storytelling/stories/:id (detail)                                │   │
│  │  - /storytelling/stories/:id/edit (editor)                           │   │
│  │  - /storytelling/worlds (world building)                             │   │
│  │  - /storytelling/characters (character management)                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Route Structure

| Route | Auth Required | Component | Description |
|-------|---------------|-----------|-------------|
| `/storytelling` | No | `StorytellingPage` | Landing page with CTA |
| `/storytelling/account` | Yes | `StorytellingAccountWorkspace` | Account summary and navigation |
| `/storytelling/account/edit` | Yes | `EditProfileForm` | Profile editing form |
| `/storytelling/billing` | Yes | `BillingDashboardRoute` | Billing dashboard |
| `/storytelling/onboarding` | Yes | `OnboardingDashboardRoute` | Onboarding interview preview |
| `/storytelling/referrals` | Yes | `ReferralsDashboard` | Referral stats and history |

---

## 4. Data Model (Frontend Types)

```typescript
// User Profile
interface SessionUser {
  id: number;
  username: string;
  email: string;
  displayName?: string;
  isActive: boolean;
  isAdmin: boolean;
  createdAt: string;
}

// Profile Update Input
interface UserProfileUpdateInput {
  display_name?: string;
  email?: string;
  bio?: string;
  avatar_url?: string;
}

// Billing Dashboard
interface BillingDashboard {
  account: UserAccount;
  recentTransactions: UserTransaction[];
  availablePackages: CreditPackage[];
}

interface UserAccount {
  id: number;
  user_id: number;
  current_balance: number;
  total_spent: number;
  total_credits_added: number;
  currency: string;
  created_at: string;
}

interface UserTransaction {
  id: number;
  account_id: number;
  transaction_type: string;
  amount: number;
  balance_after: number;
  description: string | null;
  created_at: string;
}

interface CreditPackage {
  id: number;
  name: string;
  credit_amount: number;
  price_usd: number;
  bonus_percentage: number;
  is_active: boolean;
  description: string | null;
}

// Interview/Onboarding
interface InterviewQuestionsPayload {
  interview_id: string;
  interview_title: string;
  interview_description: string;
  questions: InterviewQuestion[];
}

interface InterviewQuestion {
  id: string;
  question: string;
  subtitle?: string;
  order: number;
  question_type: string;
}

interface InterviewStatusPayload {
  interview_id: string;
  completed: boolean;
  completed_at: string | null;
}

interface UserInsightsPayload {
  has_completed_onboarding: boolean;
  insights: Record<string, unknown>;
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

interface ReferralRecord {
  id: number;
  referred_user_id: number | null;
  is_anonymous: boolean;
  source_platform: string | null;
  source_content_type: string | null;
  is_converted: boolean;
  converted_at: string | null;
  has_created_story: boolean;
  has_published_story: boolean;
  created_at: string;
}

interface ReferralRewardsResponse {
  rewards: RewardRecord[];
  total: number;
}

interface RewardRecord {
  id: number;
  referral_id: number;
  reward_type: string;
  coin_amount: number;
  awarded_at: string;
}
```

---

## 5. API Endpoints Consumed

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/me` | User | Get current user session |
| PUT | `/api/v1/users/me` | User | Update user profile |
| GET | `/api/v1/billing/dashboard` | User | Billing dashboard data |
| GET | `/api/v1/interview/questions/:id` | User | Get interview questions |
| GET | `/api/v1/interview/status/:id` | User | Get interview status |
| GET | `/api/v1/interview/user-insights` | User | Get user insights |
| GET | `/api/v1/referrals/stats` | User | Referral statistics |
| GET | `/api/v1/referrals/history` | User | Referral history |
| GET | `/api/v1/referrals/rewards` | User | Referral rewards |

---

## 6. Component Architecture

### 6.1 Page Components

| Component | File | Purpose |
|-----------|------|---------|
| `StorytellingPage` | `app/storytelling/page.tsx` | Landing page with CTA to chatbot |
| `StorytellingAccountPage` | `app/storytelling/account/page.tsx` | Account page wrapper |
| `BillingPage` | `app/storytelling/billing/page.tsx` | Billing page wrapper |
| `OnboardingPage` | `app/storytelling/onboarding/page.tsx` | Onboarding page wrapper |
| `ReferralsPage` | `app/storytelling/referrals/page.tsx` | Referrals page wrapper |
| `EditProfilePage` | `app/storytelling/account/edit/page.tsx` | Edit profile page wrapper |

### 6.2 Workspace Components

| Component | File | Purpose |
|-----------|------|---------|
| `StorytellingAccountWorkspace` | `app/storytelling/account/account-workspace.tsx` | Account summary with nav links |
| `BillingDashboardRoute` | `app/storytelling/billing/billing-dashboard.tsx` | Billing stats, transactions, packages |
| `OnboardingDashboardRoute` | `app/storytelling/onboarding/onboarding-dashboard.tsx` | Interview preview and insights |
| `ReferralsDashboard` | `app/storytelling/referrals/referrals-dashboard.tsx` | Referral stats and history |
| `EditProfileForm` | `app/storytelling/account/edit/edit-profile-form.tsx` | Profile editing form |

### 6.3 Component Details: StorytellingAccountWorkspace

```typescript
// Props: None (uses session context)
// Layout: Two-column grid (1.2fr / 0.8fr)
// Left: AccountSummaryPanel
// Right: Workspace scope description with nav links
```

### 6.4 Component Details: BillingDashboardRoute

```typescript
// State:
// - dashboard: BillingDashboard | null
// - error: string | null
// - loading: boolean

// Data Loading: useEffect + fetchBillingDashboard()
// Layout: Stat cards (3 columns) + Transaction table + Packages table
```

### 6.5 Component Details: OnboardingDashboardRoute

```typescript
// State:
// - questions: InterviewQuestionsPayload | null
// - status: InterviewStatusPayload | null
// - insights: UserInsightsPayload | null
// - error: string | null
// - loading: boolean

// Data Loading: useEffect + Promise.all([fetchQuestions, fetchStatus, fetchInsights])
// Layout: Two-column grid (Interview preview + Insights)
```

---

## 7. Platform Integration

The Storytelling frontend integrates with the shared platform through:

1. **Surface Resolution**: `resolveSurfaceId()` maps `/storytelling/*` paths to `"storytelling"` surface ID.

2. **Platform Context**:
   - `surface_id`: `"storytelling"`
   - `app_id`: `"storytelling"`
   - `owner_scope`: `"user"`
   - `requires_auth`: `true` (except landing page)

3. **App Membership**: Storytelling surface requires authentication (`granted: isAuthenticated`).

4. **Shared Shell**: Uses `AppShell` for consistent navigation, theme, and maintenance gating.

5. **Default Auth Destination**: When auth is required, redirects to `/storytelling/account`.

6. **Legacy Route Bridging**: `/app/*` routes redirect to corresponding `/storytelling/*` routes:
   - `/app/account` → `/storytelling/account`
   - `/app/account/edit` → `/storytelling/account/edit`
   - `/app/billing` → `/storytelling/billing`
   - `/app/referrals` → `/storytelling/referrals`
   - `/app/onboarding` → `/storytelling/onboarding`

---

## 8. Unit Tests

### 8.1 Existing Tests
- **None currently** - Storytelling-specific unit tests are pending

### 8.2 Recommended Unit Tests

```typescript
// components/storytelling/__tests__/account-workspace.test.tsx
describe('StorytellingAccountWorkspace', () => {
  it('renders user summary panel');
  it('shows edit profile link');
  it('shows billing link');
  it('shows referrals link');
  it('displays user display name');
});

// components/storytelling/__tests__/billing-dashboard.test.tsx
describe('BillingDashboardRoute', () => {
  it('shows loading state while fetching');
  it('shows error state on API failure');
  it('renders stat cards with correct values');
  it('renders transaction table');
  it('renders available packages table');
  it('handles empty transaction list');
});

// components/storytelling/__tests__/onboarding-dashboard.test.tsx
describe('OnboardingDashboardRoute', () => {
  it('shows loading state while fetching');
  it('shows error state on API failure');
  it('renders interview questions');
  it('shows interview status');
  it('shows user insights');
  it('handles completed onboarding state');
  it('handles pending onboarding state');
});

// components/storytelling/__tests__/edit-profile-form.test.tsx
describe('EditProfileForm', () => {
  it('renders form with current user data');
  it('submits profile update on save');
  it('shows validation errors');
  it('shows success message on save');
});
```

---

## 9. Integration Tests

### 9.1 Recommended Playwright E2E Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Storytelling Landing | Visit /storytelling | Landing page renders with CTA |
| Account Page | Login → Visit /storytelling/account | Account summary renders |
| Billing Page | Login → Visit /storytelling/billing | Billing dashboard loads |
| Onboarding Page | Login → Visit /storytelling/onboarding | Onboarding interview preview loads |
| Profile Edit | Login → Visit /storytelling/account/edit → Edit → Save | Profile updates |
| Referrals Page | Login → Visit /storytelling/referrals | Referral stats load |

---

## 10. Suggestions and Improvements

### 10.1 Immediate Improvements
1. **Migrate to TanStack Query**: Replace `useEffect` + `useState` with `useQuery` for consistent data fetching.
2. **Implement Referrals Dashboard**: Complete the referrals dashboard component.
3. **Implement Edit Profile Form**: Complete the profile editing form with validation.
4. **Add Story Creation Routes**: Begin implementing story listing and creation routes.

### 10.2 Architecture Improvements
1. **Add Custom Hooks**: Create `useBillingDashboard()`, `useOnboarding()`, `useReferrals()` hooks.
2. **Implement Optimistic Updates**: Profile edits should use optimistic updates.
3. **Add Error Boundaries**: Wrap route components with React Error Boundaries.
4. **Implement Route Guards**: Add guards for onboarding completion status.

### 10.3 Testing Improvements
1. **Add Component Unit Tests**: Use Vitest + React Testing Library for all workspace components.
2. **Add E2E Tests**: Create Playwright tests for all storytelling routes.
3. **Mock API Responses**: Use MSW for consistent test data.
4. **Add Accessibility Tests**: Integrate axe-core for WCAG compliance.

### 10.4 Performance Improvements
1. **Implement Prefetching**: Use Next.js `prefetchQuery` for common navigation targets.
2. **Add Loading Skeletons**: Replace generic loading states with skeleton UI.
3. **Implement Code Splitting**: Lazy-load heavy components (editors, charts).
4. **Use React Server Components**: Move data fetching to server components where possible.

### 10.5 UX Improvements
1. **Add Story Creation Flow**: Implement story listing, creation, and editing.
2. **Add World Building UI**: Implement world, character, location, and lore management.
3. **Add AI Writing Assistant**: Integrate AI writing assistance into story editor.
4. **Add Story Chat**: Integrate story chat for AI-assisted story development.

### 10.6 Security Considerations
1. **Input Sanitization**: Sanitize all user-generated content before rendering.
2. **CSRF Protection**: Ensure CSRF tokens are properly handled.
3. **Rate Limiting**: Implement client-side rate limiting for form submissions.
4. **Session Timeout**: Auto-logout after inactivity.

### 10.7 Future Feature Ideas
1. **Story Editor**: Rich text editor with AI assistance.
2. **World Builder**: Visual world building interface.
3. **Character Sheets**: Character management with AI-generated profiles.
4. **Scene Planner**: Scene-by-scene story planning.
5. **Publishing Flow**: Story publishing and sharing.
6. **Collaboration**: Multi-user story collaboration.
7. **Version History**: Story version tracking and rollback.
