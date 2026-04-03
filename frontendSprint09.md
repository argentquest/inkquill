# Sprint 09: Billing, Referrals, Onboarding, Blog Tools

## Goal

Add the commercial and support surfaces once the core product loop already works.

## In Scope

- billing dashboard
- referrals
- referral intro
- welcome interview
- prompt library
- AI model pages
- blog dashboard/editor/media

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/billing` | billing pages | P1 | Billing dashboard |
| `/app/referrals` | referral pages | P1 | Referral dashboard |
| `/public/referrals` or `/app/referrals/intro` | `pages/referral_intro.html` | P2 | Intro/explainer |
| `/app/onboarding/interview` | interview pages | P2 | Welcome interview |
| `/app/prompts` | prompt pages | P1 | Prompt library |
| `/app/ai-models` | model pages | P2 | Model catalog and selectors |
| `/app/blog/dashboard` | blog pages | P2 | Author dashboard |
| `/app/blog/editor` | blog pages | P2 | Create/edit post |
| `/app/blog/media` | blog media pages | P2 | Media manager |

## Shared Components

- `BillingSummaryPanel`
- `TransactionTable`
- `PackageSelector`
- `ReferralStatsPanel`
- `PromptPicker`
- `AiModelSelector`
- `MediaLibraryGrid`
- `RichTextEditorField`

## Backend/API Dependencies

- billing endpoints
- referral endpoints
- welcome interview endpoints
- prompt endpoints
- ai-model endpoints
- blog dashboard/editor/media endpoints

## UI Behavior Capture Targets

- billing purchase flow
- referral copy/share flow
- onboarding interview flow
- prompt apply flow
- blog editor and media picker

## Risks and Decisions

- Billing needs careful UX around state refresh and transaction history.
- Blog editor should reuse the editor abstraction from Sprint 6.

## Task List

- [ ] Build billing dashboard route.
- [ ] Build transaction history and package-selection UI.
- [ ] Build referrals dashboard route.
- [ ] Build referral intro route or section.
- [ ] Build welcome interview route.
- [ ] Build prompt library route.
- [ ] Build AI models route.
- [ ] Build blog dashboard route.
- [ ] Build blog editor route.
- [ ] Build blog media manager route.
- [ ] Capture billing, referral, onboarding, prompt, and blog-editor behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- billing and referrals are usable
- onboarding flow is reachable
- prompt library works
- blog author tools are functional
