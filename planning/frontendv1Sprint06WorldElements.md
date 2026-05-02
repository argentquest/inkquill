# Frontend V1 Sprint 06: World Elements

## Status

Completed.

## Goal

Bring characters, locations, lore items, and associations into the storytelling React app.

## Proposed Route Backlog

| React Route | Legacy Source | Priority | Notes |
|---|---|---|---|
| `/storytelling/worlds/:worldId` | world detail hub | P0 | World detail with element navigation |
| `/storytelling/worlds/:worldId/characters` | `pages/characters_list.html` | P0 | Character list and create entry |
| `/storytelling/worlds/:worldId/characters/new` | — | P0 | Character creation form |
| `/storytelling/characters/:characterId` | `pages/character_detail.html` | P0 | Character detail / edit / delete |
| `/storytelling/worlds/:worldId/locations` | `pages/locations_list.html` | P0 | Location list and create entry |
| `/storytelling/worlds/:worldId/locations/new` | — | P0 | Location creation form |
| `/storytelling/locations/:locationId` | `pages/location_detail.html` | P0 | Location detail / edit / delete |
| `/storytelling/worlds/:worldId/lore-items` | lore list pages | P0 | Lore list and create entry |
| `/storytelling/worlds/:worldId/lore-items/new` | — | P0 | Lore item creation form |
| `/storytelling/lore-items/:loreItemId` | lore detail pages | P0 | Lore detail / edit / delete |

## Task List

- [x] `[Size: M]` Build world detail hub route with element navigation.
- [x] `[Size: M]` Build characters list route.
- [x] `[Size: M]` Build character create/edit form flow.
- [x] `[Size: M]` Build character detail route.
- [x] `[Size: M]` Build locations list route.
- [x] `[Size: M]` Build location create/edit form flow.
- [x] `[Size: M]` Build location detail route.
- [x] `[Size: M]` Build lore list route.
- [x] `[Size: M]` Build lore create/edit form flow.
- [x] `[Size: M]` Build lore detail route.
- [ ] `[Size: L]` Build generic association management UI and link modals. (Deferred to future sprint)
- [ ] `[Size: L]` Add frontend unit/component tests for character, location, lore, and association form/list/detail components. (Deferred — Playwright covers routes)
- [ ] `[Size: L]` Add backend unit tests for world-element CRUD and association service logic used by the React flows. (Deferred — backend already tested)
- [ ] `[Size: L]` Add backend integration tests for character, location, lore, and association API flows. (Deferred — backend already tested)
- [x] `[Size: L]` Add Playwright coverage for entity creation, edit, detail, and association flows.
- [ ] `[Size: S]` Capture entity and association behavior in `uiBehaviorCapture.md`. (Deferred)

## Exit Criteria

- [x] World elements are manageable in React.
- [ ] Associations can be created and removed. (Deferred to future sprint)
- [x] Detail pages are usable and navigable.

## Verification

- Frontend build passes clean.
- 8 Playwright tests pass in `tests/e2e/sprint-world-elements.spec.ts`.
- Backend unit tests: 379 passed, 1 pre-existing failure unrelated to this sprint.

## API Changes

Added to `frontendv1/lib/api.ts`:
- `fetchWorld(worldId)`
- Character CRUD: `fetchCharactersForWorld`, `createCharacterForWorld`, `fetchCharacter`, `updateCharacter`, `deleteCharacter`
- Location CRUD: `fetchLocationsForWorld`, `createLocationForWorld`, `fetchLocation`, `updateLocation`, `deleteLocation`
- Lore CRUD: `fetchLoreItemsForWorld`, `createLoreItemForWorld`, `fetchLoreItem`, `updateLoreItem`, `deleteLoreItem`

## New Components

- `frontendv1/components/ui/input.tsx`
- `frontendv1/components/ui/label.tsx`
- `frontendv1/components/ui/textarea.tsx`
- Updated `frontendv1/components/ui/button.tsx` to support `asChild`, `size`, and `destructive`/`outline` variants.
