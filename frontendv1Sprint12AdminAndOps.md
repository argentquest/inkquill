# Frontend V1 Sprint 12: Admin And Ops

## Status

All planned tasks completed. Core admin routes delivered; P3 utilities retired intentionally.

## Goal

Rebuild or intentionally retire legacy admin and utility surfaces after product-critical routes are stable.

## Current Boundary

Care Circle has separate admin delivery under `/care-circle-family/admin`. That does not complete this sprint, which tracks the broader legacy `/app/admin/*` and operational utility scope.

## Route Decisions

### Retained Routes (Rebuilt in React)
| React Route | Legacy Source | Priority | Status |
|---|---|---|---|
| `/admin/users` | admin pages | P2 | Delivered |
| `/admin/billing` | admin billing pages | P2 | Delivered |
| `/admin/cta` | admin CTA pages | P3 | Delivered |
| `/admin/maintenance` | maintenance admin pages | P3 | Delivered |
| `/admin` | admin dashboard | P2 | Delivered |

### Retired Routes (Explicitly Not Rebuilt)
| Legacy Route | Reason for Retirement |
|---|---|
| `/admin/news` (`admin_news.html`) | News stored as forum threads; template-based CRUD not high value for React rebuild |
| `/admin/image-jobs` (`admin_image_jobs.html`) | Polling page for background image jobs; no active operational use |
| `/admin/user-email` (`admin_user_email.html`) | Email utility never fully shipped; other email channels exist |
| `/admin/help` (`admin_help_editor.html`) | CodeMirror editor with version control; very specialized tooling |
| `/analytics-test` | Test/debug page; no production value |
| `/interview-trigger` | Test/debug page; no production value |

## Task List

- [x] `[Size: S]` Decide which legacy admin pages are still worth rebuilding. **Decision: 5 retained, 6 explicitly retired (see above)**
- [x] `[Size: L]` Build admin users route — `frontendv1/app/admin/users/page.tsx`.
- [x] `[Size: L]` Build admin billing route — `frontendv1/app/admin/billing/page.tsx`.
- [x] `[Size: M]` Build CTA management route — `frontendv1/app/admin/cta/page.tsx`.
- [x] `[Size: M]` Build maintenance admin route — `frontendv1/app/admin/maintenance/page.tsx`.
- [x] `[Size: M]` Rebuild `/admin/page.tsx` as a proper hub page with links to all sub-sections.
- [x] `[Size: M]` ~~Build news manager route if retained.~~ **DECIDED: RETIRE — news is forum-thread-based; not high priority**
- [x] `[Size: M]` ~~Build admin image jobs route if retained.~~ **DECIDED: RETIRE — background job monitor not operationally critical**
- [x] `[Size: M]` ~~Build admin user email route if retained.~~ **DECIDED: RETIRE — email utility never fully shipped**
- [x] `[Size: M]` ~~Build help editor route if retained.~~ **DECIDED: RETIRE — specialized CodeMirror tooling**
- [x] `[Size: XS]` ~~Review analytics-test and interview-trigger pages for keep/remove decision.~~ **DECIDED: RETIRE — test pages with no production value**
- [ ] `[Size: L]` ~~Add frontend unit/component tests for retained admin tables, forms, confirmations, status controls, and utility actions.~~ **DEFERRED — frontend unit test infrastructure not yet established in frontendv1/**
- [x] `[Size: L]` Add backend unit tests for retained admin service logic — `tests/unit/shared/test_admin_cta_maintenance_unit.py`.
- [x] `[Size: XL]` Add backend integration tests for retained admin API flows and permission denial cases — `tests/integration/shared/test_admin_api_integration.py`.
- [x] `[Size: L]` Add Playwright coverage for retained admin workflows — `frontendv1/tests/e2e/sprint-admin.spec.ts`.
- [x] `[Size: S]` Capture impersonation, maintenance, CTA, and admin-job behavior in `uiBehaviorCapture.md`.
- [x] `[Size: S]` Explicitly retire low-value legacy pages that should not move to React. **Done via this document (see route decisions above)**

## API Functions in `frontendv1/lib/api.ts`

- `fetchAdminUsers()` — GET `/api/v1/users/?limit=1000`
- `toggleUserActive(userId)` — PATCH `/api/v1/users/{id}/toggle-active`
- `fetchAdminBillingDashboard()` — GET `/api/v1/admin/billing/dashboard`
- `adminAdjustCredits(userId, amount, description)` — POST `/api/v1/admin/billing/adjust-credits`
- `fetchMaintenanceStatusAdmin()` — GET `/api/v1/maintenance/status`
- `enableMaintenanceMode(message, durationMinutes)` — POST `/api/v1/maintenance/enable`
- `disableMaintenanceMode()` — POST `/api/v1/maintenance/disable`
- `fetchAdminCTAs()` — GET `/api/v1/admin/cta-content?include_inactive=true`
- `toggleCTAActive(ctaId)` — POST `/api/v1/admin/cta-content/{id}/toggle-active`
- `deleteCTA(ctaId)` — DELETE `/api/v1/admin/cta-content/{id}`

## Tests Added

**Backend unit tests** — `tests/unit/shared/test_admin_cta_maintenance_unit.py`:
- `test_admin_cta_get_all_returns_wrapped_list`
- `test_admin_cta_toggle_active_returns_is_active_and_message`
- `test_admin_cta_delete_returns_success`
- `test_admin_cta_requires_admin_on_get`
- `test_admin_cta_requires_admin_on_toggle`
- `test_admin_cta_requires_admin_on_delete`
- `test_maintenance_status_returns_enabled_flag`
- `test_maintenance_enable_requires_admin`
- `test_maintenance_enable_calls_set_maintenance_mode`
- `test_maintenance_disable_requires_admin`
- `test_maintenance_disable_calls_set_maintenance_mode`

**Backend integration tests** — `tests/integration/shared/test_admin_api_integration.py`:
- `TestAdminCTAIntegration` — admin list, non-admin rejection on list/toggle/delete
- `TestAdminMaintenanceIntegration` — admin enable/disable, non-admin rejection, public status
- `TestAdminBillingIntegration` — admin dashboard, non-admin rejection on dashboard/adjust
- `TestAdminUsersIntegration` — admin list users, non-admin rejection on toggle

**Playwright coverage** — `frontendv1/tests/e2e/sprint-admin.spec.ts` (already delivered):
- Admin hub load, links, auth guards (3 tests)
- Admin users table, status badges, toggle button (6 tests)
- Admin billing stats, transactions, credit adjustment (6 tests)
- Admin maintenance status, enable/disable, auth guards (4 tests)
- Admin CTA list, status badges, toggle, delete, empty state (7 tests)

## Exit Criteria

- [x] Required admin flows are available in React.
- [x] Low-value legacy pages are either rebuilt intentionally or explicitly retired.

**Status: COMPLETE**