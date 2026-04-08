# Sprint: Missing Functions Closure

## Goal
Close the highest-impact missing functionality identified in `MISSING_FUNCTIONS_AUDIT.md` so that profile scheduling, print assembly, and preview behavior match the current product surface.

## Sprint Outcomes
- Profile delivery preferences become actionable.
- Print assembly uses config instead of ignoring it.
- The codebase has one clear position on linear vs grid layout.
- Feedback becomes useful beyond raw storage.
- Daily preview and template editing expose the controls already implied by the architecture.

## Sprint Tasks

### 1. Delivery scheduling engine
Status: `pending`

Implement:
- Add a scheduler helper that decides whether a profile is due now from `timezone`, `delivery_time`, and `delivery_days`.
- Update assembler execution to skip profiles not due for the current dispatch window.
- Add an explicit scheduled-run entrypoint separate from manual "send now".

Files likely involved:
- `backend/assembler.py`
- `backend/models.py`
- `backend/routers/newsletter.py`
- new scheduler helper module if needed

Exit criteria:
- Manual send-now can still send all selected profiles for a family.
- Scheduled execution sends only profiles due at the current time in their local timezone.
- Profiles with empty `delivery_days` still mean "every day".

Verification:
- Unit tests for timezone/day/time due logic.
- Integration test covering due and not-due profiles in one family.

### 2. Print provider selection and prioritization
Status: `pending`

Implement:
- Read provider config metadata during assembly.
- Enforce `required_for_print`.
- Sort or filter providers by `print_priority` for print output.
- Define behavior when too many providers exist for the target printable layout.

Files likely involved:
- `backend/content_providers/config.json`
- `backend/assembler.py`
- `backend/linear_assembler.py`

Exit criteria:
- Required print sections always appear unless their provider hard-fails.
- Print ordering is driven by config, not only registry order.
- Overflow behavior is deterministic and tested.

Verification:
- Unit tests for provider ordering and required inclusion.
- Integration test for a profile with many enabled providers.

### 3. Resolve grid assembler ambiguity
Status: `pending`

Implement one of these directions:
- Option A: build a real `GridAssembler` using `assembly.grid` config.
- Option B: remove dead grid config/docs and formally standardize on linear layout.

Files likely involved:
- `backend/grid_assembler.py`
- `backend/content_providers/config.json`
- README / architecture docs that mention grid or multi-page layout

Exit criteria:
- No dead "grid" contract remains.
- Docs and runtime behavior match.

Verification:
- If Option A: layout tests and rendered artifact snapshots.
- If Option B: grep confirms dead grid settings and misleading docs are removed.

### 4. Feedback read-path and adaptation
Status: `pending`

Implement:
- Add a service that reads `provider_feedback` by profile and provider.
- Define at least one behavior change based on feedback:
  - suppress disliked providers,
  - prioritize liked providers,
  - or inject feedback into provider prompt context.
- Add optional feedback history endpoint for frontend inspection.

Files likely involved:
- `backend/routers/feedback.py`
- `backend/database.py`
- provider generation path in `backend/assembler.py` or provider services

Exit criteria:
- Feedback affects subsequent content generation or provider selection in a testable way.
- Behavior is documented and predictable.

Verification:
- Unit tests for feedback aggregation logic.
- Integration test proving feedback changes a later result path.

### 5. Daily preview controls
Status: `pending`

Implement:
- Add template selector per provider.
- Add theme selector in preview.
- Persist selected theme/template locally.
- Add share-link generation that preserves preview state.

Files likely involved:
- `frontend_next/app/daily/DailyClient.tsx`
- `frontend_next/app/preview/PreviewClient.tsx`
- `frontend_next/lib/session.ts`
- `frontend_next/lib/api.ts`

Exit criteria:
- User can switch template and theme without code changes.
- Refresh preserves selections.
- Shared link restores the same preview state.

Verification:
- Frontend component tests or Playwright coverage for selection, persistence, and share-link restore.

### 6. Template editor variable tooling
Status: `pending`

Implement:
- Load provider variable metadata into the editor sidebar.
- Add click-to-insert merge tags for supported variables.
- Optionally warn when a saved template uses unknown placeholders.

Files likely involved:
- `frontend_next/app/templates/TemplateEditor.tsx`
- `backend/routers/providers.py`

Exit criteria:
- Editor exposes provider variables without manual memorization.
- Saved templates can be validated against known variables.

Verification:
- UI test for variable insertion.
- Unit test for template placeholder validation if added.

## Recommended Order
1. Delivery scheduling engine
2. Print provider selection and prioritization
3. Resolve grid assembler ambiguity
4. Feedback read-path and adaptation
5. Daily preview controls
6. Template editor variable tooling

## Risks
- Timezone logic will create hidden bugs if manual send-now and scheduled send share the same code path without an explicit mode.
- Print prioritization needs a clear product rule for overflow, otherwise behavior will remain unstable.
- Grid implementation can become a time sink if page constraints are not simplified first.
- Feedback adaptation needs tight product definition to avoid confusing or inconsistent content changes.

## Suggested Verification Commands
```powershell
cd C:\code2026\DailyNewsletter\backend
pytest -q
```

```powershell
cd C:\code2026\DailyNewsletter\frontend_next
npm test
```

```powershell
cd C:\code2026\DailyNewsletter\frontend_next
npm run build
```
