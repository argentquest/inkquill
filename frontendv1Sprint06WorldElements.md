# Frontend V1 Sprint 06: World Elements

## Status

Not started.

## Goal

Bring characters, locations, lore items, and associations into the storytelling React app.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/storytelling/worlds/:worldId/characters` | `pages/characters_list.html` | P0 | Character list and create entry |
| `/storytelling/characters/:characterId` | `pages/character_detail.html` | P1 | Character detail |
| `/storytelling/worlds/:worldId/locations` | `pages/locations_list.html` | P0 | Location list and create entry |
| `/storytelling/locations/:locationId` | `pages/location_detail.html` | P1 | Location detail |
| `/storytelling/worlds/:worldId/lore` | lore list pages | P1 | Lore list and create entry |
| `/storytelling/lore/:loreId` | lore detail pages | P1 | Lore detail |

## Task List

- [ ] `[Size: M]` Build characters list route.
- [ ] `[Size: M]` Build character create/edit form flow.
- [ ] `[Size: M]` Build character detail route.
- [ ] `[Size: M]` Build locations list route.
- [ ] `[Size: M]` Build location create/edit form flow.
- [ ] `[Size: M]` Build location detail route.
- [ ] `[Size: M]` Build lore list route.
- [ ] `[Size: M]` Build lore create/edit form flow.
- [ ] `[Size: M]` Build lore detail route.
- [ ] `[Size: L]` Build generic association management UI and link modals.
- [ ] `[Size: L]` Add frontend unit/component tests for character, location, lore, and association form/list/detail components.
- [ ] `[Size: L]` Add backend unit tests for world-element CRUD and association service logic used by the React flows.
- [ ] `[Size: L]` Add backend integration tests for character, location, lore, and association API flows.
- [ ] `[Size: L]` Add Playwright coverage for entity creation, edit, detail, and association flows.
- [ ] `[Size: S]` Capture entity and association behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- World elements are manageable in React.
- Associations can be created and removed.
- Detail pages are usable and navigable.
