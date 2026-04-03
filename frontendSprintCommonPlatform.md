# Sprint Common 01: Shared Platform Split

## Goal

Prepare the shared React platform so `storytelling`, `care-circle-family`, and `care-circle-patient` can exist as separate application surfaces without duplicating framework concerns.

## In Scope

- shared app-level route strategy
- app membership and access gating foundation
- ownership-scope-aware billing abstractions
- shared event transport foundation
- shared auth entry refinement for multi-app routing
- shared shell primitives for app-specific layouts
- common test scaffolding for multi-surface Playwright coverage

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/login` | existing auth surface | P0 | Shared auth entry remains platform-level |
| `/register` | existing auth surface | P0 | Shared registration with app-context routing |
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

## Backend/API Dependencies

- shared auth and session endpoints
- app membership and app-assignment contract
- billing ownership-scope contract
- realtime transport contract
- route-safe current-user and current-context endpoints

## UI Behavior Capture Targets

- shared sign-in and registration branching behavior
- app membership denied state
- route protection and redirect behavior
- shell resolution across three app surfaces
- realtime connection and disconnected states

## Risks and Decisions

- Do not let the shared layer absorb product-specific assumptions.
- App routing, auth context, and billing ownership must be explicit before deeper domain delivery.
- The patient route tree should not inherit dense family or storytelling navigation patterns.

## Task List

- [ ] Define route-space boundaries for `storytelling`, `care-circle-family`, and `care-circle-patient`.
- [ ] Add app membership and app-access guard patterns.
- [ ] Define the shared current-context contract used by all route guards.
- [ ] Add ownership-scope-aware billing abstractions for user-level and family-level usage.
- [ ] Add shared realtime transport wiring usable by family event feeds later.
- [ ] Create shell-resolution patterns so each app surface can use a distinct layout safely.
- [ ] Add shared auth-entry handling for URL- and invitation-driven app access.
- [ ] Add Playwright scaffolding for multi-surface authentication and route protection.
- [ ] Capture platform route, auth, and realtime behavior in `uiBehaviorCapture.md`.
- [ ] Verify common platform behavior against backend contracts before application sprint work starts.

## Exit Criteria

- the shared platform can route and gate three application surfaces cleanly
- billing infrastructure supports both user-scoped and family-scoped ownership
- realtime transport and app-shell resolution foundations exist for later app-specific work

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| the shared platform can route and gate three application surfaces cleanly | Playwright covers URL-driven access, membership denial, and route guards across all three top-level app entries | To be recorded during implementation |
| billing infrastructure supports both user-scoped and family-scoped ownership | Code review plus targeted tests verify billing owner-scope abstractions and surface-safe loading states | To be recorded during implementation |
| realtime transport and app-shell resolution foundations exist for later app-specific work | Code check and browser verification confirm shell resolution and connection state handling | To be recorded during implementation |

## Implementation Status

- Planning only.
- This sprint establishes platform boundaries and infrastructure required by the storytelling and care-circle tracks.
