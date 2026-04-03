# Frontend Platform Blueprint

> Purpose: define the recommended frontend architecture for running `storytelling` and `care-circle` as separate applications on one shared React platform.

## 1. Executive Direction

- Keep the current `frontendv1/` React and Next.js platform as the base implementation.
- Treat `storytelling` and `care-circle` as separate applications, not one blended product domain.
- Share platform infrastructure, not business objects or workflow assumptions.
- Split `care-circle` into two application surfaces:
  - `family`
  - `patient`
- Preserve one common brand system while allowing different UX density and interaction models by app surface.

## 2. Why This Direction

- The current repo already has a coherent React platform direction in [reacttools.md](/C:/code2025a/inbkandquill2/reacttools.md), [frontendAll.md](/C:/code2025a/inbkandquill2/frontendAll.md), and the Sprint 1 to 3 framework work.
- The external `C:\code2026\dementia_app` workspace is currently a Kivy and Buildozer mobile project, not a compatible React application base.
- Reusing the current framework avoids rebuilding:
  - auth/session foundations
  - shell and navigation systems
  - API client patterns
  - route guards
  - test harnesses
  - billing and coin infrastructure

## 3. Product Boundary Model

### Shared Platform

Shared platform responsibilities should include:

- authentication and session infrastructure
- registration and invitation entry
- branding and design tokens
- shared shell primitives
- API client and query conventions
- websocket or SSE event transport
- notification infrastructure
- media upload infrastructure
- billing and coins engine
- audit and event logging
- Playwright test patterns

### Separate Applications

Applications should remain separate at the route, domain, and permissions layers:

- `storytelling`
  - creative authoring application
  - user-scoped billing
  - current framework and shell paradigm
- `care-circle`
  - family-scoped care application
  - family-scoped billing
  - split into family and patient surfaces

## 4. Route Strategy

Recommended route spaces:

- `/storytelling/...`
- `/care-circle-family/...`
- `/care-circle-patient/...`

Common platform routes can remain outside app-specific trees:

- `/login`
- `/register`
- `/logout`
- `/invite/...`
- `/access-denied`

### Route Principles

- Use URL and invitation context to determine application entry.
- Do not require a shared app chooser after sign-up for the default flow.
- Give each application its own landing experience after authentication.
- Treat `care-circle-patient` as a direct-entry application surface with its own simplified login flow.

## 5. UX Surface Model

### Storytelling

- Continue using the richer creative and editorial interface direction.
- Remain desktop-capable and content-dense.
- Preserve the current shell and navigation style.

### Care-Circle Family

- Reuse the current shell and navigation paradigm.
- Use the same brand system and general application conventions.
- Support dashboards, patient management, shared media, scheduling, billing, and live event views.

### Care-Circle Patient

- Use a separate, simplified application surface.
- Optimize for low cognitive load and recognition-based interaction.
- Support tablet and TV-style layouts with large targets.
- Avoid dense settings, side navigation, and management controls.
- Constrain the patient experience to a permanent simplified mode.

## 6. Identity And Access Model

Use one identity foundation with specialized access and profile types.

Core concepts:

- `User`
- `AppMembership`
- `Family`
- `FamilyMembership`
- `PatientProfile`
- `PatientUser`

### Identity Rules

- Standard users and family members use the current standard login flow.
- Patient users use a direct URL plus image-based login flow.
- Patient accounts are a specialized kind of user, not a disconnected identity subsystem.
- Normal users should usually belong to one app context, not both.

## 7. Care-Circle Domain Model

Recommended core `care-circle` entities:

- `Family`
- `FamilyMembership`
- `PatientProfile`
- `PatientUser`
- `PatientAccessState`
- `FamilyMediaItem`
- `PatientContentItem`
- `ScheduledContentDelivery`
- `PatientSession`
- `FamilyEvent`
- `FamilyWallet`

### Domain Rules

- One family can have many patients.
- Each patient belongs to exactly one family.
- Each family-side account belongs to one family unit.
- One family can have multiple patient profiles active at the same time.
- Each patient has exactly one patient login identity.
- Patient profiles are archived rather than hard-deleted.
- Archived patients are hidden by default.

## 8. Role Model

### Care-Circle Family Roles

- `owner`
- `member`

### Owner Responsibilities

- manage family members
- create and archive patients
- enable and disable patient access
- reset patient login
- manage shared media and scheduled content
- manage family billing and coins
- transfer ownership

### Governance Rules

- family units may have one or two owners
- owners cannot casually remove another owner
- owner status cannot be casually demoted
- ownership changes should go through an explicit protected workflow

### Patient Constraints

- no profile editing
- no configuration management
- no access to family shell or admin tools
- no transition into the full family UI

## 9. Patient Login Model

Patient login should be treated as a dedicated product capability.

Requirements:

- direct route entry
- image-based login
- system-defined image set
- fixed image positions on the grid
- owner-managed reset flow
- failed logins captured as events
- support for access deactivation without deleting the profile

This model is optimized for consistency and recognition rather than conventional security hardening.

## 10. Content And Media Model

### Family Media

- Family media belongs to the family unit.
- All family images are visible within the family.
- Media can later gain patient-level associations without changing the ownership model.
- Login images remain separate from family-uploaded media.

### Patient Content

Patient-visible content may be:

- family-authored
- system-generated

Behavior rules:

- content can be queued for the patient’s next sign-in
- content can be scheduled using the patient’s timezone
- family users can remove or hide content after publication
- hidden content disappears from normal family-visible history

## 11. Event And Realtime Model

`care-circle-family` requires a real-time event stream.

The event model should include:

- patient login success
- patient login failure
- patient session metadata
- patient actions
- family actions
- content scheduling and delivery
- patient access enabled and disabled
- system-generated events
- device and browser metadata where available

Design rule:

- keep event records separate from content records
- render the family feed from event data, not inferred content state

## 12. Billing And Coin Ownership

The billing engine should stay shared while supporting different ownership scopes.

Recommended ownership scopes:

- `user`
- `family`

Application mapping:

- `storytelling` uses user-level billing and coin ownership
- `care-circle` uses family-level billing and coin ownership

Additional rules:

- patient-side usage may consume family-owned billable capacity
- family-level limits apply across all patients

## 13. Backend Separation

Keep one backend if practical, but separate platform and application domains cleanly.

Suggested backend areas:

- platform auth and sessions
- platform billing and coins
- storytelling domain
- care-circle domain
- realtime and events

Care-circle API areas should be explicit:

- family membership
- patient lifecycle
- patient login and reset
- patient access state
- family media library
- patient content queue
- scheduled delivery
- family event feed
- patient preview and impersonation

## 14. Frontend Folder Direction

Recommended structure inside `frontendv1/`:

```text
app/
  (public)/
  (auth)/
  storytelling/
  care-circle-family/
  care-circle-patient/
components/
  platform/
  storytelling/
  care-circle-family/
  care-circle-patient/
  ui/
lib/
  api/
  auth/
  billing/
  events/
  storytelling/
  care-circle/
```

Principles:

- keep shared UI in `components/ui` and `components/platform`
- keep app-specific components and business logic isolated
- avoid mixing storytelling assumptions into care-circle modules

## 15. Testing Strategy

Treat these as separate browser-test surfaces:

- `storytelling`
- `care-circle-family`
- `care-circle-patient`

Priority Playwright coverage:

- shared registration and login entry behavior
- URL-based app access routing
- family login versus patient login
- patient direct-entry login flow
- owner versus member restrictions
- patient archive and inactive behavior
- live family event feed
- patient preview flow
- family-scoped billing behavior
- scheduled patient content in patient timezone

## 16. Recommended Delivery Sequence

1. Lock the shared platform model and route boundaries.
2. Add app-level access and ownership scope support.
3. Define `care-circle` backend entities and contracts.
4. Add route-tree separation in the React app.
5. Build `care-circle-family` shell and patient-management foundation.
6. Build `care-circle-patient` login and simplified shell.
7. Add event streaming and session metadata.
8. Add content scheduling and content queue behaviors.
9. Add family billing ownership support.
10. Add Playwright coverage by surface.

## 17. Working Conclusions

- The current React and Next.js framework is the correct common base.
- `storytelling` and `care-circle` should share platform services but remain separate product domains.
- `care-circle-family` and `care-circle-patient` should be separate route spaces with separate UI assumptions.
- Billing, roles, events, scheduling, and patient login all need first-class architectural treatment rather than ad hoc page-level handling.
