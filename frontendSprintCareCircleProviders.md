# Sprint Care-Circle 02: DailyNewsletter Provider Runtime Import

## Goal

Import the real `DailyNewsletter` provider runtime into `care-circle` without breaking the shared `inbkandquill2` architecture, and deliver provider-backed patient sessions plus family-side provider management on top of the existing care-circle family/patient split.

## Follows

This sprint follows the completed foundation work in:

- `frontendSprintCommonPlatform.md`
- `frontendSprintCareCircleApp.md`

Those files remain the source of truth for the common platform and the family/patient surface split. This sprint is specifically for provider execution, provider-safe backend contracts, and patient-session content assembly.

## In Scope

- importing `DailyNewsletter` provider runtime patterns into shared backend services
- defining provider execution boundaries inside `care-circle`
- patient-safe filtering of imported providers
- provider-backed daily patient session assembly
- family-side provider visibility and enablement controls
- provider logging, scheduling hooks, and environment normalization
- backend and browser verification for provider-backed patient sessions

## Source Inventory

External provider inventory from `C:\code2026\DailyNewsletter\backend\content_providers`:

- core: `weather`, `daily_quote`, `daily_affirmation`, `family_greeting`, `world_news`
- memory and comfort: `nostalgia`, `local_history`, `memory_lane_photo`, `nature_scene`, `personal_affirmation`, `activity_suggestion`, `song_of_the_day`, `animal_friend`, `dog_photo`, `cat_fact`
- games and cognition: `puzzle`, `brain_booster`, `riddle`, `missing_vowels`, `finish_phrase`, `odd_one_out`, `word_scramble`, `gridless_crossword`, `crossword`, `word_connect`, `complete_the_duo`, `spot_the_difference`, `bingo`, `simple_math`, `color_match`, `whats_missing`, `ai_trivia`
- wellbeing and lifestyle: `sensory`, `gratitude`, `gentle_exercise`, `simple_recipe`, `daily_blessing`, `hobby_spotlight`, `pen_pal_letter`

Source configuration also introduces:

- provider ordering and enablement
- print-priority metadata and required-for-print flags
- theme selection
- assembly defaults for linear and grid layouts

## Provider Migration Strategy

- Keep provider runtime in the shared backend, not inside React.
- Treat providers as `care-circle` domain services, not as route-specific scripts.
- Separate provider catalog metadata from provider execution logic.
- Split providers into three operating classes:
  - patient-session providers: safe for direct patient display
  - family-only providers: visible to family management but not patient sessions
  - deferred providers: not imported until dependencies or UX rules are stable
- Preserve the patient surface as calm and read-only even when provider output becomes dynamic.
- Preserve the family surface as the place where provider enablement, scheduling, and personalization are managed.

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/care-circle-family` | current route | P1 | add provider-health and enablement summary |
| `/care-circle-family/patients/:patientId` | current route | P0 | show provider-backed patient session preview and provider assignments |
| `/care-circle-family/providers` | net-new | P0 | family-side provider registry, enablement, and patient visibility controls |
| `/care-circle-family/providers/:providerKey` | net-new | P1 | provider detail, diagnostics, and content-policy notes |
| `/care-circle-patient/home` | current route | P0 | replace seeded highlights with provider-backed session assembly |
| `/care-circle-patient/session` | deferred/current concept | P1 | optional focused patient session route for provider-driven content blocks |

## Shared Components

- `CareCircleProviderStatusGrid`
- `CareCircleProviderToggleTable`
- `CareCircleProviderDetailPanel`
- `CareCirclePatientSessionCard`
- `CareCircleStandardTextWidget`
- `CareCircleMediaWidget`
- `CareCircleCognitiveGameWidget`
- `CareCirclePatientSessionComposerPreview`
- `CareCircleProviderExecutionBadge`
- `CareCircleProviderFailureState`

## Backend/API Dependencies

- provider catalog read/update endpoints
- provider execution service and provider registry loader
- patient-session assembly endpoint backed by real provider output
- provider-safe filtering rules for patient versus family visibility
- provider diagnostics/logging contract
- define async job scheduler strategy (e.g., Celery or FastAPI Background Tasks) for executing heavy LLM provider queries off-hours.
- normalized config/env contract for imported provider services
- SQLAlchemy models and Alembic migrations for provider logs, configuration settings, and execution history

## Execution Phases

1. Provider classification
- classify each external provider as patient-safe, family-only, or deferred
- define dependency risks for LLM, SMTP, external HTTP, image generation, and print-only logic

2. Backend runtime import
- import shared provider base/runtime helpers from `DailyNewsletter` into `app/services/care_circle/`
- normalize config loading to this repo's settings system
- implement provider registry loading from DB-backed catalog rows

3. Session assembly
- replace seeded patient highlights with provider-backed assembly for active patients
- keep deterministic fallback behavior when provider execution fails
- record provider execution results in logs or stored generation records as needed

4. Family controls
- expose family-side provider visibility, enablement, and preview controls
- keep dangerous or noisy provider types out of patient-facing routes by contract, not by frontend convention

5. Verification
- add backend unit coverage for provider registry loading, filtering, ordering, and fallback handling
- add integration coverage for provider-backed patient session assembly
- add Playwright coverage for family provider management and patient provider-backed session rendering

## Risks and Decisions

- Do not import print-assembly assumptions directly into the patient React surface.
- Do not allow external-provider runtime complexity to leak into route handlers; keep it in backend services.
- LLM-backed providers must degrade safely when keys, quotas, or upstream services fail.
- Patient-safe filtering must be enforced in backend contracts, not inferred in the UI.
- Providers that depend on rich media generation or heavy external APIs may need a deferred phase rather than immediate migration.
- Secret-bearing `.env` values from `DailyNewsletter` must be remapped, rotated, and normalized before any production-like execution is enabled.

## Task List

- [ ] classify every imported `DailyNewsletter` provider into patient-safe, family-only, or deferred
- [ ] create a shared `care-circle` provider runtime package in the backend
- [ ] import provider base/helpers from the source repo where still structurally useful
- [ ] normalize provider config loading into `app.core.config` and `.env_template`
- [ ] add DB-backed provider enablement and patient-visibility update flows
- [ ] build a real provider-backed patient-session assembly service
- [ ] replace seeded patient session highlights with provider-backed content for active patients
- [ ] add family-side provider registry and provider-detail routes in `frontendv1/`
- [ ] expose provider preview or diagnostics on the family patient-detail route
- [ ] add backend unit tests for provider registry loading, filtering, and failure fallback
- [ ] add backend integration tests for provider-backed session generation
- [ ] add Playwright coverage for family provider controls and provider-backed patient sessions
- [ ] capture provider-management and patient-session runtime behavior in `uiBehaviorCapture.md`
- [ ] verify imported provider env/config mapping before enabling any real external execution path
- [ ] migrate and sanitize OpenRouter/OpenAI LLM keys from DailyNewsletter into inbkandquill2 vault/env without committing secrets
- [ ] abstract or disable legacy SMTP/Mail parameters that powered the old email newsletter
- [ ] create SQLAlchemy models and Alembic migrations for provider logs, configuration settings, and execution history
- [ ] define async job scheduler strategy (e.g., Celery / FastAPI Background Tasks) for executing heavy LLM provider queries off-hours

## Exit Criteria

- provider execution lives in shared backend services rather than frontend mocks or route-local scripts
- patient sessions are assembled from real provider runtime output with safe fallback behavior
- family routes can manage provider visibility and enablement without exposing unsafe controls to patients
- provider filtering, ordering, and fallback logic are covered by backend tests
- provider-backed family and patient flows are covered by Playwright

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| provider execution lives in shared backend services rather than frontend mocks or route-local scripts | Code review confirms imported provider runtime is centralized under backend `care-circle` services and wired through API routes | To be filled during implementation |
| patient sessions are assembled from real provider runtime output with safe fallback behavior | Backend tests and browser checks confirm patient sessions render provider-backed content and degrade safely on failures | To be filled during implementation |
| family routes can manage provider visibility and enablement without exposing unsafe controls to patients | Browser verification confirms family provider controls exist and patient routes remain simplified/read-only | To be filled during implementation |
| provider filtering, ordering, and fallback logic are covered by backend tests | Unit and integration suites pass for provider registry loading, safe filtering, and assembly behavior | To be filled during implementation |
| provider-backed family and patient flows are covered by Playwright | Targeted care-circle provider browser suite passes locally | To be filled during implementation |

## Implementation Status

- This sprint document is created before provider-runtime code migration starts.
- `care-circle` foundation work is already complete enough to support this sprint:
  - shared platform routing and membership guards are in place
  - family and patient surfaces already exist in `frontendv1/`
  - live database tables and provider catalog rows already exist
  - the current patient session still uses seeded content and must be replaced during this sprint
- No provider-runtime code migration is marked complete in this sprint yet.
