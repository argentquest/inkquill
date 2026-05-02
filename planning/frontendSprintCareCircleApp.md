# Sprint Care-Circle 01: Family and Patient Foundations

## Goal

Establish `care-circle` as a second application on the shared platform, with separate family and patient route spaces, household ownership, and patient-safe interaction foundations.

## Current Review Status

- Last reviewed against the repo on 2026-04-27.
- Core `care-circle-family` and `care-circle-patient` delivery is in place and most circle-friend workflows are now implemented.
- The family dashboard, patient list/detail, provider management, patient sign-in, patient daily session, billing/referrals/account flows, join-code sharing, invite email, and admin surfaces are delivered.
- `/care-circle-family/events` and `/care-circle-family/media` currently exist as scaffold routes rather than production-complete API-backed experiences.
- The dedicated `/care-circle-patient/session` route is still not a separate delivered surface; the calm session experience currently lives on `/care-circle-patient/home`.

## In Scope

- `care-circle-family` route and shell foundation
- `care-circle-patient` route and shell foundation
- family and patient identity model assumptions in the frontend
- patient direct-entry login surface
- patient calm-content and image-based easy-sign-in foundations
- family patient-list and patient-state foundation
- family event-feed foundation
- family media-library foundation
- patient personalization and scheduled-content preference foundations

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/care-circle-family` | net-new | P0 | Family landing dashboard |
| `/care-circle-family/patients` | net-new | P0 | Patient list and management entry |
| `/care-circle-family/patients/:patientId` | net-new | P0 | Patient detail and management hub |
| `/care-circle-family/media` | net-new | P1 | Shared family media library |
| `/care-circle-family/events` | net-new | P0 | Realtime family event feed |
| `/care-circle-patient` | net-new | P0 | Patient app landing and login entry |
| `/care-circle-patient/login` | net-new | P0 | Direct image-based sign-in flow |
| `/care-circle-patient/home` | net-new | P0 | Simplified patient home after login |
| `/care-circle-patient/session` | net-new | P1 | Calm read-only session surface for daily patient content |

## Shared Components

- `CareCircleFamilyShell`
- `CareCirclePatientShell`
- `FamilyPatientCard`
- `PatientAccessStateBadge`
- `PatientImageLoginGrid`
- `PatientDailyHighlights`
- `PatientPreferenceSummary`
- `FamilyEventFeed`
- `FamilyMediaLibraryGrid`

## Backend/API Dependencies

- family membership and family context endpoints
- patient list, create, archive, and access-state endpoints
- patient login and login-reset endpoints
- patient session bootstrap endpoint with daily-content summary and simplified surface metadata
- patient preference and personalization endpoints
- family media endpoints
- family event-stream endpoint
- family-owned billing and balance endpoints

## UI Behavior Capture Targets

- family landing and patient management flow
- patient direct-entry login behavior
- fixed-position image grid interaction
- family-managed patient personalization and preference capture
- patient calm daily-content session rendering
- patient inactive or archived access states
- live family event feed behavior
- family media library loading and empty states

## Risks and Decisions

- Keep the patient application permanently simplified and separate from family patterns.
- The patient surface should stay calm and read-only by default, with family-side preference management driving what the patient sees.
- Do not overfit early family pages before the household model and patient auth contract are stable.
- Family media, patient content, events, and access state should be treated as first-class behaviors, not side effects of generic CRUD pages.

## Task List

- [x] Define `care-circle-family` and `care-circle-patient` as separate top-level route trees.
- [x] Build the family landing route and shell foundation.
- [x] Build the patient direct-entry login route with fixed-position image-grid behavior.
- [x] Apply family-managed patient profile, patient preference, and image-based easy-sign-in concepts to the care-circle routes.
- [x] Build a family patient list route with active, inactive, and archived-state handling.
- [x] Build a patient detail hub for family-side management actions.
- [x] Build the first patient post-login session surface as a calm daily-highlights view with minimal actions.
- [x] Build the first version of the realtime family event feed route.
- [x] Build the first version of the shared family media library route.
- [x] Add route-safe handling for patient archive and access deactivation states.
- [x] Add Playwright coverage for family entry, patient direct login, patient-state restrictions, and calm daily-session rendering.
- [x] Capture patient login, family event feed, and patient-state behavior in `uiBehaviorCapture.md`.
- [x] Capture family-managed patient preference behavior and patient daily-session behavior in `uiBehaviorCapture.md`.
- [x] Verify family-owned billing and family-context loading assumptions against backend contracts.
- [x] Surface the owner join code on the account page and add owner-sent invite email delivery by recipient email address.

## Exit Criteria

- care-circle exists as a distinct application with separate family and patient route spaces
- patient direct-entry login and simplified shell are established
- patient interaction model supports calm daily-content viewing driven by family-managed preferences
- family-side patient management is reachable and stable, while event-feed and media surfaces remain scaffold foundations

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| care-circle exists as a distinct application with separate family and patient route spaces | Browser verification and code review confirm independent family and patient route trees with the correct shells | `cd frontendv1; npm run build`; `cd frontendv1; npx playwright test tests/e2e/sprint-care-circle-import.spec.ts --reporter=line` |
| patient direct-entry login and simplified shell are established | Playwright covers patient login route, fixed image-grid interaction, and post-login patient shell rendering | `cd frontendv1; npx playwright test tests/e2e/sprint-care-circle-import.spec.ts --reporter=line` |
| patient interaction model supports calm daily-content viewing driven by family-managed preferences | Playwright and code checks confirm family-side profile rendering, image-based sign-in, and simplified patient session rendering | `cd frontendv1; npx playwright test tests/e2e/sprint-care-circle-import.spec.ts --reporter=line` |
| family-side patient management is reachable and stable, while event-feed and media surfaces remain scaffold foundations | Code review plus backend and browser checks confirm family landing, patient list, patient detail, patient auth restrictions, and provider-backed patient sessions; event and media routes currently remain scaffold pages | `cd frontendv1; npm run build`; `cd frontendv1; npm run test:e2e -- tests/e2e/sprint-care-circle-family.spec.ts --reporter=line`; `.\.venv\Scripts\python.exe -m pytest tests\unit\care_circle\test_care_circle_unit.py -q` |
| family owners can share access through visible join-code and invite-email controls | Playwright covers owner account rendering and invite submission, and integration tests confirm owner summary plus invite-email backend behavior | `cd frontendv1; npx playwright test tests/e2e/sprint-care-circle-family.spec.ts --reporter=line`; `.\.venv\Scripts\python.exe -m pytest tests/integration/care_circle/test_family_membership_integration.py -q` |

## Implementation Status

- Reviewed on 2026-04-27: most circle-friend delivery is complete, with event/media still explicitly scaffold-level.
- Care-circle route import work is now active in `frontendv1/`.
- Initial import work now brings `DailyNewsletter` concepts into `frontendv1/` as:
  - family-managed patient profile routes
  - image-based patient sign-in
  - calm patient daily-highlights session
- The import now uses shared backend contracts, database models, seeded DailyNewsletter provider catalog data, and route-level React Query clients instead of local-only UI data.
- Backend domain delivery now includes SQLAlchemy models, Alembic migration `7b8f4c2a1d10`, `care-circle` API routes, and unit coverage for provider, family patient, patient auth, and patient session routes.
- Frontend verification now passes for `npm run build` and the targeted Playwright care-circle spec.
- Owner account delivery now exposes the family join code and a simple invite-email form backed by owner-only Care Circle API endpoints and email delivery templates.
- Additional family-owner surfaces now exist beyond the original minimum sprint scope, including account edit, members, referrals, template studio, scheduler admin, and family admin pages.

## DailyNewsletter Provider Import Scope

The imported `DailyNewsletter` app includes a provider registry that must be carried into the care-circle backend import rather than left behind as mock-only frontend behavior.

Provider groups identified in the source app:

- core daily content: `weather`, `daily_quote`, `daily_affirmation`, `family_greeting`, `world_news`
- memory and comfort: `nostalgia`, `local_history`, `memory_lane_photo`, `nature_scene`, `personal_affirmation`, `activity_suggestion`, `song_of_the_day`, `animal_friend`, `dog_photo`, `cat_fact`
- games and cognition: `puzzle`, `brain_booster`, `riddle`, `missing_vowels`, `finish_phrase`, `odd_one_out`, `word_scramble`, `gridless_crossword`, `crossword`, `word_connect`, `complete_the_duo`, `spot_the_difference`, `bingo`, `simple_math`, `color_match`, `whats_missing`, `ai_trivia`
- wellbeing and lifestyle: `sensory`, `gratitude`, `gentle_exercise`, `simple_recipe`, `daily_blessing`, `hobby_spotlight`, `pen_pal_letter`

Required follow-up backend import tasks:

- [x] import the provider registry and provider configuration shape into this repo's backend
- [x] decide which providers become `care-circle-patient` daily-session cards versus family-only tools
- [x] import provider template or rendering strategy where still relevant
- [x] add backend tests for provider selection, ordering, and patient-safe filtering

## Provider Classification Summary

**Patient-Session Cards** (patient_visible=True): All providers except family-only below are available for patient daily sessions.

**Family-Only Tools** (patient_visible=False):
- `simple_recipe` - Recipe content (may require cooking facilities/abilities)
- `pen_pal_letter` - Letter writing activity
- `world_news` - External news content

**Provider Safety**: All providers in `app/services/care_circle/providers/` inherit from `BaseCareCircleProvider` and implement `is_safe_for_patient = True` by default. The session assembler enforces patient-safe filtering via the `is_safe_for_patient` property check before including providers in patient sessions.

## DailyNewsletter Environment Notes

The source application's `.env` includes sensitive runtime settings for LLM access, database access, SMTP delivery, and provider logging.

Environment migration rules:

- do not copy source `.env` secrets verbatim into this repo
- treat imported API keys, SMTP credentials, and database credentials as secrets to rotate and re-enter safely
- only copy variable names and required configuration categories into this repo's `.env_template` or deployment docs
- map source settings into this repo's existing config system before wiring provider execution

Environment categories found in the source app:

- OpenRouter and OpenAI-compatible LLM configuration
- PostgreSQL connection settings
- SMTP email settings
- provider log output directory
- Cloudflare and pgAdmin support in `.env.example`

