# Frontend V1 Sprint 03: Care Circle Polish And Production

## Status

Completed.

## Goal

Finish the remaining Care Circle product gaps and make the deployed production surface easier to operate.

## In Scope

- API-backed family event feed
- family media upload and library workflows
- production route verification for family, patient, admin, scheduler, provider, and account flows
- deployment smoke checklist for the Ubuntu/Docker host path
- clearer user-facing empty/error/loading states where Care Circle still has scaffold UI
- production-safe help text and support surfaces

## Route Backlog

| React Route | Status | Notes |
|---|---|---|
| `/care-circle-family/events` | implemented | API-backed activity feed with loading, empty, and error states |
| `/care-circle-family/media` | implemented | Upload, list, empty, error, and deletion workflow backed by `/api/blog/media/*` |
| `/care-circle-patient/home` | implemented | Validate production data, provider fallback states, and PDF/newsletter cache expectations |
| `/care-circle-family/admin/scheduler` | implemented | Verify production controls, auth denial, and logs/errors |
| `/care-circle-family/admin/template-studio` | implemented | Verify template read/write flow and file permissions on production host |

## Task List

- [x] `[Size: S]` Define backend contract for family activity/events if current APIs are insufficient.
- [x] `[Size: M]` Build API-backed event feed with loading, empty, and error states.
- [x] `[Size: M]` Define backend contract for media upload/list/delete if current APIs are insufficient.
- [x] `[Size: L]` Build family media upload and library management.
- [x] `[Size: M]` Add unit/component tests for media UI loading, empty, error, and action states.
- [x] `[Size: M]` Add backend unit tests for event/activity service logic introduced by this sprint.
- [x] `[Size: L]` Add backend unit tests for media service logic introduced by this sprint.
- [x] `[Size: M]` Add backend integration tests for event-feed API paths.
- [x] `[Size: L]` Add backend integration tests for media upload/list/delete API paths.
- [x] `[Size: S]` Add or update Playwright coverage for event feed behavior.
- [x] `[Size: M]` Add or update Playwright coverage for media library behavior.
- [x] `[Size: S]` Add production smoke-test checklist for family, patient, scheduler, provider, cache, PDF, and email flows.
- [x] `[Size: XS]` Update Care Circle production docs with any final frontend verification commands.

## Exit Criteria

- Event feed is no longer hardcoded.
- Media library is a real workflow, not a placeholder.
- Production deployment has a documented browser smoke checklist.
- Care Circle can be verified end to end on the Ubuntu single-host deployment.

## Verification Notes

- Media tasks marked complete reflect work delivered during Sprint 02: `/care-circle-family/media` backed by `/api/blog/media/list|upload|DELETE`, 13 backend unit tests in `tests/unit/blog/test_blog_media_unit.py`, care-circle integration tests in `tests/integration/care_circle/test_care_circle_media_integration.py`, and Playwright media empty/error state tests in `frontendv1/tests/e2e/sprint-care-circle-family.spec.ts`.
- Route backlog updated: `/care-circle-family/events` and `/care-circle-family/media` both changed from scaffold to implemented.
- Production browser smoke checklist and frontend verification commands added to `docs/care_circle_single_host_production.md` under "## Frontend Browser Smoke Checklist" and "## Frontend Verification Commands".
