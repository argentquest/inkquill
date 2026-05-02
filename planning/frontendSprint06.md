# Sprint 06: Editors, Review, Documents

## Goal

Deliver the high-complexity authoring surfaces after the core object graph is stable.

## Current Review Status

- Last reviewed against the repo on 2026-04-27.
- React delivery for editors, review, and document management has not started.
- The planned editor abstraction, document manager, upload flows, and autosave behavior remain pending.

## In Scope

- act editor
- scene editor
- act AI review
- document manager
- document import flows

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/acts/:actId` | `pages/act_editor_ui.html` | P0 | Rich editor |
| `/app/acts/:actId/review` | `pages/act_ai_review.html` | P1 | Review workflow |
| `/app/scenes/:sceneId` | `pages/scene_editor_ui.html` | P0 | Rich editor |
| `/app/documents` | `pages/document_manager.html` | P1 | Upload and manage docs |
| `/app/import` | import/document flows | P2 | Merge if possible into docs |

## Shared Components

- `EditorPageLayout`
- `RichTextEditorField`
- `AutosaveStatus`
- `PromptPicker`
- `AiModelSelector`
- `ReviewDiffPanel`
- `DocumentTable`
- `FileUploadField`

## Backend/API Dependencies

- act CRUD and review
- scene CRUD
- websocket ticket endpoint
- prompts endpoints
- documents list/upload/delete/download
- import-related endpoints

## UI Behavior Capture Targets

- act autosave
- scene autosave
- AI model selection
- prompt application
- document upload and processing states

## Risks and Decisions

- Editor state must be designed before code starts.
- Separate editing state from API transport state.
- Treat upload and processing as distinct document states.

## Task List

- [ ] Choose and scaffold the React editor abstraction.
- [ ] Build act editor route and data-loading flow.
- [ ] Build scene editor route and data-loading flow.
- [ ] Implement autosave state management for act and scene editors.
- [ ] Implement prompt picker and AI model selector integrations.
- [ ] Build act AI review route and comparison UI.
- [ ] Build document manager route.
- [ ] Implement document upload flow.
- [ ] Implement document processing state refresh in the UI.
- [ ] Build document delete/download actions.
- [ ] Decide whether import flows remain separate routes or merge into documents.
- [ ] Capture autosave, prompt, and document upload behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- act and scene editing are usable
- save state is trustworthy
- document management works end-to-end
- review flow is functional

## Implementation Status

- Not started in the React app.
