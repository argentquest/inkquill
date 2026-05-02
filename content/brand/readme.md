# Ink & Quill — Design System

A design system extracted from the Ink & Quill product suite. Ink & Quill is a **multi-surface creative + care platform** built on a shared Next.js 15 / React 19 frontend. The brand is literary, warm, and paper-forward: cream backgrounds, warm-brown ink type, Garamond display, generously rounded cards, and a signature orange ember accent used sparingly.

## The product

Ink & Quill is a single platform hosting three distinct app surfaces, each sharing one shell:

| Surface | Route prefix | Purpose |
|---|---|---|
| **Storytelling** | `/storytelling/*` | Creative authoring — onboarding interviews, account, billing, referrals. Writers use it with an AI as a brainstorming partner. |
| **Care Circle** | `/care-circle-family/*` · `/care-circle-patient/*` | Family coordination for caregiving. Family side (owners + members) manages "Friend" profiles, content providers, newsletters. Patient/Friend side has a picture-based sign-in and a calm daily-highlights reader view. |
| **Chatbot** | `/chatbot/*` | Intentionally narrow chat workspace — one conversation rail, starter prompts, prompt queue. Styled as a lab tool. |

All three live under one `Ink & Quill` wordmark, one top nav, one cookie banner, one toast center.

## Sources

- **Codebase** (local mount): `inkquill/frontendv1/` — Next.js 15 App Router, React 19, TypeScript strict, Tailwind 3.4, Radix UI, React Query, Lucide icons.
- **Tailwind theme**: `inkquill/frontendv1/tailwind.config.ts`
- **Global CSS**: `inkquill/frontendv1/app/globals.css`
- **Components**: `inkquill/frontendv1/components/{ui,shell,platform,care-circle-family,care-circle-patient,chatbot}/`
- **Marketing content** (voice samples): `inkquill/marketing-content/{blog-article-samples.html, email-marketing-templates.md, instagram-content-samples.md, twitter-x-content-samples.md, reddit-community-posts.md, tiktok-video-scripts.md}`

No logos, icon SVGs, or raster brand assets were present in the repo — all iconography in the product comes from **lucide-react**. Marketing imagery is not in the repo either; placeholders are used with clear labels.

---

## Index

- **`colors_and_type.css`** — CSS variables for colors, type, radii, spacing, shadows. Import this first in any Ink & Quill artifact.
- **`fonts/`** — (No custom fonts shipped — Google Fonts substitutes loaded via `@import` in `colors_and_type.css`.)
- **`assets/`** — Icon reference, wordmark SVG, sample backgrounds.
- **`preview/`** — Design system cards rendered in the Design System tab.
- **`ui_kits/care-circle-family/`** — Family caregiver dashboard recreation.
- **`ui_kits/care-circle-patient/`** — Picture-based sign-in + calm daily highlights reader.
- **`ui_kits/chatbot/`** — Focused chat workspace.
- **`ui_kits/storytelling/`** — Onboarding + account workspace.
- **`SKILL.md`** — Skill manifest for Claude Code compatibility.

---

## Content Fundamentals

**Voice — two registers, one sensibility.**

1. **Product UI copy** is a distinctive style I'll call *literary lab notebook*: short, declarative, a little bit wry, talking about the product almost in the third person. Signature quirks:
   - Eyebrow + display title + one explanatory paragraph, every time. The eyebrow is a category tag (ALL CAPS, wide tracking). The title is a *complete sentence ending in a period*, which is unusual — it gives everything a dignified, finished feel.
   - "This surface…", "This app is intentionally narrow…", "The shared platform resolves…" — it describes itself calmly, without hype.
   - Examples from the codebase:
     - *"Storytelling account / Account shell for the storytelling workspace."*
     - *"Chatbot app / Simple chat-first UI. / This app is intentionally narrow: one conversation rail, a short prompt queue, and no storytelling or care-circle workflow assumptions inside the surface."*
     - *"Choose the 3 pictures that belong to you."*
     - *"Ink & Quill frontend Sprint 1 foundation for the React rebuild."* (footer)
   - "Friend" is the user-facing term for a care-circle patient. Never "patient" in patient-facing UI.
   - No exclamation points in product UI. Terminal periods on titles.

2. **Marketing voice** is much warmer and more energetic — written like a writing coach who happens to love emoji:
   - Second person: *"Your characters should too."*, *"Ready to get started?"*
   - Sentence fragments for emphasis. Lots of em-dashes.
   - Occasional ✨ 🎭 📚 💡 in headlines. Never in product UI.
   - Hashtag-heavy on social (`#WritingTips #WritingCommunity #AuthorLife`).
   - Signs off as "The Ink & Quill Team" or "Happy writing,".

**Casing**
- Sentence case for UI labels and buttons: *"Edit profile"*, *"Review billing"*, *"New Friend"* (proper-noun capitalization on "Friend").
- Title Case is rare; only used for proper nouns (app names: *Care Circle*, *Storytelling*, *Chatbot*).
- ALL CAPS + wide tracking (0.24–0.32em) is reserved for **eyebrows** and **micro-labels** (form labels, stat card labels, chat role labels). Never for headlines.

**Punctuation and tone**
- Titles end with periods. (*"Focused workspace."* is styled without a period in the code — but most titles do end with one.) This is inconsistent in the codebase; the design system prefers **terminal periods on display titles**.
- Em-dashes favored over parenthetical commas.
- No emoji in product UI. Emoji live in marketing + the patient picture-login grid (where they are the *content*, not decoration).

**I vs. you**
- Product: mostly neutral/descriptive ("The shared platform…"). Where it addresses the user, it uses **you** ("Welcome back, {name}.", "Choose the 3 pictures that belong to you.").
- Marketing: almost exclusively second person.

**Vibe**: a writer's desk. Warm lamplight, cream paper, deep inkwell. Calm, competent, a little old-fashioned. Not twee — there are no quill illustrations, no parchment textures. The *type* and *color* do all the work.

---

## Visual Foundations

### Colors
- **Paper** (`#f6f1e8`) is the app background everywhere. Not white — never pure white.
- **Ink-900** (`#231913`) is the default text. All text sits on a warm-brown scale (`ink-50` through `ink-900`), not neutral gray.
- **White with transparency** (`bg-white/70`–`/88`) is the card treatment — translucent white floating on paper.
- **Ember** (`#d86c3d`) is the high-emphasis accent: selection highlight, focus borders on the patient picture-login, a very rare call to action. Used maybe 1–2 places per screen.
- **Forest** (`#1f3b36`) is a secondary dark: the chatbot sidebar gradient, success messages.
- **Mist** (`#dce5e2`) tints the radial gradient at the top of the app shell and info banners.

### Type
- **Display** — EB Garamond (substitute for Garamond). Used on every h1/h2/h3. Medium weight (500). Tight leading (1.08–1.15). Feels like a book jacket.
- **Body/UI** — Lora (substitute for Georgia). The whole product is set in a serif, including buttons and form labels. This is the single most distinctive brand choice.
- **Mono** — JetBrains Mono (substitute for Courier New). Rare; only for technical preview states.
- **Eyebrow treatment** — 12px, uppercase, `letter-spacing: 0.24–0.32em`, `color: ink-600`. Appears above almost every title and beside almost every stat value.

### Spacing & layout
- 4px base. Common values: 12, 16, 20, 24, 32, 48.
- Pages use a **max-width of `7xl` (1280px)** centered with `px-4 md:px-6`, `py-8`.
- Sections are separated by `space-y-8` (32px).
- Grids often use `[minmax(0,1.2fr)_minmax(0,0.8fr)]` for 2-up asymmetry.

### Backgrounds
- **App shell**: a layered background — a radial mist-blue wash at top-left, fading into a vertical cream gradient from `ink-50` → `ink-100`. This is the single most recognizable backdrop.
- **Patient shell**: a warmer variant — radial soft-yellow at top, fading into `#fdfaf4` → `#f4ecdc`. Sun-through-curtains feeling.
- **Page headers**: `linear-gradient(135deg, paper 96%, mist 90%)` — a diagonal paper-to-mist wash on the hero block.
- **Chatbot aside**: dark forest → ink gradient, white text. The only inverse surface in the system.
- No full-bleed photography. No hand-drawn illustrations. No repeating patterns. The gradients and the type *are* the brand.

### Animation
- Extremely restrained. CSS `transition` only, usually unspecified property (`transition` utility = all). ~180ms.
- No bounces, no springs. The system is quiet.
- Radix dialogs have the stock `data-[state=open]:animate-in` fade + zoom-95 entrance.

### Hover / press states
- **Hover**: lighten the surface. `bg-white/80` → `bg-white`; `hover:bg-black/5` for ghost buttons; text goes from `ink-700` → `ink-900`.
- **Primary button hover**: `bg-ink-900` → `bg-ink-700` (slightly lighter).
- **Card hover**: border darkens from `black/10` → `black/20` and the fill brightens.
- **Press**: no explicit pressed styles. `disabled:opacity-60` is the only down-ish state.
- **Focus**: `focus:ring-2 focus:ring-ink-200` on inputs; `focus:border-ember` on the chat textarea.

### Borders & shadows
- Everything has a `border` with `rgba(35, 25, 19, 0.10)` — black/10. Dividers are also black/10.
- One shadow token: `shadow-panel` = `0 20px 60px rgba(19, 22, 26, 0.12)`. Generous, soft, warm-ish. Used on every card and panel. No inner shadows.

### Corner radii — the "pebble" scale
Ink & Quill is built from rounded rectangles with unusually large radii:
- `22px` alerts, small cards
- `24px` buttons (pill via `rounded-full`), inner cards
- `28px` cards
- `32px` hero panels / big sections
- `rounded-full` for buttons, badges, tags, tab links

No sharp corners anywhere. No square cards.

### Transparency & blur
- **Cards** are `bg-white/70` to `/88` — always translucent over paper.
- **Sticky top nav** uses `bg-paper/85 backdrop-blur` — the blur is subtle but always on.
- **Dialog overlays** use `bg-ink-900/50 backdrop-blur-sm`.
- Blur is a tool of *layering*, never a decorative filter.

### Imagery
- **Warm, never cool.** When real photography is added, it should lean amber/gold, film-grainy, soft-focus. Nothing with blue LED lighting.
- Avatars: solid color circles with a Lucide icon inside (e.g. `Bot` or `User2`), colored `bg-ink-900` / `bg-amber-600`.

### Layout rules
- **Sticky top nav** (z-40) with backdrop blur. Wordmark left, actions right, primary links wrap below.
- **Breadcrumbs** immediately below the nav.
- **PageHeader hero** at the top of every page (eyebrow + display title + paragraph + optional action button).
- **Content grid** below with cards.
- **Footer** at the end with text links.

---

## Iconography

**Primary icon set: Lucide (`lucide-react` v0.468).** Stroke-based, 1.5px stroke weight, consistent visual language.

Used everywhere in the product:
- `Users`, `Puzzle`, `CreditCard`, `Gift`, `UserCircle`, `Camera`, `Activity`, `UserCheck` — Care Circle family dashboard cards.
- `Bot`, `User2`, `Sparkles`, `CornerDownLeft` — Chatbot.
- `Info`, `AlertTriangle`, `CheckCircle2` — alert banners.
- `X` — dialog close.
- `GripVertical`, `ChevronUp`, `ChevronDown`, `ToggleLeft`, `ToggleRight` — drag/toggle controls.

**Sizing**: mostly `h-5 w-5` (20px) for nav icons; `h-4 w-4` (16px) for inline button icons; `h-10 w-10` avatar bubbles hold a `h-5 w-5` icon centered.

**Color**: icons inherit from text (`currentColor`) — always `ink-700`, `ink-900`, or `paper` on inverse surfaces. The ember orange is never used on icons.

**Icon backgrounds**: when icons sit in a badge, the badge is `bg-ink-900/6` (6% ink), `rounded-2xl`, 40×40px.

**Emoji**: *never in product UI chrome.* The one exception is the Care Circle patient picture-login grid, where emoji are the content (☀️ 🐶 🌸 🎂 🐦 🚗 🌳 🏠 🌙 ⭐ 🚤 🎩). Marketing content uses emoji freely (✨ 🎭 📚 💡).

**Unicode/typographic icons**: no. The system relies entirely on Lucide.

**Delivery**: Lucide is loaded from npm (`lucide-react`) in the React app; in this design system we reference it by CDN: `https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.js` for plain HTML mocks, and copy individual icon SVGs to `assets/icons/` when needed.

**Logo / wordmark**: there is no SVG logo in the codebase. The brand mark is literally the text "Ink & Quill" set in EB Garamond medium, `letter-spacing: 0.08em`, at 24px (`text-2xl`). A clean typographic wordmark, no ampersand stylization, no mark. I've created `assets/wordmark.svg` as a canonical vector version.

---

## Type substitution — flag to the user

The codebase references the **local system fonts** `Georgia`, `Garamond`, and `Courier New`. These aren't web fonts and aren't shipped in the repo. I've substituted Google Fonts that match closely:

| In codebase | Substituted with | Reason |
|---|---|---|
| Georgia (serif) | **Lora** | Matches warmth, x-height, and body readability of Georgia. |
| Garamond (display) | **EB Garamond** | An open-source Garamond — same classical proportions. |
| Courier New (mono) | **JetBrains Mono** | Cleaner modern mono; mono is rarely used in this product. |

**Action requested:** if you own licenses to Monotype Garamond or a preferred alternative (Adobe Garamond Pro, ITC Garamond, Sabon), please share the font files so we can swap them in. The font stacks in `colors_and_type.css` already list the system fonts first, so anyone with them locally gets the original look.

---

## How to use this system

1. Every artifact starts with `<link rel="stylesheet" href="colors_and_type.css">` (adjust path).
2. Use CSS variables for colors — never hardcode hex values.
3. Always set `body { background: var(--bg-app); }` — never pure white.
4. Wrap pages in the app shell backdrop (`background: var(--bg-shell)`) for the Storytelling / Care Circle family surfaces. Use `var(--bg-patient)` for the Friend-facing surface.
5. Page = TopNav + Breadcrumbs + PageHeader hero + section cards + Footer.
6. Cards = `bg-white/78`, `rounded-[28px]`, `border black/10`, `shadow-panel`, `p-6`.
7. Titles = `font-display`, display sizes, ending in a period.
8. Eyebrows above every title.
9. Icons from Lucide, stroke-only, currentColor.
10. Emoji only in content, never in chrome.
