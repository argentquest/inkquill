# Frontend V1 Sprint 07: Editors And Documents

## Status

Completed.

## Goal

Deliver the high-complexity authoring surfaces: act editor, scene editor, and document management.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/storytelling/acts/:actId` | `pages/act_editor_ui.html` | P0 | Rich act editor — implemented |
| `/storytelling/acts/:actId/review` | `pages/act_ai_review.html` | P1 | AI review workflow — deferred to future sprint |
| `/storytelling/scenes/:sceneId` | scene editor pages | P0 | Scene editor — implemented |
| `/storytelling/documents` | document pages | P1 | Document manager — implemented |
| `/storytelling/imports` | import pages | P2 | Decide whether to merge into documents — deferred |

## Task List

- [x] `[Size: L]` Build act editor route and data-loading flow.
- [x] `[Size: L]` Build scene editor route and data-loading flow.
- [x] `[Size: M]` Build document manager route.
- [x] `[Size: M]` Implement document upload flow.
- [x] `[Size: M]` Build document delete/download actions.
- [x] `[Size: L]` Add Playwright coverage for editor and document actions.
- [ ] `[Size: L]` Implement autosave state management. — deferred
- [ ] `[Size: M]` Implement prompt picker and AI model selector integrations. — deferred
- [ ] `[Size: L]` Build act AI review route and comparison UI. — deferred
- [ ] `[Size: M]` Implement document processing-state refresh polling. — deferred
- [ ] `[Size: XS]` Decide whether imports remain separate routes or merge into documents. — deferred
- [ ] `[Size: XL]` Add frontend unit/component tests for editor state, autosave indicators, prompt/model controls, AI review comparison, and document actions. — deferred
- [ ] `[Size: L]` Add backend unit tests for editor save, AI review orchestration, document upload, processing status, download, and delete logic. — deferred
- [ ] `[Size: L]` Add backend integration tests for act editor, scene editor, AI review, and document API flows. — deferred
- [ ] `[Size: S]` Capture autosave, prompt, review, and document behavior in `uiBehaviorCapture.md`. — deferred

## Exit Criteria

- [x] Act and scene editing are usable.
- [x] Save state is trustworthy (explicit save with mutation feedback).
- [ ] AI review can be triggered and understood. — deferred
- [x] Documents can be uploaded and managed.

## Verification Notes

- `frontendv1/app/storytelling/acts/[actId]/page.tsx` — act metadata editing, scene list, scene creation/deletion.
- `frontendv1/app/storytelling/scenes/[sceneId]/page.tsx` — scene field editing (title, mood, characters_present, plot_points, summary, content), save, delete.
- `frontendv1/app/storytelling/documents/page.tsx` — document list, upload with world selector, status badges, download link, delete.
- Backend `GET /documents/` list endpoint added in `app/routers/document_upload.py`.
- API types updated: `SceneEntry` and `SceneCreatePayload` extended with `mood`, `characters_present`, `plot_points`, `image_prompt_definition`, `story_class_id`.
- Navigation updated: Documents added to storytelling hub card grid and `lib/apps.ts` primary links.
- Playwright tests: `tests/e2e/sprint-editors-documents.spec.ts` — 7 passing tests covering act editor load/edit, scene creation, scene editor save/delete, documents list, and document delete.
- Build verified: `npm run build` passes clean.
- Test command for this sprint:
  ```powershell
  cd frontendv1; npm run test:e2e -- tests/e2e/sprint-editors-documents.spec.ts
  ```
