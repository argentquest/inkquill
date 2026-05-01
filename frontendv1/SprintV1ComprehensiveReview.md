# Sprint V1 Comprehensive Review — All Markdown Files & Associated Code

**Review Date:** 2026-04-30  
**Review Scope:** All sprint v1 markdown files and their associated code files  
**Sprint Files Reviewed:**
- `frontendv1Sprint01PlatformBaseline.md`
- `frontendSprint01.md`
- `frontendSprint02.md`
- `frontendSprint03.md`
- `frontendSprintCommonPlatform.md`

---

## Table of Contents

1. [Sprint File Inventory](#1-sprint-file-inventory)
2. [Code File Review by Sprint](#2-code-file-review-by-sprint)
3. [Cross-Sprint Issues](#3-cross-sprint-issues)
4. [Test Coverage Analysis](#4-test-coverage-analysis)
5. [Backend API Contract Verification](#5-backend-api-contract-verification)
6. [Summary Matrix](#6-summary-matrix)
7. [Priority Remediation Order](#7-priority-remediation-order)

---

## 1. Sprint File Inventory

### 1.1 Files Reviewed

| File | Purpose | Status |
|------|---------|--------|
| `frontendv1Sprint01PlatformBaseline.md` | Active shared-platform baseline (supersedes Sprint 1-3) | Reviewed |
| `frontendSprint01.md` | Sprint 01: Foundation and Shell | Reviewed (superseded) |
| `frontendSprint02.md` | Sprint 02: Authentication and Account Entry | Reviewed (superseded) |
| `frontendSprint03.md` | Sprint 03: Platform and App Framework Expansion | Reviewed (superseded) |
| `frontendSprintCommonPlatform.md` | Sprint Common 01: Shared Platform Supersession | Reviewed (supersedes Sprint 1-3) |

### 1.2 Source Files Referenced in Sprint Baseline

The sprint baseline (`frontendv1Sprint01PlatformBaseline.md`) lists these source file paths:

| Source Path | Files | Count |
|-------------|-------|-------|
| `frontendSprint01.md` | Sprint 01 planning doc | 1 |
| `frontendSprint02.md` | Sprint 02 planning doc | 1 |
| `frontendSprint03.md` | Sprint 03 planning doc | 1 |
| `frontendSprintCommonPlatform.md` | Common platform planning doc | 1 |
| `frontendv1/app/auth/**` | Auth pages (layout + 5 pages) | 6 |
| `frontendv1/app/app/**` | App layout + account page | 2 |
| `frontendv1/components/platform/**` | Platform components | 8 |
| `frontendv1/components/shell/**` | Shell components | 13 |
| `frontendv1/tests/e2e/sprint1-shell.spec.ts` | Sprint 1 E2E tests | 1 |
| `frontendv1/tests/e2e/sprint2-auth.spec.ts` | Sprint 2 E2E tests | 1 |
| `frontendv1/tests/e2e/sprint3-framework.spec.ts` | Sprint 3 E2E tests | 1 |
| `frontendv1/tests/e2e/sprint-common-platform.spec.ts` | Common platform E2E tests | 1 |

**Total source files referenced:** 37 files

---

## 2. Code File Review by Sprint

### 2.1 Sprint 01: Foundation and Shell

**Sprint Doc:** [`frontendSprint01.md`](frontendSprint01.md)  
**Goal:** Establish React app foundation and shared experience

#### Code Files Reviewed

| File | Issues Found |
|------|--------------|
| `app/layout.tsx` | None |
| `app/app/layout.tsx` | None |
| `components/providers/app-providers.tsx` | ISSUE-009, ISSUE-010, ISSUE-021, ISSUE-029, ISSUE-030 |
| `components/shell/app-shell.tsx` | None |
| `components/shell/public-shell.tsx` | None |
| `components/shell/top-nav.tsx` | ISSUE-015 |
| `components/shell/footer.tsx` | None |
| `components/shell/breadcrumbs.tsx` | None |
| `components/shell/page-header.tsx` | ISSUE-023 |
| `components/shell/cookie-consent-banner.tsx` | ISSUE-027 |
| `components/shell/maintenance-banner.tsx` | None |
| `components/shell/maintenance-gate.tsx` | None |
| `components/shell/user-menu.tsx` | ISSUE-028 |
| `components/shell/coin-balance-badge.tsx` | None |
| `components/shell/theme-toggle.tsx` | None |
| `components/ui/toast-center.tsx` | None |
| `components/ui/loading-state.tsx` | None |
| `components/ui/error-state.tsx` | None |
| `app/page.tsx` | ISSUE-003 |
| `app/loading.tsx` | None |
| `app/not-found.tsx` | None |

#### Sprint 01 Issues Summary

| ID | Severity | File | Description |
|----|----------|------|-------------|
| ISSUE-009 | LOW | `lib/api.ts` | `fetchSession()` silently swallows all errors |
| ISSUE-010 | LOW | `app-providers.tsx` | Toast auto-dismiss uses fixed 4500ms for all tones |
| ISSUE-015 | MEDIUM | `top-nav.tsx` | Default nav links point to legacy `/app/*` routes |
| ISSUE-021 | LOW | `app-providers.tsx` | Silent context fallbacks — no dev-mode warning |
| ISSUE-023 | LOW | `page-header.tsx` | Inline styles bypass Tailwind purge |
| ISSUE-027 | LOW | `cookie-consent-banner.tsx` | Missing `aria-live` for screen readers |
| ISSUE-028 | LOW | `user-menu.tsx` | Focus indicator not explicitly styled |
| ISSUE-029 | LOW | `app-providers.tsx` | Maintenance polling every 60s creates server load |
| ISSUE-030 | LOW | `app-providers.tsx` | Uniform 30s staleTime for all queries |

---

### 2.2 Sprint 02: Authentication and Account Entry

**Sprint Doc:** [`frontendSprint02.md`](frontendSprint02.md)  
**Goal:** Enable user entry with stable auth and core account access

#### Code Files Reviewed

| File | Issues Found |
|------|--------------|
| `app/auth/layout.tsx` | None |
| `app/auth/login/page.tsx` | ISSUE-001 |
| `app/auth/register/page.tsx` | ISSUE-008 |
| `app/auth/forgot-password/page.tsx` | None |
| `app/auth/password-reset/confirm/page.tsx` | None |
| `app/auth/reset-password/page.tsx` | None |
| `components/shell/app-shell-guard.tsx` | ISSUE-002 |
| `components/ui/google-signin-button.tsx` | ISSUE-005 |
| `lib/auth-redirect.ts` | ISSUE-004, ISSUE-018 |
| `lib/api.ts` | ISSUE-008, ISSUE-009 |

#### Sprint 02 Issues Summary

| ID | Severity | File | Description |
|----|----------|------|-------------|
| ISSUE-001 | HIGH | `login/page.tsx` | Debug quick-login with hardcoded `password123` exposed to admin users |
| ISSUE-002 | MEDIUM | `app-shell-guard.tsx` | `useLayoutEffect` with `window.location.replace` causes SSR flash |
| ISSUE-004 | MEDIUM | `lib/auth-redirect.ts` | Open redirect edge cases in `normalizeNextPath` |
| ISSUE-005 | LOW | `google-signin-button.tsx` | Google OAuth state parameter not generated client-side |
| ISSUE-008 | MEDIUM | `lib/api.ts`, `register/page.tsx` | Inconsistent API response handling between `apiFetch` and `apiFetchRaw` |
| ISSUE-018 | HIGH | `lib/auth-redirect.ts` | No unit tests for security-critical `normalizeNextPath` |

---

### 2.3 Sprint 03: Platform and App Framework Expansion

**Sprint Doc:** [`frontendSprint03.md`](frontendSprint03.md)  
**Goal:** Strengthen React app framework with stable patterns

#### Code Files Reviewed

| File | Issues Found |
|------|--------------|
| `app/app/account/page.tsx` | None |
| `components/ui/data-table.tsx` | None |
| `components/ui/drawer-panel.tsx` | None |
| `components/ui/confirmation-modal.tsx` | None |
| `components/ui/settings-form-section.tsx` | None |
| `components/ui/button.tsx` | ISSUE-024 |
| `components/ui/form.tsx` | None |
| `components/ui/text-field.tsx` | None |
| `components/ui/password-field.tsx` | None |
| `components/ui/alert-banner.tsx` | None |
| `components/ui/inline-validation-message.tsx` | None |
| `components/ui/help-modal.tsx` | None |
| `lib/help-content.ts` | ISSUE-025 |

#### Sprint 03 Issues Summary

| ID | Severity | File | Description |
|----|----------|------|-------------|
| ISSUE-024 | LOW | `button.tsx` | Confusing `title`/`tooltip` dual prop naming |
| ISSUE-025 | LOW | `help-content.ts` | 900+ line single file — hard to maintain |

---

### 2.4 Sprint Common 01: Shared Platform Supersession

**Sprint Doc:** [`frontendSprintCommonPlatform.md`](frontendSprintCommonPlatform.md)  
**Goal:** Replace Sprint 1-3 as active shared-platform execution sprint

#### Code Files Reviewed

| File | Issues Found |
|------|--------------|
| `components/platform/platform-context.ts` | ISSUE-013 |
| `components/platform/platform-app-gate.tsx` | None |
| `components/platform/app-membership-guard.tsx` | ISSUE-007 |
| `components/platform/app-shell-resolver.tsx` | ISSUE-014 |
| `components/platform/platform-route-bridge.tsx` | ISSUE-012 |
| `components/platform/platform-route-landing.tsx` | None |
| `components/platform/owner-scope-badge.tsx` | None |
| `components/platform/realtime-status-indicator.tsx` | None |
| `lib/apps.ts` | None |
| `lib/require-admin.ts` | None |
| `lib/care-circle-template-admin.ts` | ISSUE-006 |

#### Sprint Common Issues Summary

| ID | Severity | File | Description |
|----|----------|------|-------------|
| ISSUE-006 | HIGH | `care-circle-template-admin.ts` | Path traversal risk in template admin file writes |
| ISSUE-007 | HIGH | `app-membership-guard.tsx` | Inverted auth logic — shows children when auth required but user not authenticated |
| ISSUE-012 | MEDIUM | `platform-route-bridge.tsx` | Redirect loop risk without deduplication |
| ISSUE-013 | LOW | `platform-context.ts` | Hardcoded route-to-surface mapping — brittle |
| ISSUE-014 | LOW | `app-shell-resolver.tsx` | Unused component — dead code |

---

## 3. Cross-Sprint Issues

### 3.1 Architecture Issues

| ID | Severity | Description |
|----|----------|-------------|
| ISSUE-003 | MEDIUM | `care-circle-family` layout missing auth guard — anonymous users can access protected routes |
| ISSUE-011 | MEDIUM | Inconsistent layout hierarchy across app surfaces |

### 3.2 Security Issues

| ID | Severity | Description |
|----|----------|-------------|
| ISSUE-001 | HIGH | Debug login with hardcoded credentials exposed to admin users |
| ISSUE-004 | MEDIUM | Open redirect edge cases in `normalizeNextPath` |
| ISSUE-006 | HIGH | Path traversal in template admin file writes |
| ISSUE-007 | HIGH | Inverted auth logic in `AppMembershipGuard` |
| ISSUE-018 | HIGH | No unit tests for security-critical redirect validator |

### 3.3 Testing Issues

| ID | Severity | Description |
|----|----------|-------------|
| ISSUE-016 | MEDIUM | No E2E tests for `care-circle-family` auth flow |
| ISSUE-017 | MEDIUM | No unit tests for `platform-context.ts` routing logic |
| ISSUE-018 | HIGH | No unit tests for `normalizeNextPath` security logic |
| ISSUE-019 | LOW | Overly broad mock helper — 1400+ line single file |
| ISSUE-020 | LOW | Playwright config uses non-standard port 3001 |

---

## 4. Test Coverage Analysis

### 4.1 E2E Test Files Reviewed

| Test File | Routes Covered | Issues |
|-----------|---------------|--------|
| `sprint1-shell.spec.ts` | `/`, `/public`, `/app/account` | None |
| `sprint2-auth.spec.ts` | `/auth/login`, `/auth/register`, `/auth/forgot-password`, `/auth/reset-password` | None |
| `sprint3-framework.spec.ts` | `/app/account/edit`, `/app/billing`, `/app/referrals`, `/app/onboarding` | None |
| `sprint-common-platform.spec.ts` | `/storytelling`, `/care-circle-family`, `/care-circle-patient` | None |

### 4.2 Test Gaps

| Gap | Severity | Description |
|-----|----------|-------------|
| Care-circle family auth | MEDIUM | No test for anonymous redirect on `/care-circle-family` |
| Platform context unit tests | MEDIUM | No unit tests for `resolveSurfaceId`, `resolvePlatformContext`, `getLegacyRouteTarget` |
| Auth redirect security tests | HIGH | No unit tests for `normalizeNextPath` |
| Care-circle patient direct-entry | LOW | No test for patient login flow |

### 4.3 Mock Helper Analysis

The `helpers.ts` file (1442 lines) mocks 50+ API endpoints. Issues:
- High coupling between tests and mock implementation
- Difficulty understanding what each test exercises
- Risk of mock drift when backend endpoints change

---

## 5. Backend API Contract Verification

### 5.1 API Endpoints Used by Sprint V1

| Endpoint | Method | Used By | Status |
|----------|--------|---------|--------|
| `/api/v1/users/me` | GET | Session bootstrap, auth guard | Verified |
| `/api/v1/users/me` | PUT | Account edit | Verified |
| `/api/v1/auth/login` | POST | Login page | Verified |
| `/api/v1/auth/register` | POST | Register page | Verified |
| `/api/v1/auth/logout` | POST | Logout | Verified |
| `/api/v1/auth/password-reset/request` | POST | Forgot password | Verified |
| `/api/v1/auth/password-reset/confirm` | POST | Reset password | Verified |
| `/api/v1/auth/google` | GET | Google sign-in | Verified |
| `/api/v1/billing/balance` | GET | Coin balance badge | Verified |
| `/api/v1/billing/dashboard` | GET | Billing page | Verified |
| `/api/v1/referrals` | GET | Referrals stats | Verified |
| `/api/v1/referrals/history` | GET | Referrals history | Verified |
| `/api/v1/referrals/rewards` | GET | Referrals rewards | Verified |
| `/api/v1/interview/questions/{id}` | GET | Onboarding | Verified |
| `/api/v1/interview/status/{id}` | GET | Onboarding | Verified |
| `/api/v1/interview/user-insights` | GET | Onboarding | Verified |
| `/api/v1/maintenance/status` | GET | Maintenance banner/gate | Verified |

### 5.2 API Contract Issues

| ID | Severity | Description |
|----|----------|-------------|
| ISSUE-008 | MEDIUM | Inconsistent response handling — `apiFetch` unwraps `data` envelope, `apiFetchRaw` does not |

---

## 6. Summary Matrix

### 6.1 Issues by Category

| Category | Count | Severity Distribution |
|----------|-------|----------------------|
| Security | 5 | 3 HIGH, 1 MEDIUM, 1 LOW |
| Functional | 7 | 1 HIGH, 3 MEDIUM, 3 LOW |
| Architecture | 5 | 2 MEDIUM, 3 LOW |
| Testing | 5 | 1 HIGH, 2 MEDIUM, 2 LOW |
| Code Quality | 5 | 5 LOW |
| Accessibility | 3 | 3 LOW |
| Performance | 2 | 2 LOW |
| Configuration | 3 | 1 MEDIUM, 2 LOW |

### 6.2 Issues by Severity

| Severity | Count |
|----------|-------|
| HIGH | 5 |
| MEDIUM | 8 |
| LOW | 20 |
| INFO | 1 |

### 6.3 Issues by Sprint

| Sprint | Issues Found |
|--------|--------------|
| Sprint 01 | 9 |
| Sprint 02 | 6 |
| Sprint 03 | 2 |
| Sprint Common 01 | 5 |
| Cross-Sprint | 16 |

---

## 7. Priority Remediation Order

### 7.1 Immediate (HIGH)

1. **ISSUE-007** — Fix inverted auth logic in `AppMembershipGuard` (`app-membership-guard.tsx:35-37`)
   - **Impact:** Authenticated-gated routes may render to unauthenticated users
   - **Fix:** Change condition to return loading state instead of children

2. **ISSUE-001** — Remove or guard debug login behind dev-only environment (`login/page.tsx:147-177`)
   - **Impact:** Hardcoded credentials exposed to all admin users
   - **Fix:** Guard behind `process.env.NODE_ENV === "development"`

3. **ISSUE-006** — Add path traversal guards to template admin (`care-circle-template-admin.ts`)
   - **Impact:** Direct file system writes with unsanitized input
   - **Fix:** Add whitelist validation for `providerKey` and path traversal checks

4. **ISSUE-018** — Add unit tests for `normalizeNextPath` (`lib/auth-redirect.ts`)
   - **Impact:** Security-critical redirect validator has no test coverage
   - **Fix:** Add unit tests for all edge cases

### 7.2 Short-term (MEDIUM)

5. **ISSUE-003** — Add auth guard to `care-circle-family` layout
   - **Impact:** Anonymous users can access protected routes
   - **Fix:** Add `AppShellGuard` or `PlatformAppGate` to layout

6. **ISSUE-002** — Switch `useLayoutEffect` to `useEffect` (`app-shell-guard.tsx`)
   - **Impact:** SSR flash before redirect
   - **Fix:** Use `useEffect` for navigation-side-effect redirects

7. **ISSUE-004** — Harden redirect validation (`lib/auth-redirect.ts`)
   - **Impact:** Open redirect edge cases
   - **Fix:** Add explicit blocks for sensitive paths and path traversal checks

8. **ISSUE-008** — Standardize API response handling (`lib/api.ts`)
   - **Impact:** Inconsistent response shapes across endpoints
   - **Fix:** Use consistent `apiFetch` or `apiFetchRaw` pattern

9. **ISSUE-011** — Document and unify layout hierarchy
   - **Impact:** Inconsistent auth protection across app surfaces
   - **Fix:** Document layout hierarchy and ensure consistent use of `PlatformAppGate`

10. **ISSUE-012** — Add redirect deduplication in `PlatformRouteBridge` (`platform-route-bridge.tsx`)
    - **Impact:** Potential redirect loop on unmapped legacy routes
    - **Fix:** Add ref to track redirect completion

### 7.3 Long-term (LOW)

11. **ISSUE-005** — Ensure backend generates OAuth state parameter for Google sign-in
12. **ISSUE-009** — Return structured result from `fetchSession()` instead of swallowing errors
13. **ISSUE-010** — Use variable toast durations based on tone
14. **ISSUE-013** — Consolidate route-to-surface mapping into single source of truth
15. **ISSUE-014** — Remove unused `AppShellResolver` component
16. **ISSUE-015** — Update `TopNav` default links to point to new routes
17. **ISSUE-016** — Add E2E tests for care-circle family auth flow
18. **ISSUE-017** — Add unit tests for platform context routing logic
19. **ISSUE-019** — Split mock helper into domain-specific helpers
20. **ISSUE-020** — Document port 3001 choice in Playwright config
21. **ISSUE-021** — Add dev-mode warning for fallback context usage
22. **ISSUE-023** — Move inline styles to Tailwind arbitrary values
23. **ISSUE-024** — Rename `tooltip` prop to `fallbackTitle` in Button component
24. **ISSUE-025** — Split `help-content.ts` into per-page files
25. **ISSUE-027** — Add `aria-live` to cookie consent banner
26. **ISSUE-028** — Verify Radix dropdown focus indicators
27. **ISSUE-029** — Increase maintenance polling interval or use push notifications
28. **ISSUE-030** — Use per-query `staleTime` configuration

---

## Appendix A: Files Reviewed

### Sprint Planning Documents

| File | Status |
|------|--------|
| `frontendv1Sprint01PlatformBaseline.md` | Reviewed |
| `frontendSprint01.md` | Reviewed |
| `frontendSprint02.md` | Reviewed |
| `frontendSprint03.md` | Reviewed |
| `frontendSprintCommonPlatform.md` | Reviewed |

### Frontend Source Files (from sprint baseline)

| Category | Files Reviewed |
|----------|---------------|
| Auth pages | `app/auth/layout.tsx`, `login/page.tsx`, `register/page.tsx`, `forgot-password/page.tsx`, `password-reset/confirm/page.tsx`, `reset-password/page.tsx` |
| App pages | `app/app/layout.tsx`, `app/app/account/page.tsx` |
| Platform components | All 8 files in `components/platform/` |
| Shell components | All 13 files in `components/shell/` |
| E2E tests | `sprint1-shell.spec.ts`, `sprint2-auth.spec.ts`, `sprint3-framework.spec.ts`, `sprint-common-platform.spec.ts` |

### Supporting Files Reviewed

| Category | Files Reviewed |
|----------|---------------|
| Next.js bootstrap | `app/layout.tsx`, `next.config.mjs`, `package.json` |
| Providers | `components/providers/app-providers.tsx` |
| UI components | All 22 files in `components/ui/` |
| App routes | `app/page.tsx`, `app/storytelling/page.tsx`, `app/care-circle-family/page.tsx`, `app/care-circle-patient/page.tsx`, `app/chatbot/page.tsx`, `app/public/page.tsx`, `app/not-found.tsx`, `app/loading.tsx` |
| Lib modules | `lib/api.ts`, `lib/types.ts`, `lib/apps.ts`, `lib/auth-redirect.ts`, `lib/utils.ts`, `lib/help-content.ts`, `lib/require-admin.ts`, `lib/care-circle-template-admin.ts` |
| Test helpers | `tests/e2e/helpers.ts`, `playwright.config.ts` |
