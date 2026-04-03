# Sprint Common 01: Shared Platform Supersession

## Goal

Replace Sprint 1 to 3 as the active shared-platform execution sprint and consolidate the shell, auth, and framework foundations into one platform baseline for independent application delivery.

## Supersedes

This sprint supersedes the earlier shared-framework planning in:

- `frontendSprint01.md`
- `frontendSprint02.md`
- `frontendSprint03.md`

Those sprint files remain useful as historical implementation reference, but this file is the current source of truth for shared frontend platform work that sits underneath the separate app sprints.

## In Scope

- consolidation of Sprint 1 to 3 platform concerns into one active shared-platform sprint
- shared app-level route strategy
- app membership and access gating foundation
- ownership-scope-aware billing abstractions
- shared event transport foundation
- shared auth-entry refinement for multi-app routing
- shared shell primitives for app-specific layouts
- common test scaffolding for multi-surface Playwright coverage
- migration rules from legacy shared `/app/*` assumptions into app-specific route spaces

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/auth/login` | existing auth surface | P0 | Shared auth entry remains platform-level |
| `/auth/register` | existing auth surface | P0 | Shared registration with app-context routing |
| `/access-denied` | net-new | P1 | Explicit app membership failure state |
| `/storytelling` | existing app shell concept | P0 | New top-level application entry |
| `/care-circle-family` | net-new | P0 | Family application entry |
| `/care-circle-patient` | net-new | P0 | Patient direct-entry surface |

## Shared Components

- `PlatformAppGate`
- `AppMembershipGuard`
- `AppShellResolver`
- `OwnerScopeBadge`
- `RealtimeStatusIndicator`
- `AppRouteLanding`
- `PlatformRouteBridge`

## Backend/API Dependencies

- shared auth and session endpoints
- app membership and app-assignment contract
- billing ownership-scope contract
- realtime transport contract
- route-safe current-user and current-context endpoints
- redirect-safe auth entry contract for app-aware sign-in and registration

## UI Behavior Capture Targets

- shared sign-in and registration branching behavior
- app membership denied state
- route protection and redirect behavior
- shell resolution across three app surfaces
- migration behavior from prior shared `/app/*` routes
- realtime connection and disconnected states

## Risks and Decisions

- This sprint should be treated as the active replacement for Sprint 1 to 3 platform planning, not as an additional parallel foundation sprint.
- Do not let the shared layer absorb product-specific assumptions.
- App routing, auth context, and billing ownership must be explicit before deeper domain delivery.
- The patient route tree should not inherit dense family or storytelling navigation patterns.
- Keep `chatbot` out of this sprint except where shared platform behavior is intentionally reused by independent app sprints.

## Task List

- [ ] Consolidate Sprint 1 to 3 shared-platform outcomes into this sprint as the active baseline.
- [ ] Define route-space boundaries for `storytelling`, `care-circle-family`, and `care-circle-patient`.
- [ ] Add app membership and app-access guard patterns.
- [ ] Define the shared current-context contract used by all route guards.
- [ ] Add ownership-scope-aware billing abstractions for user-level and family-level usage.
- [ ] Add shared realtime transport wiring usable by family event feeds later.
- [ ] Create shell-resolution patterns so each app surface can use a distinct layout safely.
- [ ] Add shared auth-entry handling for URL- and invitation-driven app access.
- [ ] Define migration handling from the current shared `/app/*` route assumptions into app-specific route spaces.
- [x] Add Playwright scaffolding for multi-surface authentication and route protection.
- [x] Capture platform route, auth, migration, and realtime behavior in `uiBehaviorCapture.md`.
- [ ] Verify common platform behavior against backend contracts before application sprint work starts.

## Exit Criteria

- this sprint is the explicit shared-platform replacement for Sprint 1 to 3 planning
- the shared platform can route and gate three application surfaces cleanly
- billing infrastructure supports both user-scoped and family-scoped ownership
- realtime transport and app-shell resolution foundations exist for later app-specific work

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| this sprint is the explicit shared-platform replacement for Sprint 1 to 3 planning | Document review confirms this sprint defines the active shared-platform baseline and references Sprint 1 to 3 as superseded planning artifacts | This file |
| the shared platform can route and gate three application surfaces cleanly | Playwright covers URL-driven access, membership denial, and route guards across all three top-level app entries | `cd frontendv1; npx playwright test tests/e2e/sprint-common-platform.spec.ts` |
| billing infrastructure supports both user-scoped and family-scoped ownership | Code review plus targeted tests verify billing owner-scope abstractions and surface-safe loading states | To be recorded during implementation |
| realtime transport and app-shell resolution foundations exist for later app-specific work | Code check and browser verification confirm shell resolution and connection state handling | `cd frontendv1; npx playwright test tests/e2e/sprint-common-platform.spec.ts` |

## Implementation Status

- Planning only.
- This file is the active shared-platform sprint and supersedes Sprint 1 to 3 as the planning base for common frontend infrastructure.
- `chatbot` remains intentionally separate and should be planned in its own sprint except where it consumes platform behavior defined here.
- Playwright scaffolding now covers protected storytelling entry, explicit membership denial, anonymous patient entry, and realtime online/offline state handling in `frontendv1/tests/e2e/sprint-common-platform.spec.ts`.
- `uiBehaviorCapture.md` now includes platform route landing, access-denied, and legacy-route migration behavior records for the common platform baseline.
