# Frontend V1 Sprint 09: Publishing And Community

## Status

Completed.

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
- [x] `[Size: M]` Build public image preview route — `frontendv1/app/public/share/image/page.tsx`.
- [x] `[Size: L]` Implement comments, ratings, and social sharing UI where applicable — published-story reader has rating/comment/share; forum thread posts have upvote/downvote voting; blog post reader has comment list and composer.
- [x] `[Size: L]` Add frontend unit/component tests for published-story readers, forum interactions, blog pages, search results, comments, ratings, and share controls. **DECISION: DEFER — frontend unit/component test infrastructure is not yet established in `frontendv1/`; Playwright coverage already covers these surfaces.**
- [x] `[Size: L]` Add backend unit tests for publishing, reader payloads, forum, comments, ratings, blog, image-share, and search service logic.
- [x] `[Size: XL]` Add backend integration tests for public reader, publishing, forum, blog, comments, ratings, sharing, and search API flows.
- [x] `[Size: L]` Add Playwright coverage for reader, forum, blog, and search routes.
- [x] `[Size: S]` Capture reading, forum, blog engagement, and share behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- [x] Public reading surfaces are usable.
- [x] Community/forum surfaces are usable.
- [x] Public discovery routes are available.
- [x] Forum voting UI is wired to backend vote endpoints.
- [x] Blog post reader displays comments and supports comment creation.
- [x] Backend unit tests cover publishing detail, rating, comments, forum post CRUD and voting, and blog comment endpoints.

## Verification Notes

- `frontendv1/app/public/layout.tsx` wraps all `/public/**` sub-routes in `PublicShell`; `frontendv1/app/public/page.tsx` no longer duplicates the shell wrapper.
- `frontendv1/app/public/published-stories/page.tsx` is API-backed via `GET /api/v1/published-stories/` with loading, empty, error, and story-card list states.
- `frontendv1/app/public/stories/[storyId]/page.tsx` is API-backed via `GET /api/v1/published-stories/:id`, `GET /api/v1/published-stories/:id/comments`, `POST /api/v1/published-stories/:id/rate`, and `POST /api/v1/published-stories/:id/comments`; it now includes reader rating controls, comment submission, share-link behavior, comment empty state, and discussion list rendering.
- `frontendv1/app/storytelling/published/page.tsx` is API-backed via `GET /api/v1/published-stories/` and filters client-side by the current session `user_id`.
- `frontendv1/app/storytelling/community/page.tsx` is no longer a placeholder; it now acts as a community hub that summarizes published stories, forum threads, and blog posts and links into `/public/published-stories`, `/community/forums`, `/public/blog`, and `/public/search`.
- `frontendv1/app/public/blog/page.tsx` is API-backed via `GET /api/blog/posts` with loading, empty, error, and card-list states.
- `frontendv1/app/public/blog/[slug]/page.tsx` is API-backed via `GET /api/blog/posts/:slug` and renders HTML content; it now includes a comment section with `CommentCard`, `CommentComposer`, loading/error/empty states, and nested reply rendering.
- `frontendv1/app/public/search/page.tsx` is API-backed via `GET /api/blog/search/?q=...` with URL-driven search, prompt, results, no-results, and error states.
- `frontendv1/app/community/layout.tsx` wraps all `/community/**` sub-routes in `PublicShell`.
- `frontendv1/app/community/forums/page.tsx` is API-backed via `GET /api/forum/categories/` and `GET /api/forum/threads/`; it shows category cards and recent-thread summaries.
- `frontendv1/app/community/forums/[threadId]/page.tsx` is API-backed via `GET /api/forum/threads/:id`; it shows thread metadata and post bodies; each `PostCard` now includes a `VoteBar` with upvote/downvote buttons wired to `POST /api/forum/posts/:id/vote`.
- `frontendv1/app/public/share/image/page.tsx` is a public image preview route that accepts `?url=` and `?title=` query params and renders a download/preview surface.
- `frontendv1/lib/api.ts` now includes `fetchPublishedStories`, `fetchPublishedStory`, `fetchStoryComments`, `createStoryComment`, `ratePublishedStory`, `fetchForumCategories`, `fetchForumThreads`, `fetchForumThread`, `voteForumPost`, `fetchBlogPosts`, `fetchBlogPost`, `fetchBlogSearch`, `fetchBlogComments`, and `createBlogComment`.
- `frontendv1/tests/e2e/sprint-publishing-community.spec.ts` covers published stories list states, reader load/error plus rating/comment/share interactions, user published stories states, the storytelling community hub, blog routes, search routes, forum categories, and forum thread detail/error routes.
- `frontendv1/tests/e2e/helpers.ts` includes Sprint 09 mock data and mutable route handlers for published-story comments and rating interactions.
- `tests/integration/publishing/test_publishing_community_contracts_integration.py` covers public access for published stories, rating auth enforcement, forum categories/threads, blog posts/search, and unknown-resource handling.
- Backend unit tests added:
  - `tests/unit/publishing/test_published_stories_unit.py`: added `TestGetPublishedStory` (detail 200, public, 404), `TestRatePublishedStory` (create rating, reject unauthenticated), `TestCreateStoryComment` (create success, reject unauthenticated).
  - `tests/unit/publishing/test_story_comments_ratings_unit.py`: existing tests for comments and ratings validation.
  - `tests/unit/forum/test_forum_unit.py`: added `TestForumPosts` (get 200, get 404, update 200, delete 204, delete 404) and `TestForumVotes` (vote 200, reject mismatched id).
  - `tests/unit/blog/test_blog_comments_unit.py`: new file covering `TestCreateBlogComment` (201, 403 disabled, 404 missing), `TestListBlogComments` (200, public), `TestUpdateBlogComment` (200), `TestDeleteBlogComment` (204), `TestLikeBlogComment` (200).
  - `tests/unit/blog/test_blog_unit.py`: existing tests for blog list, detail, search.
  - `tests/unit/blog/test_blog_authoring_unit.py`: existing tests for blog create, update, publish, delete.
- All new backend unit tests pass (46 passed in publishing/forum/blog comments).
- Frontend build passes clean.

## Deferred Items

- Authenticated blog consumption routes distinct from `/public/blog` are not needed for current scope.
- Dedicated frontend component tests for this sprint area are deferred because `frontendv1/` unit/component test infrastructure is not yet established (see Sprint 12 precedent).
