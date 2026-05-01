# Sprint 05: World Elements and Associations

## Goal

Bring characters, locations, lore items, and their associations into the React app.

## Current Review Status

- Last reviewed against the repo on 2026-04-27.
- React delivery for world entities and associations has not started.
- Storytelling data models and backend endpoints exist in the backend, but the React routes for characters, locations, lore, and associations are still pending.

## In Scope

- character list/detail/form
- location list/detail/form
- lore item list/detail/form
- association/link workflows
- character generator

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/app/worlds/:worldId/characters` | `pages/characters_list.html` | P0 | List and create entry |
| `/app/characters/:characterId` | `pages/character_detail.html` | P1 | Detail route |
| `/app/worlds/:worldId/locations` | `pages/locations_list.html` | P0 | List and create entry |
| `/app/locations/:locationId` | `pages/location_detail.html` | P1 | Detail route |
| `/app/worlds/:worldId/lore-items` | `pages/lore_items_list.html` | P0 | List and create entry |
| `/app/lore-items/:loreItemId` | `pages/lore_item_detail.html` | P1 | Detail route |
| `/app/worlds/:worldId/character-generator` | `pages/character_generator.html` | P2 | Guided generator |

## Shared Components

- `EntityListTable`
- `EntityDetailHeader`
- `AssociationChipList`
- `AssociationManagerPanel`
- `LinkCharacterModal`
- `LinkLocationModal`
- `LinkLoreItemModal`

## Backend/API Dependencies

- character CRUD
- location CRUD
- lore item CRUD
- association endpoints
- character generation helper endpoints

## UI Behavior Capture Targets

- entity form save and delete flows
- association modal behavior
- entity detail action patterns

## Risks and Decisions

- Use one shared entity-list pattern where possible.
- Keep associations generic rather than hardcoding by page.

## Task List

- [ ] Build characters list route for a world.
- [ ] Build character create/edit form flow.
- [ ] Build character detail route.
- [ ] Build locations list route for a world.
- [ ] Build location create/edit form flow.
- [ ] Build location detail route.
- [ ] Build lore items list route for a world.
- [ ] Build lore item create/edit form flow.
- [ ] Build lore item detail route.
- [ ] Build generic association management UI and link modals.
- [ ] Build character generator route if still in scope.
- [ ] Capture entity form and association modal behavior in `uiBehaviorCapture.md`.

## Exit Criteria

- user can manage world elements
- associations can be created and removed
- detail pages are usable and navigable

## Implementation Status

- Not started in the React app.
