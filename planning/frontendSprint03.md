# Sprint 03: Platform and App Framework Expansion

## Goal

Strengthen the React application framework so later domain work reuses stable patterns instead of inventing them page by page.

## In Scope

- query and mutation conventions
- API form workflow patterns
- modal, drawer, and confirmation patterns
- reusable list/table and empty-state patterns
- account edit and preferences
- onboarding/welcome flow
- legal/help/about routes
- billing/referrals shell entry routes when backend contracts are ready

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/account/edit` | `pages/account.html` | P0 | Complete the core account-management surface |
| `/app/onboarding` | welcome/interview entry surfaces | P1 | Keep this minimal and product-safe |
| `/app/billing` | billing shell surface | P1 | Route and state foundation first |
| `/app/referrals` | referral intro/dashboard | P1 | Shared account/commercial pattern |
| `/help`, `/about`, `/privacy`, `/terms` | info/legal pages | P1 | Public content surfaces on the shared shell |

## Shared Components

- `EntityPageLayout`
- `DataTable`
- `EntityListView`
- `FormActionsBar`
- `ConfirmationModal`
- `DrawerPanel`
- `EmptyState`
- `SettingsFormSection`

## Backend/API Dependencies

- `/api/v1/users/me`
- billing dashboard and balance-related endpoints
- referrals endpoints
- account update endpoints
- maintenance and route-guard behavior already established in Sprint 1

## UI Behavior Capture Targets

- shared form submit and validation behavior
- reusable confirmation flow
- billing/referral route loading and error states
- public content-route shell behavior

## Risks and Decisions

- Do not overbuild product-specific pages before the shared route and component patterns settle.
- Keep onboarding light unless a backend-backed requirement forces more workflow complexity.

## Task List

- [x] Standardize query and mutation patterns for route-level CRUD screens.
- [x] Build reusable data table/list, modal, drawer, and confirmation components for later sprints.
- [x] Build account edit route and shared settings-form patterns.
- [x] Build minimal onboarding/welcome route if the backend contract is active.
- [x] Build billing shell route with stable loading, empty, and error states.
- [x] Build referrals shell route and intro/dashboard entry flow.
- [x] Build public legal/help/about routes on the shared public shell.
- [x] Capture shared form, modal, and route-state behavior in `uiBehaviorCapture.md`.
- [x] Verify the new framework routes against real backend APIs where available.

## Exit Criteria

- shared route patterns exist for forms, tables/lists, and confirmations
- account/commercial framework routes are reachable and stable
- legal/help/about content routes exist on the public shell

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| shared route patterns exist for forms, tables/lists, and confirmations | Code check for the reusable Sprint 3 components and route usage | `frontendv1/components/ui/data-table.tsx`, `frontendv1/components/ui/drawer-panel.tsx`, `frontendv1/components/ui/confirmation-modal.tsx`, `frontendv1/components/ui/settings-form-section.tsx`, `frontendv1/app/app/account/edit/page.tsx` |
| account/commercial framework routes are reachable and stable | Playwright covers account edit save, billing dashboard load, referrals load, and onboarding route load | `frontendv1/tests/e2e/sprint3-framework.spec.ts` |
| legal/help/about content routes exist on the public shell | Playwright verifies public info routes and code adds the public route pages | `frontendv1/app/help/page.tsx`, `frontendv1/app/about/page.tsx`, `frontendv1/app/privacy/page.tsx`, `frontendv1/app/terms/page.tsx`, `frontendv1/tests/e2e/sprint3-framework.spec.ts` |
| Sprint 3 code compiles for production | Run `npm run build` in `frontendv1` | Passed locally |
| Sprint 3 browser verification passes locally | Run `npm run test:e2e -- tests/e2e/sprint3-framework.spec.ts` and `npm run test:e2e` in `frontendv1` | Passed locally |
| account update endpoint exists for the React profile form | Backend unit/integration coverage added for `PUT /api/v1/users/me` | `tests/unit/test_users_prompt_world_storyclass_unit.py`, `tests/integration/test_auth_users_integration.py` |

## Implementation Status

- `frontendv1/`: Sprint 3 framework routes now extend the Sprint 1/2 shell with account edit, billing, referrals, onboarding preview, and public info pages.
- Implemented: shared `DataTable`, `DrawerPanel`, `ConfirmationModal`, and `SettingsFormSection` components plus route-level query/mutation usage for the new framework surfaces.
- Backend support: added `PUT /api/v1/users/me` so the account edit route can persist changes through the real API contract instead of staying read-only.
- Testing: Playwright covers account edit save, billing, referrals, onboarding, and public info routes.
- Verified: `npm run build`, `npm run test:e2e -- tests/e2e/sprint3-framework.spec.ts`, and `npm run test:e2e` pass locally in `frontendv1`.
- Backend test execution is not verified in this environment because the local Python environment is missing `sqlalchemy`, but the backend tests for the new profile-update endpoint were added.
