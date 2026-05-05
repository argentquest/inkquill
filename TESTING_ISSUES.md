# Care Circle App — Testing Issues

**Tester:** Eric Silver  
**Date:** 2026-05-03  
**Session:** Manual exploratory testing

---

## Open Issues

### ~~Issue 1~~ ✅ RESOLVED — Blog creation restricted to non-admin users
**Area:** Blog  
**Type:** Access Control / Bug  
**Estimate:** `S`  
**Rationale:** Likely a single permission check/guard on the blog creation route — find the check, extend it to any `is_admin` user.  
**Description:** Creating a blog should be available to any user with admin privileges. Currently this capability appears to be gated beyond admin access.  
**Expected:** Any admin user can create a blog.  
**Actual:** Blog creation is not accessible to all admins.

---

### ~~Issue 2~~ ✅ RESOLVED — Search button visible on pages other than Blog and Forum
**Area:** Navigation / UI  
**Type:** Bug  
**Estimate:** `S`  
**Rationale:** Conditional render based on the active route — hide the button everywhere except the Blog and Forum pages.  
**Description:** The Search button should only appear on the Blog page and the Forum page. It is currently visible elsewhere.  
**Expected:** Search button shown only on Blog and Forum pages.  
**Actual:** Search button appears on pages where it should be hidden.

---

### ~~Issue 3~~ ✅ RESOLVED — "Stories" button visible in public / care-circle context
**Area:** Navigation / UI  
**Type:** Bug  
**Estimate:** `S`  
**Rationale:** Same pattern as Issue 2 — gate the Stories nav item on the Storytelling app context only.  
**Description:** The "Stories" button is visible publicly and within the care-circle (circle-friends) context, where it does not belong. Stories is a feature of the Storytelling app only — circle-friends has no stories feature.  
**Expected:** Stories button visible only within the Storytelling app context, not in public views or circle-friends pages.  
**Actual:** Stories button is shown publicly and in circle-friends context.

---

### ~~Issue 4~~ ✅ RESOLVED — Circle-friends home page has two menus; should have one
**Area:** Circle-Friends / Navigation / UI  
**Type:** Bug / UX  
**Estimate:** `M`  
**Rationale:** Requires identifying both menu components, removing one, and migrating the preferred layout into the shared header — touches layout, routing, and possibly the header component.  
**Description:** The circle-friends home page is displaying two menus. There should only be one. The preferred layout is from the second (lower) menu, which should be consolidated into the common header at the top, replacing or merging with the first menu.  
**Expected:** Single navigation menu using the second menu's layout, integrated into the common header.  
**Actual:** Two separate menus visible on the circle-friends home page.

---

### ~~Issue 5~~ ✅ RESOLVED — Care-circle family page has 11+ blocks needing grouping
**Area:** Circle-Friends / `/care-circle-family`  
**Type:** UX / Layout  
**Estimate:** `M`  
**Rationale:** Requires auditing all blocks, designing category groupings, and adding section headers with visual separation. Accounting reorder adds a small ordering constraint. No backend changes expected.  
**Description:** The care-circle family page (`/care-circle-family`) displays more than 11 blocks without any categorization, making the page hard to navigate. Blocks should be grouped into logical categories. Accounting-related blocks should be placed at the bottom.  
**Expected:** Blocks grouped by category; accounting group at the bottom of the page.  
**Actual:** 11+ ungrouped blocks displayed on the page.

**Fix notes:** Expanded the landing page to show route cards for all sub-features and grouped them under sections: Care & Circle, Community, Account, Admin (conditional), and Accounting (bottom). Sections use `text-sm font-semibold uppercase tracking-[0.2em]` headers.

---

### ~~Issue 6~~ ✅ RESOLVED — Replace block icons with larger custom SVGs on care-circle family page
**Area:** Circle-Friends / `/care-circle-family`  
**Type:** UX / Visual Design  
**Estimate:** `L`  
**Rationale:** Each of the 11+ blocks needs a unique, purpose-built SVG illustration. Design + production of that many SVGs is the bulk of the work; wiring them into the component is straightforward once assets exist.  
**Description:** The blocks on the care-circle family page currently use small generic icons. Each block should have a custom SVG illustration generated for it, displayed at a larger size to improve visual appeal and clarity.  
**Expected:** Each block has a unique, larger SVG graphic instead of a small icon.  
**Actual:** Blocks use small generic icon fonts.

**Fix notes:** Created `frontendv1/components/care-circle-family/care-circle-feature-icons.tsx` with 14 purpose-built inline SVGs (56×56 viewBox, rendered at `h-9 w-9`). Each card now shows a distinctive, larger icon inside a `h-14 w-14` container.

---

### ~~Issue 7~~ ✅ RESOLVED — Admin menu items should be consolidated under an "Admin" submenu
**Area:** Navigation / Menu  
**Type:** UX / Organization  
**Estimate:** `S`  
**Rationale:** Restructuring existing menu items into a nested submenu — no new features, just reorganization of the nav config/component.  
**Description:** The navigation menu currently has admin-related items scattered at the top level. All admin items should be grouped under a single "Admin" submenu entry to keep the menu clean and role-appropriate.  
**Expected:** A top-level "Admin" menu item with all admin-related items as submenus beneath it.  
**Actual:** Admin-related items appear as standalone top-level menu entries.

---

### ~~Issue 8~~ ✅ RESOLVED — Home page app cards: remove "Shared platform" tag; update Care Circle Family description
**Area:** Home Page / App Cards  
**Type:** Content / UX  
**Estimate:** `XS`  
**Rationale:** Pure copy/content change — remove a label, update description text and badge tags. No logic changes.  
**Description:** Two changes to the home page app cards:  
1. Remove the "Shared platform" label/badge — it should not appear on any card.  
2. The **Care Circle Family** card description should be updated to:

> Family-side coordination, events, friends, and household-owned billing live here.

With capability badges/tags:
- Family scope
- Realtime ready

**Expected:** No "Shared platform" label visible; Care Circle Family card shows updated description and capability tags.  
**Actual:** "Shared platform" label present; card descriptions are minimal/incorrect.

---

### ~~Issue 9~~ ✅ RESOLVED — Patients page: add Table of Contents for quick jump to each person's block
**Area:** Circle-Friends / `/care-circle-family/patients`  
**Type:** UX / Feature  
**Estimate:** `S`  
**Rationale:** Add anchor IDs to each friend block and render a TOC strip at the top from the same data list. Frontend-only, no backend changes.  
**Description:** The patients page displays a block for each friend/patient, which is a good concept. However, when the list grows long, users need a fast way to navigate. A sticky or top-of-page Table of Contents (TOC) should list each person's name as a clickable anchor link that scrolls/jumps the browser to their corresponding block.  
**Expected:** TOC strip at the top of the page with each friend's name as a clickable in-page anchor link jumping to their block.  
**Actual:** No TOC; user must scroll through all blocks manually.

---

### ~~Issue 10~~ ✅ RESOLVED — Patients page: show basic stats on each friend's block
**Area:** Circle-Friends / `/care-circle-family/patients`  
**Type:** Feature / UX  
**Estimate:** `M`  
**Rationale:** Requires backend queries for join date and newsletter-sent count per patient, surfacing them in the API response, and rendering a stats row in the frontend card component.  
**Description:** Each friend's block on the patients page should display key stats at a glance to give context without navigating away. Requested stats include:
- **Joined** — date the friend was added to the circle
- **Newsletters mailed** — count of newsletters sent to this friend

Additional stats may be added over time.  
**Expected:** Each friend block shows a small stats row with joined date and newsletter count.  
**Actual:** No stats visible on friend blocks.

---

### ~~Issue 11~~ ✅ RESOLVED — Patient edit page too long; reorganize into tabs
**Area:** Circle-Friends / `/care-circle-family/patients/17?edit=1`  
**Type:** UX / Layout  
**Estimate:** `L`  
**Rationale:** Requires auditing every block on the page, mapping each to a tab, implementing the tab shell, and ensuring form state and validation work across tabs. No backend changes expected, but the frontend refactor is significant.  
**Description:** The patient edit page is excessively long and requires heavy scrolling to reach all sections. The page should be restructured into a tab-based layout, grouping related fields together so users can navigate between sections without scrolling.  
**Expected:** Each existing block/section on the page becomes its own tab. Tab names and grouping to be determined by inspecting the page blocks.  
**Actual:** All fields rendered in a single long scrolling page.

**Fix notes:** The patient detail page already had top-level tabs (Overview, Edit Profile, Preferences, Providers, Newsletter). Added a secondary tab bar inside the **Edit Profile** tab with 5 sub-tabs: Family & Access, Schedule & Location, Identity & Background, People & Interests, and Image Sign-in. Also enriched the **Overview** tab to display preferences, hobbies, and family members so key data is visible immediately without tab switching.

---

### ~~Issue 12~~ ✅ RESOLVED — Media page: image previews not working
**Area:** Circle-Friends / `/care-circle-family/media`  
**Type:** Bug  
**Estimate:** `S`  
**Rationale:** Root cause is already identified — a path mismatch between where files are stored and the URL the backend generates. Fix is a targeted change to one or two files.  
**Description:** Image previews on the media page are not rendering/displaying correctly.  
**Expected:** Uploaded images display as visual thumbnails/previews on the media page.  
**Actual:** Image previews are broken or not showing.

**Root cause identified:** Path mismatch between storage and URL generation.
- Files are stored at `runtime/data/uploads/blog_media/` (set by `LOCAL_STORAGE_BASE_PATH` + `LOCAL_STORAGE_BLOG_MEDIA_PATH` in config)
- `LocalStorageProvider._get_public_url` hardcodes the URL as `/static/uploads/blog/{path}`, pointing to `app/static/uploads/blog/` — a directory that does not exist
- FastAPI only mounts `app/static/` as `/static` ([app/main.py:258](app/main.py))
- Relevant files: [app/services/storage/local_storage.py](app/services/storage/local_storage.py) · [app/routers/blog_media.py](app/routers/blog_media.py) · [app/core/config.py](app/core/config.py)

**Fix notes:**
- Updated `_get_public_url` in `LocalStorageProvider` to return `/uploads/blog/{path}` instead of the misaligned `/static/uploads/blog/{path}`.
- Added an explicit `app.mount("/uploads/blog", StaticFiles(...))` in `main.py` pointing to `LOCAL_STORAGE_BASE_PATH / LOCAL_STORAGE_BLOG_MEDIA_PATH`, ensuring the URL route matches the physical storage directory used by the upload router.
- `blog_media.py` instantiates `LocalStorageProvider(str(UPLOAD_DIR))`, so storage path and public URL generation are now fully aligned.

---

### ~~Issue 13~~ ✅ RESOLVED — Forums have no categories; seed app-scoped categories for Circle Friends and Storytelling
**Area:** Forums  
**Type:** Missing Data / Feature  
**Estimate:** `M`  
**Rationale:** Requires wiring app-scoping to the forum category model (if not already there), writing a seed/migration for the categories, and verifying the forum UI filters by app context. Content is defined (see below).  
**Description:** The forum has no categories configured. Each app should have its own scoped forum categories. Proposed seed categories below.

**Circle Friends — 5 categories:**
| # | Name | Purpose |
|---|------|---------|
| 1 | Care Tips & Resources | Caregiving advice, medical info, daily routines, and best practices |
| 2 | Family Coordination | Planning, schedules, events, and logistics for the care circle |
| 3 | Memory Lane | Sharing memories, photos, and stories about friends and loved ones |
| 4 | Wellness & Activities | Ideas for outings, activities, and keeping friends engaged |
| 5 | Getting Help | Questions about using the Circle Friends app and troubleshooting |

**Storytelling — 5 categories:**
| # | Name | Purpose |
|---|------|---------|
| 1 | Story Feedback & Critique | Share works-in-progress and get reader feedback |
| 2 | World Building | Discuss worlds, lore, settings, and fictional history |
| 3 | Character Workshop | Character development, backstories, and motivation deep-dives |
| 4 | Writing Craft & Tips | General writing advice, prompts, and technique discussions |
| 5 | AI Collaboration | Strategies for working with AI tools, prompt tips, and generation techniques |

**Expected:** Forum shows the above categories scoped to the active app context.  
**Actual:** Forum shows no categories.

**Fix notes:**
- Added `app_source` column to `ForumCategory` model with a composite unique constraint on `(app_source, slug)`.
- Created Alembic migration `j6k7l8m9n0o1_add_app_source_to_forum_categories.py`.
- Updated CRUD, schemas, and router to support filtering by `app_source`.
- Created `scripts/seed_forum_categories.py` to insert the 10 defined categories.
- Updated frontend `fetchForumCategories` to accept an `app_source` param.
- Updated `/community/forums` and `/community/forums/new` to read `?app_source` and filter categories/threads accordingly.

---

### ~~Issue 14~~ ✅ RESOLVED — Home page of each app should surface recent blogs and forum activity
**Area:** Home Page / Circle Friends & Storytelling  
**Type:** Feature  
**Estimate:** `M`  
**Rationale:** Needs two new backend queries (recent posts + recent forum threads scoped by app), API endpoints or inclusion in the home page data fetch, and two new frontend sections. Straightforward but touches both ends of the stack.  
**Description:** Each app's home page should display a community activity snapshot to encourage engagement. The content should be scoped to the active app.

**Required sections:**
- **Recent Blog Posts** — 3 most recent published blog posts, showing title, author, and date
- **Recent Forum Posts** — Last 10 forum posts, showing thread title, category, author, and timestamp

**Expected:** Both sections visible on each app's home page, filtered to that app's context.  
**Actual:** No blog or forum activity surfaced on app home pages.

**Fix notes:** Added "Recent Blog Posts" (up to 3) and "Recent Forum Posts" (up to 10) sections to both `/care-circle-family` and `/storytelling` home pages. Uses existing `fetchBlogPosts({ app_source })` and `fetchForumThreads({ app_source })` endpoints. Sections render conditionally when data exists. Updated Playwright mock helpers to return app-scoped data and filter by `app_source`.

---

## Resolved Issues

All issues from this testing session have been resolved.

| # | Title | Resolution |
|---|-------|------------|
| 1 | Blog creation restricted to non-admin users | Fixed permission check on blog creation route. |
| 2 | Search button visible on pages other than Blog and Forum | Added conditional route-based visibility. |
| 3 | "Stories" button visible in public / care-circle context | Scoped Stories nav to Storytelling app only. |
| 4 | Circle-friends home page has two menus | Consolidated into single header menu. |
| 5 | Care-circle family page has 11+ blocks needing grouping | Grouped cards by category with Accounting at bottom. |
| 6 | Replace block icons with larger custom SVGs | Added 14 custom inline SVGs at larger size. |
| 7 | Admin menu items should be consolidated under an "Admin" submenu | Restructured nav into nested Admin submenu. |
| 8 | Home page app cards: remove "Shared platform" tag; update Care Circle Family description | Removed badge and updated copy. |
| 9 | Patients page: add Table of Contents for quick jump | Added anchor TOC strip at top of patients list. |
| 10 | Patients page: show basic stats on each friend's block | Added Joined date and Newsletters mailed count. |
| 11 | Patient edit page too long; reorganize into tabs | Added 5 sub-tabs inside Edit Profile; enriched Overview tab. |
| 12 | Media page: image previews not working | Fixed path mismatch between storage and URL generation. |
| 13 | Forums have no categories; seed app-scoped categories | Added `app_source` to categories, seeded 10 categories, updated UI filters. |
| 14 | Home page of each app should surface recent blogs and forum activity | Added Recent Blog Posts and Recent Forum Posts sections to both app home pages. |

---

## Notes

_Add session-level observations here._
