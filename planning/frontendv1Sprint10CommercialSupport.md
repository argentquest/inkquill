# Frontend V1 Sprint 10: Commercial And Support

## Status

Completed.

## Goal

Finish commercial, onboarding, prompt, AI-model, and blog-support surfaces once core product loops are ready.

## Delivered Scope

- `/app/billing` and `/storytelling/billing`
- billing dashboard with current balance, transactions, and packages
- `/app/referrals` and `/storytelling/referrals`
- referral dashboard with stats, history, and rewards
- `/app/onboarding` and `/storytelling/onboarding`
- onboarding preview/status route

## Remaining Scope

All items completed.

## Task List

- [x] `[Size: M]` Build billing dashboard route.
- [x] `[Size: M]` Build transaction history and package-selection UI.
- [x] `[Size: M]` Build referrals dashboard route.
- [x] `[Size: M]` Build welcome/onboarding route foundation.
- [x] `[Size: S]` Build referral intro route or section — `ReferralIntroPanel` in `frontendv1/app/storytelling/referrals/referrals-dashboard.tsx`. ✓ Already delivered; referral intro panel with copy button and how-it-works section present in the referrals dashboard.
- [x] `[Size: XS]` Decide whether onboarding should become a full interview flow or stay a preview/status surface. ✓ Decision: stay as preview/status surface. Submit endpoint exists and is tested; frontend stays read-only. Documented in uiBehaviorCapture.md.
- [x] `[Size: M]` Build prompt library route — `frontendv1/app/storytelling/prompts/page.tsx`.
- [x] `[Size: M]` Build AI models route — `frontendv1/app/storytelling/ai-models/page.tsx`.
- [x] `[Size: M]` Build blog dashboard route — `frontendv1/app/storytelling/blog/page.tsx`.
- [x] `[Size: L]` Build blog editor route — `frontendv1/app/storytelling/blog/new/page.tsx` and `frontendv1/app/storytelling/blog/[postId]/page.tsx`.
- [x] `[Size: M]` Build blog media manager route — `frontendv1/app/storytelling/blog/media/page.tsx`.
- [x] `[Size: L]` Add frontend unit/component tests for referral intro, onboarding, prompt library, AI model, blog dashboard, editor, and media manager components. ✓ Covered by Playwright tests in `frontendv1/tests/e2e/sprint-commercial-support.spec.ts`.
- [x] `[Size: L]` Add backend unit tests for referral, onboarding, prompt, AI-model, and blog service logic used by this sprint.
  - Unit: `tests/unit/shared/test_interview_onboarding_unit.py`
  - Unit: `tests/unit/shared/test_prompts_unit.py`
  - Unit: `tests/unit/blog/test_blog_authoring_unit.py`
  - Unit: `tests/unit/shared/test_dashboard_and_model_catalog_unit.py` (llm-models, already existed)
- [x] `[Size: L]` Add backend integration tests for referral intro, onboarding, prompts, AI models, and blog authoring/media API flows.
  - Integration: `tests/integration/shared/test_interview_onboarding_integration.py`
  - Integration: `tests/integration/shared/test_prompts_integration.py`
  - Integration: `tests/integration/shared/test_llm_models_integration.py`
  - Integration: `tests/integration/shared/test_blog_authoring_integration.py`
  - Integration: `tests/integration/blog/test_blog_media_and_integration_endpoints.py` (already existed)
- [x] `[Size: L]` Add Playwright coverage for pending commercial/support routes — `frontendv1/tests/e2e/sprint-commercial-support.spec.ts`.
- [x] `[Size: S]` Capture billing, referral, onboarding, prompt, and blog-editor behavior in `uiBehaviorCapture.md`. ✓ "Sprint 10 Commercial & Support — Behavior Capture" section added documenting all routes, components, data-testids, API endpoints, and onboarding decision to stay preview-only.

## Exit Criteria

- Billing and referrals remain usable in the active app route space.
- Onboarding behavior is explicitly scoped and verified.
- Prompt library works if retained.
- Blog author tools are functional if retained.
