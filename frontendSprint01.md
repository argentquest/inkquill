# Sprint 01: Foundation and Shell

## Goal

Establish the React application foundation and the shared experience every other route depends on.

## In Scope

- app bootstrap
- routing
- authenticated shell
- public shell
- top navigation
- breadcrumbs and page header pattern
- theme toggle
- toast/notification system
- cookie consent
- global loading and error states
- session bootstrap
- coin balance fetch
- maintenance banner handling
- Playwright browser coverage for Sprint 1 shell behavior

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/` | `pages/index.html` | P0 | Public home shell and content rails |
| `/app/*` layout | `layouts/base.html`, `_topbar.html` | P0 | Main app shell |
| `/public/*` layout | `layouts/base.html`, footer/public nav | P0 | Public shell |
| `/app/account` | `pages/account.html` | P0 | Good first authenticated page |

## Shared Components

- `AppShell`
- `PublicShell`
- `TopNav`
- `PageHeader`
- `Breadcrumbs`
- `Footer`
- `CookieConsentBanner`
- `MaintenanceBanner`
- `UserMenu`
- `CoinBalanceBadge`
- `ThemeToggle`
- `ToastCenter`
- `LoadingState`
- `ErrorState`

## Backend/API Dependencies

- auth session bootstrap
- `/api/v1/users/me`
- `/api/v1/billing/balance`
- maintenance status endpoints

## UI Behavior Capture Targets

- top navigation
- coin balance refresh behavior
- account dropdown
- theme toggle persistence
- maintenance banner behavior
- global error and toast behavior

## Risks and Decisions

- Decide app-wide state strategy early.
- Decide route protection and redirect rules early.
- Keep shell simple; avoid premature design complexity.

## Task List

- [x] Set up the React app bootstrap and route tree.
- [x] Create authenticated and public layout shells.
- [x] Implement top navigation, footer, page header, and breadcrumbs.
- [x] Implement global user/session bootstrap.
- [x] Implement global coin balance fetch and refresh behavior.
- [x] Implement theme toggle and persisted theme state.
- [x] Implement toast/notification system.
- [x] Implement global loading, empty, and error presentation patterns.
- [x] Implement cookie consent banner.
- [x] Implement maintenance banner and maintenance-aware routing behavior.
- [x] Validate `/` and `/app/account` as working shell routes.
- [x] Add Playwright configuration and frontend test scripts.
- [x] Add Sprint 1 browser tests for `/`, `/public`, and `/app/account`.
- [x] Cover theme persistence, cookie consent persistence, maintenance mode, and balance/session failure states in Playwright.
- [x] Add direct Playwright coverage for toast display and dismissal behavior.
- [x] Run Playwright and verify the Sprint 1 frontend suite passes.

## Exit Criteria

- user can load public and authenticated shells
- session bootstrap works
- coin balance renders in shell
- cookie consent behavior works
- toast and notification behavior works
- maintenance state can be displayed globally
- route-level loading and error states exist
- Sprint 1 Playwright browser suite passes locally

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| user can load public and authenticated shells | Playwright route checks for `/`, `/public`, `/app/account` | `tests/e2e/sprint1-shell.spec.ts` |
| session bootstrap works | Playwright mocks `/api/v1/users/me` for authenticated and anonymous states | `tests/e2e/helpers.ts`, `tests/e2e/sprint1-shell.spec.ts` |
| coin balance renders in shell | Playwright mocks `/api/v1/billing/balance` and checks nav/account rendering | `tests/e2e/helpers.ts`, `tests/e2e/sprint1-shell.spec.ts` |
| cookie consent behavior works | Playwright accepts the consent banner and verifies it stays dismissed after reload | `tests/e2e/sprint1-shell.spec.ts`, `components/shell/cookie-consent-banner.tsx` |
| toast and notification behavior works | Playwright verifies warning toast appears on balance failure and can be dismissed | `tests/e2e/sprint1-shell.spec.ts`, `components/ui/toast-center.tsx` |
| maintenance state can be displayed globally | Playwright mocks active maintenance and checks banner + gate | `tests/e2e/helpers.ts`, `tests/e2e/sprint1-shell.spec.ts`, `components/shell/maintenance-banner.tsx`, `components/shell/maintenance-gate.tsx` |
| route-level loading and error states exist | Code check for `app/loading.tsx` and `app/error.tsx`; runtime failure notifications verified in Playwright | `frontendv1/app/loading.tsx`, `frontendv1/app/error.tsx`, `tests/e2e/sprint1-shell.spec.ts` |
| Sprint 1 Playwright browser suite passes locally | Run `npm run test:e2e` | Passed locally |

## Implementation Status

- `frontendv1/`: Next.js + TypeScript Sprint 1 workspace using the Option 1 stack direction.
- Implemented: public shell, app shell, top nav, footer, breadcrumbs, page headers, toast center, cookie consent, maintenance banner/gate, theme persistence, session bootstrap, and coin balance fetch.
- Testing: Playwright browser suite covers home, public shell, account shell, anonymous/authenticated state, maintenance mode, theme persistence, cookie consent persistence, toast display/dismissal, and failure toasts.
- Verified: `npm run build` and `npm run test:e2e` complete successfully in `frontendv1`.
