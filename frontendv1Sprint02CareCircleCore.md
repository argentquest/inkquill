# Frontend V1 Sprint 02: Care Circle Core

## Status

Completed.

## Goal

Capture the delivered Care Circle family/friend and patient experience as the first substantially complete product surface in `frontendv1/`.

## Delivered Scope

- `/care-circle-family` family landing dashboard
- `/care-circle-family/patients` friend list
- `/care-circle-family/patients/new` friend creation
- `/care-circle-family/patients/:patientId` friend detail, edit, provider preview, and management hub
- `/care-circle-family/providers` provider catalog
- `/care-circle-family/providers/:providerKey` provider detail and patient-level configuration
- `/care-circle-family/account`, account edit, join code, and invite email
- `/care-circle-family/billing` and `/care-circle-family/referrals`
- `/care-circle-family/members`
- `/care-circle-family/admin`, template studio, scheduler admin, and family admin surfaces
- `/care-circle-patient/login` image-based friend sign-in
- `/care-circle-patient/home` calm patient daily session backed by provider session data
- backend provider runtime, provider registry, patient-safe filtering, and session assembly integration

## Scaffold Or Remaining Scope

- `/care-circle-family/events` is now API-backed by a read-only family activity feed.
- `/care-circle-family/media` exists but upload and API-backed media workflows are not complete.
- A dedicated `/care-circle-patient/session` route is still planned; the current session surface is `/care-circle-patient/home`.
- Production verification and deployment hardening belong in `frontendv1Sprint03CareCirclePolishAndProduction.md`.

## Source Files

- `frontendSprintCareCircleApp.md`
- `frontendSprintCareCircleProviders.md`
- `frontendv1/app/care-circle-family/**`
- `frontendv1/app/care-circle-patient/**`
- `frontendv1/components/care-circle-family/**`
- `frontendv1/components/care-circle-patient/**`
- `frontendv1/tests/e2e/sprint-care-circle-family.spec.ts`
- `frontendv1/tests/e2e/sprint-care-circle-patient.spec.ts`
- `frontendv1/tests/e2e/sprint-care-circle-import.spec.ts`

## Task List

- [x] `[Size: L]` Deliver separate family and patient route trees.
- [x] `[Size: XL]` Deliver friend list, create, detail, edit, and access-state handling.
- [x] `[Size: M]` Deliver image-based friend sign-in.
- [x] `[Size: L]` Deliver patient daily highlights/session route.
- [x] `[Size: L]` Deliver provider catalog and provider detail routes.
- [x] `[Size: L]` Deliver patient-provider configuration flows.
- [x] `[Size: M]` Deliver account, join-code, and invite-email controls.
- [x] `[Size: XL]` Deliver family billing/referrals/member/admin foundations.
- [x] `[Size: L]` Add frontend unit/component coverage for Care Circle family and patient components where practical.
- [x] `[Size: L]` Add backend unit tests for Care Circle CRUD, provider filtering, patient auth, session assembly, invite, and membership behavior.
- [x] `[Size: L]` Add backend integration tests for family, patient, provider, membership, and invite API flows used by the frontend.
- [x] `[Size: L]` Add Playwright coverage for core family and patient flows.
- [x] `[Size: M]` Replace static event feed with API-backed activity data.
- [x] `[Size: L]` Replace media scaffold with real upload, list, and provider-consumption flows.
- [x] `[Size: S]` Add backend unit coverage for the family activity-feed API endpoint.
- [x] `[Size: M]` Add integration coverage for the family activity-feed API contract.
- [x] `[Size: S]` Add Playwright coverage for the API-backed family activity-feed route.
- [x] `[Size: M]` Add unit tests for media UI state handling when the media scaffold becomes a real workflow.
- [x] `[Size: L]` Add integration tests for media API contracts when the media route is implemented.
- [x] `[Size: XS]` Decide whether to add or retire the separate `/care-circle-patient/session` route.

## Verification Notes

- Current task status was reviewed against `frontendv1/app/care-circle-family/**`, `frontendv1/app/care-circle-patient/**`, and care-circle Playwright specs on 2026-04-27.
- Family activity-feed implementation added `GET /api/v1/care-circle/family/events`, `fetchCareCircleActivityEvents()`, and an API-backed `/care-circle-family/events` route.
- Care Circle media library implementation now uses the existing authenticated local-storage media endpoints at `/api/blog/media/list`, `/api/blog/media/upload`, and `DELETE /api/blog/media/{file_path}` to back `/care-circle-family/media`.
- Playwright coverage now verifies the API-backed media library route renders seeded uploads and supports upload/delete UI behavior through mocked media API responses on 2026-04-28.
- Backend unit tests added in `tests/unit/blog/test_blog_media_unit.py` covering `get_file_type`, `generate_filename`, upload size enforcement (413), delete user-scoping (403/404), and list user-scoping (empty + exclusion of other-user files). All 13 tests pass.
- Backend integration tests added in `tests/integration/care_circle/test_care_circle_media_integration.py` covering auth enforcement (401), upload/list/delete lifecycle, aspect-ratio crop URLs, cross-user list isolation, and cross-user delete protection (403).
- Playwright UI state tests added to `sprint-care-circle-family.spec.ts` for the media empty state ("No media uploaded yet") and error state ("Media library unavailable" with "Reload library" retry button).
- `/care-circle-patient/session` route decision: **retired**. The daily patient session experience is fully delivered at `/care-circle-patient/home` backed by the `/api/v1/care-circle/patient/session/:id` API endpoint. No separate `/care-circle-patient/session` page route is needed or planned.
