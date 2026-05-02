# Sprint 02: Authentication and Account Entry

## Goal

Enable user entry into the React app with stable auth and core account access.

## In Scope

- login
- register
- forgot password
- reset password
- Google sign-in entry
- account landing flow
- Playwright browser coverage for Sprint 2 auth behavior

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/auth/login` | `pages/login.html` | P0 | Primary auth route |
| `/auth/register` | `pages/register.html` | P0 | Registration flow |
| `/auth/forgot-password` | `pages/forgot_password.html` | P1 | Recovery flow |
| `/auth/reset-password` | `pages/reset_password.html` | P1 | Token-driven reset |
| `/auth/password-reset/confirm` | backend email/reset link shape | P1 | Alias route that redirects to the React reset screen |
| `/app/account` | `pages/account.html` | P0 | First post-login landing candidate |

## Shared Components

- `TextField`
- `PasswordField`
- `InlineValidationMessage`
- `Button`
- `AlertBanner`
- `GoogleSigninButton`
- `AccountSummaryPanel`
- `AppShellGuard`

## Backend/API Dependencies

- auth login
- auth register
- password reset request
- password reset confirm
- auth logout
- Google auth redirect
- `/api/v1/users/me`

## UI Behavior Capture Targets

- login form error handling
- register validation flow
- password reset success/error messaging
- Google sign-in trigger behavior
- protected-route redirect behavior
- logout return-to-login behavior

## Risks and Decisions

- Cookie-backed auth must hydrate cleanly into the React shell after login and registration.
- Protected routes should fail closed and redirect to login when session bootstrap resolves anonymous.
- Password reset links need a React alias route when backend emails use the legacy confirm path.

## Task List

- [x] Build login page and submission flow.
- [x] Build register page and submission flow.
- [x] Build forgot password page and submission flow.
- [x] Build reset password page and token handling flow.
- [x] Add shared auth form validation and error handling.
- [x] Add Google sign-in entry control to auth screens.
- [x] Implement post-login redirect behavior.
- [x] Implement logout flow from the React shell.
- [x] Build the initial account landing page using `/api/v1/users/me`.
- [x] Test session bootstrap and protected-route redirects after login/logout.
- [x] Add Playwright coverage for login, register, forgot password, reset password, protected-route redirect, logout, and Google entry behavior.
- [x] Run build and Playwright verification for Sprint 2 auth flows.

## Exit Criteria

- user can authenticate and reach account page
- auth errors render clearly
- logout still works from shell
- password reset flows are usable
- protected routes redirect anonymous users to login
- Google sign-in entry points to the backend auth route
- Sprint 2 Playwright auth coverage passes locally

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| user can authenticate and reach account page | Playwright covers login and registration success flows into `/app/account` | `frontendv1/tests/e2e/sprint2-auth.spec.ts` |
| auth errors render clearly | Playwright mocks login failure and checks visible error messaging | `frontendv1/tests/e2e/helpers.ts`, `frontendv1/tests/e2e/sprint2-auth.spec.ts` |
| logout still works from shell | Playwright logs out from the authenticated shell and verifies return to `/auth/login` | `frontendv1/components/shell/user-menu.tsx`, `frontendv1/tests/e2e/sprint2-auth.spec.ts` |
| password reset flows are usable | Playwright covers forgot-password request success and token-driven password reset success | `frontendv1/app/auth/forgot-password/page.tsx`, `frontendv1/app/auth/reset-password/page.tsx`, `frontendv1/tests/e2e/sprint2-auth.spec.ts` |
| protected routes redirect anonymous users to login | Playwright opens `/app/account` anonymously and verifies redirect to the login route with `next` preserved | `frontendv1/components/shell/app-shell-guard.tsx`, `frontendv1/tests/e2e/sprint2-auth.spec.ts` |
| Google sign-in entry points to the backend auth route | Playwright asserts the Google entry link target | `frontendv1/components/ui/google-signin-button.tsx`, `frontendv1/tests/e2e/sprint2-auth.spec.ts` |
| Sprint 2 Playwright auth coverage passes locally | Run `npm run test:e2e -- tests/e2e/sprint2-auth.spec.ts` and `npm run test:e2e` | Passed locally |
| Sprint 2 code compiles for production | Run `npm run build` | Passed locally |

## Implementation Status

- `frontendv1/`: Sprint 2 auth and account-entry flows now sit on top of the Sprint 1 shell foundation.
- Implemented: login, register, forgot password, reset password, Google sign-in entry, logout, account landing, protected-route guard, and legacy reset-link alias routing.
- Testing: Playwright covers anonymous redirect, login success/error, registration success, forgot password, reset password, logout, and Google auth entry.
- Verified: `npm run build`, `npm run test:e2e -- tests/e2e/sprint2-auth.spec.ts`, and `npm run test:e2e` complete successfully in `frontendv1`.
