# Creative UI Direction

## Purpose

This document defines the visual and interaction direction for the React rebuild. It exists to keep the new frontend from collapsing into a generic SaaS dashboard or a component-library demo. The product is for creative people, so the interface should feel like a creative tool first and an admin system second.

This document should be used together with:

- [reacttools.md](/C:/code2025a/inbkandquill2/reacttools.md)
- [frontendAll.md](/C:/code2025a/inbkandquill2/frontendAll.md)
- [frontendRouteBacklog.md](/C:/code2025a/inbkandquill2/frontendRouteBacklog.md)
- [frontendComponentInventory.md](/C:/code2025a/inbkandquill2/frontendComponentInventory.md)
- [uiBehaviorCapture.md](/C:/code2025a/inbkandquill2/uiBehaviorCapture.md)

## Core Product Feel

The frontend should feel:

- editorial rather than corporate
- immersive rather than crowded
- intentional rather than template-driven
- expressive rather than ornamental
- calm and clear under heavy information density

The product is not a finance dashboard, CRM, or operations console. Users are building worlds, stories, characters, scenes, and supporting creative assets. The UI should reflect authorship, discovery, and iteration.

## Primary Design Goals

1. Make long-form creative work feel welcoming and focused.
2. Make complex data relationships feel understandable without looking technical.
3. Make browsing and editing content feel visually rewarding.
4. Support desktop-first depth without making mobile web feel neglected.
5. Preserve speed and clarity even when the screen contains dense controls.

## What The UI Should Not Look Like

Avoid these failure modes:

- generic admin template styling
- flat white cards on pale gray backgrounds everywhere
- heavy purple-on-white default AI-product styling
- overuse of tiny controls and crowded toolbars
- decorative gradients with no structural purpose
- excessive glassmorphism or fake depth that hurts readability
- component-library defaults left mostly untouched
- every page using the same box-grid layout regardless of content

## Visual Principles

### 1. Content First

The primary visual subject should be the user’s content:

- story titles
- scene text
- character profiles
- world descriptions
- uploaded references

Chrome should support the work, not dominate it.

### 2. Strong Typography

Typography should carry a large part of the product identity. Use a deliberate pairing:

- one expressive display or editorial heading face
- one highly readable UI/body face
- one optional mono face for metadata, debug, and technical views

Typography should create contrast between:

- workspace titles
- narrative content
- metadata
- navigation
- support text

### 3. Layered Atmosphere

Pages should have a sense of depth and environment without becoming visually noisy. Prefer:

- subtle tonal backgrounds
- restrained gradients
- soft section separation
- occasional illustration, texture, or shape systems where appropriate

This is especially important for dashboards, world hubs, and story workspaces.

### 4. Controlled Density

Creative tools often contain a lot of information. Density is acceptable, but it must be structured. Use:

- clear layout zones
- strong heading hierarchy
- consistent spacing rhythms
- expandable advanced controls
- focused editing states

### 5. Purposeful Motion

Animation should communicate transitions, reveal structure, and reinforce state changes. Motion should support:

- entering a workspace
- opening drawers, modals, and side panels
- autosave confirmation
- chat streaming
- generation progress
- reordering or relationship mapping

Avoid generic micro-animation applied everywhere.

## Product Surface Modes

The product should not have one visual mode for every route. It should have multiple surface types with distinct treatment.

### Workspace Surfaces

Used for:

- story editor
- scene editor
- world builder
- character and lore editing

These should feel focused, rich, and content-driven. They can use more immersive spacing, stronger typography, and persistent side panels.

### Library Surfaces

Used for:

- world lists
- story lists
- image libraries
- document collections

These should feel browseable and organized, with better visual browsing than plain admin tables.

### Community Surfaces

Used for:

- blog
- forum
- public worlds
- published stories

These should feel editorial and readable. They need stronger content presentation and less application chrome.

### Admin Surfaces

Used for:

- billing administration
- maintenance
- analytics
- support tools

These can be denser and more conventional, but still visually consistent with the wider product. This is where table-heavy patterns can be more acceptable.

## Page-Level Design Direction

### Home, Dashboard, and Entry Points

These pages should orient and inspire, not just list links. They should answer:

- what is active
- what needs attention
- what can be created next
- what content matters most right now

The first screen should feel alive and relevant.

### World and Story Hubs

World and story pages should work like creative control rooms. They should combine:

- summary information
- key actions
- linked content
- progress state
- recent activity

These pages should be visually richer than plain CRUD details.

### Editor Views

Editors should reduce surrounding clutter and increase reading comfort. The user should feel that the text area is the main event. Sidebars and controls should remain available without visually overwhelming the page.

### Tables and Management Views

Use tables where they are the right tool, but do not default to tables when cards, boards, split views, or structured lists communicate the content better.

## Interaction Principles

### Explicit State

The interface should clearly show:

- loading
- saving
- streaming
- pending background work
- completion
- validation issues
- destructive action risk

Creative users should not have to guess whether the system accepted their work.

### Gentle Progression

Complex flows should reveal themselves in stages. Avoid forcing every advanced control into the first view. Use:

- tabs
- drawers
- accordions
- segmented controls
- progressive disclosure

### Keyboard-Friendly Desktop Use

Desktop workflows matter. The React rebuild should support:

- reliable focus management
- keyboard navigation
- command/search affordances
- fast modal and panel interaction
- low-friction text editing

### Mobile Web Adaptation

Mobile web should support meaningful authoring, but with simplified density. Mobile should not merely hide content; it should reorganize it. Priorities:

- readable text
- clear action grouping
- collapsible metadata
- stable editor behavior
- touch-friendly list and modal interaction

## Design System Direction

The recommended stack should be used like this:

- `Radix UI` for accessible primitives
- `Tailwind CSS` for custom visual identity and layout systems
- `TanStack Table` for dense data views where tables are genuinely appropriate
- `TipTap` for rich editing with a custom content-first presentation layer

The design system should define:

- semantic color tokens
- typography tokens
- spacing rhythm
- elevation/shadow rules
- border radius rules
- motion timing
- page shell patterns
- panel and modal patterns
- empty state patterns

Avoid relying on library default themes as the product identity.

## Color Direction

The product should avoid a sterile enterprise palette. The color system should feel sophisticated and creative without becoming whimsical or noisy.

Recommended direction:

- one warm or atmospheric neutral base family
- one deep anchor color for contrast and structure
- one expressive accent family
- one reserved highlight for generation/AI/system feedback

Color should be used to:

- organize the interface
- identify state
- establish mood

It should not be used to compensate for weak typography or layout.

## Typography Direction

Typography is one of the highest-leverage choices in this rebuild.

Recommended structure:

- Display: expressive but controlled, suitable for world/story headings
- Body/UI: highly readable at long-form lengths and small UI sizes
- Mono: sparse use for technical details, tokens, IDs, and system metadata

The heading system should distinguish:

- editorial/public pages
- workspace pages
- admin pages

One type treatment should not flatten all of them.

## Imagery and Illustration

Imagery should support the product’s sense of imagination. Use it selectively:

- rich thumbnails for worlds and stories
- atmospheric empty states
- visually meaningful cards where content benefits from preview

Avoid stock-illustration overload or placeholder-heavy layouts that feel unfinished.

## Writing and Tone in the UI

Microcopy should be:

- clear
- direct
- calm
- supportive

Avoid hype-heavy AI wording. Prefer language that treats the product as a creative environment, not a novelty generator.

## Accessibility and Readability

Visual ambition cannot come at the expense of usability. The rebuild should maintain:

- strong contrast
- readable text sizes
- visible focus states
- reduced-motion support
- keyboard accessibility
- clear error messaging

Readable and beautiful are not competing goals here.

## Implementation Guidance

When building React pages and components:

- start from layout and typography, not decorative detail
- define page-specific visual patterns instead of forcing one universal card layout
- create a small number of strong primitives and reuse them consistently
- keep admin patterns in admin areas
- create richer content presentation patterns for story and world surfaces

## Initial Mood References

These references are directionally useful because they feel more creative or editorial than standard SaaS tooling:

- Milanote
- Readwise Reader
- Are.na
- Framer
- Notion, selectively for clarity rather than visual identity

These are references for tone and interaction patterns, not templates to imitate directly.

## Delivery Implications

This visual direction affects sprint planning:

- Sprint 1 should establish tokens, type system, shell, spacing, and responsive rules
- Sprint 2 and Sprint 3 should validate the design language on worlds, stories, and content libraries
- editor surfaces should be treated as signature UX, not generic forms
- admin surfaces can intentionally use simpler patterns later

## Acceptance Standard

The React rebuild is visually successful when:

- a creative user would recognize it as a tool for making things, not managing tickets
- story and world pages feel distinctive and memorable
- dense screens remain readable and confident
- public and workspace surfaces feel related but not identical
- the product no longer looks like a template with the logo swapped
