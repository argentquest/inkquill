# Storytelling Table Cutover Inventory

Generated from the live `inkquill_codebase` database on `2026-04-05`.

Scope of this document:
- inventory of all new `storytelling_*` tables and current row counts
- old vs new foreign-key structure comparison
- code cutover plan to move application reads to the new tables

Important constraints:
- this was a database-only create-and-copy exercise
- original non-prefixed storytelling tables still exist and remain untouched
- shared tables such as `users`, `prompts`, `generated_images`, and `ai_call_logs` were not duplicated

## New Table Inventory

| New table | Source table | Row count |
| --- | --- | ---: |
| `storytelling_worlds` | `worlds` | 14 |
| `storytelling_world_roles` | `world_roles` | 0 |
| `storytelling_world_collaborators` | `world_collaborators` | 0 |
| `storytelling_story_classes` | `story_classes` | 10 |
| `storytelling_stories` | `stories` | 6 |
| `storytelling_acts` | `acts` | 7 |
| `storytelling_scenes` | `scenes` | 7 |
| `storytelling_characters` | `characters` | 50 |
| `storytelling_locations` | `locations` | 29 |
| `storytelling_location_connections` | `location_connections` | 1 |
| `storytelling_lore_items` | `lore_items` | 32 |
| `storytelling_story_character_associations` | `story_character_associations` | 0 |
| `storytelling_story_location_associations` | `story_location_associations` | 0 |
| `storytelling_story_lore_item_associations` | `story_lore_item_associations` | 0 |
| `storytelling_act_character_associations` | `act_character_associations` | 0 |
| `storytelling_act_location_associations` | `act_location_associations` | 0 |
| `storytelling_act_lore_item_associations` | `act_lore_item_associations` | 0 |
| `storytelling_scene_character_associations` | `scene_character_associations` | 0 |
| `storytelling_scene_location_associations` | `scene_location_associations` | 0 |
| `storytelling_scene_lore_item_associations` | `scene_lore_item_associations` | 0 |
| `storytelling_story_chat_sessions` | `story_chat_sessions` | 0 |
| `storytelling_story_chat_messages` | `story_chat_messages` | 0 |
| `storytelling_brainstorm_sessions` | `brainstorm_sessions` | 0 |
| `storytelling_brainstorm_favorites` | `brainstorm_favorites` | 0 |
| `storytelling_brainstorm_stories` | `brainstorm_stories` | 0 |
| `storytelling_user_interview_responses` | `user_interview_responses` | 0 |
| `storytelling_published_stories` | `published_stories` | 0 |
| `storytelling_story_comments` | `story_comments` | 0 |
| `storytelling_story_ratings` | `story_ratings` | 0 |

Total new prefixed tables: `29`

## Foreign-Key Comparison

### Summary

For the copied storytelling domain, the foreign-key graph is structurally the same as the old schema, with table targets rewritten from old storytelling tables to the new `storytelling_*` tables.

What did not change:
- delete/update behaviors
- self-referential edges
- references to shared tables

What did change:
- storytelling-internal references now point to `storytelling_*` tables
- shared references still point to shared tables such as `users`, `prompts`, `generated_images`, and `ai_call_logs`

### Shared Tables Still Referenced By New Storytelling Tables

These remain external dependencies for the new prefixed schema:
- `users`
- `prompts`
- `generated_images`
- `ai_call_logs`

### Old To New FK Mapping

#### World Layer

| Old FK | New FK | Behavior |
| --- | --- | --- |
| `world_roles.world_id -> worlds.id` | `storytelling_world_roles.world_id -> storytelling_worlds.id` | `ON DELETE CASCADE` |
| `world_roles.created_by_user_id -> users.id` | `storytelling_world_roles.created_by_user_id -> users.id` | `ON DELETE SET NULL` |
| `world_collaborators.world_id -> worlds.id` | `storytelling_world_collaborators.world_id -> storytelling_worlds.id` | `ON DELETE CASCADE` |
| `world_collaborators.user_id -> users.id` | `storytelling_world_collaborators.user_id -> users.id` | `ON DELETE CASCADE` |
| `world_collaborators.invited_by_user_id -> users.id` | `storytelling_world_collaborators.invited_by_user_id -> users.id` | `ON DELETE SET NULL` |
| `worlds.user_id -> users.id` | `storytelling_worlds.user_id -> users.id` | `ON DELETE CASCADE` |
| `worlds.current_image_id -> generated_images.id` | `storytelling_worlds.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |

#### Story Structure Layer

| Old FK | New FK | Behavior |
| --- | --- | --- |
| `story_classes.world_id -> worlds.id` | `storytelling_story_classes.world_id -> storytelling_worlds.id` | `ON DELETE CASCADE` |
| `stories.world_id -> worlds.id` | `storytelling_stories.world_id -> storytelling_worlds.id` | `ON DELETE RESTRICT` |
| `stories.user_id -> users.id` | `storytelling_stories.user_id -> users.id` | no explicit delete rule |
| `stories.current_image_id -> generated_images.id` | `storytelling_stories.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |
| `acts.story_id -> stories.id` | `storytelling_acts.story_id -> storytelling_stories.id` | `ON DELETE CASCADE` |
| `acts.story_class_id -> story_classes.id` | `storytelling_acts.story_class_id -> storytelling_story_classes.id` | `ON DELETE SET NULL` |
| `acts.system_prompt_id -> prompts.id` | `storytelling_acts.system_prompt_id -> prompts.id` | `ON DELETE SET NULL` |
| `acts.current_image_id -> generated_images.id` | `storytelling_acts.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |
| `scenes.act_id -> acts.id` | `storytelling_scenes.act_id -> storytelling_acts.id` | `ON DELETE CASCADE` |
| `scenes.story_class_id -> story_classes.id` | `storytelling_scenes.story_class_id -> storytelling_story_classes.id` | `ON DELETE SET NULL` |
| `scenes.current_image_id -> generated_images.id` | `storytelling_scenes.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |

#### Entity Layer

| Old FK | New FK | Behavior |
| --- | --- | --- |
| `characters.world_id -> worlds.id` | `storytelling_characters.world_id -> storytelling_worlds.id` | `ON DELETE CASCADE` |
| `characters.current_location_id -> locations.id` | `storytelling_characters.current_location_id -> storytelling_locations.id` | `ON DELETE SET NULL` |
| `characters.current_image_id -> generated_images.id` | `storytelling_characters.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |
| `locations.world_id -> worlds.id` | `storytelling_locations.world_id -> storytelling_worlds.id` | `ON DELETE CASCADE` |
| `locations.parent_location_id -> locations.id` | `storytelling_locations.parent_location_id -> storytelling_locations.id` | `ON DELETE SET NULL` |
| `locations.current_image_id -> generated_images.id` | `storytelling_locations.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |
| `lore_items.world_id -> worlds.id` | `storytelling_lore_items.world_id -> storytelling_worlds.id` | `ON DELETE CASCADE` |
| `lore_items.current_location_id -> locations.id` | `storytelling_lore_items.current_location_id -> storytelling_locations.id` | `ON DELETE SET NULL` |
| `lore_items.current_image_id -> generated_images.id` | `storytelling_lore_items.current_image_id -> generated_images.id` | `ON DELETE SET NULL` |
| `location_connections.from_location_id -> locations.id` | `storytelling_location_connections.from_location_id -> storytelling_locations.id` | `ON DELETE CASCADE` |
| `location_connections.to_location_id -> locations.id` | `storytelling_location_connections.to_location_id -> storytelling_locations.id` | `ON DELETE CASCADE` |

#### Association Layer

| Old FK | New FK | Behavior |
| --- | --- | --- |
| `story_character_associations.story_id -> stories.id` | `storytelling_story_character_associations.story_id -> storytelling_stories.id` | `ON DELETE CASCADE` |
| `story_character_associations.character_id -> characters.id` | `storytelling_story_character_associations.character_id -> storytelling_characters.id` | `ON DELETE CASCADE` |
| `story_location_associations.story_id -> stories.id` | `storytelling_story_location_associations.story_id -> storytelling_stories.id` | `ON DELETE CASCADE` |
| `story_location_associations.location_id -> locations.id` | `storytelling_story_location_associations.location_id -> storytelling_locations.id` | `ON DELETE CASCADE` |
| `story_lore_item_associations.story_id -> stories.id` | `storytelling_story_lore_item_associations.story_id -> storytelling_stories.id` | `ON DELETE CASCADE` |
| `story_lore_item_associations.lore_item_id -> lore_items.id` | `storytelling_story_lore_item_associations.lore_item_id -> storytelling_lore_items.id` | `ON DELETE CASCADE` |
| `act_character_associations.act_id -> acts.id` | `storytelling_act_character_associations.act_id -> storytelling_acts.id` | `ON DELETE CASCADE` |
| `act_character_associations.character_id -> characters.id` | `storytelling_act_character_associations.character_id -> storytelling_characters.id` | `ON DELETE CASCADE` |
| `act_location_associations.act_id -> acts.id` | `storytelling_act_location_associations.act_id -> storytelling_acts.id` | `ON DELETE CASCADE` |
| `act_location_associations.location_id -> locations.id` | `storytelling_act_location_associations.location_id -> storytelling_locations.id` | `ON DELETE CASCADE` |
| `act_lore_item_associations.act_id -> acts.id` | `storytelling_act_lore_item_associations.act_id -> storytelling_acts.id` | `ON DELETE CASCADE` |
| `act_lore_item_associations.lore_item_id -> lore_items.id` | `storytelling_act_lore_item_associations.lore_item_id -> storytelling_lore_items.id` | `ON DELETE CASCADE` |
| `scene_character_associations.scene_id -> scenes.id` | `storytelling_scene_character_associations.scene_id -> storytelling_scenes.id` | `ON DELETE CASCADE` |
| `scene_character_associations.character_id -> characters.id` | `storytelling_scene_character_associations.character_id -> storytelling_characters.id` | `ON DELETE CASCADE` |
| `scene_location_associations.scene_id -> scenes.id` | `storytelling_scene_location_associations.scene_id -> storytelling_scenes.id` | `ON DELETE CASCADE` |
| `scene_location_associations.location_id -> locations.id` | `storytelling_scene_location_associations.location_id -> storytelling_locations.id` | `ON DELETE CASCADE` |
| `scene_lore_item_associations.scene_id -> scenes.id` | `storytelling_scene_lore_item_associations.scene_id -> storytelling_scenes.id` | `ON DELETE CASCADE` |
| `scene_lore_item_associations.lore_item_id -> lore_items.id` | `storytelling_scene_lore_item_associations.lore_item_id -> storytelling_lore_items.id` | `ON DELETE CASCADE` |

#### Chat, Brainstorm, Interview, Publish Layer

| Old FK | New FK | Behavior |
| --- | --- | --- |
| `story_chat_sessions.user_id -> users.id` | `storytelling_story_chat_sessions.user_id -> users.id` | `ON DELETE CASCADE` |
| `story_chat_sessions.story_id -> stories.id` | `storytelling_story_chat_sessions.story_id -> storytelling_stories.id` | `ON DELETE CASCADE` |
| `story_chat_messages.session_id -> story_chat_sessions.id` | `storytelling_story_chat_messages.session_id -> storytelling_story_chat_sessions.id` | `ON DELETE CASCADE` |
| `story_chat_messages.cost_log_id -> ai_call_logs.id` | `storytelling_story_chat_messages.cost_log_id -> ai_call_logs.id` | `ON DELETE SET NULL` |
| `brainstorm_sessions.user_id -> users.id` | `storytelling_brainstorm_sessions.user_id -> users.id` | no explicit delete rule |
| `brainstorm_sessions.interview_response_id -> user_interview_responses.id` | `storytelling_brainstorm_sessions.interview_response_id -> storytelling_user_interview_responses.id` | no explicit delete rule |
| `brainstorm_favorites.session_id -> brainstorm_sessions.id` | `storytelling_brainstorm_favorites.session_id -> storytelling_brainstorm_sessions.id` | no explicit delete rule |
| `brainstorm_favorites.user_id -> users.id` | `storytelling_brainstorm_favorites.user_id -> users.id` | no explicit delete rule |
| `brainstorm_stories.favorite_id -> brainstorm_favorites.id` | `storytelling_brainstorm_stories.favorite_id -> storytelling_brainstorm_favorites.id` | no explicit delete rule |
| `brainstorm_stories.story_id -> stories.id` | `storytelling_brainstorm_stories.story_id -> storytelling_stories.id` | no explicit delete rule |
| `brainstorm_stories.user_id -> users.id` | `storytelling_brainstorm_stories.user_id -> users.id` | no explicit delete rule |
| `user_interview_responses.user_id -> users.id` | `storytelling_user_interview_responses.user_id -> users.id` | no explicit delete rule |
| `published_stories.story_id -> stories.id` | `storytelling_published_stories.story_id -> storytelling_stories.id` | `ON DELETE CASCADE` |
| `published_stories.user_id -> users.id` | `storytelling_published_stories.user_id -> users.id` | `ON DELETE CASCADE` |
| `story_comments.parent_comment_id -> story_comments.id` | `storytelling_story_comments.parent_comment_id -> storytelling_story_comments.id` | `ON DELETE CASCADE` |
| `story_comments.published_story_id -> published_stories.id` | `storytelling_story_comments.published_story_id -> storytelling_published_stories.id` | `ON DELETE CASCADE` |
| `story_comments.user_id -> users.id` | `storytelling_story_comments.user_id -> users.id` | `ON DELETE CASCADE` |
| `story_ratings.published_story_id -> published_stories.id` | `storytelling_story_ratings.published_story_id -> storytelling_published_stories.id` | `ON DELETE CASCADE` |
| `story_ratings.user_id -> users.id` | `storytelling_story_ratings.user_id -> users.id` | `ON DELETE CASCADE` |

## Structural Notes

### Internal Storytelling References Were Successfully Repointed

Examples:
- `storytelling_stories.world_id` now points to `storytelling_worlds`
- `storytelling_acts.story_id` now points to `storytelling_stories`
- `storytelling_scenes.act_id` now points to `storytelling_acts`
- `storytelling_characters.current_location_id` now points to `storytelling_locations`

### Shared Dependencies Were Intentionally Left Shared

Examples:
- all `*_user_id` columns still point to `users`
- all `current_image_id` columns still point to `generated_images`
- `storytelling_acts.system_prompt_id` still points to `prompts`
- `storytelling_story_chat_messages.cost_log_id` still points to `ai_call_logs`

### Cycles Still Exist In The New Schema

These are inherited from the old storytelling schema:
- `storytelling_characters.current_location_id -> storytelling_locations.id`
- `storytelling_locations.parent_location_id -> storytelling_locations.id`
- `storytelling_lore_items.current_location_id -> storytelling_locations.id`

That means a future cutover should not assume the storytelling schema is a simple DAG. Any future re-copy or dual-write strategy should preserve deferred or staged FK handling.

## Code Cutover Plan

### Goal

Move application reads from old storytelling tables to the new `storytelling_*` tables, while leaving shared tables unchanged.

### Phase 1: Freeze The Mapping

Create a single source-of-truth mapping document in code:

- `worlds` -> `storytelling_worlds`
- `world_roles` -> `storytelling_world_roles`
- `world_collaborators` -> `storytelling_world_collaborators`
- `story_classes` -> `storytelling_story_classes`
- `stories` -> `storytelling_stories`
- `acts` -> `storytelling_acts`
- `scenes` -> `storytelling_scenes`
- `characters` -> `storytelling_characters`
- `locations` -> `storytelling_locations`
- `location_connections` -> `storytelling_location_connections`
- `lore_items` -> `storytelling_lore_items`
- all storytelling association tables -> corresponding `storytelling_*` names
- `story_chat_sessions` -> `storytelling_story_chat_sessions`
- `story_chat_messages` -> `storytelling_story_chat_messages`
- `brainstorm_*` -> `storytelling_brainstorm_*`
- `user_interview_responses` -> `storytelling_user_interview_responses`
- `published_stories` -> `storytelling_published_stories`
- `story_comments` -> `storytelling_story_comments`
- `story_ratings` -> `storytelling_story_ratings`

### Phase 2: Add Parallel SQLAlchemy Models

Add new model classes for the `storytelling_*` tables rather than renaming existing ones in place.

Recommendation:
- keep old models temporarily for comparison and rollback
- add new prefixed models in a separate module such as `app/models/storytelling_prefixed.py`
- update only read-path routers/services first

### Phase 3: Read-Only Cutover First

Switch these read-heavy areas first:
- world detail/list endpoints
- story detail/list endpoints
- act and scene read endpoints
- character, location, and lore read endpoints
- story graph and association reads

Do not switch writes first.

Reason:
- read cutover is easier to verify
- row-count and FK parity already exist
- failures are easier to isolate

### Phase 4: Switch CRUD Writes

After reads are stable:
- world CRUD
- story CRUD
- act CRUD
- scene CRUD
- character/location/lore CRUD
- association table writes

At that point choose one of these strategies:
- write only to new prefixed tables and freeze old tables
- dual-write for a temporary validation window

Recommendation:
- use a short dual-write window only if you need rollback insurance
- otherwise cut directly to new writes once read paths are proven

### Phase 5: Switch Secondary Storytelling Features

Move these after core content CRUD:
- story chat
- brainstorm flows
- welcome interview and importer flows
- published stories, comments, ratings

These all depend on the core story identity graph, so they should come after core world/story/act/scene/entity cutover.

### Phase 6: Shared-Adjacent Tables Stay Shared

Do not move these during the first code cutover:
- `generated_images`
- `uploaded_documents`
- `prompts`
- `chat_sessions`
- `chat_messages`
- `ai_call_logs`

They are either clearly shared already or not part of the database-only copy performed here.

### Phase 7: Verification Requirements

For each cutover slice, verify:
- row counts old vs new
- spot-check foreign-key integrity
- API response parity for representative endpoints
- full backend unit and integration suite
- Playwright coverage for any UI paths reading storytelling data

### Suggested Cutover Order

1. models for `storytelling_worlds`, `storytelling_story_classes`, `storytelling_stories`
2. models for `storytelling_acts`, `storytelling_scenes`
3. models for `storytelling_characters`, `storytelling_locations`, `storytelling_lore_items`
4. models for association tables
5. switch read routers/services
6. switch write routers/services
7. move story chat and brainstorm
8. move publish/comment/rating flows
9. deprecate old non-prefixed storytelling tables after stable verification

## Recommendation

The database state is now good enough to begin a read-path cutover.

Best next step:
- add parallel SQLAlchemy models for the new `storytelling_*` tables
- switch a narrow, read-only slice first:
  - worlds
  - stories
  - acts
  - scenes

That is the highest-signal, lowest-risk way to evaluate whether the new prefixed schema should become the app source of truth.
