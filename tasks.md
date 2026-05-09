# Hub Page Editorial Redesign — Tasks

## Status Key
- [x] Completed
- [ ] Pending

---

## Overview

This redesign applies the editorial look-and-feel from `care-circle-family.jsx` (the approved dashboard mockup) to all three hub pages in the Next.js app: **Care Circle Family**, **Storytelling**, and **Chatbot**.

The guiding principle is a **broadsheet newspaper aesthetic** — warm, typographic, unhurried. Pages feel like a curated daily edition rather than a generic SaaS dashboard. Navigation is structural; the sidebar is editorial.

The newsletter (Care Circle email) was already redesigned with the Ellis theme. This task brings the same design language into the web app shell.

---

## Design Language

### Colour Palette
| Token | Hex | Role |
|---|---|---|
| `ink-900` | `#231913` | Primary text, headings |
| `ink-600` | `#6b5c52` | Secondary text, section labels |
| `ink-400` | `#a89080` | Tertiary text, metadata |
| `ember` | `#d86c3d` | Accent — links, dots, highlights |
| `forest` | `#1f3b36` | Deep accent — eyebrow labels, gradient start |
| `paper` | `#fcfaf6` | Page background |
| `white/70–80` | — | Card surfaces (glass-like layering) |

### Typography
- **Display / headings** — `font-display` = EB Garamond, serif. Used in `PageHeader` h1 and section titles.
- **Body / UI** — `font-sans` = Lora, serif. Used in card labels, descriptions, metadata.
- **Section labels** — `text-sm font-semibold uppercase tracking-[0.2em]` in `ink-600`. Mimics a newspaper's column header rule.

### Surfaces & Depth
Cards use a **layered glass effect**: `bg-white/70`, `border border-black/10`, `shadow-panel`, `rounded-[24px]` or `rounded-[28px]`. On hover, border darkens to `black/20` and background brightens to `bg-white`. This gives tactile depth without heavy shadows.

The `PageHeader` has a **warm gradient background** (paper → ember glow at bottom-right) with a forest→ember vertical accent bar on the left edge and an ember dot before the eyebrow label.

### Spacing & Layout
- Section gaps: `space-y-8` between sections
- Card grids: `gap-4`, responsive `sm:grid-cols-2 lg:grid-cols-3` (or 4 for storytelling)
- Two-column layout at `xl`: main content (`flex-1 min-w-0`) + fixed sidebar (`w-72 shrink-0`), hidden below xl
- Page content wrapped in `space-y-8` outer container

---

## Visual Structure (per hub page)

```
┌─────────────────────────────────────────────────────┐
│  PageHeader (eyebrow · h1 · description)            │
│  Warm gradient, forest→ember accent bar             │
├──────────────────────────────────┬──────────────────┤
│  SectionHeading "Care & Circle"  │                  │
│  Section A · Manage all →        │  HubSidebar      │
│  ┌──────┐ ┌──────┐ ┌──────┐     │                  │
│  │ Card │ │ Card │ │ Card │     │  ┌─────────────┐ │
│  └──────┘ └──────┘ └──────┘     │  │ Blog posts  │ │
│                                  │  └─────────────┘ │
│  SectionHeading "Community"      │  ┌─────────────┐ │
│  Section B · All threads →       │  │Forum threads│ │
│  ┌──────┐ ┌──────┐ ┌──────┐     │  └─────────────┘ │
│  │ Card │ │ Card │ │ Card │     │                  │
│  └──────┘ └──────┘ └──────┘     │  (hidden < xl)   │
├──────────────────────────────────┴──────────────────┤
│  (no bottom RecentSection — content moved to sidebar)│
└─────────────────────────────────────────────────────┘
```

---

## New Components

### `SectionHeading` — `frontendv1/components/shell/section-heading.tsx`
**[x] Done**

Replaces the ad-hoc `<h2>` section labels across hub pages. Modelled on the `.ccfh-sec` row from the JSX mockup: newspaper section rule with optional section identifier on the left and a right-aligned action link.

```
Care & Circle          Section A · Manage all →
──────────────────────────────────────────────
```

Props:
- `title` — e.g. `"Care & Circle"`
- `meta` — optional secondary label, e.g. `"Section A"` (rendered in `ink-400`, smaller)
- `action` — optional `{ label, href }` for a right-side text link in `ember`

Styling: `flex items-baseline justify-between`. Label: `text-sm font-semibold uppercase tracking-[0.2em] text-ink-600`. Meta: `text-xs text-ink-400`. Action link: `text-xs text-ember hover:underline`.

---

### `HubSidebar` — `frontendv1/components/shell/hub-sidebar.tsx`
**[x] Done**

A right-hand editorial sidebar that surfaces community content (blog posts, forum threads) alongside the main nav grid. Modelled on the `.ccfh-stack` aside from the JSX mockup — stacked cards with section headings and action links.

- Returns `null` if both arrays are empty (no blank sidebar space)
- Shows up to 4 items per section
- Each item is a bordered card link with title + metadata line
- Uses `SectionHeading` internally for the "Blog" and "Forum" sub-headings
- Marked `"use client"` for future interactivity headroom; currently pure display
- Hidden below `xl` breakpoint (sidebar wraps under main content at smaller sizes — the grid cards remain primary)

Data sources (existing API, no new endpoints needed):
- `fetchBlogPosts({ app_source })` from `@/lib/api`
- `fetchForumThreads({ app_source })` from `@/lib/api`

---

## Page Updates

### `frontendv1/app/care-circle-family/page.tsx`
**[ ] Pending**

**Before:** Plain welcome line, inline `SectionHeader` function, sections stacked full-width, blog/forum appear at the bottom in a `RecentSection` block only when data exists.

**After:**
1. **PageHeader** at the top — `eyebrow="Care Circle Family"`, personalised `title` using `user.display_name`, `description="Manage your care circle, contribute to daily editions, and stay connected with family."` Visually matches the masthead from the mockup.
2. **SectionHeading** replaces the local `SectionHeader` fn everywhere. Two sections get editorial metadata:
   - "Care & Circle" → `meta="Section A"`, `action={{ label: "Manage all", href: "/care-circle-family/members" }}`
   - "Community" → `meta="Section B"`, `action={{ label: "All threads", href: "/community/forums" }}`
   - Account / Admin / Accounting — title only (no meta needed)
3. **Two-column layout** at `xl`: card grids live in `flex-1`, sidebar in a `w-72 hidden xl:block` column.
4. **HubSidebar** in the right column, fed by existing `useQuery` calls for `app_source: "care-circle"`.
5. **Remove** the conditional `RecentSection` block at the bottom — that content now lives in the sidebar permanently.
6. **Remove** the local `SectionHeader`, `RecentSection`, `BlogRow`, `ForumRow` component functions (all replaced by shared components).

---

### `frontendv1/app/storytelling/page.tsx`
**[ ] Pending**

**Before:** `PageHeader` present. Inline `<h2 className="text-sm font-semibold uppercase...">` headings. `RecentSection` block at the bottom.

**After:**
1. **SectionHeading** replaces the two inline `<h2>` headings:
   - "Product" → `<SectionHeading title="Product" />`
   - "Account & Tools" → `<SectionHeading title="Account & Tools" />`
2. **Two-column layout** at `xl`, same pattern as care-circle page.
3. **HubSidebar** fed by `app_source: "storytelling"` data. `blogHref="/storytelling/blog"`, `forumHref="/community/forums"`.
4. **Remove** the conditional `RecentSection` block at the bottom.
5. **Remove** local `RecentSection`, `BlogRow`, `ForumRow` component functions.

---

### `frontendv1/app/chatbot/page.tsx`
**[ ] Pending**

**Before:** `PageHeader` with developer-note copy:
- title: `"A narrow conversation surface before deeper app work."`
- description: `"Chatbot becomes the third application on the shared platform and the first one delivered as a clean chat-first UI."`

These are internal planning notes, not user-facing copy.

**After:** Replace with product copy:
- `title`: `"Your AI assistant"`
- `description`: `"Ask anything, brainstorm ideas, or get quick answers — a focused AI chat workspace."`

No structural changes — `ChatbotWorkspace` stays exactly as-is.

---

## Files Changed

| File | Status | Type |
|---|---|---|
| `frontendv1/components/shell/section-heading.tsx` | ✅ Done | New |
| `frontendv1/components/shell/hub-sidebar.tsx` | ✅ Done | New |
| `frontendv1/app/care-circle-family/page.tsx` | ✅ Done | Edit |
| `frontendv1/app/storytelling/page.tsx` | ✅ Done | Edit |
| `frontendv1/app/chatbot/page.tsx` | ✅ Done | Edit |

---

## Verification

- [x] Run `npm run build` inside `frontendv1/` — no TypeScript errors
- [ ] `/care-circle-family` — PageHeader renders with warm gradient, section headings show meta + action links, sidebar appears at xl with blog/forum cards, no bottom RecentSection
- [ ] `/storytelling` — SectionHeading headings, sidebar at xl, no bottom RecentSection
- [ ] `/chatbot` — PageHeader shows user-facing product copy
- [ ] Resize viewport below `xl` (< 1280px) — sidebar hides, main card grid fills full width cleanly
- [ ] Dark mode — card surfaces use `bg-[var(--bg-card-strong)]` logic via CSS vars (white/70 auto-adapts via dark-mode overrides in global CSS)
