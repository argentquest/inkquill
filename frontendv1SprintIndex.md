# Frontend V1 Sprint Index

> Purpose: active, reorganized roadmap for the `frontendv1/` React rebuild.

This series supersedes the older `frontendSprint*.md` numbering as the working order for future frontend delivery. The older files remain useful as history and detailed source notes.

## Current Status Snapshot

- Last reviewed against the repo on 2026-05-01.
- Shared platform, auth, shell, and framework foundations are complete.
- Care Circle is the most complete product surface; family/friend and patient flows are mostly delivered.
- Storytelling has a route boundary, account/commercial shell, and partial community/publishing surfaces (public reading, forums, blog, search), but core story, world, editor, chat, builder, and map workflows are still pending.
- Chatbot backend-backed app is complete with session history, per-turn usage, and restore behavior.
- Legacy admin and blog tooling are partially rebuilt in React (users, billing, CTA, maintenance); low-value pages were explicitly retired.

## Shirt Size Legend

- `XS`: small doc, wiring, or decision task; usually less than half a day.
- `S`: one contained UI/API/test change with low uncertainty.
- `M`: one route or workflow with normal loading, error, empty, and test coverage.
- `L`: multi-component or multi-route workflow, likely touching API contracts and Playwright.
- `XL`: broad product slice with multiple workflows, backend coordination, and higher sequencing risk.

## Active Sprint Order

1. [frontendv1Sprint01PlatformBaseline.md](frontendv1Sprint01PlatformBaseline.md) - completed shared platform baseline
2. [frontendv1Sprint02CareCircleCore.md](frontendv1Sprint02CareCircleCore.md) - completed Care Circle family/friend and patient flows
3. [frontendv1Sprint03CareCirclePolishAndProduction.md](frontendv1Sprint03CareCirclePolishAndProduction.md) - completed Care Circle hardening, event feed, media library, and deployment smoke checklist
4. [frontendv1Sprint04StorytellingBoundary.md](frontendv1Sprint04StorytellingBoundary.md) - completed storytelling app boundary with stories/worlds/community entry routes
5. [frontendv1Sprint05StoryBackbone.md](frontendv1Sprint05StoryBackbone.md) - next major storytelling product sprint
6. [frontendv1Sprint06WorldElements.md](frontendv1Sprint06WorldElements.md) - pending world entities and associations
7. [frontendv1Sprint07EditorsDocuments.md](frontendv1Sprint07EditorsDocuments.md) - pending rich editors, AI review, documents
8. [frontendv1Sprint08StoryChatBuilderSpatial.md](frontendv1Sprint08StoryChatBuilderSpatial.md) - pending story/world chat, builder, hierarchy, map
9. [frontendv1Sprint09PublishingCommunity.md](frontendv1Sprint09PublishingCommunity.md) - completed: public reading, forums, blog, search, forum voting, blog comments, image share, and backend unit tests
10. [frontendv1Sprint10CommercialSupport.md](frontendv1Sprint10CommercialSupport.md) - completed billing/referrals/onboarding/prompts/AI-models/blog
11. [frontendv1Sprint11ChatbotApp.md](frontendv1Sprint11ChatbotApp.md) - completed independent chatbot app with session history and per-turn usage
12. [frontendv1Sprint12AdminAndOps.md](frontendv1Sprint12AdminAndOps.md) - completed: rebuilt 5 admin routes, explicitly retired 6 low-value legacy pages

## Mapping From Older Sprint Files

| New Sprint | Older Source Files |
|---|---|
| `frontendv1Sprint01PlatformBaseline.md` | `frontendSprint01.md`, `frontendSprint02.md`, `frontendSprint03.md`, `frontendSprintCommonPlatform.md` |
| `frontendv1Sprint02CareCircleCore.md` | `frontendSprintCareCircleApp.md`, `frontendSprintCareCircleProviders.md` |
| `frontendv1Sprint03CareCirclePolishAndProduction.md` | `frontendSprintCareCircleApp.md`, `frontendSprintCareCircleArchitectureDocs.md`, deployment docs |
| `frontendv1Sprint04StorytellingBoundary.md` | `frontendSprintStorytellingApp.md` |
| `frontendv1Sprint05StoryBackbone.md` | `frontendSprint04.md` |
| `frontendv1Sprint06WorldElements.md` | `frontendSprint05.md` |
| `frontendv1Sprint07EditorsDocuments.md` | `frontendSprint06.md` |
| `frontendv1Sprint08StoryChatBuilderSpatial.md` | `frontendSprint07.md` |
| `frontendv1Sprint09PublishingCommunity.md` | `frontendSprint08.md` |
| `frontendv1Sprint10CommercialSupport.md` | `frontendSprint09.md` |
| `frontendv1Sprint11ChatbotApp.md` | `frontendSprintChat.md` |
| `frontendv1Sprint12AdminAndOps.md` | `frontendSprint10.md` |

## Working Rules

- Treat this `frontendv1Sprint*.md` series as the active execution order.
- Keep older `frontendSprint*.md` files as implementation history unless they contain details not yet migrated here.
- When work changes user-visible behavior, add or update Playwright coverage in `frontendv1/tests/e2e/`.
- When a sprint task is completed, update its task list and add verification notes before calling the sprint done.
- Task shirt sizes are planning estimates, not commitments; revise them when backend contracts or UI scope become clearer.
