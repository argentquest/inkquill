# UI Behavior Capture Worksheet

> Purpose: capture how legacy UI elements actually behave before the React rebuild.
>
> Why this matters:
> - Templates and JS files show structure, but not always the intended interaction model.
> - Some of the legacy UX value is in timing, transitions, disabled states, autosave behavior, polling, and contextual feedback.
> - This worksheet lets product and engineering record those behaviors so the React rebuild preserves function instead of only layout.

How to use:
1. Pick a page or flow from `frontendRouteBacklog.md`.
2. Record each important interactive element.
3. Describe current behavior as observed in the legacy app.
4. Decide whether React should preserve, improve, simplify, or remove it.
5. Link API dependencies and edge cases.

Recommended priority:
- capture `P0` and `P1` pages first
- focus on elements with async behavior, background jobs, streaming, autosave, and multi-step state

---

## Behavior Record Template

Copy this block for each important UI element:

```md
### Page
- Route:
- Screen name:

### Element
- Element name:
- Element type: button / form / modal / editor / nav / table / badge / chat / other
- Legacy location: template, partial, JS file if known

### Purpose
- What job does this element do for the user?
- What user decision or action does it support?

### Trigger
- How does it open/run/change?
- Is it automatic, manual, route-driven, or state-driven?

### Inputs
- What data does it need?
- What route params, page state, user state, or API payload feed it?

### States
- Default state:
- Loading state:
- Empty state:
- Success state:
- Error state:
- Disabled state:

### Behavior Details
- What happens immediately when the user interacts?
- What happens after the backend responds?
- Does it poll, stream, debounce, autosave, or retry?
- Does it change other parts of the page?

### Validation And Guardrails
- Required fields:
- Invalid cases:
- Permission or ownership rules:
- Destructive action confirmation:

### Accessibility And Input
- Keyboard behavior:
- Focus behavior:
- Screen-reader concerns:
- Mobile behavior:

### API And Data
- API endpoints involved:
- Background jobs or websockets involved:
- Data written:
- Data read/refreshed afterward:

### React Rebuild Decision
- Keep / Improve / Simplify / Remove:
- React notes:
- Open questions:
```

---

## Quick Capture Table

Use this for fast discovery passes before writing full detail.

| Page | Element | What it does | Trigger | Loading/Async behavior | Error behavior | APIs | Keep/Improve/Remove | Notes |
|---|---|---|---|---|---|---|---|---|
| Example: `/app/stories/:storyId` | Publish button | Publishes story to public reader | click | shows pending state until publish completes | inline alert | story publish | Keep | confirm exact success UX |
| `/app/account/edit` | Profile settings form | Updates username, email, and display name for the authenticated shell | submit | disables save during mutation and preserves session-backed values on success | toast error plus field validation | `/api/v1/users/me` | Keep | reset action uses confirmation modal before discarding draft |
| `/app/billing` | Billing dashboard route | Loads balance, transactions, and package options into one framework route | route load | query-based loading state and table/package panels | route-level retry state | `/api/v1/billing/dashboard` | Keep | establishes commercial-route baseline for later work |
| `/app/referrals` | Referral stats and history views | Shows referral performance and rewards inside the app shell | route load | parallel queries for stats, history, and rewards | route-level retry state | `/api/v1/referrals/stats`, `/api/v1/referrals/history`, `/api/v1/referrals/rewards` | Keep | side panel summarizes conversion and platform mix |
| `/app/onboarding` | Onboarding preview route | Reads onboarding status and interview metadata without rebuilding the full wizard yet | route load | query-based question preview and status cards | route-level retry state | `/api/v1/interview/questions/new_user_onboarding`, `/api/v1/interview/status/new_user_onboarding`, `/api/v1/interview/user-insights` | Simplify | keep route intentionally light until later onboarding UX needs more depth |
| `/help`, `/about`, `/privacy`, `/terms` | Public content shell pages | Proves shared public framework for support/legal content | route load | static shell render | standard app/global error only | none for Sprint 3 | Keep | content can deepen later without changing shell structure |

---

## High-Priority Elements To Capture First

### Global Shell

- top navigation
- coin balance badge refresh
- user account dropdown
- maintenance banner
- help button and help panel
- notification/toast behavior

### Auth

- login form
- register form
- forgot/reset password forms
- Google sign-in button

### Worlds and Stories

- world create/edit form
- story create/edit form
- story outline tree
- story publish controls
- story generation modal

### Editors

- act editor autosave
- scene editor autosave
- AI model selector
- prompt picker
- review highlights and accept/reject actions

### Documents and Media

- document upload area
- document processing state row
- blog media upload and picker
- image generation modal
- image job monitor

### Chat

- world chat send flow
- story chat send flow
- session switching
- streaming message behavior
- context/source sidebar

### Community

- forum thread creation/reply
- blog post editor
- blog comments and moderation actions
- social sharing bar

### Admin

- admin user impersonation
- billing credit adjustments
- CTA editor preview/apply
- maintenance enable/disable flow

---

## Filled Examples

### Example 1
- Route: `/app/worlds/new`
- Screen name: Create World

- Element name: World save button
- Element type: form action
- Legacy location: `world_form.html`, `world_form_handler.js`

- What job does this element do for the user?
- Creates or updates a world and moves the user into the world workflow.

- Trigger:
- Manual click after form completion.

- Inputs:
- title, description, metadata, possibly image-related fields.

- States:
- Default state: enabled when form is valid.
- Loading state: disabled button with saving indicator.
- Success state: success message and redirect to world detail.
- Error state: inline error banner and field errors.

- Behavior details:
- Sends create/update request.
- On success, refreshes local page state or redirects.
- Should prevent duplicate submissions.

- APIs:
- world create/update endpoints.

- React rebuild decision:
- Keep
- React notes: use optimistic disabled state but do not optimistic-create the record.

### Example 2
- Route: `/app/stories/:storyId`
- Screen name: Story Detail

- Element name: Story generation modal
- Element type: modal
- Legacy location: `_story_generation_modal.html`, `story_generation_modal.js`

- What job does this element do for the user?
- Guides AI-assisted story setup or generation inside the story creation flow.

- Trigger:
- Opened from story creation/wizard CTA.

- Inputs:
- world selection, concept, tone, genre, prompt selections.

- States:
- Default state: multi-step form.
- Loading state: generation request pending.
- Success state: generated outline/recommendation shown for review.
- Error state: inline modal error without losing entered values.

- Behavior details:
- Multi-step interaction.
- Likely blocks duplicate submission while generation is in progress.
- Result may populate story fields or create downstream objects.

- APIs:
- story generation endpoints.

- React rebuild decision:
- Keep
- React notes: should be its own state machine, not ad hoc component state.

### Example 3
- Route: `/app/acts/:actId`
- Screen name: Act Editor

- Element name: Autosave indicator
- Element type: editor status control
- Legacy location: `act_save_handler.js`, `act_editor_main.js`

- What job does this element do for the user?
- Tells the user whether current act content is dirty, saving, saved, or failed.

- Trigger:
- State-driven after editor changes.

- Inputs:
- editor dirty state, debounce timer, save request status.

- States:
- Default state: saved/clean.
- Loading state: saving.
- Success state: saved with timestamp.
- Error state: failed save with retry path.

- Behavior details:
- Save is debounced.
- Should not interrupt typing.
- Must survive rapid edits and out-of-order responses.

- APIs:
- act update endpoint.

- React rebuild decision:
- Keep
- React notes: centralize with editor state hook; do not bury inside the editor component.

### Example 4
- Route: `/app/worlds/:worldId/chat`
- Screen name: World Chat

- Element name: Message send composer
- Element type: chat input
- Legacy location: `world_chat_main.js`, `world_chat_message_handler.js`

- What job does this element do for the user?
- Sends a user message and starts streamed assistant output.

- Trigger:
- send button or enter key.

- Inputs:
- message text, session id, selected context or world scope.

- States:
- Default state: ready.
- Loading state: send disabled, streaming reply visible.
- Error state: send failure and retry guidance.

- Behavior details:
- Sends message request or websocket event.
- Opens/uses active session.
- Streaming content appears progressively.
- May refresh message list and source/context panel after completion.

- APIs:
- world chat endpoints, websocket ticket endpoint.

- React rebuild decision:
- Keep
- React notes: separate transport state from rendered transcript state.

### Example 5
- Route: `/app/documents`
- Screen name: Document Manager

- Element name: Upload dropzone
- Element type: file upload
- Legacy location: `document_manager.html`, `document_upload.js`

- What job does this element do for the user?
- Uploads source documents and exposes processing status.

- Trigger:
- drag-and-drop or file picker.

- Inputs:
- file(s), world/story/document association context if any.

- States:
- Default state: idle.
- Loading state: upload progress and processing state.
- Success state: file listed in table with processed/ready status.
- Error state: row-level or global upload error.

- Behavior details:
- Upload may be immediate.
- Processing can continue after upload succeeds.
- UI should refresh row status until complete.

- APIs:
- document upload/list/delete/download endpoints.

- React rebuild decision:
- Keep
- React notes: model upload and processing as separate states.

---

## Recommended Capture Order By Sprint

1. Sprint 1-2:
   top nav, account dropdown, theme toggle, auth forms, maintenance banner
2. Sprint 3-5:
   world form, story form, story detail tree, association modals, entity detail actions
3. Sprint 6:
   act editor, scene editor, story generation modal, prompt picker, document upload
4. Sprint 7:
   world chat, story chat, world builder, hierarchy, map behavior
5. Sprint 8-10:
   published story reader, forum/blog interactions, billing/referrals, admin tools
