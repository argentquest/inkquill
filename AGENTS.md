# AGENTS.md

## Purpose
This file defines how coding agents should operate in this repository.

## Current Program Direction
- Backend-first delivery.
- Frontend is being rebuilt in React.
- Prefer API consistency and testability over template/view work.
- Remove legacy assumptions when they conflict with the new architecture.

## Primary Goals For Agents
- Keep backend API routes stable and explicit for React clients.
- Increase and maintain automated test coverage.
- Favor pragmatic, production-safe changes over backward compatibility.
- Keep data model and migrations coherent with current code truth.

## Working Rules
- Do not use destructive git commands (`reset --hard`, mass checkout reverts).
- Do not revert user changes unless explicitly requested.
- Use focused, incremental commits (if asked to commit).
- Prefer direct fixes over speculative refactors.
- If a change touches auth, billing, or data writes, add/adjust tests.
- When working against a sprint document, update the sprint task list as each task is implemented.
- If you add or change exit criteria in a sprint document, add explicit verification notes for each criterion.

## Frontend Delivery Rules
- The active frontend rebuild workspace is `frontendv1/` unless the user explicitly redirects to another frontend workspace.
- Follow the Option 1 frontend stack direction documented in `reacttools.md` unless the user explicitly changes direction.
- Keep frontend work aligned with `creative-ui-direction.md`, `frontendAll.md`, and the current sprint markdown file.
- Preserve shell-level behavior for session bootstrap, balance loading, maintenance state, theme persistence, cookie consent, and notifications unless the sprint intentionally changes that behavior.
- Prefer route-level delivery with working states over placeholder-only UI.

## Frontend Testing Rules
- Frontend browser verification should use `Playwright` in `frontendv1/`.
- Add or update Playwright coverage for meaningful frontend behavior changes, especially route loading, auth/session state, maintenance state, notifications, persistence, and other user-visible flows.
- For frontend API-dependent tests, prefer controlled mocking in Playwright when the goal is UI behavior verification.
- Do not mark a frontend sprint task complete until the relevant frontend tests are added or updated and pass locally.
- Keep frontend test commands documented in the sprint markdown file when they are part of exit verification.

## Code Style Expectations
- Python-first conventions:
  - Clear function names.
  - Small, focused helpers.
  - Type hints where practical.
  - Concise comments for non-obvious logic only.
- Keep API response shapes predictable for frontend consumption.
- Avoid introducing new Azure-specific dependencies/paths.

## Testing Policy
- Unit tests should use mocks for external/service dependencies.
- Integration tests should exercise real app paths with controlled test DB state.
- Add regression tests for each meaningful bug fix.
- Frontend sprint work should include browser-level verification when the work changes user-visible behavior.

## Standard Test Commands
- Unit tests:
```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit -q
```
- Unit + integration (current stable subset):
```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit tests\integration --ignore=tests/integration/test_document_upload_integration.py --ignore=tests/integration/test_image_generation_integration.py -q
```
- Coverage (backend API profile):
```powershell
.\.venv\Scripts\python.exe -m pytest tests\unit tests\integration --ignore=tests/integration/test_document_upload_integration.py --ignore=tests/integration/test_image_generation_integration.py --cov --cov-config=.coveragerc.backend_api --cov-report=term -q
```
- Frontend build:
```powershell
cd frontendv1; npm run build
```
- Frontend Playwright browser tests:
```powershell
cd frontendv1; npm run test:e2e
```

## Coverage Target
- Maintain backend API scoped coverage at or above current target.
- If coverage drops, prioritize low-coverage high-impact routers first.

## Database And Schema
- Use SQLAlchemy models as source of truth for schema evolution.
- Keep Alembic baseline/migrations aligned with current models.
- Validate model/database consistency when changing table structures.

## Artifacts And Planning Docs
- `database_model.mmd`: generated ER diagram from current SQLAlchemy metadata.
- `frontendAll.md` and sprint markdown files: React rebuild planning source.
- Keep planning docs updated when backend contracts change.
- Keep the active sprint markdown file current when frontend task status or exit verification changes.

## Related Docs
- `DEPLOYMENT_GUIDE.md`: deployment runbook and environment setup details.
- `database_model.mmd`: current database ER diagram (generated from SQLAlchemy metadata).
- `frontendAll.md`: React rebuild roadmap and sequencing.
- `frontendComponentInventory.md`: component-level frontend inventory.
- `creative-ui-direction.md`: frontend creative direction and UI guidance.
- `reacttools.md`: frontend stack decision and implementation references.
- `BACKEND_ENDPOINT_MATRIX.md`: backend route/test coverage matrix.

## Definition Of Done For Agent Tasks
- Code compiles/imports cleanly.
- Relevant tests pass locally.
- Coverage impact checked when backend code changes.
- Frontend work includes updated sprint-task status and explicit exit-criteria verification when a sprint doc exists.
- Any behavioral/API changes are documented in the task response.
