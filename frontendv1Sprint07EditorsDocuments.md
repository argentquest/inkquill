# Frontend V1 Sprint 07: Editors And Documents

## Status

Not started.

## Goal

Deliver the high-complexity authoring surfaces: act editor, scene editor, AI review, and document management.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/storytelling/acts/:actId` | `pages/act_editor_ui.html` | P0 | Rich act editor |
| `/storytelling/acts/:actId/review` | `pages/act_ai_review.html` | P1 | AI review workflow |
| `/storytelling/scenes/:sceneId` | scene editor pages | P0 | Scene editor |
| `/storytelling/documents` | document pages | P1 | Document manager |
| `/storytelling/imports` | import pages | P2 | Decide whether to merge into documents |

## Task List

- [ ] `[Size: M]` Choose and scaffold the React editor abstraction.
- [ ] `[Size: L]` Build act editor route and data-loading flow.
- [ ] `[Size: L]` Build scene editor route and data-loading flow.
- [ ] `[Size: L]` Implement autosave state management.
- [ ] `[Size: M]` Implement prompt picker and AI model selector integrations.
- [ ] `[Size: L]` Build act AI review route and comparison UI.
- [ ] `[Size: M]` Build document manager route.
- [ ] `[Size: M]` Implement document upload flow.
- [ ] `[Size: M]` Implement document processing-state refresh.
- [ ] `[Size: M]` Build document delete/download actions.
- [ ] `[Size: XS]` Decide whether imports remain separate routes or merge into documents.
- [ ] `[Size: XL]` Add frontend unit/component tests for editor state, autosave indicators, prompt/model controls, AI review comparison, and document actions.
- [ ] `[Size: L]` Add backend unit tests for editor save, AI review orchestration, document upload, processing status, download, and delete logic.
- [ ] `[Size: L]` Add backend integration tests for act editor, scene editor, AI review, and document API flows.
- [ ] `[Size: L]` Add Playwright coverage for autosave, review, upload, processing, and document actions.
- [ ] `[Size: S]` Capture autosave, prompt, review, and document behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- Act and scene editing are usable.
- Save state is trustworthy.
- AI review can be triggered and understood.
- Documents can be uploaded and managed.
