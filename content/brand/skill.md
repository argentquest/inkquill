# Ink & Quill Design System

A design system for the Ink & Quill product suite — a warm, paper-forward platform spanning three surfaces: Storytelling (long-form creative writing), Care Circle (family caregiving with picture-based patient sign-in), and Chatbot (focused single-thread workspace).

## When to use

Apply this system whenever the user is building or mocking work for Ink & Quill, or asking for designs that match the Ink & Quill brand (literary, cream-and-ink, Garamond/Lora serif, pebble-rounded cards).

## Starting an artifact

1. Import foundations first. Every HTML file must begin with:
   ```html
   <link rel="stylesheet" href="colors_and_type.css">
   ```
   Adjust the relative path to reach the design-system root.

2. Use the prebuilt shared UI components. For React/JSX artifacts, load the shared kit after React + Babel:
   ```html
   <link rel="stylesheet" href="ui_kits/shared/kit.css">
   <script type="text/babel" src="ui_kits/shared/components.jsx"></script>
   ```
   This exposes globals: `Button`, `Card`, `PageHeader`, `StatCard`, `Badge`, `Tag`, `TextField`, `Alert`, `TopNav`, `Breadcrumbs`, `Footer`, `AppShell`, `PatientShell`, and the Lucide-style icon set (`IconUsers`, `IconBot`, `IconSparkles`, etc.). All expect to live inside `AppShell` (or `PatientShell` for the Friend surface).

3. Never hardcode hex. Use CSS variables declared in `colors_and_type.css` — `--paper`, `--ink-900`, `--ember`, `--forest`, `--mist`, and the semantic `--success-*` / `--info-*` / `--warning-*` / `--danger-*` trios.

## Page anatomy

A standard Ink & Quill page is assembled in this exact order:

1. **`<AppShell>`** wrapper — establishes the cream + mist backdrop. Use `<PatientShell>` only for the Friend-facing surface (warmer, yellow-tinted gradient).
2. **`<TopNav>`** — sticky, translucent, `Ink & Quill` wordmark in EB Garamond, links wrap below.
3. **`<Breadcrumbs crumbs={[...]}>`** — small uppercase trail with chevron separators.
4. **`<PageHeader>`** — the hero block. Every page has one. Contains `eyebrow`, `title` (sentence ending in a period), `description`, optional `action` button.
5. **Content cards** — `<Card>` + `<StatCard>` in a `iq-grid` (use `iq-grid--2`, `--3`, `--4`, or `--dashboard`).
6. **`<Footer>`** — close with text-only nav links.

## Voice rules (non-negotiable)

- Titles are **full sentences ending in periods**: *"Welcome back, Rose."*, *"Choose the 3 pictures that belong to you."*
- **Eyebrow above every title.** ALL CAPS, `letter-spacing: 0.24–0.32em`, `--fg-3` color. Category tag, not a phrase.
- The product talks about itself calmly in third person: *"This app is intentionally narrow…"*, *"The shared platform resolves…"*.
- **"Friend" is the user-facing term** for a care-circle patient. Use "Friend" in any patient-facing copy; "patient" only appears in internal family-side labels.
- **No exclamation points, no emoji** in product chrome. Emoji are allowed only in content (the picture-login grid) or marketing voice.
- Sentence case for labels and buttons. Title Case only for proper nouns (app names: *Care Circle*, *Storytelling*, *Chatbot*).

## Visual rules

- Background is `--paper` (#f6f1e8), never white. Cards are translucent white (`rgba(255,255,255,0.78)`).
- Type is serif throughout: **EB Garamond** for display, **Lora** for body/UI. Buttons are serif too.
- Radii are generous: 22 / 24 / 28 / 32 / `rounded-full`. No sharp corners.
- Borders are `rgba(35,25,19,0.10)`. Shadow token is `--shadow-panel` (soft, 60px blur). Apply liberally.
- **Ember (`#d86c3d`)** is reserved — use sparingly on focus states, selection highlights, rare primary CTAs. 1–2 places per screen max.
- **Forest (`#1f3b36`)** is the dark inverse — used only on the Chatbot sidebar. Never use it in Storytelling or Care Circle surfaces.
- Animation: 180ms CSS transitions. No springs, no bounces.

## Iconography

- **Lucide icons only.** Stroke-based, 1.5–2px weight, `currentColor`. Never filled icons, never multi-color. The shared components file exposes a curated set as `IconUsers`, `IconBot`, `IconSparkles`, etc. — use these; do not inline new SVG paths unless the shared file is missing the icon you need.
- **Sizing**: 16px (inline in buttons), 18px (nav), 20px (dashboard tiles). Icons in 40–44px rounded-2xl badges (`rgba(35,25,19,0.06)` background) for dashboard entry tiles.
- **No icons on ember.** Ember is a text/border accent only.
- **No emoji icons** in product chrome. Unicode symbols are fine as micro-accents (✦ for coin balance) but avoid.

## Surface-specific notes

- **Care Circle Family** — dashboard is an 8-tile grid of entry cards, each with a Lucide icon badge, title, and one-line description. Friends list uses expanded cards with stage/delivery stats and `Badge` status chips.
- **Care Circle Patient (Friend)** — larger type throughout (48px hero, 20px body, 44px emoji tiles). Picture-login grid is 4 columns, emoji-first, pick 3. Ember outlines the selected tiles.
- **Chatbot** — dark forest aside (the only inverse surface), cream conversation panel on the right. Assistant bubbles get `--bg-chat-assistant` (warm cream); user bubbles get `--ink-900` with cream text.
- **Storytelling** — project shelf on the left, chapter canvas on the right with a slightly warmer paper (#fefcf6) and the textarea in EB Garamond. Writing conversation lives under the shelf.

## Component cheatsheet

| Need | Component |
|---|---|
| Page hero block | `<PageHeader eyebrow title description action />` |
| Small category tag above a title | `<Eyebrow>` |
| Translucent content container | `<Card>` |
| KPI tile (label + big number + detail) | `<StatCard>` |
| Status chip | `<Badge tone="success\|warning\|danger\|info\|neutral\|coin">` |
| Soft pill (filter, metadata) | `<Tag>` or `className="iq-chip-soft"` |
| Labelled input | `<TextField label hint error>` |
| Inline banner | `<Alert tone title detail>` |
| Button | `<Button variant="primary\|secondary\|ghost\|danger">` |

## Reference kits

Working implementations live in `ui_kits/`:

- `care-circle-family/` — dashboard, friends list, friend detail, providers
- `care-circle-patient/` — picture login + daily highlights reader
- `chatbot/` — focused chat workspace
- `storytelling/` — project shelf + chapter canvas + writing chat

Copy from these for any new Ink & Quill work.

## Font substitution

The codebase lists Georgia / Garamond / Courier New (system fonts). This design system substitutes:

- **Lora** for Georgia (body/UI)
- **EB Garamond** for Garamond (display)
- **JetBrains Mono** for Courier New (mono)

Stacks in `colors_and_type.css` list the originals first so local users see their installed fonts. If the user provides licensed Garamond files, swap them in at `fonts/` and update the `@font-face` declarations.
