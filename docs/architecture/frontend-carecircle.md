# Frontend CareCircle Architecture Document

## 1. Overview

The CareCircle frontend is a dual-surface React application built with Next.js 14 (App Router) and TypeScript. It serves two distinct user personas:
- **Family Members**: Authenticated users who manage patient profiles, configure content providers, and monitor care delivery.
- **Patients**: End-users (often elderly or cognitively impaired) who receive daily curated content cards through a simplified, image-based authentication flow.

### Key Characteristics
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom design tokens
- **State Management**: TanStack Query (React Query) for server state, React useState for local UI state
- **Authentication**: Cookie-based (HttpOnly access tokens) + image-based patient auth
- **Testing**: Playwright E2E tests

### Accuracy Review
- **Last reviewed**: 2026-04-05
- Reviewed against:
  - `frontendv1/app/care-circle-family/` (7 route pages)
  - `frontendv1/app/care-circle-patient/` (4 route pages)
  - `frontendv1/components/care-circle-family/` (4 components)
  - `frontendv1/components/care-circle-patient/` (4 components)
  - `frontendv1/lib/api.ts` (CareCircle API functions, lines 244-320)
- **Implementation status**:
  - **Fully implemented routes**:
    - `/care-circle-family` - family dashboard landing (layout + page)
    - `/care-circle-family/patients` - patient list with `FamilyPatientsClient`
    - `/care-circle-family/patients/[patientId]` - patient detail with `FamilyPatientDetailClient`
    - `/care-circle-family/providers` - provider catalog grid, query-driven via `fetchCareCircleProviders`
    - `/care-circle-family/providers/[providerKey]` - provider detail, client-side with specs panel and scaffolded diagnostics panel
    - `/care-circle-patient/login` - image-based auth via `PatientImageLoginPanel`
    - `/care-circle-patient/home` - patient session via `PatientSessionClient` (requires `?patient=` search param)
  - **Scaffold/placeholder routes**:
    - `/care-circle-family/events` - static event feed with hardcoded entries, no API integration
    - `/care-circle-family/media` - upload placeholder with static UI, no actual upload functionality
  - **API client coverage in `lib/api.ts`**:
    - `fetchCareCircleProviders()` - GET `/care-circle/providers`
    - `fetchCareCirclePatients()` - GET `/care-circle/family/patients`
    - `fetchCareCirclePatient(id)` - GET `/care-circle/family/patients/{id}`
    - `fetchCareCirclePatientAuthCatalog()` - GET `/care-circle/patient/auth/catalog`
    - `loginCareCirclePatient(keys)` - POST `/care-circle/patient/auth/login`
    - `fetchCareCirclePatientSession(id)` - GET `/care-circle/patient/session/{id}`
    - **Missing API functions**: `updateCareCircleProvider()`, `fetchPatientProviderConfigs()`, `upsertPatientProviderConfig()` are not yet exported from `api.ts` despite backend endpoints existing.
  - The document's component and route sections should be read as "implemented plus near-term scaffolding", not as proof that every listed family-facing workflow is fully operational today.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CareCircle Frontend                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────┐                    ┌──────────────────────────┐   │
│  │   Family Surface     │                    │    Patient Surface       │   │
│  │  (Authenticated)     │                    │   (Image-based Auth)     │   │
│  │                      │                    │                          │   │
│  │  /care-circle-family │                    │  /care-circle-patient    │   │
│  │  ├── /               │                    │  ├── /login              │   │
│  │  ├── /patients       │                    │  ├── /home               │   │
│  │  ├── /patients/:id   │                    │                          │   │
│  │  ├── /providers      │                    │                          │   │
│  │  ├── /providers/:key │                    │                          │   │
│  │  ├── /events         │                    │                          │   │
│  │  └── /media          │                    │                          │   │
│  └─────────┬────────────┘                    └──────────┬───────────────┘   │
│            │                                            │                   │
│            ▼                                            ▼                   │
│  ┌──────────────────────┐                    ┌──────────────────────────┐   │
│  │  Family Components   │                    │   Patient Components     │   │
│  │                      │                    │                          │   │
│  │  - FamilyPatientCard │                    │  - PatientShell          │   │
│  │  - PatientDetail     │                    │  - PatientSessionClient  │   │
│  │  - AccessStateBadge  │                    │  - PatientDailyHighlights│   │
│  │  - ProviderConfig    │                    │  - PatientImageLoginPanel│   │
│  └─────────┬────────────┘                    └──────────┬───────────────┘   │
│            │                                            │                   │
│            └────────────────────┬───────────────────────┘                   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Shared Platform Layer                         │   │
│  │                                                                      │   │
│  │  - AppShellResolver (route-based surface resolution)                 │   │
│  │  - PlatformAppGate (auth gating per surface)                         │   │
│  │  - PlatformContext (surface_id, owner_scope, memberships)            │   │
│  │  - AppProviders (Session, Balance, Maintenance, Theme)               │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        API Client Layer (lib/api.ts)                 │   │
│  │                                                                      │   │
│  │  - fetchCareCircleProviders()                                        │   │
│  │  - fetchCareCirclePatients()                                         │   │
│  │  - fetchCareCirclePatient(id)                                        │   │
│  │  - fetchCareCirclePatientAuthCatalog()                               │   │
│  │  - loginCareCirclePatient(imageKeys)                                 │   │
│  │  - fetchCareCirclePatientSession(id)                                 │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│                    Backend API (/api/v1/care-circle/*)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Route Structure

| Route | Auth Required | Component | Status | Description |
|-------|---------------|-----------|--------|-------------|
| `/care-circle-family` | Yes | Layout + Page | **Implemented** | Family dashboard landing |
| `/care-circle-family/patients` | Yes | `FamilyPatientsClient` | **Implemented** | List all family patients with React Query |
| `/care-circle-family/patients/:patientId` | Yes | `FamilyPatientDetailClient` | **Implemented** | Patient detail view with content cards |
| `/care-circle-family/providers` | Yes | Inline page with `fetchCareCircleProviders` | **Implemented** | Provider catalog grid with status badges |
| `/care-circle-family/providers/:providerKey` | Yes | Inline page with client-side fetch | **Implemented** | Provider detail with specs panel; diagnostics panel is scaffolded |
| `/care-circle-family/events` | Yes | Static page | **Scaffold** | Hardcoded event entries, no API integration |
| `/care-circle-family/media` | Yes | Static page | **Scaffold** | Upload placeholder, no actual upload functionality |
| `/care-circle-patient` | No | Layout + Page | **Implemented** | Patient entry point (redirects to login) |
| `/care-circle-patient/login` | No | `PatientImageLoginPanel` | **Implemented** | Image-based authentication |
| `/care-circle-patient/home` | Patient Session (via `?patient=` param) | `PatientSessionClient` | **Implemented** | Daily content dashboard; requires `?patient={id}` search param |

---

## 4. Data Model (Frontend Types)

```typescript
// CareCircle Provider (catalog item)
interface CareCircleProvider {
  providerKey: string;      // Unique key (e.g., "joke", "daily_quote")
  label: string;            // Display name
  icon?: string | null;     // Icon identifier
  category: string;         // Category grouping
  enabled: boolean;         // Globally enabled
  displayOrder: number;     // Sort order
  patientVisible: boolean;  // Visible to patients
  familyVisible: boolean;   // Visible to family
}

// CareCircle Patient Record
interface CareCirclePatientRecord {
  id: string;
  displayName: string;
  familyName: string;
  stage: string;                    // "early", "mild", "moderate", "severe"
  accessState: string;              // "active", "inactive", "archived"
  timezone: string;                 // IANA timezone
  deliveryTime?: string | null;     // HH:MM format
  days: string[];                   // Delivery days
  familyMembers: string[];          // Family member names
  preferences: string[];            // Patient preferences
  authImageKeys: string[];          // Image keys for auth
  highlights?: CareCircleHighlight[]; // Daily content cards
}

// Daily Content Highlight
interface CareCircleHighlight {
  title: string;
  body: string;
  kind: string;
  providerKey: string;
  displayOrder: number;
}

// Auth Catalog Item (for patient login)
interface CareCircleAuthCatalogItem {
  key: string;
  label: string;
  emoji: string;
}
```

---

## 5. API Endpoints Consumed

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/care-circle/providers` | User | List provider catalog |
| PUT | `/api/v1/care-circle/providers/:key` | User | Update provider settings |
| GET | `/api/v1/care-circle/family/patients` | User | List family patients |
| GET | `/api/v1/care-circle/family/patients/:id` | User | Get patient detail |
| GET | `/api/v1/care-circle/patient/auth/catalog` | None | Get auth image catalog |
| POST | `/api/v1/care-circle/patient/auth/login` | None | Patient image-based login |
| GET | `/api/v1/care-circle/patient/session/:id` | None | Get patient daily session |
| GET | `/api/v1/care-circle/family/patients/:id/provider-configs` | User | List patient provider configs |
| PUT | `/api/v1/care-circle/family/patients/:id/provider-configs/:key` | User | Upsert patient provider config |

All current CareCircle frontend API calls are centralized in `frontendv1/lib/api.ts` (lines 244-320).

### 5.1 Backend Response Envelope

The backend wraps all CareCircle responses in an `ApiResponse` envelope:
```json
{
  "success": true,
  "data": { ... },
  "errors": null
}
```

The frontend's `apiGet<T>()` helper in `lib/api.ts` extracts `payload.data` automatically, so component code works with the unwrapped type directly.

### 5.2 Patient Session Refresh Flow

1. Patient navigates to `/care-circle-patient/home?patient={id}` (set after login redirect).
2. `PatientSessionClient` mounts and calls `fetchCareCirclePatientSession(patientId)`.
3. Backend `GET /api/v1/care-circle/patient/session/{id}` triggers `assemble_daily_patient_session()` to regenerate content cards.
4. Backend reads the fresh session from DB and returns it in the `ApiResponse` envelope.
5. `PatientSessionClient` passes the session data to `PatientDailyHighlights` for rendering.
6. Each refresh triggers a new server-side assembly (on-demand, not cached).

---

## 6. Component Architecture

### 6.1 Care Circle Family Components

| Component | File | Purpose |
|-----------|------|---------|
| `FamilyPatientCard` | `care-circle-family/family-patient-card.tsx` | Patient card with stage, timezone, preferences |
| `FamilyPatientsClient` | `care-circle-family/family-patients-client.tsx` | Patient list with React Query |
| `FamilyPatientDetailClient` | `care-circle-family/family-patient-detail-client.tsx` | Patient detail view |
| `PatientAccessStateBadge` | `care-circle-family/patient-access-state-badge.tsx` | Visual status indicator |

### 6.2 Care Circle Patient Components

| Component | File | Purpose |
|-----------|------|---------|
| `PatientShell` | `care-circle-patient/patient-shell.tsx` | Patient layout wrapper |
| `PatientSessionClient` | `care-circle-patient/patient-session-client.tsx` | Session data fetcher with React Query |
| `PatientDailyHighlights` | `care-circle-patient/patient-daily-highlights.tsx` | Content card renderer |
| `PatientImageLoginPanel` | `care-circle-patient/patient-image-login-panel.tsx` | Image-based auth UI |

---

## 7. Platform Integration

The CareCircle frontend integrates with the shared platform through:

1. **Surface Resolution**: `resolveSurfaceId()` maps `/care-circle-family/*` and `/care-circle-patient/*` paths to their respective surface IDs.

2. **Platform Context**: Each surface has distinct `owner_scope`:
   - `care-circle-family` → `"family"` (user-owned, family-scoped)
   - `care-circle-patient` → `"patient"` (no auth, direct access)

3. **App Membership**: `buildMemberships()` grants access based on auth state:
   - Family surface requires authentication
   - Patient surface is always accessible

4. **Shared Shell**: Both surfaces use `AppShell` for consistent navigation, theme, and maintenance gating.

---

## 8. Unit Tests

### 8.1 Existing Tests
- **Playwright E2E**: `tests/e2e/sprint-care-circle-family.spec.ts`
- **Playwright E2E**: `tests/e2e/sprint-care-circle-patient.spec.ts`
- **Playwright E2E**: `tests/e2e/sprint-care-circle-import.spec.ts`

### 8.2 Test Coverage Areas

| Test File | Coverage |
|-----------|----------|
| `sprint-care-circle-family.spec.ts` | Family patient listing, patient detail, provider config |
| `sprint-care-circle-patient.spec.ts` | Patient login flow, session loading, content display |
| `sprint-care-circle-import.spec.ts` | Provider import and registration |

### 8.3 Recommended Unit Tests (Missing)

```typescript
// components/care-circle-family/__tests__/family-patient-card.test.tsx
describe('FamilyPatientCard', () => {
  it('renders patient display name and stage');
  it('shows delivery time when available');
  it('shows "Flexible" when deliveryTime is null');
  it('renders preference tags');
  it('links to patient detail page');
});

// components/care-circle-patient/__tests__/patient-session-client.test.tsx
describe('PatientSessionClient', () => {
  it('shows loading state while fetching');
  it('shows error state on API failure');
  it('renders PatientDailyHighlights on success');
  it('calls fetchCareCirclePatientSession with correct patientId');
});

// lib/__tests__/api-care-circle.test.ts
describe('CareCircle API functions', () => {
  it('fetchCareCircleProviders calls correct endpoint');
  it('loginCareCirclePatient sends correct payload');
  it('fetchCareCirclePatientSession calls correct endpoint');
});
```

---

## 9. Integration Tests

### 9.1 Playwright E2E Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Family Patient List | Login → Navigate to family → View patients | Patient cards render with correct data |
| Patient Login | Navigate to patient login → Select auth images | Redirects to patient home |
| Patient Session | Login as patient → View home | Daily highlights render |
| Provider Config | Login → Navigate to patient → Update provider config | Config saves and reflects |

---

## 10. Suggestions and Improvements

### 10.1 Immediate Improvements
1. **Add React Query Error Boundaries**: Wrap patient session queries with `ErrorBoundary` for graceful degradation.
2. **Implement Provider Config UI**: The provider config endpoints exist but no UI for family members to toggle providers per patient.
3. **Add Missing API Functions**: `updateCareCircleProvider()`, `fetchPatientProviderConfigs()`, and `upsertPatientProviderConfig()` need to be added to `lib/api.ts` to match backend endpoints.
4. **Add Loading Skeletons**: Replace generic `LoadingState` with skeleton cards matching the final UI.
5. **Implement Pagination**: Patient list should paginate for families with many patients.

### 10.2 Architecture Improvements
1. **Separate API Module**: Extract CareCircle-specific API calls into `lib/api/care-circle.ts` for better organization.
2. **Custom React Query Hooks**: Create `useCareCirclePatients()`, `usePatientSession()` hooks for reusable data fetching.
3. **Optimistic Updates**: Provider config toggles should use optimistic updates for better UX.
4. **WebSocket for Real-time Updates**: Consider WebSocket for live patient session updates when providers regenerate content.

### 10.3 Testing Improvements
1. **Add Component Unit Tests**: Use Vitest + React Testing Library for component-level tests.
2. **Mock API Responses**: Use MSW (Mock Service Worker) for consistent test data.
3. **Add Visual Regression Tests**: Use Playwright screenshots for patient UI consistency.
4. **Accessibility Tests**: Add axe-core integration for WCAG compliance (critical for care applications).

### 10.4 Performance Improvements
1. **Prefetch Patient Data**: Use Next.js `prefetchQuery` on patient list hover.
2. **Image Optimization**: Use Next.js `Image` component for auth images with proper sizing.
3. **Content Caching**: Patient session data should use `staleTime` to avoid unnecessary refetches.

### 10.5 Security Considerations
1. **Rate Limiting on Patient Login**: Image-based auth should have rate limiting to prevent brute force.
2. **Session Timeout**: Patient sessions should timeout after inactivity.
3. **Content Filtering**: Ensure provider-generated content is safe for patient consumption.

---

## 11. Document Maintenance Guidance

### 11.1 Source of Truth

The following files are the **authoritative source** for CareCircle frontend behavior. When this document conflicts with code, the code wins and this document should be updated:

- `frontendv1/app/care-circle-family/` - family route pages (Next.js App Router)
- `frontendv1/app/care-circle-patient/` - patient route pages (Next.js App Router)
- `frontendv1/components/care-circle-family/` - family UI components
- `frontendv1/components/care-circle-patient/` - patient UI components
- `frontendv1/lib/api.ts` - API client functions (CareCircle section: lines 244-320)

### 11.2 When to Update This Document

Update this document when any of the following change:
- New route pages are added under `care-circle-family/` or `care-circle-patient/`
- New components are created in the `care-circle-*` component directories
- API functions are added, removed, or changed in `lib/api.ts`
- TypeScript interfaces for CareCircle types change
- The platform integration layer (`AppShellResolver`, `PlatformAppGate`, `PlatformContext`) changes

### 11.3 How to Update Safely

1. Verify the route exists in the filesystem under `frontendv1/app/`.
2. Read the actual page/component file to confirm its implementation depth.
3. Check `lib/api.ts` for the corresponding API function.
4. Update the Route Structure table (Section 3) with the correct status label.
5. Update the Component Architecture table (Section 6) if new components are added.
6. Update the API Endpoints Consumed table (Section 5) if new API functions are added.
7. Update the "Last reviewed" date in the Accuracy Review section.

### 11.4 Implementation Status Language

Use these labels consistently in the Route Structure table:
- **Implemented**: Route page and component are functional with real data fetching.
- **Scaffold**: Route page exists but contains placeholder/static content without API integration.
- **Planned**: Route is described but no page file exists yet.
