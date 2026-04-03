# React Route-By-Route Backlog

> Purpose: route-level execution backlog for the React frontend rebuild.
>
> How to use:
> - Treat this as the page backlog, not a design spec.
> - Build in sprint order unless there is a backend dependency reason to change sequence.
> - Add implementation tickets under each route as work is decomposed.
> - Use `uiBehaviorCapture.md` to record how important legacy UI elements behave before the React version is finalized.

Reference docs:
- `frontendAll.md`
- `frontendboth.md`
- `BACKEND_ENDPOINT_MATRIX.md`

Priority legend:
- `P0`: product-critical, build first
- `P1`: important primary flow
- `P2`: secondary or dependent flow
- `P3`: low-priority, legacy, or admin utility

Status legend:
- `Keep`: preserve as a React page
- `Merge`: merge into another React page/flow
- `Defer`: build later
- `Review`: confirm whether to keep at all

---

## Sprint 1: Shell, Session, Global App State

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| Global app shell | `layouts/base.html` | `/app/*` and `/public/*` layouts | P0 | Keep | auth, billing balance, maintenance | app shell, top nav, footer, breadcrumbs, page header, toasts, theme provider | Foundation for all authenticated/public pages |
| `/` | `pages/index.html` | `/` | P0 | Keep | dashboard/home aggregates, public content APIs | hero, content rails, CTA blocks, cards, announcement banners | Public home should be API-driven, not server-rendered |
| `/ui/account` | `pages/account.html` | `/app/account` | P0 | Keep | `/api/v1/users/me` | account summary, profile form, session status, coin summary | Often the first authenticated sanity page |
| Maintenance state | banner/partials | global app state | P0 | Keep | maintenance endpoints | maintenance banner, route guard, read-only notice | Must exist before broader rollout |

## Sprint 2: Auth and Entry

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| `/auth/login` | `pages/login.html` | `/auth/login` | P0 | Keep | auth login | auth form, validation, error banner, OAuth button | First production entry point |
| `/auth/register` | `pages/register.html` | `/auth/register` | P0 | Keep | auth register | auth form, validation, terms checkbox | |
| `/auth/forgot-password` | `pages/forgot_password.html` | `/auth/forgot-password` | P1 | Keep | password reset request | simple form, status panel | |
| `/auth/reset-password` | `pages/reset_password.html` | `/auth/reset-password` | P1 | Keep | password reset confirm | token form, password strength UI | |
| Google sign-in entry | `_google_signin_button.html` | embedded in auth pages | P1 | Keep | Google auth redirect | OAuth button | Shared control, not a route |

## Sprint 3: Worlds and Core Authoring Root

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| `/ui/worlds` | `pages/worlds_list.html` | `/app/worlds` | P0 | Keep | worlds list | data table/card grid, filters, empty state | Core object index |
| `/ui/worlds/new` | `pages/world_form.html` | `/app/worlds/new` | P0 | Keep | create world | world form, autosave/submit bar, validation | |
| `/ui/worlds/{id}` | `pages/world_detail.html` | `/app/worlds/:worldId` | P0 | Keep | world get, related counts/stories | detail header, tab shell, summary cards | Should become the hub page |
| `/ui/worlds/{id}/edit` | `pages/world_form.html` | `/app/worlds/:worldId/edit` | P0 | Merge | world update | world form | Likely share component with create |
| `/ui/worlds/{id}/stories` | server-rendered section | `/app/worlds/:worldId/stories` | P1 | Merge | world stories | story list panel | Could remain a tab inside world detail |
| `/ui/worlds/gallery` or public world listing | public/world pages | `/public/worlds` | P1 | Keep | public worlds | public card grid, search/filter | Public discovery surface |

## Sprint 4: Story Backbone

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| `/ui/stories` | `pages/stories_list.html` | `/app/stories` | P0 | Keep | stories list | story cards/table, filter bar | |
| `/ui/stories/new` | `pages/story_form.html` | `/app/stories/new` | P0 | Keep | create story, worlds, story classes | story form, selectors, validation | |
| `/ui/stories/{id}` | `pages/story_detail.html` | `/app/stories/:storyId` | P0 | Keep | story detail, acts, associations | detail header, outline tree, stats, publish panel | Primary story hub |
| `/ui/stories/{id}/edit` | `pages/story_form.html` | `/app/stories/:storyId/edit` | P0 | Merge | story update | story form | |
| `/ui/stories/wizard` | `pages/story_wizard.html` | `/app/stories/wizard` | P1 | Keep | story generate, worlds, prompts | stepper, AI generation panel, review step | Important conversion flow |
| `/ui/stories/basic/new` | `pages/basic_story_form.html` | `/app/basic-stories/new` | P1 | Keep | basic story create | simplified story form | |
| `/ui/stories/basic/quick-start` | quick-start page | `/app/basic-stories/quick-start` | P2 | Keep | story helper endpoints | template chooser, guided CTA | Validate actual value before polishing |
| `/ui/basic-stories/{id}` | `pages/basic_story_editor.html` | `/app/basic-stories/:storyId` | P1 | Keep | basic story get/update/chat | single-document editor, assistant panel | Separate editing mode |

## Sprint 5: World Elements and Associations

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| `/ui/worlds/{id}/characters` | `pages/characters_list.html` | `/app/worlds/:worldId/characters` | P0 | Keep | characters list/create | entity list, filters, row actions | |
| `/ui/worlds/{id}/characters/new` | `pages/character_form.html` | `/app/worlds/:worldId/characters/new` | P1 | Merge | create character | entity form | |
| `/ui/characters/{id}` | `pages/character_detail.html` | `/app/characters/:characterId` | P1 | Keep | character detail | profile layout, tabs, associations, image block | |
| `/ui/characters/{id}/edit` | `pages/character_form.html` | `/app/characters/:characterId/edit` | P1 | Merge | update character | entity form | |
| `/ui/worlds/{id}/locations` | `pages/locations_list.html` | `/app/worlds/:worldId/locations` | P0 | Keep | locations list/create | entity list/map launch links | |
| `/ui/locations/{id}` | `pages/location_detail.html` | `/app/locations/:locationId` | P1 | Keep | location detail | detail layout, map relationships | |
| `/ui/worlds/{id}/lore-items` | `pages/lore_items_list.html` | `/app/worlds/:worldId/lore-items` | P0 | Keep | lore list/create | entity list | |
| `/ui/lore-items/{id}` | `pages/lore_item_detail.html` | `/app/lore-items/:loreItemId` | P1 | Keep | lore detail | document-like detail layout | |
| Association modals | partials | route-local UI | P1 | Keep | association endpoints | link entity modal, role selector, chip list | Shared across stories/acts/scenes |
| `/ui/worlds/{id}/character-generator` | `pages/character_generator.html` | `/app/worlds/:worldId/character-generator` | P2 | Keep | character generation helpers | guided generator, preview cards | Useful but not core CRUD |

## Sprint 6: Editors, Review, Documents

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| `/ui/acts/{id}` | `pages/act_editor_ui.html` | `/app/acts/:actId` | P0 | Keep | act get/update, prompts, ws ticket | rich editor, autosave status, AI panel, association rail | High complexity |
| `/ui/acts/{id}/review` | `pages/act_ai_review.html` | `/app/acts/:actId/review` | P1 | Keep | act review | diff/review panel, highlights, accept/reject actions | |
| `/ui/scenes/{id}` | `pages/scene_editor_ui.html` | `/app/scenes/:sceneId` | P0 | Keep | scene get/update, ws ticket | rich editor, autosave, AI panel | |
| Document manager route | `pages/document_manager.html` | `/app/documents` | P1 | Keep | documents list/upload/delete/download | upload zone, processing states, document table | Critical for React app if docs remain part of product |
| Import from document flows | import pages/handlers | `/app/import` or inside documents | P2 | Merge | document import APIs | wizard stepper, preview, job status | Prefer merging into docs/world import flow |

## Sprint 7: Chat, Builder, Spatial Tools

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| World chat page | `pages/world_chat.html` or embedded | `/app/worlds/:worldId/chat` | P1 | Keep | world chat, ws ticket | chat shell, thread list, prompt composer, source/context panel | |
| Story chat page | story chat template | `/app/stories/:storyId/chat` | P1 | Keep | story chat, ws ticket | chat shell | |
| Public chat | public world chat page | `/public/worlds/:worldId/chat` | P2 | Keep | public chat | public chat shell | |
| World builder | world builder templates | `/app/world-builder` and `/app/world-builder/:worldId` | P1 | Keep | world builder endpoints | questionnaire, generation review, create/update flow | |
| World hierarchy | `pages/world_hierarchy.html` | `/app/worlds/:worldId/hierarchy` | P2 | Keep | hierarchy data | tree view, drilldown panels | |
| World map | `pages/world_map.html` | `/app/worlds/:worldId/map` | P2 | Keep | locations, location connections | map canvas, pins, edge editor | Build after core locations are stable |

## Sprint 8: Publishing, Community, Public Discovery

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| Published stories list | `pages/published_stories.html` | `/public/published-stories` | P1 | Keep | published stories list | public card grid, filters, rating summary | |
| Published story reader | `pages/published_story_detail.html` | `/public/published-stories/:storyId` | P1 | Keep | published story detail, comments, ratings | reading layout, comments, social share | |
| User published stories | `pages/user_published_stories.html` | `/public/authors/:userId/stories` | P2 | Keep | published story user list | author header, story rail | |
| Forum categories/threads | forum pages | `/app/community/forum/*` | P1 | Keep | forum APIs | category list, thread list, editor, moderation controls | |
| Blog home/post/author/tag | blog pages | `/app/blog/*` and `/public/blog/*` | P1 | Keep | blog APIs | article list, article page, author profile, engagement controls | |
| Public image preview/share | public image pages | `/public/image` and `/public/image-share` | P2 | Keep | image/public share APIs | image viewer, share metadata | |
| Social preview/share | social pages | `/public/share/*` or route-local | P2 | Keep | share/preview APIs | share modal, preview card | |
| Global search | `pages/global_search.html` | `/app/search` | P2 | Keep | search APIs | global search bar, mixed results view | Could move earlier if product value is high |

## Sprint 9: Billing, Referrals, Onboarding, Blog Tools

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| Billing dashboard | billing pages | `/app/billing` | P1 | Keep | billing/account/package APIs | credit cards, transaction table, purchase flow | |
| Referrals dashboard | referral pages | `/app/referrals` | P1 | Keep | referral stats/history | referral summary, copy-link tools, rewards table | |
| Referral intro | `pages/referral_intro.html` | `/public/referrals` or `/app/referrals/intro` | P2 | Keep | referral public/summary content | marketing-style explainer page | |
| Welcome interview | interview pages | `/app/onboarding/interview` | P2 | Keep | welcome interview APIs | onboarding wizard | |
| Prompt library | prompt pages | `/app/prompts` | P1 | Keep | prompt APIs | prompt list, form, use-prompt modal | |
| AI model pages | model pages and selectors | `/app/ai-models` | P2 | Keep | ai-model APIs | model catalog, selectors, badges | |
| Blog dashboard/editor | blog pages | `/app/blog/dashboard`, `/app/blog/editor`, `/app/blog/posts/:id/edit` | P2 | Keep | blog author/editor APIs | article editor, media selector, analytics panels | |
| Blog media | blog media pages | `/app/blog/media` | P2 | Keep | blog media APIs | upload manager, media grid, picker modal | |

## Sprint 10: Admin, Support, Low-Priority Legacy

| Legacy Route | Legacy Template | React Route | Priority | Status | Backend/API | Shared Components | Notes |
|---|---|---|---|---|---|---|---|
| Admin users | admin pages | `/app/admin/users` | P2 | Keep | admin user APIs | admin table, edit modal, impersonation controls | |
| Admin billing | admin pages | `/app/admin/billing` | P2 | Keep | admin billing APIs | admin dashboard, user credit tools | |
| Admin CTA | admin pages | `/app/admin/cta` | P3 | Keep | CTA APIs | CTA form/list/test tools | |
| Maintenance admin | admin pages | `/app/admin/maintenance` | P3 | Keep | maintenance APIs | toggle controls, status panel | |
| News manager | admin/news pages | `/app/admin/news` | P3 | Keep | news APIs | CRUD table/editor | |
| Admin image jobs | `pages/admin_image_jobs.html` | `/app/admin/image-jobs` | P3 | Keep | image job/admin APIs | jobs table, retry/debug actions | |
| Admin user email | `pages/admin_user_email.html` | `/app/admin/user-email` | P3 | Keep | email/admin endpoints | targeted messaging form | |
| Help editor | help/admin pages | `/app/admin/help` | P3 | Keep | help content APIs | markdown/content editor | |
| Analytics test | `pages/analytics_test.html` | `/app/admin/analytics-test` | P3 | Review | analytics test endpoints | diagnostics form | Likely internal only |
| Interview trigger | `pages/interview_trigger.html` | `/app/admin/interview-trigger` | P3 | Review | interview/admin endpoints | admin tool | Confirm actual need |
| Legal/help/info pages | misc templates | `/privacy`, `/terms`, `/help`, `/about` | P2 | Keep | mostly CMS/static | content page shell | Can be delivered with markdown/CMS |

---

## Route Consolidation Recommendations

- Merge create/edit variants into shared React form pages where possible.
- Treat world detail, story detail, and blog author/profile pages as tabbed hubs instead of proliferating sub-pages.
- Keep rich editors as dedicated routes.
- Move low-value diagnostics into admin-only tools instead of public/product navigation.

## Pages That Need Behavior Capture Before Build

Capture UI behavior first for these areas in `uiBehaviorCapture.md`:
- top navigation and coin balance refresh
- story generation modal
- act editor autosave and websocket generation
- scene editor autosave and prompt tools
- world chat and story chat session behavior
- document upload and processing states
- image generation modal and job polling
- association/link modals
- world map interactions
- blog editor and media picker

## Recommended Next Planning Artifact Links

- Component map: `frontendComponentInventory.md`
- UI behavior worksheet: `uiBehaviorCapture.md`
