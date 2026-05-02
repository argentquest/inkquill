# Frontend V1 Sprint 04: Storytelling Boundary

## Status

Completed.

## Goal

Make storytelling an explicit top-level app surface before rebuilding the actual storytelling workflows.

## Delivered Scope

- `/storytelling` entry route
- `/storytelling/account`
- `/storytelling/account/edit`
- `/storytelling/billing`
- `/storytelling/referrals`
- `/storytelling/onboarding`
- storytelling layout through `AppShellResolver` and `PlatformAppGate`
- legacy `/app/account`, `/app/billing`, `/app/referrals`, and `/app/onboarding` bridge behavior
- Playwright coverage for protected storytelling access and commercial/account framework routes

## Remaining Scope

- `/storytelling/stories`
- `/storytelling/worlds`
- `/storytelling/community`
- route-specific navigation that reflects real storytelling workflows
- `uiBehaviorCapture.md` notes for the storytelling route bridge and shell behavior

## Source Files

- `frontendSprintStorytellingApp.md`
- `frontendv1/app/storytelling/**`
- `frontendv1/app/app/**`
- `frontendv1/components/platform/platform-route-bridge.tsx`
- `frontendv1/tests/e2e/sprint-common-platform.spec.ts`
- `frontendv1/tests/e2e/sprint3-framework.spec.ts`

## Task List

- [x] `[Size: S]` Define `/storytelling` route tree.
- [x] `[Size: S]` Add storytelling landing route.
- [x] `[Size: M]` Add storytelling shell and guard behavior.
- [x] `[Size: M]` Bridge delivered `/app/*` framework routes into storytelling-safe route space.
- [x] `[Size: M]` Preserve user-scoped billing and referrals under storytelling.
- [x] `[Size: M]` Add unit/component coverage for storytelling shell, route bridge, and route guard behavior where practical.
- [x] `[Size: M]` Add backend/API integration coverage for user-scoped account, billing, referrals, and onboarding contracts used by storytelling routes.
- [x] `[Size: M]` Add Playwright smoke coverage for delivered storytelling routes.
- [x] `[Size: L]` Add real story/world/community route groups.
- [x] `[Size: M]` Add unit/component tests for story/world/community route entry components as they are introduced.
- [x] `[Size: L]` Add backend integration tests for story/world/community entry API contracts before marking those route groups complete.
- [x] `[Size: XS]` Capture storytelling bridge behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- Storytelling has a distinct route boundary.
- Legacy framework routes continue to resolve safely.
- Story, world, and community route groups have real entry points for later sprints.

## Verification Notes

- `/storytelling/stories` added at `frontendv1/app/storytelling/stories/page.tsx` — API-backed via `GET /api/v1/stories/`, with loading, empty, and error states.
- `/storytelling/worlds` added at `frontendv1/app/storytelling/worlds/page.tsx` — API-backed via `GET /api/v1/worlds/`, with loading, empty, and error states.
- `/storytelling/community` added at `frontendv1/app/storytelling/community/page.tsx` — static placeholder reserved for later product work.
- `fetchUserStories()` and `fetchUserWorlds()` API functions with `StoryEntry` and `WorldEntry` interfaces added to `frontendv1/lib/api.ts`.
- Playwright spec added at `frontendv1/tests/e2e/sprint-storytelling-boundary.spec.ts` with 9 tests covering list rendering, empty states, error states, and auth guard redirects for all three routes.
- Seed data and route mocks for `/api/v1/stories/` and `/api/v1/worlds/` added to `frontendv1/tests/e2e/helpers.ts`.
- Backend integration tests added at `tests/integration/story/test_storytelling_entry_contracts_integration.py` covering auth enforcement (401), empty list for new users, list shape after create, and user isolation.
- Storytelling bridge behavior captured in `uiBehaviorCapture.md` Quick Capture Table: account bridge, stories list, worlds list, and community placeholder rows added.
