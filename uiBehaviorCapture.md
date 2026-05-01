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
| `/storytelling`, `/care-circle-family`, `/care-circle-patient` | Platform route landing | Resolves the active app surface, owner scope, and realtime banner inside the shared shell | route load | session bootstrap gates protected surfaces and realtime status toggles on browser online/offline events | protected surfaces redirect to login; forced membership denial redirects to `/access-denied` | `/api/v1/users/me` | Keep | this is the common platform baseline for app-specific shells |
| `/access-denied` | Membership failure state | Gives an explicit failure route when app membership or invitation routing blocks a surface | redirect from guard | redirect-only entry after guard evaluation | user sees explicit denial copy instead of landing in the wrong app | none directly; fed by guard redirect state | Keep | preserve query-driven surface context for debugging and support |
| legacy `/app/*` routes | Platform route bridge | Moves legacy shared-shell routes into the new app-specific spaces | route load | immediate client redirect into the resolved app surface | loading state shown until redirect completes | none directly; mapping is local route policy | Keep | migration behavior needs route-by-route verification as legacy pages are retired |
| `/app/account` → `/storytelling/account` | Storytelling account bridge | `PlatformRouteBridge` maps the legacy `/app/account` path into the storytelling-scoped account route; the user lands at `/storytelling/account` without changing the URL pattern they bookmarked | route load | immediate client redirect; no async fetch before redirect | redirect completes before any content is painted | none — client-only route map | Keep | bridge covers account, billing, referrals, and onboarding; each maps one-to-one to the storytelling equivalent |
| `/storytelling/stories` | Stories list entry | Loads the authenticated user's story list from `/api/v1/stories/` and renders them as cards | route load | spinner shown while query runs; cards appear on success | error state shown with "Reload stories" retry; empty state shown when list is empty | `GET /api/v1/stories/` | Keep | entry point only; deep authoring routes live in later sprints |
| `/storytelling/worlds` | Worlds list entry | Loads the authenticated user's worlds from `/api/v1/worlds/` and renders them as cards | route load | spinner shown while query runs; cards appear on success | error state shown with "Reload worlds" retry; empty state shown when list is empty | `GET /api/v1/worlds/` | Keep | entry point only; world builder and editor routes live in later sprints |
| `/storytelling/community` | Community placeholder | Reserved route for story discovery and writer profiles; currently renders a static placeholder with a "coming soon" message | route load | static render — no async fetch | none | none | Keep — expand later | intentionally lightweight; content will deepen once community product decisions are made |
| `/public/published-stories` | Published stories list | Public listing of all published stories sorted by recency; shows title, description, publisher, world, view count, and average rating as cards | route load | spinner shown while query runs; cards appear on success | error state with "Reload stories" retry; empty state when no stories exist | `GET /api/v1/published-stories/` | Keep | no auth required; accessible to anonymous visitors |
| `/public/stories/:storyId` | Published story reader | Full detail view for a single published story; shows metadata, word count, publisher, world, star rating, and comment list | route load | spinner while query runs; detail view appears on success; comments load in separate query | error state with "Reload story" retry | `GET /api/v1/published-stories/:id`, `GET /api/v1/published-stories/:id/comments` | Keep | rating POST requires auth; comments GET is public |
| `/storytelling/published` | User published stories | Authenticated surface showing only the current user's published stories; filters full list by user_id from session | route load | awaits session query then published list query; user-scoped filter applied client-side | error state with "Reload published stories" retry; empty state when user has no published stories | `GET /api/v1/published-stories/`, `GET /api/v1/users/me` | Keep | session user_id used to filter list; no user-specific backend endpoint exists yet |
| `/public/blog` | Blog post list | Public list of published blog posts with title, excerpt, featured image, and publication date | route load | spinner while posts load; cards appear on success | error state with retry; empty state when no posts exist | `GET /api/blog/posts` | Keep | sameOriginFetch (not under /api/v1) |
| `/public/blog/:slug` | Blog post reader | Full blog post content rendered from HTML field; shows title, excerpt, publication date, view count | route load | spinner while post loads; content rendered on success | error state for missing/unpublished posts | `GET /api/blog/posts/:slug` | Keep | sameOriginFetch; dangerouslySetInnerHTML for HTML content field |
| `/public/search` | Global search | Search box over blog posts using full-text search; URL query param `q` drives active query; shows result cards with title, excerpt, date | manual submit or URL-driven on load | no fetch until query is at least 2 chars; spinner shown while results load | error state for search failure; no-results state for empty results | `GET /api/blog/search/?q=...` | Keep | sameOriginFetch; uses `useSearchParams` with Suspense boundary for SSR safety |
| `/community/forums` | Forum categories and recent threads | Public forum landing showing category cards with thread counts and a list of recent threads across all categories | route load | two parallel queries for categories and threads; both needed before rendering | error state with "Reload forums" retry; empty state when no categories exist | `GET /api/forum/categories/`, `GET /api/forum/threads/` | Keep | sameOriginFetch (not under /api/v1) |
| `/community/forums/:threadId` | Forum thread detail | Thread header with title, category, author, and stats; list of post cards with content, author, and vote counts | route load | spinner while thread loads; posts rendered on success | error state for unknown or deleted threads | `GET /api/forum/threads/:id` | Keep | sameOriginFetch; supports deleted-post rendering with visual fade |
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

---

## Care Circle Behavior Capture

### Example 6
- Route: `/care-circle-patient/login`
- Screen name: Patient Picture Sign-In

- Element name: Daily Sign-In Keys
- Element type: image grid validation
- Legacy location: `frontendv1/app/care-circle-patient/login`

- What job does this element do for the user?
- Authenticates the patient without forcing passwords or typing.
- Default state: Grid of picture buttons.
- Trigger/Behavior: User selects three exact keys; submits array to backend. Redirects to `/home` on success.
- API: `/api/v1/care-circle/patient/auth/login`
- React rebuild decision: Keep exactly as built.

### Example 7
- Route: `/care-circle-family/events`
- Screen name: Family Event Stream

- Element name: Asynchronous Activity Feed
- Element type: list
- Legacy location: `frontendv1/app/care-circle-family/events`

- What job does this element do for the user?
- Streams realtime LLM provider activities (e.g. Generation delays, Fallback triggers) and patient session activities.
- Behavior details: Fetches telemetry dynamically, pushes alerts asynchronously.
- React rebuild decision: Keep but extend with WebSocket integration later.

### Example 8
- Route: `/care-circle-family/patients/:patientId/preferences`
- Screen name: Patient Preferences

- Element name: Family Managed Patient Settings
- Element type: form / toggle list
- Legacy location: Concept migrated from DailyNewsletter DB

- What job does this element do for the user?
- Family configures what providers the patient can use, blocking negative topics or injecting preferred topics (e.g. 1950s music).
- Behavior details: Directly impacts the `CareCircleProviderPatientConfig` map during session assembly.
- React rebuild decision: Improve to include explicit inline toggles mapping directly to the DB schema.

### Example 9
- Route: `/care-circle-patient/session`
- Screen name: Calm Daily Content

- Element name: Patient Highlights View
- Element type: read-only cards
- Legacy location: `frontendv1/app/care-circle-patient/home`

- What job does this element do for the user?
- Serves generative AI output (Weather, Word Scrambles, Daily Quotes) exactly as structured from OpenRouter.
- Behavior details: Completely read-only. No action required. Assembly triggered dynamically behind API.
- React rebuild decision: Keep the calm interface; no stressful CTAs.

---

## Admin Behavior Capture

### Admin Users Page
- Route: `/admin/users` (React), legacy `/app/admin/users`
- Screen name: User Management

- Element name: User table with active/inactive toggle
- Element type: table with action buttons
- Legacy location: `app/templates/pages/admin_users.html`

- What job does this element do for the user?
- Admin can view all registered users and toggle their active/inactive status to suspend or reinstate access.

- Trigger: Click "Deactivate" or "Activate" button on a user row.

- Inputs: User ID (from table row), target active state.

- States:
  - Default: Button shows "Deactivate" for active users, "Activate" for inactive.
  - Loading: Spinner replaces button text, button disabled.
  - Success: Query invalidates and table re-renders with updated status badge.
  - Error: No error state shown in current implementation (toggle silently fails).

- Behavior details:
  - Toggles user `is_active` flag via `PATCH /api/v1/users/{id}/toggle-active`.
  - Query cache invalidated on success, refreshing the user list.
  - Non-admin users receive 403 on API call.

- APIs:
  - `GET /api/v1/users/?limit=1000` — list all users
  - `PATCH /api/v1/users/{id}/toggle-active` — toggle active status

- React rebuild decision: Keep as-is.

### Admin Billing Page
- Route: `/admin/billing` (React), legacy `/app/admin/billing_dashboard`
- Screen name: Billing Dashboard

- Element name: Stats grid, transaction list, manual credit adjustment form
- Element type: dashboard with table and form
- Legacy location: `app/templates/pages/admin_billing_dashboard.html`

- What job does this element do for the user?
- Admin monitors system-wide billing stats and can manually adjust user credits (positive or negative).

- Trigger: Submit credit adjustment form with user ID, amount, and description.

- Inputs: User ID (number), amount (coins, positive or negative), description text.

- States:
  - Default: Form fields empty with submit button disabled until all fields filled.
  - Loading: Submit button shows spinner and "Adjusting…", disabled.
  - Success: Green "Credits adjusted successfully" message, form cleared.
  - Error: Red "Failed to adjust credits" message shown below form.

- Behavior details:
  - `POST /api/v1/admin/billing/adjust-credits` with JSON body `{user_id, amount, description}`.
  - Form resets on success, success message appears for 3+ seconds.
  - Amount can be negative (deduction) or positive (bonus).

- APIs:
  - `GET /api/v1/admin/billing/dashboard` — system stats, recent transactions, user accounts
  - `POST /api/v1/admin/billing/adjust-credits` — manual credit adjustment

- React rebuild decision: Keep as-is. Form validation requires all three fields before enabling submit.

### Admin Maintenance Page
- Route: `/admin/maintenance` (React), legacy `/app/admin/maintenance`
- Screen name: Maintenance Mode

- Element name: Status indicator, message input, duration input, enable/disable button
- Element type: toggle controls with form
- Legacy location: `app/templates/pages/admin_maintenance.html`

- What job does this element do for the user?
- Admin enables or disables site-wide maintenance mode with optional custom message and duration.

- Trigger: Click "Enable maintenance mode" or "Disable maintenance mode" button.

- Inputs: Optional message string, duration in minutes (default 5).

- States:
  - Default (site live): Show green "Site is live" label with enable form.
  - Enabled: Show amber "Maintenance mode is ON" label with custom message and disable button.
  - Loading: Button shows spinner, disabled.

- Behavior details:
  - `GET /api/v1/maintenance/status` — public endpoint (no auth required for status)
  - `POST /api/v1/maintenance/enable?message=...&duration_minutes=...` — admin only
  - `POST /api/v1/maintenance/disable` — admin only
  - Status polls every 15 seconds when page is open.
  - Non-admin users receive 403 on enable/disable.

- APIs:
  - `GET /api/v1/maintenance/status` — public, returns `{enabled, message, estimated_end_time}`
  - `POST /api/v1/maintenance/enable` — admin only, requires `message` and `duration_minutes` query params
  - `POST /api/v1/maintenance/disable` — admin only

- React rebuild decision: Keep as-is.

### Admin CTA Page
- Route: `/admin/cta` (React), legacy `/app/admin/cta_manager`
- Screen name: CTA Content Management

- Element name: CTA list with toggle and delete buttons
- Element type: list with row-level actions
- Legacy location: `app/templates/pages/admin_cta_manager.html`

- What job does this element do for the user?
- Admin views all CTA content blocks and can toggle active/inactive or delete entries.

- Trigger: Click "Activate", "Deactivate", or trash icon on a CTA row.

- Inputs: CTA ID (from row), action type.

- States:
  - Default: Each row shows title, position/style badges, active/inactive badge, and action buttons.
  - Loading: Spinner on the action button that was clicked.
  - Empty: Centered icon and "No CTA entries found" message.

- Behavior details:
  - `GET /api/v1/admin/cta-content?include_inactive=true` — list all CTAs
  - `POST /api/v1/admin/cta-content/{id}/toggle-active` — toggle is_active
  - `DELETE /api/v1/admin/cta-content/{id}` — delete CTA
  - Query invalidates on both toggle and delete.
  - No confirmation modal before delete in current implementation.

- APIs:
  - `GET /api/v1/admin/cta-content?include_inactive=true`
  - `POST /api/v1/admin/cta-content/{id}/toggle-active`
  - `DELETE /api/v1/admin/cta-content/{id}`

- React rebuild decision: Keep as-is. Consider adding delete confirmation modal in future.

### Admin Hub
- Route: `/admin` (React), legacy `/app/admin/dashboard`
- Screen name: Platform Admin Hub

- Element name: Section cards linking to admin sub-routes
- Element type: navigation grid
- Legacy location: `app/templates/pages/admin_dashboard.html`

- What job does this element do for the user?
- Provides entry point to all admin surfaces with icon+label+description cards.

- Trigger: Click a card to navigate to sub-route.

- Behavior details:
  - Cards for: Users, Billing, CTA Content, Maintenance Mode, Care Circle Admin.
  - Auth guard redirects non-authenticated to login, non-admin to access-denied.
  - Admin badge shown on the page header.

- React rebuild decision: Keep as-is.

---

## Sprint 10 Commercial & Support — Behavior Capture

### Billing Dashboard (`/storytelling/billing`)
- Route: `/storytelling/billing`, `/app/billing`
- Screen name: Billing Dashboard

- Element name: Billing dashboard route
- Element type: route
- What it does: Loads account balance, recent transactions, and available credit packages into one dashboard surface.
- Trigger: Route load (query-based loading state).
- Loading state: Spinner shown while queries run; balance, transaction table, and package cards appear on success.
- Error state: Error message with "Reload" retry link.
- Empty state: Zero-balance state with packages still visible.
- API: `GET /api/v1/billing/dashboard`, `GET /api/v1/billing/balance`, `GET /api/v1/billing/transactions`, `GET /api/v1/billing/packages`
- Keep/Improve/Remove: Keep

### Referral Intro Panel (`/storytelling/referrals`)
- Route: `/storytelling/referrals`, `/app/referrals`
- Screen name: Referrals Dashboard

- Element name: ReferralIntroPanel
- Element type: info panel
- Legacy location: `frontendv1/app/storytelling/referrals/referrals-dashboard.tsx`
- What it does: Shows a two-column explainer (how it works + referral link copy) at the top of the referrals page.
- Trigger: Rendered automatically when stats are loaded; referral link shown when `stats.referral_url` or `stats.referral_code` is populated.
- Copy button: Click copies `stats.referral_url` to clipboard via `navigator.clipboard`. Shows "Copied!" for 2 seconds then reverts.
- Data-testid: `referral-intro-panel`, `referral-url`, `copy-referral-link`
- States: Empty link field hides the panel's link box entirely.
- API: `GET /api/v1/referrals/stats`
- Keep/Improve/Remove: Keep

### Referral Stats, History, and Rewards
- Element name: Referral data tables
- Element type: table
- What it does: Shows total referrals, conversion rate, coins earned, plus paginated history and reward rows.
- Trigger: Parallel queries on route load.
- Loading state: `<LoadingState>` spinner.
- Error state: Full-route `<ErrorState>` with retry.
- APIs: `GET /api/v1/referrals/stats`, `GET /api/v1/referrals/history`, `GET /api/v1/referrals/rewards`
- Keep/Improve/Remove: Keep

### Onboarding Preview (`/storytelling/onboarding`)
- Route: `/storytelling/onboarding`, `/app/onboarding`
- Screen name: Onboarding Dashboard

- Element name: Onboarding preview route
- Element type: route
- Legacy location: `frontendv1/app/storytelling/onboarding/onboarding-dashboard.tsx`
- What it does: Previews the new-user onboarding interview questions and current completion status without a full wizard flow.
- Trigger: Route load.
- Left panel: Lists all questions from the interview JSON file with their order number and subtitle. No input fields — read-only preview.
- Right panel: Shows "Onboarding completed" or "Onboarding still pending" status, driven by `status.completed`.
- Insights section: Reads `insights.has_completed_onboarding` from `/api/v1/interview/user-insights`.
- Loading state: `<LoadingState>` spinner.
- Error state: Full-route `<ErrorState>` with retry.
- API: `GET /api/v1/interview/questions/new_user_onboarding`, `GET /api/v1/interview/status/new_user_onboarding`, `GET /api/v1/interview/user-insights`
- Decision: Remains a preview/status surface — do NOT expand to a full interview wizard within this sprint. The onboarding interview submission endpoint (`POST /api/v1/interview/submit`) is tested but the frontend route stays read-only until a later sprint prioritizes the full wizard flow.
- Keep/Improve/Remove: Keep as-is (preview only).

### Prompt Library (`/storytelling/prompts`)
- Route: `/storytelling/prompts`
- Screen name: Prompt Library

- Element name: Prompt library route
- Element type: list + form
- Legacy location: `frontendv1/app/storytelling/prompts/page.tsx`
- What it does: Displays user's prompts and shared prompts in a two-section card grid. New prompt form slides in above the list.
- Trigger: Route load.
- "My prompts" section: Fetches user prompts. Empty state shows dashed-border card with `BookOpen` icon.
- "Shared prompts" section: Fetches shared prompts, only rendered when list is non-empty.
- New prompt button: Shows `NewPromptForm` inline above the list. Form fields: title (text), type (select), prompt content (textarea), reason_to_use (text). Submit creates prompt and invalidates `my-prompts` query.
- Delete button: Trash icon on each owned prompt card; calls `deletePrompt(id)` mutation and invalidates query.
- Loading state: Spinner centered in content area.
- Error state: `<ErrorState>` with retry link.
- data-testid: `prompt-card`, `my-prompts-list`, `my-prompts-empty`, `new-prompt-form`, `new-prompt-button`, `delete-prompt-button`
- API: `GET /api/v1/prompts/my-prompts`, `GET /api/v1/prompts/shared`, `POST /api/v1/prompts/`, `DELETE /api/v1/prompts/{id}`
- Keep/Improve/Remove: Keep

### AI Model Catalog (`/storytelling/ai-models`)
- Route: `/storytelling/ai-models`
- Screen name: AI Models

- Element name: AI models route
- Element type: catalog/list
- Legacy location: `frontendv1/app/storytelling/ai-models/page.tsx`
- What it does: Displays available LLM models grouped into active and inactive sections with pricing, provider, and type.
- Trigger: Route load.
- Summary bar: Shows total count, active count, and provider list.
- ModelCard: Shows icon, display_name, model_name (monospace), description, type, max_tokens, and input/output pricing.
- Inactive models: Shown with reduced opacity and "Inactive" badge.
- Empty state: Shown when `models.length === 0`.
- data-testid: `model-card`, `models-empty-state`, `active-models-list`, `inactive-models-list`, `models-summary`
- API: `GET /api/v1/llm-models/`
- Keep/Improve/Remove: Keep

### Blog Dashboard (`/storytelling/blog`)
- Route: `/storytelling/blog`
- Screen name: Blog Dashboard

- Element name: Blog dashboard route
- Element type: list
- Legacy location: `frontendv1/app/storytelling/blog/page.tsx`
- What it does: Lists author's blog posts split into Drafts and Published sections with edit, publish, and delete actions.
- Trigger: Route load; fetches posts for `user.id`.
- New post link: Navigates to `/storytelling/blog/new`. Media link goes to `/storytelling/blog/media`.
- PostRow: Title, excerpt (line-clamp-2), status badge, date. Actions: Publish (if draft), Edit link, Delete button.
- Publish button: `publishBlogPost(id)` mutation, invalidates author-posts query.
- Delete button: `deleteBlogPost(id)` mutation, invalidates author-posts query.
- Empty state: Shown when `posts.length === 0`; includes "New post" CTA.
- data-testid: `blog-post-row`, `blog-drafts-list`, `blog-published-list`, `blog-empty-state`, `publish-post-button`, `edit-post-link`, `delete-post-button`
- API: `GET /api/blog/posts?author_id={userId}`, `POST /api/blog/posts/{id}/publish`, `DELETE /api/blog/posts/{id}`
- Keep/Improve/Remove: Keep

### Blog Editor — New (`/storytelling/blog/new`)
- Route: `/storytelling/blog/new`
- Screen name: New Blog Post

- Element name: New blog post form
- Element type: form
- Legacy location: `frontendv1/app/storytelling/blog/new/page.tsx`
- What it does: Form with title, excerpt, content fields; Save draft or Publish buttons; on success redirects to dashboard.
- Trigger: Route load.
- Fields: Title (text), Excerpt (text, optional), Content (textarea, min-h-64).
- Save draft: `createBlogPost({..., status: "draft"})`.
- Publish: `createBlogPost({..., status: "published"})`.
- Disabled state: Buttons disabled while `isPending` or `!canSubmit`.
- Error state: Inline error text with `data-testid="post-save-error"`.
- data-testid: `post-title-input`, `post-excerpt-input`, `post-content-input`
- API: `POST /api/blog/posts`
- Keep/Improve/Remove: Keep

### Blog Editor — Edit (`/storytelling/blog/[postId]`)
- Route: `/storytelling/blog/{postId}`
- Screen name: Edit Blog Post

- Element name: Edit blog post form
- Element type: form
- Legacy location: `frontendv1/app/storytelling/blog/[postId]/page.tsx`
- What it does: Loads existing post, pre-fills form, tracks dirty state, saves updates or publishes.
- Trigger: Route load; uses `fetchBlogPostById(postId)`.
- Dirty state: "Unsaved changes" label appears when user edits. Save button disabled when `!dirty`.
- Update: `updateBlogPost(postId, {title, content, excerpt})`.
- Publish (if not yet published): `publishBlogPost(postId)` then redirect to dashboard.
- Cancel link: Returns to `/storytelling/blog`.
- data-testid: `edit-title-input`, `edit-excerpt-input`, `edit-content-input`
- API: `GET /api/blog/posts/{id}`, `PUT /api/blog/posts/{id}`, `POST /api/blog/posts/{id}/publish`
- Keep/Improve/Remove: Keep

### Blog Media Manager (`/storytelling/blog/media`)
- Route: `/storytelling/blog/media`
- Screen name: Media Library

- Element name: Blog media manager route
- Element type: media grid
- Legacy location: `frontendv1/app/storytelling/blog/media/page.tsx`
- What it does: Displays uploaded media tiles with hover-reveal delete button; upload via hidden file input.
- Trigger: Route load.
- Upload: Hidden `<input type="file" accept="image/*">` triggered by button click. On file select, `uploadCareCircleMedia(file)` is called. Success shows toast and invalidates `blog-media` query.
- MediaTile: Thumbnail (or `ImageIcon` placeholder), original filename, file type. Delete button appears on hover.
- Delete: `deleteCareCircleMedia(storage_path)` mutation, invalidates `blog-media` query. Shows toast on error.
- Empty state: Shown when `items.length === 0`.
- data-testid: `media-tile`, `upload-media-button`, `media-empty-state`, `media-grid`, `delete-media-button`
- API: `GET /api/blog/media/list`, `POST /api/blog/media/upload`, `DELETE /api/blog/media/{storage_path}`
- Keep/Improve/Remove: Keep

---

## Sprint 11 — Chatbot App Behavior Capture

### Chatbot Workspace (`/chatbot`)

- Route: `/chatbot`
- Screen name: Chatbot Workspace

#### Element: Session Rail

- Element type: nav / list
- Legacy location: `ChatbotWorkspace` component, `SessionRail` sub-component
- Purpose: Allow user to switch between chatbot sessions and create new ones
- Trigger: Click on session item, click "New conversation" button
- Inputs: `ChatbotSession[]` fetched from `GET /api/v1/chatbot/sessions`
- States:
  - Default: list of sessions with active session highlighted
  - Loading: spinner with "Loading sessions..."
  - Empty: only "New conversation" button visible
- Behavior Details:
  - Session list is ordered by `updated_at` descending (most recent first)
  - Active session highlighted with `bg-white/20`
  - Hover reveals delete button (trash icon) with opacity-0 → opacity-100 transition
  - "New conversation" creates a session via `POST /api/v1/chatbot/sessions` then navigates
  - On session delete, session list is refetched; if active session is deleted, clears selection

#### Element: Message Transcript

- Element type: chat / list
- Legacy location: `ChatbotWorkspace`, `MessageBubble` sub-component
- Purpose: Display conversation between user and assistant
- Trigger: Automatic after `sendMessage` mutation succeeds
- Inputs: `ChatbotMessage[]` from `GET /api/v1/chatbot/sessions/:id`
- States:
  - Loading: centered spinner
  - Empty (no session): "Select or create a session to begin."
  - Empty (session, no messages): "No messages yet. Send something to start."
  - Populated: list of `MessageBubble` components
  - Pending: "Assistant" bubble with spinner while awaiting AI response
  - Error: red error banner with "Retry" button
- Behavior Details:
  - Auto-scrolls to bottom when `messages` array changes
  - User messages: right-aligned, amber-600 background, "You" label
  - Assistant messages: left-aligned, `--bg-chat-assistant` background, "Assistant" label
  - Per-turn usage shown in assistant bubble footer: `X→Y tokens · $0.00XX · gpt-4o`

#### Element: Composer / Prompt Input

- Element type: form / textarea
- Legacy location: `ChatbotWorkspace`, `<textarea id="chatbot-prompt">`
- Purpose: User types message to send to AI assistant
- Trigger: Type in textarea, Cmd/Ctrl+Enter or button click to submit
- Inputs: text from textarea, `activeSessionId` for target session
- States:
  - Default: enabled with placeholder text
  - Disabled: while `sending` or `creating` (opacity-50)
  - Error: shows error banner above composer with retry link
- Behavior Details:
  - Submit via Cmd/Ctrl+Enter (not plain Enter, which would add newline)
  - When no active session: creating a new session first, then sending (chained)
  - `createSessionAndSend` helper handles no-session case by creating then sending
  - Draft cleared on successful send

#### Element: Starter Prompts

- Element type: button / nav
- Legacy location: `ChatbotWorkspace` starter prompt buttons
- Purpose: One-click shortcuts to send common prompts
- Trigger: Click on starter prompt button
- Inputs: prompt text, `activeSessionId`
- States:
  - Default: 3 buttons with Sparkles icon
  - Hover: border and background lighten
- Behavior Details:
  - With active session: calls `sendMessage` directly
  - Without session: calls `createSessionAndSend` (creates session then sends)
  - Prompts: "Summarize a care update for a family member.", "Help me outline a short story scene.", "Turn notes into a calm conversational response."

#### Element: Assistant Pending State

- Element type: chat / loading
- Legacy location: inline in `ChatbotWorkspace` rendered while `sending === true`
- Purpose: Visual feedback that AI is processing
- Trigger: Appears when `sendMessage` mutation is in-flight
- States:
  - Visible: shows typing indicator bubble with Bot avatar and spinner
- Behavior Details:
  - Replaces any empty-state text while waiting
  - Does not persist after response arrives

#### Element: Retry / Error State

- Element type: form / error
- Legacy location: error banner above composer, "Retry" button
- Purpose: Allow user to re-attempt a failed send
- Trigger: `sendMessage` onError callback
- States:
  - Error: shows error message text + "Retry" button
- Behavior Details:
  - Clears on retry (`setSendError(null)`) then calls `handleSubmit(draft)` again
  - Error message comes from API error response (extracted from `err.message`)

### Chatbot History (`/chatbot/history`)

- Route: `/chatbot/history`
- Screen name: Conversation History

#### Element: History List

- Element type: table / list
- Purpose: View all past sessions with timestamps
- Trigger: Navigate to `/chatbot/history`
- Inputs: `GET /api/v1/chatbot/sessions`
- States:
  - Loading: centered spinner
  - Empty: "No conversation history yet." with link to `/chatbot`
  - Populated: grid rows with session link, date, delete button
- Behavior Details:
  - Each row links to `/chatbot/sessions/:id`
  - Delete button removes session with confirmation dialog
  - Date formatted as "Apr 30, 14:00" style

### Chatbot Settings (`/chatbot/settings`)

- Route: `/chatbot/settings`
- Screen name: Chatbot Settings

#### Element: Settings Cards

- Element type: cards / info
- Purpose: Inform user about model, billing, and privacy
- States: Static display only; no interactive state
- Behavior Details:
  - Shows default model (GPT-4o)
  - Links to `/app/billing` for balance
  - Notes that chatbot is independent from storytelling/Care Circle

### Session Restore (`/chatbot/sessions/:sessionId`)

- Route: `/chatbot/sessions/:sessionId`
- Screen name: Chatbot Session Detail
- Purpose: Deep-link to a specific chatbot session
- Trigger: Direct navigation or URL bookmark
- Inputs: `sessionId` from route params, passed as `initialSessionId` to `ChatbotWorkspace`
- States:
  - Loaded: same workspace UI as `/chatbot` but with pre-selected session
- Behavior Details:
  - `ChatbotWorkspace` receives `initialSessionId` prop
  - `activeSessionId` state is initialized from prop
  - Session is fetched via `fetchChatbotSession(initialSessionId)` on mount

