# Sprint Storytelling 01: App Boundary Refactor

## Goal

Refit the current React rebuild so storytelling becomes an explicit top-level application on the shared platform without regressing existing creative-product flows.

## In Scope

- storytelling route-tree normalization
- storytelling landing experience
- storytelling shell alignment with the new app boundary
- user-scoped billing and current-user context alignment
- storytelling-safe migration of existing Sprint 1 to 3 routes
- storytelling Playwright smoke coverage after route-space changes

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/storytelling` | current app dashboard concept | P0 | Dedicated storytelling landing route |
| `/storytelling/account` | current account patterns | P1 | Storytelling-scoped account entry |
| `/storytelling/billing` | current billing shell | P1 | User-level ownership retained |
| `/storytelling/worlds` | planned world routes | P0 | App-space normalization target |
| `/storytelling/stories` | planned story routes | P0 | App-space normalization target |
| `/storytelling/community` | planned community routes | P1 | Reserved route group for later sprints |

## Shared Components

- `StorytellingShell`
- `StorytellingNav`
- `StorytellingLandingHero`
- `StorytellingUsagePanel`
- `StorytellingRouteBridge`

## Backend/API Dependencies

- current user and session endpoints
- user-level billing and balance endpoints
- current storytelling dashboard data sources
- existing story and world route contracts as they come online

## UI Behavior Capture Targets

- storytelling landing experience
- nav persistence across storytelling routes
- migration-safe redirects from current app routes
- user-level billing ownership behavior

## Risks and Decisions

- Do not let the new application boundary break in-progress rebuild routes.
- Preserve the current creative and editorial shell assumptions for storytelling.
- Keep storytelling user-scoped even though care-circle will be family-scoped.

## Task List

- [ ] Define the storytelling top-level route tree under `/storytelling`.
- [ ] Add a dedicated storytelling landing experience.
- [ ] Move or bridge current rebuild routes into storytelling-safe path space.
- [ ] Add storytelling shell and navigation wrappers on the shared platform.
- [ ] Preserve user-scoped billing and balance behavior under storytelling routes.
- [ ] Add redirect handling for any legacy or interim route paths that should resolve into storytelling.
- [ ] Add Playwright smoke coverage for storytelling entry, shell, and protected route access.
- [ ] Capture storytelling route-bridge and shell behavior in `uiBehaviorCapture.md`.
- [ ] Verify storytelling routing against current backend contracts and existing React route assumptions.

## Exit Criteria

- storytelling is a clearly bounded application on the shared platform
- existing storytelling rebuild work remains reachable under the new route structure
- storytelling retains user-scoped billing and account behavior

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| storytelling is a clearly bounded application on the shared platform | Code review and browser verification confirm storytelling routes resolve under the dedicated app tree with the correct shell | To be recorded during implementation |
| existing storytelling rebuild work remains reachable under the new route structure | Playwright smoke coverage exercises entry, protected routes, and migration-safe redirects | To be recorded during implementation |
| storytelling retains user-scoped billing and account behavior | Targeted route checks verify user-owned balance and billing surfaces remain correct after the app split | To be recorded during implementation |

## Implementation Status

- Planning only.
- This sprint focuses on turning the current rebuild into an explicit standalone storytelling application on the shared platform.
