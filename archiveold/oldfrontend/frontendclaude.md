# Frontend Documentation — Existing Capability Reference

> **Purpose:** This document describes the complete existing frontend of the InkandQuill2 application. It serves as the authoritative reference for the React rewrite. Every page, component, interaction pattern, and API contract documented here must be replicated or intentionally superseded in the new frontend.

---

## Table of Contents

1. [Technology Stack (Current)](#1-technology-stack-current)
2. [Layout & Navigation Shell](#2-layout--navigation-shell)
3. [Authentication & Sessions](#3-authentication--sessions)
4. [Page Inventory](#4-page-inventory)
5. [Component Library](#5-component-library)
6. [JavaScript Module Reference](#6-javascript-module-reference)
7. [CSS Architecture](#7-css-architecture)
8. [API Contracts](#8-api-contracts)
9. [WebSocket Protocols](#9-websocket-protocols)
10. [Rich Text Editing](#10-rich-text-editing)
11. [Feature Areas in Detail](#11-feature-areas-in-detail)
12. [Admin Surfaces](#12-admin-surfaces)
13. [Public (Unauthenticated) Routes](#13-public-unauthenticated-routes)
14. [Routing Map](#14-routing-map)
15. [State & Data Patterns](#15-state--data-patterns)
16. [Theme System](#16-theme-system)
17. [Billing & Coin System](#17-billing--coin-system)
18. [Analytics & Tracking](#18-analytics--tracking)

---

## 1. Technology Stack (Current)

| Concern | Current Technology |
|---|---|
| Templating | Jinja2 (server-side rendered) |
| UI Framework | Tabler Premium (Bootstrap-based) |
| Icons | Font Awesome 6.5.2 |
| Rich Text Editor | Quill.js 1.3.6 |
| Real-time | Native WebSocket API |
| HTTP Requests | Fetch API with `credentials: 'include'` |
| Theme | CSS custom properties + localStorage |
| Maps | Custom canvas/SVG world map |
| Auth | JWT in HttpOnly cookies |

All pages are server-rendered HTML with JavaScript progressively enhancing them. There is no bundler, no SPA routing, and no component framework — every page is a full HTML document extending `base.html`.

---

## 2. Layout & Navigation Shell

### Base Template (`app/templates/layouts/base.html`)

Every authenticated page extends this template. It provides:

- **HTML `<head>`:**
  - Charset UTF-8, responsive viewport
  - Extensible `<title>` block
  - SVG favicon
  - Font Awesome 6.5.2 (CDN)
  - Tabler Premium CSS (6 files: core, flags, payments, socials, vendors, themes)
  - Application CSS (`/css/main.css`)
  - Open Graph and Twitter Card meta tags (SEO/social sharing)
  - Google Analytics tag (configurable GA ID)
  - Early theme-detection script (prevents FOUC)

- **`<body>`:**
  - Tabler sidebar **disabled** via CSS override — layout is full-width with horizontal top nav only
  - `_topbar.html` partial injected at top
  - `content` block: page-specific content
  - Cookie consent banner (bottom, gradient indigo→purple)
  - JS includes: Tabler vendors, main.js, page-specific scripts

### Top Navigation (`_topbar.html`)

Horizontal navbar containing:

| Section | Items |
|---|---|
| Brand | Logo / site name |
| **Stories** dropdown | My Stories, Create Story, Story Classes, Story Wizard |
| **Worlds** dropdown | My Worlds, Create World, World Gallery (public) |
| **Tools** dropdown | Document Manager, Prompt Library, AI Models |
| **Community** dropdown | Forum, Published Stories |
| **Admin** dropdown | (admin users only) Users, Billing, News, CTAs, Maintenance, Help Editor |
| Right side | Coin balance badge, Theme toggle, User avatar + account dropdown |

Coin balance is fetched asynchronously via `GET /api/v1/billing/balance` on every page load.

### Footer (`_footer.html`)

Gradient design (indigo→purple), includes:
- Site links (About, Privacy, Terms, Help)
- Copyright

### Breadcrumbs (`_breadcrumbs.html`)

Contextual breadcrumbs rendered server-side and shown below the hero header on most pages.

---

## 3. Authentication & Sessions

### Mechanism
- JWT stored in **HttpOnly cookies** (`access_token`)
- All API calls use `credentials: 'include'`
- OAuth support: Google Sign-In (`_google_signin_button.html`)
- Session middleware for OAuth state management
- Anonymous user sessions supported on some public pages

### Auth Pages

| Page | Template | Route |
|---|---|---|
| Login | `login.html` | `/auth/login` |
| Register | `register.html` | `/auth/register` |
| Forgot Password | `forgot_password.html` | `/auth/forgot-password` |
| Reset Password | `reset_password.html` | `/auth/reset-password` |

**`auth_forms.js`** handles form validation, error display, and submission for all auth forms.

### WebSocket Auth

WebSockets cannot send cookies. The pattern used:
1. Frontend calls `GET /api/v1/auth/ws-ticket` → receives a short-lived token
2. Token appended as query param: `ws://.../generate?ticket={token}`

---

## 4. Page Inventory

### 4.1 Stories

#### Stories List (`/ui/stories`)
- Template: `stories_list.html`
- Lists all stories for the current user
- Cards with title, world, status, last-updated
- Filter/sort controls
- "Create Story" CTA

#### Story Detail (`/ui/stories/{id}`)
- Template: `story_detail.html`
- Story metadata, description, cover image
- Acts list with expand/collapse
- Scenes nested under acts
- "Generate Act" / "Generate Scene" triggers
- Associations: linked characters, locations, lore items
- Publish/unpublish controls
- Story stats (word count, act count)

#### Story Form (Create/Edit) (`/ui/stories/new`, `/ui/stories/{id}/edit`)
- Template: `story_form.html`
- Fields: title, description, genre, world (dropdown), story class, cover image
- `story_form_handler.js` — validation and submission
- `story_crud.js` — CRUD API calls

#### Story Wizard (`/ui/stories/wizard`)
- Template: `story_wizard.html`
- Multi-step guided story creation
- Steps: World selection → Story concept → Genre/tone → AI outline generation
- `story_generation_modal.js` — modal for AI generation
- Partial: `_story_generation_modal.html`

#### Basic Story (Simplified Mode)

| Page | Template | Route |
|---|---|---|
| Create | `basic_story_form.html` | `/ui/basic-stories/new` |
| Editor | `basic_story_editor.html` | `/ui/basic-stories/{id}` |

Streamlined single-document story mode without acts/scenes hierarchy. Has its own AI assistant (`basic_story_editor_ai_assistant.js`).

#### Act Editor (`/ui/acts/{id}`)
- Template: `act_editor_ui.html`
- Full-featured Quill.js rich text editor
- AI generation via WebSocket (streaming text)
- Auto-save
- AI model selector (partial: `_ai_model_selector.html`)
- Prompt selector (`act_prompt_manager.js`)
- Associations panel: link characters/locations/lore items
- Word count display
- JS modules: `act_editor_main.js`, `act_form_handler.js`, `act_save_handler.js`, `act_ai_processor.js`, `act_ui_updater.js`, `act_websocket_handler.js`, `quill_setup_act.js`

#### Act AI Review (`/ui/acts/{id}/review`)
- Template: `act_ai_review.html`
- Sends act content to AI for review/critique
- Highlights suggested changes inline
- Review components (modular):
  - `act_review_components/api_handler_review.js`
  - `act_review_components/quill_manager_review.js`
  - `act_review_components/text_highlighter_review.js`
  - `act_review_components/ui_updater_review.js`
- Main: `act_ai_review_page.js`

#### Scene Editor (`/ui/scenes/{id}`)
- Template: `scene_editor_ui.html`
- Identical pattern to Act Editor
- JS: `scene_editor_main.js`, `scene_crud.js`, `scene_prompt_selector.js`, `scene_quill_manager.js`, `scene_save_handler.js`, `scene_ui_updater.js`, `scene_ai_processor.js`, `scene_websocket_handler.js`

#### Story Classes (`/ui/story-classes`)
- Template: `story_class_list.html`
- Manage reusable story "classes" (templates/genres)
- `story_class_crud.js`

---

### 4.2 World Building

#### World List (`/ui/worlds/`)
- Template: `world_list.html`
- Cards for each world with name, description, element counts
- "Create World" CTA
- `world_crud.js`

#### World Create/Edit
- Template: `world_form.html`
- Fields: name, description, genre, visibility (public/private), cover image
- `world_form_handler.js`

#### World Detail (`/ui/worlds/{id}`)
- Template: `world_detail.html`
- Hero header with world name and description
- Stats: character count, location count, lore item count, story count
- Quick navigation to sub-sections (Characters, Locations, Lore, Stories, Map, Chat)
- World builder wizard link
- Import controls (from document, from book)

#### World Hierarchy (`/ui/worlds/{id}/hierarchy`)
- Template: `world_hierarchy.html` (resizable panels layout)
- Tree-view of all world elements
- Three-panel: World tree | Element detail | Stories
- `world_hierarchy.js` — expand/collapse, panel resize
- Drag-and-drop ordering

#### World Builder (`/ui/worlds/{id}/builder`)
- Template: world_builder.html (AI-driven wizard)
- Guides user through building out a world step by step
- Calls world builder API endpoints

#### World Chat (`/ui/worlds/{id}/chat`)
- Template: `world_chat.html`
- Chat interface for discussing world with AI
- Session list in sidebar (create, load, delete)
- Context-aware: incorporates characters, locations, lore items
- Message history with AI responses
- AI model selector
- Cost display per message
- JS: `world_chat_main.js`, `world_chat_context_loader.js`, `world_chat_message_handler.js`, `world_chat_session_manager.js`
- CSS: `world_chat.css`

#### World Map (`/ui/worlds/{id}/map`)
- Template: `world_map.html`
- Custom canvas/SVG map visualization
- Pin locations on map
- `world_map.js`

#### Characters

| Page | Template | Route |
|---|---|---|
| Character List | `character_list_for_world.html` | `/ui/worlds/{id}/characters` |
| Create/Edit | `character_form.html` | `/ui/characters/new?world={id}`, `/ui/characters/{id}/edit` |

- Character form: name, description, backstory, visual description, species, motivations
- AI-assisted backstory generation
- Image generation for character portraits
- `character_crud.js`, `character_form_handler.js`

#### Locations

| Page | Template | Route |
|---|---|---|
| Location List | `location_list_for_world.html` | `/ui/worlds/{id}/locations` |
| Create/Edit | `location_form.html` | `/ui/locations/new?world={id}`, `/ui/locations/{id}/edit` |

- Location form: name, description, type/scale, parent location
- Resizable form panels (`location_form_resize.js`)
- Image generation
- `location_crud.js`, `location_form_handler.js`

#### Lore Items

| Page | Template | Route |
|---|---|---|
| Lore List | `lore_item_list_for_world.html` | `/ui/worlds/{id}/lore-items` |
| Create/Edit | `lore_item_form.html` | `/ui/lore-items/new?world={id}`, `/ui/lore-items/{id}/edit` |

- Lore item form: name, description, type, linked elements
- `lore_item_crud.js`, `lore_item_form_handler.js`

---

### 4.3 Story Chat

#### Story Chat (`/ui/stories/{id}/chat`)
- Template: `story_chat.html`
- Similar to World Chat but scoped to a story
- Sidebar: chat sessions list
- Main area: message thread
- AI model selector
- Context: story acts, scenes, linked world elements
- `story_chat.js`
- CSS: `story_chat.css`

---

### 4.4 Documents & Imports

#### Document Manager (`/ui/documents`)
- Template: `document_manager.html`
- Upload and manage source documents (PDFs, text files)
- Processing status tracking
- Delete documents
- `document_crud.js`, `document_upload.js`

#### Import World from Document (`/ui/worlds/import-from-document`)
- Template: `import_from_document.html`
- Upload document → AI extracts world elements
- `world_importer_form_handler.js`

#### Import World from Book (`/ui/worlds/import-from-book`)
- Template: `import_from_book.html`
- Paste book text → AI extracts world elements
- `world_importer_from_doc_handler.js`

#### Create World from Document (`/ui/worlds/create-from-document`)
- Template: `create_from_document.html`
- Combined create+import flow
- `create_from_document_handler.js`

---

### 4.5 Community

#### Forum Home (`/forum`)
- Template: `forum_home.html` (also references `forum.css`)
- Category cards with thread/post counts

#### Forum Category (`/forum/category/{slug}`)
- Template: `forum_category.html`
- Thread listing with pagination
- Thread metadata: author, replies, views, last activity
- "New Thread" CTA

#### Forum Thread (`/forum/thread/{id}`)
- Template: `forum_thread.html`
- Post listing in thread
- Reply form with Quill editor
- Like/react on posts
- Pagination

#### Published Stories Gallery (`/ui/published-stories`)
- Template: `published_stories_gallery.html`
- Cards for published stories
- Sorting/filtering

#### View Published Story (`/public/stories/{id}`)
- Template: `view_published_story.html`
- Read-only story viewer
- Comments section
- Like/bookmark controls
- Social sharing (`_social_sharing.html`, `social_sharing.js`)
- CSS: `social-sharing.css`

---

### 4.6 Blog

The blog system is fully integrated:

| Page | Template | Route |
|---|---|---|
| Blog Index | `blog/index.html` | `/blog` |
| Post Detail | `blog/post_detail.html` | `/blog/post/{slug}` |
| Blog Editor | `blog/editor.html` | `/blog/editor`, `/blog/editor/{id}` |
| Admin Blog List | `blog/admin_list.html` | `/blog/admin/list` |

- Blog posts have categories, tags, SEO meta
- Editor uses Quill.js
- AI writing assistant (`blog_ai_writing` router)
- Media management (`blog_media` router)

---

### 4.7 Prompts

#### Prompt Library (`/ui/prompts`)
- Template: `prompt_list.html`
- List of saved prompts (system and user-defined)
- Categories/types
- `prompt_crud.js`

#### Prompt Form
- Template: `prompt_form.html`
- Fields: name, content, type, world scope
- `prompt_form_handler.js`

#### Use Prompt Modal (`_use_prompt_modal.html`)
- Modal invoked from editors to insert a prompt
- Shared partial across act and scene editors

---

### 4.8 Account & User

#### My Account (`/ui/account`)
- Template: `my_account.html`
- Profile info, preferences
- Coin balance
- Subscription info
- Password change

#### Edit User (`/ui/account/edit`)
- Template: `edit_user.html` (also `edit_user.js`)

#### Referrals (`/ui/referrals`)
- Template: `referrals.html`
- Referral link generation and tracking
- Reward status
- `referral_tracking.js`

#### Billing Dashboard (`/ui/billing`)
- Template: `billing_dashboard.html`
- Coin balance history
- Purchase options
- Transaction log
- `billing_dashboard.js`

#### Welcome Interview (`/ui/welcome-interview`)
- Template: `welcome_interview.html`
- Onboarding flow for new users
- 3 variants: simple, full, standard (partials: `interview_simple.html`, `interview_full.html`, `interview.html`)
- `interview.js`

---

### 4.9 Help & Legal

| Page | Template | Route |
|---|---|---|
| User Guide | `user_guide.html` | `/ui/guide` |
| Terms | `terms.html` | `/terms` |
| Terms of Service | `terms_of_service.html` | `/terms-of-service` |
| Privacy Policy | `privacy.html` | `/privacy` |

Contextual **help button** (`_help_button.html`) appears on most pages and opens a slide-in help panel or modal with page-specific content.

---

### 4.10 Image Handling

#### Image Generation (modal-based)
- Partial: `image_generation_modal.html` (`modules/image_generation_modal.js`)
- Available from character, location, lore item, story forms
- AI model selection for image provider (DALL-E 3, RunPod)
- Aspect ratio selection
- Job polling: `image_job_monitor.js`

#### Image Preview (`/public/image/{id}`)
- Template: `image_preview.html`
- Standalone image viewer

#### Image Share (`/public/image/{id}/share`)
- Template: `image_share.html`
- Social sharing for generated images

---

## 5. Component Library

### Tabler Premium Components Used

- **Cards** with status bars, ribbons, hover effects, gradient borders
- **Modals** (standard Bootstrap/Tabler modals with enhanced headers)
- **Dropdowns** (nav dropdowns, model selectors)
- **Badges** for status, counts, metadata
- **Toast notifications** (`notifications.js` — wraps Tabler's toast)
- **Progress bars** (indeterminate for loading states)
- **Avatars** (user, world, story thumbnails)
- **Forms** with validation states
- **Tabs** (used in detail pages)
- **Accordion** (FAQ, expandable sections)
- **Pagination** (forum, galleries)

### Custom Template Components (`app/templates/components/`)

| Component | File | Purpose |
|---|---|---|
| Basic Card | `basic_card.html` | Standard content card |
| Action Card | `action_card.html` | Card with action buttons |
| Status Card | `status_card.html` | Card with status indicator |
| Base Modal | `base_modal.html` | Modal shell |
| Confirmation Modal | `confirmation_modal.html` | Yes/No confirmation |
| Success Modal | `success_modal.html` | Success feedback |
| Input | `input.html` | Form input |
| Textarea | `textarea.html` | Form textarea |
| Select | `select.html` | Form select |
| Button | `button.html` | Styled button |
| Button Group | `button_group.html` | Grouped buttons |
| Breadcrumb | `breadcrumb.html` | Navigation breadcrumb |
| Alert | `alert.html` | Inline alert message |
| Progress Bar | `progress_bar.html` | Progress indicator |
| Badge | `badge.html` | Status badge |
| Icon | `icon.html` | Font Awesome icon wrapper |

### Shared Modals (Partials)

| Modal | Partial | Purpose |
|---|---|---|
| Link Character | `_link_character_modal.html` | Attach characters to story/act/scene |
| Link Location | `_link_location_modal.html` | Attach locations |
| Link Lore Item | `_link_lore_item_modal.html` | Attach lore items |
| Use Prompt | `_use_prompt_modal.html` | Insert saved prompt into editor |
| Story Generation | `_story_generation_modal.html` | AI story generation config |
| Image Generation | `image_generation_modal.html` | AI image generation |
| Help | `_help_modal.html` | Contextual help content |

### AI Model Selectors (3 variants)

| Variant | Partial |
|---|---|
| Dropdown | `_ai_model_selector.html` |
| Card grid | `_ai_model_card_selector.html` |
| Button group | `_ai_model_button_selector.html` |

All three read from `GET /api/v1/ai-models` and store selection in page state or `localStorage`.

---

## 6. JavaScript Module Reference

### Architecture Pattern

No bundler. Scripts loaded via `<script>` tags in templates. Modules communicate through:
- Direct function calls (same-page scripts)
- DOM events
- Shared global state (minimal — mostly passed via `data-*` attributes from server-rendered HTML)

### Core Modules

| File | Purpose |
|---|---|
| `main.js` | Global init: coin balance fetch, GA tracking, cookie consent, theme initialization |
| `utils.js` | `escapeHtml()`, XSS prevention helpers, common DOM utilities |
| `sidebar.js` | Sidebar open/close (legacy, mostly disabled) |
| `notifications.js` | `showToast(message, type)` — wraps Tabler toasts |
| `maintenance.js` | Detects maintenance mode, shows banner |
| `auth_forms.js` | Login/register form validation, submission, error display |
| `help-modal.js` | Help panel show/hide |
| `theme_toggle.js` (inferred) | Theme switching, localStorage persistence |

### Story & Act Modules

| File | Key Responsibilities |
|---|---|
| `story_crud.js` | `createStory()`, `updateStory()`, `deleteStory()` — wraps `/api/v1/stories` |
| `story_form_handler.js` | Form validation, submit, redirect after save |
| `story_class_crud.js` | `createStoryClass()`, `updateStoryClass()`, `deleteStoryClass()` |
| `story_associations_handler.js` | Add/remove character, location, lore item associations to stories |
| `story_generation_modal.js` | Opens generation modal, POSTs to `/api/v1/stories/generate` |
| `act_editor_main.js` | Orchestrates all act editor modules on page load |
| `act_crud.js` | `createAct()`, `updateAct()`, `deleteAct()` |
| `act_form_handler.js` | Act metadata form (title, order, summary) |
| `act_save_handler.js` | Debounced auto-save of Quill content |
| `act_ai_processor.js` | Initiates AI generation request, handles response stream |
| `act_ui_updater.js` | Updates progress bars, button states, word count |
| `act_prompt_manager.js` | Loads and applies prompt templates |
| `act_websocket_handler.js` | WebSocket lifecycle for act generation |
| `quill_setup_act.js` | Configures Quill instance for act editor |
| `act_ai_review_page.js` | Orchestrates AI review — send content, parse response |
| `scene_editor_main.js` | Scene editor orchestration (mirrors act_editor_main) |
| `scene_crud.js` | Scene CRUD |
| `scene_save_handler.js` | Scene auto-save |
| `scene_ai_processor.js` | Scene AI generation |
| `scene_websocket_handler.js` | WebSocket for scene generation |
| `scene_quill_manager.js` | Quill for scenes |
| `scene_ui_updater.js` | Scene UI updates |
| `scene_prompt_selector.js` | Prompt selection for scenes |

### World Modules

| File | Key Responsibilities |
|---|---|
| `world_crud.js` | `createWorld()`, `updateWorld()`, `deleteWorld()` |
| `world_form_handler.js` | World form validation and submit |
| `world_hierarchy.js` | Tree rendering, expand/collapse, panel resize |
| `world_map.js` | Map canvas, pinning locations |
| `world_importer_form_handler.js` | World import from document (URL/text) |
| `world_importer_from_doc_handler.js` | Import from uploaded document |
| `character_crud.js` | Character CRUD |
| `character_form_handler.js` | Character form + AI generation trigger |
| `location_crud.js` | Location CRUD |
| `location_form_handler.js` | Location form |
| `location_form_resize.js` | Resizable form panels |
| `lore_item_crud.js` | Lore item CRUD |
| `lore_item_form_handler.js` | Lore item form |

### Chat Modules

| File | Key Responsibilities |
|---|---|
| `world_chat_main.js` | Orchestrates world chat: init, event binding |
| `world_chat_context_loader.js` | Fetches and formats world context for chat |
| `world_chat_message_handler.js` | Sends messages, appends AI responses |
| `world_chat_session_manager.js` | Load/create/delete chat sessions |
| `story_chat.js` | All story chat functionality |

### Rich Text / Quill Modules

| File | Key Responsibilities |
|---|---|
| `quill_manager.js` | General-purpose Quill setup and helpers |
| `quill_setup_act.js` | Act-specific Quill config |
| `scene_quill_manager.js` | Scene-specific Quill config |
| `modules/ai_quill_toolbar.js` | Custom AI toolbar button: triggers AI generation from within editor |

### Image Modules

| File | Key Responsibilities |
|---|---|
| `image_generator.js` | Image generation form submission, provider selection |
| `image_job_monitor.js` | Polls `GET /api/v1/image-jobs/{id}` until complete |
| `modules/image_generation_modal.js` | Modal open/close, form wiring |

### Document Modules

| File | Key Responsibilities |
|---|---|
| `document_crud.js` | List, delete documents |
| `document_upload.js` | File upload with progress |
| `import_world_handler.js` | Coordinates world import flow |
| `create_from_document_handler.js` | Create world from document |

### Utility / UI Modules

| File | Key Responsibilities |
|---|---|
| `prompt_crud.js` | Prompt CRUD operations |
| `prompt_form_handler.js` | Prompt form submission |
| `social_sharing.js` | Open share dialogs for Twitter/Facebook/etc |
| `billing_dashboard.js` | Billing page interactions |
| `referral_tracking.js` | Referral link copy, tracking |
| `coin_animation.js` | CSS coin-fly animation on balance change |
| `ai_model_selector.js` | Model dropdown interactions |
| `interview.js` | Onboarding interview step flow |

### AI Review Sub-modules (`act_review_components/`)

| File | Responsibility |
|---|---|
| `api_handler_review.js` | POST content to review endpoint, parse response |
| `quill_manager_review.js` | Quill setup in review mode (read-only with highlights) |
| `text_highlighter_review.js` | Apply inline highlight ranges from AI response |
| `ui_updater_review.js` | Update review panel UI state |

---

## 7. CSS Architecture

### File Organization

```
app/static/css/
├── main.css                      # Entry point — imports all below
├── style.css                     # Legacy/additional overrides
├── story_chat.css                # Story chat page styles
├── world_chat.css                # World chat page styles
├── core/
│   ├── variables.css             # CSS custom properties (full design tokens)
│   ├── reset.css                 # Normalization
│   ├── typography.css            # Font stack, headings, text utilities
│   └── layout.css                # Grid, containers, responsive utilities
├── components/
│   ├── buttons.css               # Button variants
│   ├── cards.css                 # Card containers
│   ├── forms.css                 # Inputs, labels, validation
│   ├── navigation.css            # Nav bar, dropdowns
│   ├── help-button.css           # Help button
│   ├── help-button-layout.css    # Help button layout variants
│   ├── help-panel.css            # Slide-in help panel
│   ├── help-modal.css            # Help modal dialog
│   ├── tabler-overrides.css      # Tabler framework overrides
│   └── social-sharing.css        # Social share buttons
├── pages/
│   ├── dashboard.css             # Dashboard
│   ├── editor.css                # Act/Scene/Story editor
│   ├── auth.css                  # Login/Register
│   ├── story-wizard.css          # Story wizard
│   ├── basic-story-editor.css    # Simplified editor
│   └── basic-story-editor-extracted.css
└── modules/
    └── ai_quill_toolbar.css      # AI toolbar in Quill
```

### Design Tokens (`variables.css`)

```css
/* Primary palette */
--color-primary: #6366F1;          /* Indigo */
--color-success: #10B981;
--color-warning: #F59E0B;
--color-danger:  #EF4444;
--color-info:    #3B82F6;

/* Tabler compatibility */
--tblr-primary: var(--color-primary);
--tblr-purple: #7C3AED;
--tblr-bg-surface: #ffffff;        /* light mode */
--tblr-bg-surface-secondary: #f8fafc;

/* Spacing scale: --space-0 through --space-16 */
/* Shadow system: --shadow-sm through --shadow-2xl */
```

### Dark Mode

All CSS uses `var()` tokens. Dark mode applied via:
```css
:root[data-theme="dark"] {
  --tblr-bg-surface: #1e2130;
  --tblr-body-color: #c8d3e1;
  /* ... */
}
```

Theme detected from `localStorage` → `data-theme` attribute on `<html>` before first paint.

### Key UI Patterns

- **Hero headers:** `linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%)` with radial overlay
- **Card hover:** `translateY(-4px)` + enhanced shadow + border-color change to primary
- **Animated border:** gradient top border slides in on hover via CSS transform
- **Animations:** `fadeInUp` keyframes with staggered 0.1s delays for list items
- **Transitions:** `cubic-bezier(0.4, 0, 0.2, 1)` throughout

---

## 8. API Contracts

All API calls go to `/api/v1/`. Authentication via cookie (`credentials: 'include'`).

### Auth

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/login` | Login with email/password |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/logout` | Clear session |
| GET | `/api/v1/auth/ws-ticket` | Get WebSocket auth ticket |
| POST | `/api/v1/auth/forgot-password` | Request password reset |
| POST | `/api/v1/auth/reset-password` | Submit new password |

### Users

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update profile |
| GET | `/api/v1/billing/balance` | Get coin balance |

### Worlds

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/worlds/` | List user's worlds |
| POST | `/api/v1/worlds/` | Create world |
| GET | `/api/v1/worlds/{id}` | Get world detail |
| PUT | `/api/v1/worlds/{id}` | Update world |
| DELETE | `/api/v1/worlds/{id}` | Delete world |

### Stories

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/stories/` | List stories |
| POST | `/api/v1/stories/` | Create story |
| GET | `/api/v1/stories/{id}` | Get story |
| PUT | `/api/v1/stories/{id}` | Update story |
| DELETE | `/api/v1/stories/{id}` | Delete story |
| POST | `/api/v1/stories/generate` | AI story generation |

### Acts

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/acts/{id}` | Get act |
| POST | `/api/v1/acts/` | Create act |
| PUT | `/api/v1/acts/{id}` | Update act (content auto-save) |
| DELETE | `/api/v1/acts/{id}` | Delete act |
| POST | `/api/v1/acts/{id}/review` | Submit for AI review |

### Scenes

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/scenes/{id}` | Get scene |
| POST | `/api/v1/scenes/` | Create scene |
| PUT | `/api/v1/scenes/{id}` | Update scene |
| DELETE | `/api/v1/scenes/{id}` | Delete scene |

### World Elements

| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/v1/characters/` | List/create characters |
| GET/PUT/DELETE | `/api/v1/characters/{id}` | Manage character |
| GET/POST | `/api/v1/locations/` | List/create locations |
| GET/PUT/DELETE | `/api/v1/locations/{id}` | Manage location |
| GET/POST | `/api/v1/lore-items/` | List/create lore items |
| GET/PUT/DELETE | `/api/v1/lore-items/{id}` | Manage lore item |

### Chat Sessions

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/world-chat/sessions?world_id={id}` | List world chat sessions |
| POST | `/api/v1/world-chat/sessions` | Create session |
| DELETE | `/api/v1/world-chat/sessions/{id}` | Delete session |
| GET | `/api/v1/story-chat/sessions?story_id={id}` | List story chat sessions |
| POST | `/api/v1/story-chat/sessions` | Create session |

### Image Generation

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/images/generate` | Trigger image generation |
| GET | `/api/v1/image-jobs/{id}` | Poll job status |
| GET | `/api/v1/images/{id}` | Get image metadata |

### Documents

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/documents/` | List documents |
| POST | `/api/v1/documents/upload` | Upload document (multipart) |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Prompts

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/prompts/` | List prompts |
| POST | `/api/v1/prompts/` | Create prompt |
| PUT | `/api/v1/prompts/{id}` | Update prompt |
| DELETE | `/api/v1/prompts/{id}` | Delete prompt |

### AI Models

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/ai-models/` | List available AI models |
| GET | `/api/v1/ai-model-configs/` | Get model configurations |

### Associations

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/associations/` | Add element association (story↔character etc.) |
| DELETE | `/api/v1/associations/{id}` | Remove association |

---

## 9. WebSocket Protocols

### Act Generation

**Endpoint:** `ws://{host}/ws/stories/{storyId}/acts/{actId}/generate?ticket={token}`

**Flow:**
1. Frontend fetches ticket: `GET /api/v1/auth/ws-ticket`
2. Opens WebSocket with ticket in query string
3. Sends start message:
   ```json
   {
     "type": "start",
     "prompt_id": "optional-prompt-id",
     "model_id": "optional-model-id",
     "context": "optional-additional-context"
   }
   ```
4. Receives streaming messages:
   ```json
   { "type": "text", "content": "partial text chunk" }
   { "type": "complete", "total_tokens": 1234, "cost": 0.05 }
   { "type": "error", "message": "error description" }
   ```
5. `text` chunks are appended to Quill editor in real-time
6. `complete` updates token count and coin balance display

### Scene Generation

**Endpoint:** `ws://{host}/ws/stories/{storyId}/scenes/{sceneId}/generate?ticket={token}`

Identical message protocol to act generation.

### World Chat

**Endpoint:** `ws://{host}/ws/worlds/{worldId}/chat?ticket={token}&session_id={id}`

**Messages (client → server):**
```json
{ "type": "message", "content": "user message text" }
```

**Messages (server → client):**
```json
{ "type": "text", "content": "partial AI response" }
{ "type": "complete", "cost": 0.03 }
{ "type": "context_loaded", "element_count": 5 }
{ "type": "error", "message": "..." }
```

### Story Chat

**Endpoint:** `ws://{host}/ws/stories/{storyId}/chat?ticket={token}&session_id={id}`

Same message protocol as world chat.

---

## 10. Rich Text Editing

### Quill.js Configuration

Version: 1.3.6 (CDN)

**Toolbar configuration (act/scene editors):**
- Text formatting: Bold, Italic, Underline, Strike
- Headings: H1, H2, H3
- Lists: Ordered, Unordered
- Blockquote, Code Block
- Link insertion
- Clean (remove formatting)
- **AI Generation button** (custom — triggers WebSocket generation)

**Custom Module: AI Quill Toolbar** (`modules/ai_quill_toolbar.js`)
- Registers a custom Quill module
- Adds "Generate with AI" button to toolbar
- On click: reads current document, triggers act/scene generation

**Content Format:**
- Stored as HTML (Delta converted to HTML)
- Sent to API as HTML string in `content` field
- Word count calculated from plain text extraction

**Auto-save:**
- Debounced 2 seconds after last keystroke
- `PUT /api/v1/acts/{id}` or `PUT /api/v1/scenes/{id}` with content
- Visual indicator in UI ("Saving..." → "Saved")

---

## 11. Feature Areas in Detail

### 11.1 AI-Assisted Writing (Act/Scene Editors)

The core writing experience:

1. User opens Act or Scene editor
2. Page loads with existing content in Quill editor
3. User can type normally — auto-save fires after 2s idle
4. User selects a **prompt** (from prompt library or custom)
5. User selects an **AI model** (from model selector)
6. User clicks "Generate" — WebSocket opens, AI streams content into editor
7. User can stop generation, undo, or continue editing
8. After generation: token count and cost displayed
9. AI Review: user can send act to review endpoint, see highlighted suggestions inline

**Key data passed to AI:**
- Current act/scene content
- Story metadata (title, genre, world)
- Linked characters, locations, lore items
- Selected prompt template
- World context (via RAG/direct context)

### 11.2 World Chat

AI conversation scoped to a world:

1. User opens World Chat
2. Session selector shows previous sessions (or "New Chat")
3. User types message — sends via WebSocket
4. Context loader assembles: world description + all characters + all locations + all lore items
5. AI responds with streaming text
6. Response appended to chat thread
7. Session persisted — user can return to previous conversations

### 11.3 Image Generation

1. User clicks "Generate Image" on character/location/story
2. Modal opens with visual prompt (pre-filled from element description)
3. User selects aspect ratio (portrait/landscape/square)
4. User selects AI provider (DALL-E 3 or RunPod)
5. POST to `/api/v1/images/generate` → returns `job_id`
6. `image_job_monitor.js` polls `GET /api/v1/image-jobs/{job_id}` every 2s
7. On completion: image URL displayed in modal
8. User can save as profile image for the element

### 11.4 World Import from Document

1. User uploads PDF/text document to Document Manager
2. User navigates to "Import from Document"
3. Selects document → POST to import endpoint
4. Background job runs: AI extracts characters, locations, lore items from text
5. User reviews extracted elements before confirming
6. Elements created in selected world

### 11.5 Story Wizard

Multi-step creation flow:
1. **Step 1:** Choose or create a world
2. **Step 2:** Enter story concept/premise
3. **Step 3:** Select genre, tone, narrative style
4. **Step 4:** AI generates outline (acts list)
5. **Step 5:** Review and confirm — story + acts created

### 11.6 Associations

World elements can be linked to stories, acts, and scenes:
- **Link Character Modal:** search/filter characters → click to link
- **Link Location Modal:** same pattern for locations
- **Link Lore Item Modal:** same pattern for lore items
- Linked elements appear as chips/tags in the editor sidebar
- Associations feed context to AI generation

---

## 12. Admin Surfaces

All require `is_admin=True` on user record.

| Page | Route | Template | Purpose |
|---|---|---|---|
| Admin Dashboard | `/ui/admin` | `admin_dashboard.html` | Overview with key metrics |
| User Management | `/ui/admin/users` | `admin_users.html` | List, search, ban, modify users |
| Billing Admin | `/ui/admin/billing` | `admin_billing_dashboard.html` | Coin grants, transaction review |
| News Manager | `/ui/admin/news` | `admin_news.html` | Create/edit news posts |
| CTA Manager | `/ui/admin/cta` | `admin_cta_manager.html` | Manage call-to-action banners |
| Maintenance | `/ui/admin/maintenance` | `admin_maintenance.html` | Enable/disable maintenance mode |
| Help Editor | `/ui/admin/help` | `admin_help_editor.html` | Edit in-app help HTML |
| Image Jobs | `/ui/admin/image-jobs` | `admin_image_jobs.html` | Monitor image generation jobs |
| User Email | `/ui/admin/email` | `admin_user_email.html` | Send email to users |

---

## 13. Public (Unauthenticated) Routes

These pages work without authentication:

| Page | Route | Template | Notes |
|---|---|---|---|
| World Gallery | `/public/gallery` | `public_world_gallery.html` | Browse public worlds |
| Public World Chat | `/public/chat/{world_id}` | `public_world_chat.html` | Chat with world AI, anonymous |
| Image Preview | `/public/image/{id}` | `image_preview.html` | View shared image |
| Image Share | `/public/image/{id}/share` | `image_share.html` | Social share image |
| Published Story | `/public/stories/{id}` | `view_published_story.html` | Read published story |
| Blog | `/blog`, `/blog/post/{slug}` | blog templates | Public blog |
| Login/Register | `/auth/*` | auth templates | Auth forms |
| Terms/Privacy | `/terms`, `/privacy` | terms/privacy templates | Legal |

Anonymous users get a temporary session ID stored in a cookie. Public chat uses this for session tracking.

---

## 14. Routing Map

Complete route inventory (view routes only — excludes API routes):

```
/                               → Home (news feed, featured worlds, published stories)
/auth/login                     → Login
/auth/register                  → Register
/auth/forgot-password           → Forgot password
/auth/reset-password            → Reset password

/ui/stories                     → My Stories list
/ui/stories/new                 → Create story form
/ui/stories/{id}                → Story detail
/ui/stories/{id}/edit           → Edit story
/ui/stories/wizard              → Story creation wizard
/ui/stories/{id}/chat           → Story chat

/ui/acts/{id}                   → Act editor
/ui/acts/{id}/review            → Act AI review
/ui/scenes/{id}                 → Scene editor

/ui/story-classes               → Story classes list

/ui/basic-stories/new           → Basic story create
/ui/basic-stories/{id}          → Basic story editor

/ui/worlds/                     → My Worlds list
/ui/worlds/create               → Create world
/ui/worlds/{id}                 → World detail
/ui/worlds/{id}/edit            → Edit world
/ui/worlds/{id}/characters      → Characters list
/ui/worlds/{id}/locations       → Locations list
/ui/worlds/{id}/lore-items      → Lore items list
/ui/worlds/{id}/hierarchy       → Hierarchy tree view
/ui/worlds/{id}/builder         → World builder wizard
/ui/worlds/{id}/chat            → World chat
/ui/worlds/{id}/map             → World map
/ui/worlds/import-from-document → Import world from document
/ui/worlds/import-from-book     → Import from book
/ui/worlds/create-from-document → Create from document

/ui/characters/new              → Create character
/ui/characters/{id}/edit        → Edit character
/ui/locations/new               → Create location
/ui/locations/{id}/edit         → Edit location
/ui/lore-items/new              → Create lore item
/ui/lore-items/{id}/edit        → Edit lore item

/ui/prompts                     → Prompt library
/ui/prompts/new                 → Create prompt
/ui/prompts/{id}/edit           → Edit prompt

/ui/documents                   → Document manager

/ui/account                     → My account
/ui/account/edit                → Edit profile
/ui/billing                     → Billing dashboard
/ui/referrals                   → Referral program
/ui/welcome-interview           → Onboarding interview
/ui/guide                       → User guide
/ui/ai-models                   → AI models info

/ui/published-stories           → Published stories gallery

/ui/admin                       → Admin dashboard
/ui/admin/users                 → Admin user management
/ui/admin/billing               → Admin billing
/ui/admin/news                  → Admin news
/ui/admin/cta                   → Admin CTA manager
/ui/admin/maintenance           → Maintenance controls
/ui/admin/help                  → Help content editor
/ui/admin/image-jobs            → Image job monitor
/ui/admin/email                 → User email tool

/forum                          → Forum home
/forum/category/{slug}          → Forum category
/forum/thread/{id}              → Forum thread

/blog                           → Blog index
/blog/post/{slug}               → Blog post
/blog/editor                    → Blog editor
/blog/editor/{id}               → Edit blog post
/blog/admin/list                → Admin blog list

/public/gallery                 → Public world gallery
/public/chat/{world_id}         → Public world chat
/public/image/{id}              → Image preview
/public/stories/{id}            → Published story reader

/terms                          → Terms of use
/terms-of-service               → Terms of service
/privacy                        → Privacy policy
```

---

## 15. State & Data Patterns

### Server-Rendered Data

The Jinja2 templates inject data into the page as:
- Direct HTML rendering of values
- `data-*` attributes on elements (e.g., `data-story-id="123"`)
- Inline `<script>` blocks with JSON: `const STORY_DATA = {{ story | tojson }};`

JavaScript reads these on page load to initialize its state.

### Client State

No global state manager. State is held in:
- Module-level variables within each JS file
- DOM attributes updated by JS
- `localStorage` for user preferences (theme, model selection)

### Optimistic Updates

Most CRUD operations:
1. Send API request
2. On success: update DOM (add/remove/update element)
3. On failure: show toast error, revert DOM change

### Loading States

- Buttons disabled with spinner icon during API calls
- Tabler indeterminate progress bars for long operations
- "Saving..." text indicator during auto-save

### Error Handling

- `showToast(message, 'error')` for API errors
- Form validation errors displayed inline below fields
- WebSocket errors shown in editor status bar

---

## 16. Theme System

### Detection Priority
1. `localStorage.getItem('theme')` — user preference
2. `window.matchMedia('(prefers-color-scheme: dark)')` — system preference
3. Default: light

### Application
- Set `data-theme="dark"` (or `"light"`) on `<html>` element
- All Tabler CSS variables respond to this attribute
- Custom CSS variables in `variables.css` also respond

### Toggle
- Toggle button in top navigation bar
- Stores new value to `localStorage`
- Smooth CSS transition on all themed properties

---

## 17. Billing & Coin System

### Coin Balance
- Displayed in top navigation bar as a badge
- Loaded on every page via `GET /api/v1/billing/balance`
- Updated after AI operations that consume coins
- Animated coin-fly effect on balance change (`coin_animation.js`)

### Cost Display
- AI generation shows token count and coin cost on completion
- Chat messages show per-message cost
- Billing dashboard shows full transaction history

### Operations That Consume Coins
- Act/Scene AI generation (WebSocket)
- World/Story chat messages
- Image generation
- AI text transformation
- Story brainstorm/outline generation

---

## 18. Analytics & Tracking

### Google Analytics
- GA4 integration loaded in `base.html`
- Consent mode support (deferred until cookie consent)
- Page view tracking automatic via GA
- Custom events tracked in `main.js` and feature JS files

### Cookie Consent
- Banner shown on first visit (bottom of page)
- Gradient styled (indigo→purple)
- Two options: Accept / Decline
- Choice stored in `localStorage`
- GA and other tracking activated only on accept

### Application Analytics
- `bot_analytics` router tracks bot/crawler visits separately
- User activity logged to `user_activities` table
- AI cost logs stored per-operation in `ai_cost_logs` table

---

## Appendix: Email Templates

For reference — these are transactional emails sent by the backend, not frontend pages. They use `app/templates/emails/`:

| Template | Purpose |
|---|---|
| `base.html` | Email wrapper |
| `welcome.html` | Welcome email on registration |
| `password_reset.html` | Password reset link |
| `story_completion.html` | Story generation completion notification |
| `maintenance.html` | Maintenance mode notification |
| `test.html` | Test/debug email |

---

*This document was generated from the existing codebase as of 2026-03-30 to serve as the specification for the React frontend rewrite.*
