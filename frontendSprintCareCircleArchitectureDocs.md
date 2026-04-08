# Sprint Care-Circle 03: Backend and Frontend Architecture Documentation

## Goal

Bring the CareCircle architecture documentation up to current code truth across both backend and frontend so the docs can be used as implementation guidance without misleading engineers about what is already shipped versus what is still scaffolded or planned.

## Follows

This sprint follows the CareCircle implementation and provider-runtime work documented in:

- `frontendSprintCommonPlatform.md`
- `frontendSprintCareCircleApp.md`
- `frontendSprintCareCircleProviders.md`

Those sprints remain the source of truth for platform, route, and provider runtime delivery. This sprint is specifically for architecture-document accuracy, completeness, and maintenance discipline.

## In Scope

- reviewing `docs/architecture/backend-carecircle.md` against active backend code
- reviewing `docs/architecture/frontend-carecircle.md` against active `frontendv1` CareCircle routes and components
- explicitly marking where docs describe:
  - active implementation
  - partial/scaffolded implementation
  - future or planned architecture
- adding missing source-of-truth references to the actual router, CRUD, service, and frontend API files
- clarifying current CareCircle route coverage
- clarifying current provider/session assembly behavior
- documenting verification expectations for future architecture-doc updates

## Out of Scope

- changing CareCircle feature behavior
- adding new backend endpoints
- adding new frontend routes
- rewriting non-CareCircle architecture docs except where shared context must be referenced
- implementing deferred product features only because they are mentioned in docs

## Source Of Truth

### Backend

- `app/routers/care_circle.py`
- `app/crud/care_circle.py`
- `app/services/care_circle/provider_base.py`
- `app/services/care_circle/session_assembler.py`
- `app/models/care_circle.py`
- `app/schemas/care_circle.py`

### Frontend

- `frontendv1/app/care-circle-family/**`
- `frontendv1/app/care-circle-patient/**`
- `frontendv1/components/care-circle-family/**`
- `frontendv1/components/care-circle-patient/**`
- `frontendv1/lib/api.ts`
- `frontendv1/lib/apps/care-circle-app.ts`

### Documentation Targets

- `docs/architecture/backend-carecircle.md`
- `docs/architecture/frontend-carecircle.md`

## Documentation Problems To Correct

- docs that imply every listed route is fully implemented when some are scaffold routes
- docs that present planned async scheduling/background execution as if already shipped
- docs that omit current response-envelope behavior
- docs that do not identify the concrete files that currently define behavior
- route/component tables that still use `TBD` when there is already a route page in the repo
- provider/session descriptions that do not mention current sequential execution and on-demand regeneration

## Sprint Tasks

### 1. Backend CareCircle architecture audit
Status: `pending`

Implement:
- compare backend CareCircle architecture doc to current router, CRUD, service, model, and schema code
- correct endpoint descriptions where the actual behavior differs
- add a review-status/accuracy section near the top of the file
- note current implementation constraints and future-direction items explicitly

Exit criteria:
- `docs/architecture/backend-carecircle.md` does not claim unimplemented backend behavior as current behavior
- source-of-truth backend files are named in the doc
- current session assembly behavior is documented accurately

Verification:
- manual file-to-file comparison against active backend sources

### 2. Frontend CareCircle architecture audit
Status: `pending`

Implement:
- compare frontend CareCircle architecture doc to current `frontendv1` routes, components, and API client
- replace stale `TBD` route descriptions when a route/page already exists
- mark scaffold routes clearly where feature depth is still limited
- add a review-status/accuracy section near the top of the file

Exit criteria:
- `docs/architecture/frontend-carecircle.md` reflects the actual route tree present in `frontendv1`
- current component/API ownership is documented accurately
- scaffold versus complete surfaces are explicitly distinguished

Verification:
- manual comparison against `frontendv1/app/care-circle-family/**`, `frontendv1/app/care-circle-patient/**`, and `frontendv1/lib/api.ts`

### 3. Backend/frontend contract clarification
Status: `pending`

Implement:
- add explicit notes about backend response envelopes where relevant
- document that current frontend API calls are centralized in `frontendv1/lib/api.ts`
- document how patient session refresh currently works end-to-end

Exit criteria:
- a reader can trace CareCircle data flow from frontend route to backend route without guessing
- doc language distinguishes between architectural intent and current contract

Verification:
- read-through of both docs from route table to API section to ensure consistent terminology

### 4. Maintenance guidance for future doc edits
Status: `pending`

Implement:
- add a short accuracy-maintenance section or notes in the docs describing how to keep them current
- define that router/service/component files remain the source of truth over speculative doc language

Exit criteria:
- future contributors can tell how to update the docs safely when CareCircle contracts change

Verification:
- docs contain explicit source-of-truth references and implementation-status language

## Deliverables

- updated `docs/architecture/backend-carecircle.md`
- updated `docs/architecture/frontend-carecircle.md`
- clear implementation-status notes inside both docs

## Exit Criteria

- backend and frontend CareCircle architecture docs are reviewed against current code
- obvious inaccuracies are corrected
- partial/scaffolded routes are labeled as such
- current provider/session assembly behavior is described accurately
- docs include concrete source-of-truth file references
- task response includes verification notes describing what was checked

## Verification Notes Template

Use this when closing the sprint:

- `backend-carecircle.md`: reviewed against `app/routers/care_circle.py`, `app/crud/care_circle.py`, `app/services/care_circle/provider_base.py`, `app/services/care_circle/session_assembler.py`
- `frontend-carecircle.md`: reviewed against `frontendv1/app/care-circle-family/**`, `frontendv1/app/care-circle-patient/**`, `frontendv1/components/care-circle-family/**`, `frontendv1/components/care-circle-patient/**`, `frontendv1/lib/api.ts`
- confirmed whether each described route is implemented, scaffolded, or planned
- confirmed whether provider/session assembly notes match current code behavior

## Risks

- architecture docs can drift back into roadmap language unless implementation status is called out explicitly
- CareCircle docs can become misleading if frontend scaffold routes are documented as production-complete experiences
- backend docs can overstate scheduling/assembly maturity if future-direction notes are not kept separate from current behavior

## Suggested Follow-Up

- apply the same review-status pattern to the other architecture docs in `docs/architecture`
- add a lightweight documentation review step to future CareCircle sprints whenever routes or API contracts change
