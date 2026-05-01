# Frontend V1 Sprint 01: Platform Baseline

## Status

Completed.

## Goal

Capture the shared React platform baseline that all product surfaces now rely on.

## Delivered Scope

- Next.js App Router workspace in `frontendv1/`
- shared public and authenticated shells
- auth login, registration, password reset, logout, and Google entry controls
- session bootstrap, route guards, and app-aware redirects
- theme persistence, cookie consent, maintenance state, toast notifications, loading, and error states
- shared framework components for tables, forms, drawers, confirmations, settings sections, and route states
- platform route boundaries for `storytelling`, `care-circle-family`, `care-circle-patient`, and `chatbot`
- legacy `/app/*` bridge behavior into app-specific route spaces
- user-scoped billing/referrals/onboarding foundations

## Source Files

- `frontendSprint01.md`
- `frontendSprint02.md`
- `frontendSprint03.md`
- `frontendSprintCommonPlatform.md`
- `frontendv1/app/auth/**`
- `frontendv1/app/app/**`
- `frontendv1/components/platform/**`
- `frontendv1/components/shell/**`
- `frontendv1/tests/e2e/sprint1-shell.spec.ts`
- `frontendv1/tests/e2e/sprint2-auth.spec.ts`
- `frontendv1/tests/e2e/sprint3-framework.spec.ts`
- `frontendv1/tests/e2e/sprint-common-platform.spec.ts`

## Task List

- [x] `[Size: XL]` Establish React app bootstrap and route shell.
- [x] `[Size: XL]` Deliver auth entry, session bootstrap, and protected-route behavior.
- [x] `[Size: L]` Deliver shared framework components and route-state patterns.
- [x] `[Size: L]` Deliver app-aware platform routing and access gating.
- [x] `[Size: M]` Preserve legacy `/app/*` migration behavior with route bridges.
- [x] `[Size: M]` Add focused unit/component tests for shell, auth controls, route guards, and shared UI primitives where practical.
- [x] `[Size: L]` Add backend/API integration tests for auth, current-user, billing balance, referrals, and platform contracts used by the frontend baseline.
- [x] `[Size: L]` Add Playwright coverage for platform shell, auth, framework, and route protection.

## Verification Notes

- Existing sprint docs record prior `npm run build` and Playwright verification.
- Current status was reviewed against the route tree and e2e tests on 2026-04-27.
