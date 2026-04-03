# Frontend React Rewrite Plan

> Purpose: This document replaces `frontendboth.md` as the working planning document for the frontend rebuild. It reconciles the existing legacy frontend docs with the actual templates, JavaScript modules, and view routes in the repo, then proposes a logical React rebuild order across 10 sprints.
>
> Scope: Planning only. This does not define implementation details for the new React codebase beyond sequencing, feature grouping, and migration priorities.
>
> Source basis:
> - `frontendboth.md`
> - `frontend.md`
> - `frontendclaude.md`
> - legacy templates under `app/templates/`
> - legacy frontend scripts under `app/static/js/`
> - view routers under `app/routers/views_*.py`, `app/routers/views_blog.py`, `app/routers/views_public.py`, and related HTML-serving routers

---

## 1. Core Corrections

These points should be treated as corrected truth for the rewrite:

- The backend is `FastAPI`, not Flask.
- The legacy frontend is server-rendered Jinja plus vanilla JS and Fetch, not jQuery-driven.
- The rewrite target is a React frontend consuming backend APIs, not a template conversion.
- The backend is already moving toward standardized `ApiResponse` contracts. The React app should assume that standard envelope is the target.
- The app is not just “stories and worlds.” It also includes forum, blog, billing, referrals, public gallery/chat, social sharing, published stories, maintenance/admin tools, and onboarding/support surfaces.

---

## 2. What The Older Docs Missed Or Understated

The older frontend docs were useful, but they missed or blurred several real legacy surfaces that exist in code:

### Additional or under-documented pages

- Home page is richer than earlier docs implied:
  news, public-chat worlds, published stories, generated images, and recent forum activity are all assembled into the landing experience.
- World element detail pages exist:
  `character_detail.html`, `location_detail.html`, `lore_item_detail.html`
- Character generator exists as a dedicated guided flow:
  `pages/character_generator.html`
- Referral intro page exists in addition to the main referrals dashboard:
  `pages/referral_intro.html`
- News reader pages exist:
  `pages/news_list.html`, `pages/news_detail.html`
- Global search page exists:
  `pages/global_search.html`
- Analytics test page exists:
  `pages/analytics_test.html`
- Interview trigger page exists:
  `pages/interview_trigger.html`
- Admin utility pages extend beyond the major dashboards:
  `pages/admin_image_jobs.html`, `pages/admin_user_email.html`
- Published-story author page exists:
  `pages/user_published_stories.html`
- LLM model info view exists:
  `llm_models/llm_models_grid.html`

### Route/path mismatches in older docs

- Published stories public views are under `/published/...`, not only `/public/stories/...`
- Public image sharing uses `/public/image` and `/public/image-share`
- Some “basic story” routes are represented under `/ui/stories/basic/...` in view routing, not only `/ui/basic-stories/...`
- Blog has additional view surfaces:
  category redirect routes, tag routes, author pages, dashboard, and editor entry paths

### Legacy UI patterns that matter for React

- The shell depends heavily on a top nav, breadcrumb, header, CTA blocks, coin balance badge, theme toggle, and cookie consent.
- Editors and chat flows depend on long-lived state, autosave, streaming updates, and context sidebars.
- A non-trivial amount of UX value sits in utility modals:
  AI model selector, prompt picker, link-character/location/lore modals, image generation modal, help modal, confirmation modal.

---

## 3. Legacy Product Surface To Preserve Or Intentionally Supersede

For planning, the legacy frontend breaks into these product domains:

### Foundation

- App shell
- auth and session handling
- theme
- notifications
- help system
- maintenance banner
- cookie consent
- coin balance/global user context

### Core authoring

- worlds
- characters
- locations
- lore items
- stories
- story classes
- associations
- basic stories

### Advanced authoring

- act editor
- scene editor
- act AI review
- story wizard
- brainstorm
- image generation
- prompt library
- AI model selection
- document manager/import flows
- world hierarchy
- world map
- character generator

### Conversational interfaces

- world chat
- story chat
- public world chat

### Community and publishing

- published stories gallery
- published story reader
- user published stories
- forum
- blog
- public world gallery
- image preview/share
- social preview/share flows

### User and commercial surfaces

- account
- billing
- referrals
- welcome interview
- user guide
- legal pages

### Admin and operations

- admin dashboard
- users
- admin billing
- CTA manager
- maintenance admin
- help editor
- news manager
- image jobs
- user email

### Low-priority legacy/utility surfaces

- analytics test
- global search
- interview trigger
- examples/help demo pages

---

## 4. React Rewrite Assumptions

These assumptions should guide the rewrite order:

- Rebuild authenticated product flows before rebuilding informational/admin edge cases.
- Prioritize backend-backed user value over template parity.
- Preserve backend APIs where possible rather than inventing new ones mid-rebuild.
- Use route-level React pages and shared domain components.
- Use React Query or equivalent for API state.
- Use a single app shell with authenticated and public layouts.
- Treat Quill-era editor behavior as a product requirement, but not Quill itself as a technical requirement.
- Defer low-value legacy pages until the main product loop is stable.

---

## 5. Build Order Principles

The order below is intentional:

1. Build the shell, auth, and global state first, because every other page depends on them.
2. Build shared platform systems before deep domain pages:
   API client patterns, query/mutation conventions, form system, table/list patterns, modal/drawer patterns, route guards, and reusable account/commercial surfaces.
3. Start world-building and story-domain CRUD only after the framework and shared product systems feel stable.
4. Build editors and streaming/chat flows only after the core domain objects are stable.
5. Build community/public surfaces after the authoring core is usable.
6. Build admin tools after the main user-facing product is working.
7. Leave diagnostics, demos, and low-value legacy utilities for the end or omit them intentionally.

---

## 6. Recommended React Information Architecture

The new frontend should be organized into these primary route groups:

- `/auth`
- `/app`
- `/app/worlds`
- `/app/stories`
- `/app/chat`
- `/app/documents`
- `/app/prompts`
- `/app/billing`
- `/app/referrals`
- `/app/community`
- `/app/blog`
- `/app/admin`
- `/public`

Shared cross-cutting systems:

- app shell and navigation
- auth/session provider
- user/coin balance provider
- theme provider
- toast/notification system
- modal system
- API client layer
- websocket hooks
- editor abstraction

---

## 7. Ten-Sprint Build Plan

Each sprint assumes backend APIs already exist and are being consumed by the React app. “Done” means usable end-to-end, not just visual.

### Sprint 1: Foundation and Shell

Goal: establish the React app foundation and the global user experience.

Build:
- app bootstrap
- routing
- authenticated and public layouts
- top nav
- breadcrumbs/page header pattern
- theme toggle
- notification/toast system
- cookie consent
- global error/loading states
- user session bootstrap
- coin balance global fetch

Pages:
- shell only
- placeholder routes for major areas

Why first:
- every other sprint depends on this.

### Sprint 2: Authentication and Account Entry

Goal: users can enter the app and manage core identity/session state.

Build:
- login
- register
- forgot password
- reset password
- logout
- Google auth handoff support
- protected route handling
- account basics

Pages:
- auth pages
- `/app/account`
- `/app/account/edit`

Why now:
- this unlocks real authenticated testing for all following work.

### Sprint 3: Platform and App Framework Expansion

Goal: harden the React application into a reusable product platform before deep world-building starts.

Build:
- route group hardening for `/auth`, `/app`, and `/public`
- shared API client and query/mutation conventions
- reusable form, modal, drawer, and confirmation patterns
- reusable list/table and empty-state patterns
- account edit and user-preferences surfaces
- legal/help/about content routes
- welcome/onboarding entry flow
- billing/referrals shell routes if backend contracts are already usable

Why now:
- Sprints 1 and 2 already proved the shell and auth foundation. The next highest-leverage work is finishing the framework that every domain route will reuse.

### Sprint 4: User Platform and Commercial Core

Goal: finish the shared user/account/commercial surfaces that are product infrastructure rather than world-building.

Build:
- billing dashboard
- referrals dashboard and intro
- account edit/preferences
- user guide/help reader
- notification/preferences surfaces where required
- home/dashboard cards that summarize account and product state

Why now:
- These routes are cross-cutting product infrastructure and should not wait until the final admin sprint.

### Sprint 5: Documents, Prompts, and Shared Authoring Services

Goal: rebuild the supporting services the authoring product depends on before deep world graph pages.

Build:
- document manager
- import-from-document
- import-from-book
- create-from-document
- prompt library and prompt form
- image generation modal and job monitoring
- AI model selector shared components

Why now:
- These are base authoring systems that multiple future domains and editors will depend on.

### Sprint 6: Worlds, Stories, and Story Classes

Goal: start domain-heavy world-building only after the shared framework and services are solid.

Build:
- home/dashboard equivalent
- world list
- world create/edit
- world detail
- stories list
- story create/edit
- story detail
- story classes list/create/edit/delete

Why now:
- This creates the primary authoring loop on top of a stronger platform baseline.

### Sprint 7: World Elements and Associations

Goal: make the world content graph usable once worlds and stories are stable.

Build:
- characters list/create/edit/detail
- locations list/create/edit/detail
- lore items list/create/edit/detail
- link/unlink associations for stories
- reusable association selection components
- character generator if capacity allows

Why now:
- Editors and chat need these entities for context and UX richness.

### Sprint 8: Editors and Advanced Story Workflows

Goal: ship the high-value writing workspace after the domain graph is stable.

Build:
- act editor
- scene editor
- autosave
- prompt insertion UX
- AI model selection in editor
- association sidebars
- act AI review
- basic-story editor/form

Optional if capacity remains:
- brainstorm page
- story wizard foundation

Why now:
- editor complexity is high and should only start after the framework and domain CRUD are stable.

### Sprint 9: Chat, Public, Publishing, Forum, and Blog

Goal: rebuild the community-facing experience.

Build:
- world chat
- story chat
- chat session management
- websocket hooks
- world hierarchy
- world map
- world builder
- published stories gallery
- published story reader
- user published stories
- public world gallery
- public world chat
- image preview/share pages
- forum home/category/thread/new-thread
- blog home/post/category/tag/author/editor/dashboard
- social sharing UI hooks

Why now:
- these surfaces are important, but they are downstream of the core framework and authoring product.

### Sprint 10: Admin Completion and Legacy Triage

Goal: finish operational surfaces and decide what not to carry forward.

Build:
- admin dashboard
- admin users
- admin billing
- CTA manager
- maintenance admin
- help editor
- news manager
- image jobs
- user email

Triage in this sprint:
- analytics test page
- global search
- interview trigger page
- component demo/example/help-only legacy assets

Decision rule:
- either rebuild, merge into a better React-native surface, or explicitly retire.

---

## 8. Recommended Deliverables Per Sprint

Every sprint should end with:

- route-level pages working against real backend APIs
- loading, empty, and error states
- auth-aware navigation
- integration smoke tests for the frontend route group
- explicit parity notes:
  what matches legacy, what is intentionally different

---

## 9. What Should Be Deferred Or Possibly Retired

These should not block the first usable React release:

- analytics test page
- interview trigger page
- component demo/example pages
- duplicated/legacy blog home variants
- low-value support/example markdown assets in templates
- any purely diagnostic route with no user-facing value

Possible retire-or-merge candidates:

- `analytics_test.html`
- `interview_trigger.html`
- `examples/help_button_examples.html`
- duplicate blog home variants if one modern route covers the product need

---

## 10. Release Strategy Recommendation

Do not wait for all 10 sprints to finish before showing value.

Suggested release cuts:

- Release A after Sprint 4:
  shell + auth + framework expansion + account/commercial core
- Release B after Sprint 6:
  framework + documents/prompts + worlds/stories core
- Release C after Sprint 8:
  full authoring workspace including world graph and editors
- Release D after Sprint 10:
  community/public/admin completion

---

## 11. Highest-Risk Areas

These deserve extra planning before implementation:

- act/scene editor replacement
- autosave and conflict handling
- websocket streaming and reconnect behavior
- prompt/model-selection UX
- image generation job polling
- public/private auth boundary handling
- blog and forum breadth if both are included in the first React generation

---

## 12. Final Planning Summary

If the goal is a practical React rebuild, the first six sprints should focus almost entirely on:

- shell
- auth
- shared framework patterns
- account/commercial core
- prompts
- documents
- image generation
- worlds
- stories

That gets the product framework and the core authoring loop back online in a safer order.

World elements, editors, chat, public/community surfaces, and admin tools should follow after the shared framework and domain model are stable.

This is the recommended order because it reduces rewrite risk, aligns with the backend-first work already done, and avoids starting domain-heavy world-building before the shared product framework is ready.
