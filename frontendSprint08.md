# Sprint 08: Publishing, Community, Public Discovery

## Goal

Expose public-facing reading and community surfaces after the authoring core is usable.

## In Scope

- published stories list and reader
- user published stories
- forum
- public and authenticated blog consumption
- public image preview/share
- global search

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/public/published-stories` | `pages/published_stories.html` | P1 | Public listing |
| `/public/published-stories/:storyId` | `pages/published_story_detail.html` | P1 | Reader |
| `/public/authors/:userId/stories` | `pages/user_published_stories.html` | P2 | Author story list |
| `/app/community/forum/*` | forum pages | P1 | Forum routes |
| `/public/blog/*` | blog public pages | P1 | Blog reading |
| `/app/blog/*` | blog pages | P1 | Authenticated blog flows |
| `/public/image` | public image pages | P2 | Preview |
| `/public/image-share` | public image pages | P2 | Share |
| `/app/search` | `pages/global_search.html` | P2 | Mixed search |

## Shared Components

- `PublishedStoryReader`
- `CommentThread`
- `ForumCategoryList`
- `ForumThreadList`
- `ForumThreadView`
- `BlogPostCard`
- `BlogPostLayout`
- `AuthorProfileHeader`
- `SocialSharingBar`

## Backend/API Dependencies

- published stories APIs
- forum APIs
- blog APIs
- comments/ratings APIs
- search APIs
- public image/share APIs

## UI Behavior Capture Targets

- published story reading and comment flow
- forum create/reply/moderation interactions
- blog engagement interactions
- share controls

## Risks and Decisions

- Forum and blog can share some patterns but should not be forced into one abstraction.
- Public SEO-friendly routes need to be considered early.

## Task List

- [ ] Build published stories list route.
- [ ] Build published story reader route.
- [ ] Build user published stories route.
- [ ] Build forum category and thread routes.
- [ ] Build forum reply/create flows.
- [ ] Build public blog list and post routes.
- [ ] Build authenticated blog consumption routes as needed.
- [ ] Build public image preview and image share routes.
- [ ] Build global search route.
- [ ] Implement comments, ratings, and social sharing UI where applicable.
- [ ] Capture reading, forum, blog engagement, and share behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- public reading surfaces are usable
- forum works end-to-end
- blog reading and key interaction flows work
