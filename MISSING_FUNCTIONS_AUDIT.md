# Missing Functions Audit

## Scope
This audit reviews `C:\code2026\DailyNewsletter` for functionality that is exposed in models, config, docs, or UI but is not fully implemented in executable code.

It is not a style review. Defensive `pass` blocks and abstract base methods were excluded unless they hide a real missing workflow.

## Summary
- There are very few literal `NotImplementedError` stubs in this codebase.
- The main gaps are workflow-level features that are partially modeled in the backend and frontend, but are not actually enforced or executed.
- The most important missing implementations are scheduling, print/layout orchestration, and feedback-driven behavior.

## Confirmed Missing Or Incomplete Functions

### 1. Scheduled delivery is modeled but not implemented
The application stores and edits per-profile scheduling fields, but the assembler ignores them and sends immediately for every selected profile.

Evidence:
- `backend/models.py:21`
- `backend/models.py:24`
- `backend/models.py:27`
- `frontend_next/app/profiles/page.tsx:42`
- `frontend_next/app/profiles/page.tsx:43`
- `frontend_next/app/profiles/page.tsx:44`
- `frontend_next/app/profiles/page.tsx:261`
- `frontend_next/app/profiles/page.tsx:262`
- `frontend_next/app/profiles/page.tsx:263`
- `backend/assembler.py:128`
- `backend/assembler.py:148`

What is missing:
- A scheduler or dispatch filter that compares `timezone`, `delivery_time`, and `delivery_days` to the current time.
- A function that determines whether a profile is due for delivery now.
- A background/cron entrypoint for automatic daily sends.

Current behavior:
- `run_daily_assembler()` fetches profiles and sends newsletters without checking those scheduling fields.

### 2. Grid/2-page assembly is not implemented
The codebase still carries grid assembly concepts and grid config, but the actual grid assembler is only a compatibility shim over the linear assembler.

Evidence:
- `backend/grid_assembler.py:6`
- `backend/grid_assembler.py:8`
- `backend/content_providers/config.json`
- `backend/assembler.py:105`
- `backend/linear_assembler.py:89`

What is missing:
- A real grid placement algorithm.
- Any use of `assembly.grid` settings from config.
- Any two-page composition logic despite the product description referencing printable layout composition.

Current behavior:
- `GridAssembler` inherits `LinearAssembler` and adds no layout logic.
- The print output is a single linear render of provider sections.

### 3. Print priority / required print sections are configured but never enforced
Provider config includes `print_priority` and `required_for_print`, but assembly ignores both.

Evidence:
- `backend/content_providers/config.json:9`
- `backend/content_providers/config.json:10`
- `backend/content_providers/config.json:60`
- `backend/content_providers/config.json:61`
- `backend/content_providers/config.json:97`
- `backend/content_providers/config.json:98`
- `backend/content_providers/config.json:211`
- `backend/content_providers/config.json:212`
- `backend/assembler.py:89`
- `backend/linear_assembler.py:89`

What is missing:
- A function that ranks providers for print output by config priority.
- A function that guarantees required sections are present in assembled output.
- Overflow handling when the number of providers exceeds printable space.

Current behavior:
- Providers render in selected registry order only.
- Required print metadata is dead configuration.

### 4. Feedback collection exists, but feedback-driven personalization does not
The app stores likes/dislikes, and the router docstring says this should improve future prompts, but nothing in provider generation or profile selection reads that data.

Evidence:
- `backend/routers/feedback.py:14`
- `backend/routers/feedback.py:19`
- `backend/database.py:68`
- `frontend_next/app/daily/DailyClient.tsx:258`

What is missing:
- A function that reads `provider_feedback` when generating future provider content.
- Any per-profile provider weighting, suppression, or prompt adaptation from feedback.
- Any API or UI for feedback history, despite the architecture doc listing that as a future direction.

Current behavior:
- Feedback is write-only.

### 5. Daily preview template/theme controls described in architecture are not implemented
The architecture says preview should support multi-template switching, theme switching with persistence, and a shareable link button. The current daily preview only uses the default template and default theme.

Evidence:
- `frontend_next/architecture.md:201`
- `frontend_next/architecture.md:202`
- `frontend_next/architecture.md:203`
- `frontend_next/app/daily/DailyClient.tsx:94`
- `frontend_next/app/daily/DailyClient.tsx:118`

What is missing:
- A template selector in the preview UI.
- Theme selection UI in preview.
- Local persistence for theme/template choice.
- Share-link generation that preserves preview state.

Current behavior:
- The client loads the default template only.
- The client loads the backend default theme only.

### 6. Provider variable support in the visual template editor is incomplete
The backend exposes template variable metadata, but the GrapesJS editor does not surface or use it.

Evidence:
- `backend/routers/providers.py:21`
- `backend/routers/providers.py:66`
- `frontend_next/app/templates/TemplateEditor.tsx:61`

What is missing:
- A merge-tag picker or block list fed by provider variable metadata.
- Any validation that a template references variables the provider actually supplies.

Current behavior:
- The editor loads HTML and theme CSS, but variable insertion remains manual.

## Items I Did Not Count As Missing
- Photo upload from the family update flow.
  - `frontend_next/architecture.md` explicitly marks this as deferred.
- Abstract provider `get_content()` in the base class.
  - That is intentional abstraction, not missing implementation.
- Generic `pass` statements inside exception handlers.
  - Those are mostly cleanup/fallback paths, not absent product features.

## Recommended Delivery Order
1. Implement scheduled delivery gating and an automated dispatch entrypoint.
2. Implement print priority/required-section selection.
3. Either remove grid-layout expectations from config/docs or build the real grid assembler.
4. Implement feedback read-paths and provider adaptation.
5. Add preview/template-editor UX for template and theme selection.

## Proposed Artifact
- Sprint plan: `SPRINT_MISSING_FUNCTIONS.md`
