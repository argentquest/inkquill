# Sprint 04: Story Backbone

## Goal

Make stories usable end-to-end before rich editing begins.

## In Scope

- stories list
- create story
- edit story
- story detail hub
- story wizard
- basic story entry points

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/stories` | `pages/stories_list.html` | P0 | Story index |
| `/app/stories/new` | `pages/story_form.html` | P0 | Create flow |
| `/app/stories/:storyId` | `pages/story_detail.html` | P0 | Story hub |
| `/app/stories/:storyId/edit` | `pages/story_form.html` | P0 | Shared form |
| `/app/stories/wizard` | `pages/story_wizard.html` | P1 | Guided creation |
| `/app/basic-stories/new` | `pages/basic_story_form.html` | P1 | Simplified mode |
| `/app/basic-stories/:storyId` | `pages/basic_story_editor.html` | P1 | Simple editor |

## Shared Components

- `StoryCard`
- `StoryForm`
- `OutlineTree`
- `StoryGenerationModal`
- `StatusBadge`
- `EmptyState`

## Backend/API Dependencies

- stories list/create/get/update/delete
- story publish status
- story generation endpoints
- basic story endpoints
- world and story-class selectors

## UI Behavior Capture Targets

- story form save flow
- story detail outline interactions
- publish/unpublish controls
- story generation modal

## Risks and Decisions

- Keep story detail focused on structure and management, not full editing.
- Confirm whether basic stories remain a distinct product mode.

## Task List

- [ ] Build stories list route.
- [ ] Build create story route and shared story form.
- [ ] Build edit story route using the same story form.
- [ ] Build story detail hub with outline tree and management actions.
- [ ] Build story wizard route and step flow.
- [ ] Implement story generation modal/state flow.
- [ ] Build basic story create route.
- [ ] Build basic story editor route.
- [ ] Implement publish/unpublish UI behavior on story detail.
- [ ] Capture story form, outline tree, publish flow, and story generation modal behavior.
- [ ] Verify standard and basic story flows against backend APIs.

## Exit Criteria

- user can create and manage standard stories
- story wizard works at a usable level
- basic story mode is reachable and functional
