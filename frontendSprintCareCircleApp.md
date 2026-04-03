# Sprint Care-Circle 01: Family and Patient Foundations

## Goal

Establish `care-circle` as a second application on the shared platform, with separate family and patient route spaces, household ownership, and patient-safe interaction foundations.

## In Scope

- `care-circle-family` route and shell foundation
- `care-circle-patient` route and shell foundation
- family and patient identity model assumptions in the frontend
- patient direct-entry login surface
- family patient-list and patient-state foundation
- family event-feed foundation
- family media-library foundation

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

## Shared Components

- `CareCircleFamilyShell`
- `CareCirclePatientShell`
- `FamilyPatientCard`
- `PatientAccessStateBadge`
- `PatientImageLoginGrid`
- `FamilyEventFeed`
- `FamilyMediaLibraryGrid`

## Backend/API Dependencies

- family membership and family context endpoints
- patient list, create, archive, and access-state endpoints
- patient login and login-reset endpoints
- family media endpoints
- family event-stream endpoint
- family-owned billing and balance endpoints

## UI Behavior Capture Targets

- family landing and patient management flow
- patient direct-entry login behavior
- fixed-position image grid interaction
- patient inactive or archived access states
- live family event feed behavior
- family media library loading and empty states

## Risks and Decisions

- Keep the patient application permanently simplified and separate from family patterns.
- Do not overfit early family pages before the household model and patient auth contract are stable.
- Family media, patient content, events, and access state should be treated as first-class behaviors, not side effects of generic CRUD pages.

## Task List

- [ ] Define `care-circle-family` and `care-circle-patient` as separate top-level route trees.
- [ ] Build the family landing route and shell foundation.
- [ ] Build the patient direct-entry login route with fixed-position image-grid behavior.
- [ ] Build a family patient list route with active, inactive, and archived-state handling.
- [ ] Build a patient detail hub for family-side management actions.
- [ ] Build the first version of the realtime family event feed route.
- [ ] Build the first version of the shared family media library route.
- [ ] Add route-safe handling for patient archive and access deactivation states.
- [ ] Add Playwright coverage for family entry, patient direct login, and patient-state restrictions.
- [ ] Capture patient login, family event feed, and patient-state behavior in `uiBehaviorCapture.md`.
- [ ] Verify family-owned billing and family-context loading assumptions against backend contracts.

## Exit Criteria

- care-circle exists as a distinct application with separate family and patient route spaces
- patient direct-entry login and simplified shell are established
- family-side patient management, event feed, and media foundations are reachable and stable

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| care-circle exists as a distinct application with separate family and patient route spaces | Browser verification and code review confirm independent family and patient route trees with the correct shells | To be recorded during implementation |
| patient direct-entry login and simplified shell are established | Playwright covers patient login route, fixed image-grid interaction, and post-login patient shell rendering | To be recorded during implementation |
| family-side patient management, event feed, and media foundations are reachable and stable | Playwright smoke coverage plus code checks verify patient list, patient detail, event feed, and media routes | To be recorded during implementation |

## Implementation Status

- Planning only.
- This sprint establishes the first executable care-circle foundation and should follow the common platform sprint.
