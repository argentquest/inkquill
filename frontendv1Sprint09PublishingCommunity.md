# Frontend V1 Sprint 09: Publishing And Community

## Status

In Progress.

## Goal

Open public-facing reading, publishing, community, and discovery surfaces after authoring works.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/public/published-stories` | `pages/published_stories.html` | P1 | Public listing |
| `/public/stories/:storyId` | `pages/view_published_story.html` | P1 | Reader |
| `/storytelling/published` | user published story pages | P1 | User-owned published stories |
| `/community/forums` | forum pages | P2 | Forum categories |
| `/community/forums/:threadId` | forum thread pages | P2 | Thread detail and replies |
| `/public/blog` | blog pages | P2 | Public blog list |
| `/public/blog/:slug` | blog pages | P2 | Public blog post |
| `/public/search` | search pages | P2 | Global discovery |

## Task List

- [x] `[Size: M]` Build published stories list route.
- [x] `[Size: M]` Build published story reader route.
- [x] `[Size: M]` Build user published stories route.
- [x] `[Size: L]` Build forum category and thread routes.
- [x] `[Size: L]` Build forum reply/create flows — `ReplyComposer` in `[threadId]/page.tsx`; new thread form at `frontendv1/app/community/forums/new/page.tsx`.
- [x] `[Size: M]` Build public blog list and post routes.
- [ ] `[Size: M]` Build authenticated blog consumption routes if retained.
- [ ] `[Size: S]` Build public image preview and image share routes if retained.
- [x] `[Size: L]` Build global search route.
- [ ] `[Size: L]` Implement comments, ratings, and social sharing UI where applicable.
- [ ] `[Size: L]` Add frontend unit/component tests for published-story readers, forum interactions, blog pages, search results, comments, ratings, and share controls.
- [ ] `[Size: L]` Add backend unit tests for publishing, reader payloads, forum, comments, ratings, blog, image-share, and search service logic.
- [x] `[Size: XL]` Add backend integration tests for public reader, publishing, forum, blog, comments, ratings, sharing, and search API flows.
- [x] `[Size: L]` Add Playwright coverage for reader, forum, blog, and search routes.
- [x] `[Size: S]` Capture reading, forum, blog engagement, and share behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- [x] Public reading surfaces are usable.
- [x] Community/forum surfaces are usable.
- [x] Public discovery routes are available.

## Verification Notes

- `frontendv1/app/public/layout.tsx` wraps all `/public/**` sub-routes in `PublicShell`; `frontendv1/app/public/page.tsx` no longer duplicates the shell wrapper.
- `frontendv1/app/public/published-stories/page.tsx` is API-backed via `GET /api/v1/published-stories/` with loading, empty, error, and story-card list states.
- `frontendv1/app/public/stories/[storyId]/page.tsx` is API-backed via `GET /api/v1/published-stories/:id`, `GET /api/v1/published-stories/:id/comments`, `POST /api/v1/published-stories/:id/rate`, and `POST /api/v1/published-stories/:id/comments`; it now includes reader rating controls, comment submission, share-link behavior, comment empty state, and discussion list rendering.
- `frontendv1/app/storytelling/published/page.tsx` is API-backed via `GET /api/v1/published-stories/` and filters client-side by the current session `user_id`.
- `frontendv1/app/storytelling/community/page.tsx` is no longer a placeholder; it now acts as a community hub that summarizes published stories, forum threads, and blog posts and links into `/public/published-stories`, `/community/forums`, `/public/blog`, and `/public/search`.
- `frontendv1/app/public/blog/page.tsx` is API-backed via `GET /api/blog/posts` with loading, empty, error, and card-list states.
- `frontendv1/app/public/blog/[slug]/page.tsx` is API-backed via `GET /api/blog/posts/:slug` and renders HTML content.
- `frontendv1/app/public/search/page.tsx` is API-backed via `GET /api/blog/search/?q=...` with URL-driven search, prompt, results, no-results, and error states.
- `frontendv1/app/community/layout.tsx` wraps all `/community/**` sub-routes in `PublicShell`.
- `frontendv1/app/community/forums/page.tsx` is API-backed via `GET /api/forum/categories/` and `GET /api/forum/threads/`; it shows category cards and recent-thread summaries.
- `frontendv1/app/community/forums/[threadId]/page.tsx` is API-backed via `GET /api/forum/threads/:id`; it shows thread metadata and post bodies.
- `frontendv1/lib/api.ts` now includes `fetchPublishedStories`, `fetchPublishedStory`, `fetchStoryComments`, `createStoryComment`, `ratePublishedStory`, `fetchForumCategories`, `fetchForumThreads`, `fetchForumThread`, `fetchBlogPosts`, `fetchBlogPost`, and `fetchBlogSearch`.
- `frontendv1/tests/e2e/sprint-publishing-community.spec.ts` covers published stories list states, reader load/error plus rating/comment/share interactions, user published stories states, the storytelling community hub, blog routes, search routes, forum categories, and forum thread detail/error routes.
- `frontendv1/tests/e2e/helpers.ts` includes Sprint 09 mock data and mutable route handlers for published-story comments and rating interactions.
- `tests/integration/publishing/test_publishing_community_contracts_integration.py` covers public access for published stories, rating auth enforcement, forum categories/threads, blog posts/search, and unknown-resource handling.

## Remaining Gaps

- Forum reply/create flows are still missing from the React routes.
- Authenticated blog-consumption routes and public image preview/share routes are not yet present in `frontendv1/`.
- The new reader engagement work is implemented for published stories, but broader comments/ratings/share parity across all applicable community surfaces is not complete yet.
- Sprint verification currently relies on Playwright plus backend integration coverage; dedicated frontend component tests and backend unit tests for this sprint area still need to be added.
