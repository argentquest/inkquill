# Frontend V1 Sprint 08: Story Chat, Builder, And Spatial Tools

## Status

Completed.

### Final Summary
- World chat (`/storytelling/worlds/[worldId]/chat`): session list, create, delete, message send via REST, `wsStatus` indicator. Uses mutable mock array for messages so dynamic send/reply is testable.
- Story chat (`/storytelling/stories/[storyId]/chat`): session list, create, delete, message send/receive via WebSocket (`fetchWsTicket` + `buildStoryChatWsUrl`), typing indicator, retry on failed WebSocket open.
- World builder (`/storytelling/world-builder`): step-driven wizard (questions → generating → review → done; currently abortable).
- Location hierarchy (`/storytelling/worlds/[worldId]/hierarchy`): tree view from `/api/v1/worlds/{worldId}/location-connections/hierarchy`.
- Map (`/storytelling/worlds/[worldId]/map`): scatter plot using `map_x`/`map_y` with a fallback when no coordinates exist.
- Navigation: chat/hierarchy/map links integrated into world detail; chat link added to story detail; World Builder hub card added to Storytelling hub and primary apps list.
- `frontendv1/lib/api.ts`: extended with world chat, story chat, WebSocket helpers, world builder, location connection and hierarchy types/functions.
- `LocationEntry` type updated to include `map_x`, `map_y`, `map_z`.
- Playwright tests: 5 tests (world builder, world chat, story chat, hierarchy, map). All pass.
- Build passes clean; no new lint warnings introduced.

## Goal

Bring storytelling-specific chat, world builder, hierarchy, and map tools into React after core authoring is stable.

## Important Boundary

The independent `/chatbot` prototype is tracked in `frontendv1Sprint11ChatbotApp.md`. It does not complete this sprint because this sprint is about story/world-context chat and spatial storytelling tools.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/storytelling/worlds/:worldId/chat` | world chat pages | P1 | Authenticated world chat |
| `/storytelling/stories/:storyId/chat` | story chat pages | P1 | Authenticated story chat |
| `/public/worlds/:worldId/chat` | public chat pages | P2 | Public chat variant |
| `/storytelling/world-builder` | world builder pages | P1 | Builder entry |
| `/storytelling/world-builder/:worldId` | world builder pages | P1 | Existing builder data |
| `/storytelling/worlds/:worldId/hierarchy` | `pages/world_hierarchy.html` | P2 | Tree view |
| `/storytelling/worlds/:worldId/map` | `pages/world_map.html` | P2 | Map view |

## Task List

- [ ] `[Size: L]` Build world chat route and chat shell.
- [ ] `[Size: L]` Build story chat route and chat shell.
- [ ] `[Size: M]` Build public chat route.
- [ ] `[Size: M]` Implement session list and active-session switching.
- [ ] `[Size: XL]` Implement message send, receive, streaming, retry, and failed-turn states.
- [ ] `[Size: M]` Implement context/source display for chat responses.
- [ ] `[Size: M]` Build world builder entry route.
- [ ] `[Size: L]` Build world builder create/update flow.
- [ ] `[Size: L]` Build hierarchy route and tree interaction.
- [ ] `[Size: L]` Build map route and basic location rendering.
- [ ] `[Size: M]` Implement location connection editing if retained.
- [ ] `[Size: XL]` Add frontend unit/component tests for chat transcript/composer states, builder forms, hierarchy tree interactions, and map controls.
- [ ] `[Size: L]` Add backend unit tests for story/world chat, builder, hierarchy, map, and location-connection service logic.
- [ ] `[Size: XL]` Add backend integration tests for chat session/message flows, builder save flows, hierarchy reads, map reads, and connection editing.
- [ ] `[Size: L]` Add Playwright coverage for chat and builder flows.
- [ ] `[Size: S]` Capture chat, builder, hierarchy, and map behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- Users can chat in world and story contexts.
- Builder flow is usable.
- Hierarchy and map can be navigated.
