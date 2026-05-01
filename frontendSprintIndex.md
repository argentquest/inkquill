# Frontend Sprint Index

> Purpose: manage the React rebuild as ten separate sprint documents with one shared entry point.

> Current note: the active reorganized roadmap now lives in [frontendv1SprintIndex.md](frontendv1SprintIndex.md). This older index remains as historical planning context.

Core reference docs:
- [frontendAll.md](frontendAll.md)
- [frontendRouteBacklog.md](frontendRouteBacklog.md)
- [frontendComponentInventory.md](frontendComponentInventory.md)
- [uiBehaviorCapture.md](uiBehaviorCapture.md)
- [BACKEND_ENDPOINT_MATRIX.md](BACKEND_ENDPOINT_MATRIX.md)

## Current Review Status

- Last reviewed against the repo on 2026-04-27.
- `frontendSprint01.md`, `frontendSprint02.md`, and `frontendSprint03.md` are historical shared-foundation sprints and remain complete.
- `frontendSprintCommonPlatform.md` is the active shared-platform source of truth and is complete.
- `frontendSprintCareCircleApp.md` and `frontendSprintCareCircleProviders.md` are mostly complete; core family and patient flows are delivered, while family events/media remain scaffold-level.
- `frontendSprintCareCircleArchitectureDocs.md` is complete and the architecture docs now reflect current code truth.
- `frontendSprintStorytellingApp.md` is partially complete: the `/storytelling` app boundary, shell, account, billing, referrals, onboarding, and legacy route bridge are delivered, but story/world/community routes are not.
- `frontendSprintChat.md` is partially complete: the `/chatbot` app entry and local UI prototype exist, but multi-session, backend-backed, and tested chat flows are not delivered.
- `frontendSprint04.md` through `frontendSprint08.md` remain not started in React delivery.
- `frontendSprint09.md` is partially complete only for billing, referrals, and onboarding foundations; prompt, AI-model, and blog tooling remain not started.
- `frontendSprint10.md` remains not started for the original legacy `/app/admin/*` scope.

## Common Rules

- The backend is the source of truth for data and contracts.
- Sprint docs are execution artifacts, not broad vision docs.
- Each sprint should produce working React routes, not isolated components only.
- Reuse shared components before creating route-specific one-offs.
- Capture legacy behavior for async or high-risk UI before implementation.
- Prefer merging legacy pages into cleaner React route groups when function is preserved.

## Sprint Template

Each sprint file follows this structure:
- Goal
- In scope
- Route backlog
- Shared components
- Backend/API dependencies
- UI behavior capture targets
- Risks and decisions
- Exit criteria

## Table of Contents

1. [frontendSprint01.md](frontendSprint01.md)
2. [frontendSprint02.md](frontendSprint02.md)
3. [frontendSprint03.md](frontendSprint03.md)
4. [frontendSprint04.md](frontendSprint04.md)
5. [frontendSprint05.md](frontendSprint05.md)
6. [frontendSprint06.md](frontendSprint06.md)
7. [frontendSprint07.md](frontendSprint07.md)
8. [frontendSprint08.md](frontendSprint08.md)
9. [frontendSprint09.md](frontendSprint09.md)
10. [frontendSprint10.md](frontendSprint10.md)

## Recommended Usage

1. Start planning from this file.
2. Open the active sprint file and break route rows into tickets.
3. Track open UI behavior questions in [uiBehaviorCapture.md](uiBehaviorCapture.md).
4. Update the sprint file when routes move in or out of scope.
5. Keep [frontendAll.md](frontendAll.md) as the high-level roadmap and these sprint files as the working plan.

## Parallel Track Planning

The current repo also has app-split planning documents for the shared-platform plus multi-app direction:

- [frontendPlatformBlueprint.md](frontendPlatformBlueprint.md)
- [frontendSprintCommonPlatform.md](frontendSprintCommonPlatform.md) - active replacement for Sprint 1 to 3 shared-platform planning
- [frontendSprintStorytellingApp.md](frontendSprintStorytellingApp.md)
- [frontendSprintCareCircleApp.md](frontendSprintCareCircleApp.md)
- [frontendSprintCareCircleProviders.md](frontendSprintCareCircleProviders.md)
- [frontendSprintChat.md](frontendSprintChat.md)



