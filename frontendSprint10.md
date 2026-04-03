# Sprint 10: Admin Completion and Low-Priority Legacy

## Goal

Finish true admin and utility surfaces after the core user product and shared platform are already working.

## In Scope

- admin users
- admin billing
- CTA management
- maintenance admin
- news manager
- image jobs
- user email
- help editor
- low-priority diagnostics and utilities

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/admin/users` | admin pages | P2 | Users and impersonation |
| `/app/admin/billing` | admin billing pages | P2 | Billing admin |
| `/app/admin/cta` | admin CTA pages | P3 | CTA management |
| `/app/admin/maintenance` | maintenance admin pages | P3 | Toggle and status |
| `/app/admin/news` | news pages | P3 | CRUD |
| `/app/admin/image-jobs` | `pages/admin_image_jobs.html` | P3 | Job monitoring |
| `/app/admin/user-email` | `pages/admin_user_email.html` | P3 | Email utility |
| `/app/admin/help` | help editor pages | P3 | Help content admin |
| `/app/admin/analytics-test` | `pages/analytics_test.html` | P3 | Review before rebuilding |
| `/app/admin/interview-trigger` | `pages/interview_trigger.html` | P3 | Review before rebuilding |

## Shared Components

- `AdminDataTable`
- `AdminActionToolbar`
- `CtaEditorPanel`
- `NewsEditor`
- `UserImpersonationControl`
- `AlertBanner`
- `ConfirmationModal`

## Backend/API Dependencies

- admin user endpoints
- admin billing endpoints
- CTA endpoints
- maintenance endpoints
- news endpoints
- admin image job endpoints
- help content endpoints

## UI Behavior Capture Targets

- impersonation flow
- maintenance enable/disable flow
- CTA create/edit/preview behavior
- admin job retry/debug behavior

## Risks and Decisions

- Some admin utilities may not be worth rebuilding if operational usage is low.
- Diagnostics pages should be reviewed before spending real UI time on them.

## Task List

- [ ] Build admin users route.
- [ ] Build admin billing route.
- [ ] Build CTA management route.
- [ ] Build maintenance admin route.
- [ ] Build news manager route.
- [ ] Build admin image jobs route.
- [ ] Build admin user email route.
- [ ] Build help editor route.
- [ ] Review analytics-test and interview-trigger pages for keep/remove decision.
- [ ] Capture impersonation, maintenance, CTA, and admin-job behaviors in `uiBehaviorCapture.md`.
- [ ] Explicitly retire low-value legacy pages that should not move to React.

## Exit Criteria

- required admin flows are available in React
- low-value legacy pages are either rebuilt intentionally or explicitly retired
