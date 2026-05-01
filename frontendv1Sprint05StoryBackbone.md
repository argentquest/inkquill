# Frontend V1 Sprint 05: Story Backbone

## Status

Not started.

## Goal

Make core storytelling usable in React: stories list, story creation, story detail, story wizard, and basic story mode.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/storytelling/stories` | `pages/stories_list.html` | P0 | Story index |
| `/storytelling/stories/new` | `pages/story_form.html` | P0 | Create flow |
| `/storytelling/stories/:storyId` | `pages/story_detail.html` | P0 | Story hub |
| `/storytelling/stories/:storyId/edit` | `pages/story_form.html` | P0 | Shared edit form |
| `/storytelling/stories/wizard` | `pages/story_wizard.html` | P1 | Guided creation |
| `/storytelling/basic-stories/new` | `pages/basic_story_form.html` | P1 | Simplified mode |
| `/storytelling/basic-stories/:storyId` | `pages/basic_story_editor.html` | P1 | Simple editor |

## Task List

- [ ] `[Size: M]` Build stories list route.
- [ ] `[Size: L]` Build story create route and shared story form.
- [ ] `[Size: M]` Build story edit route.
- [ ] `[Size: L]` Build story detail hub with outline tree and management actions.
- [ ] `[Size: L]` Build story wizard route and step flow.
- [ ] `[Size: M]` Implement story generation modal and state flow.
- [ ] `[Size: M]` Build basic story create route.
- [ ] `[Size: L]` Build basic story editor route.
- [ ] `[Size: M]` Implement publish/unpublish UI behavior.
- [ ] `[Size: L]` Add frontend unit/component tests for story list, story form, story detail, wizard, generation modal, and basic-story editor behavior.
- [ ] `[Size: L]` Add backend unit tests for story CRUD, publish state, generation request shaping, and basic-story service behavior touched by the React routes.
- [ ] `[Size: L]` Add backend integration tests for standard story and basic-story API flows used by this sprint.
- [ ] `[Size: L]` Add Playwright coverage for create, edit, detail, wizard, and basic story flows.
- [ ] `[Size: S]` Capture story form, outline, publish, and generation modal behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- A user can create and manage standard stories in React.
- Story wizard works at a usable level.
- Basic story mode is reachable and functional.
