# Sprint 07: Chat, Builder, Spatial Tools

## Goal

Bring conversational and world-structure tools online after authoring is stable.

## In Scope

- world chat
- story chat
- public chat
- world builder
- world hierarchy
- world map

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/worlds/:worldId/chat` | world chat pages | P1 | Authenticated world chat |
| `/app/stories/:storyId/chat` | story chat pages | P1 | Authenticated story chat |
| `/public/worlds/:worldId/chat` | public chat pages | P2 | Public chat variant |
| `/app/world-builder` | world builder pages | P1 | Entry |
| `/app/world-builder/:worldId` | world builder pages | P1 | Manage existing builder data |
| `/app/worlds/:worldId/hierarchy` | `pages/world_hierarchy.html` | P2 | Tree view |
| `/app/worlds/:worldId/map` | `pages/world_map.html` | P2 | Map view |

## Shared Components

- `ChatLayout`
- `ConversationList`
- `MessageList`
- `MessageComposer`
- `StreamingMessage`
- `ContextSourcePanel`
- `HierarchyTree`
- `WorldMapCanvas`

## Backend/API Dependencies

- world chat APIs and websocket auth
- story chat APIs and websocket auth
- public chat APIs
- world builder APIs
- hierarchy data
- location and connection APIs

## UI Behavior Capture Targets

- chat send/stream flow
- session switching
- builder multi-step flow
- map interactions and connection editing

## Risks and Decisions

- Streaming UX must be designed intentionally.
- Map feature can slip if core chat/builder work needs more time.

## Task List

- [ ] Build world chat route and chat shell.
- [ ] Build story chat route and chat shell.
- [ ] Build public chat route.
- [ ] Implement session list and active-session switching behavior.
- [ ] Implement message send, receive, and streaming UI behavior.
- [ ] Implement context/source display for chat responses.
- [ ] Build world builder entry route.
- [ ] Build world builder create/update flow.
- [ ] Build hierarchy route and tree interaction.
- [ ] Build map route and basic location rendering.
- [ ] Implement location connection editing if retained.
- [ ] Capture chat, builder, hierarchy, and map behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- user can chat in world and story contexts
- builder flow is usable
- hierarchy and map can be navigated
