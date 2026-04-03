# Schema Gap Report
Source of truth: SQLAlchemy model code.
- Code tables: `67`
- Database tables: `19`
- Missing tables in database: `49`
- Extra tables in database: `0`

## Missing Tables
- `ai_model_configurations`
- `blog_categories`
- `blog_tags`
- `chat_samples`
- `credit_packages`
- `cta_contents`
- `forum_categories`
- `anonymous_user_sessions`
- `blog_author_profiles`
- `blog_follows`
- `blog_posts`
- `blog_subscriptions`
- `refresh_tokens`
- `social_share_daily_summaries`
- `social_shares`
- `user_accounts`
- `user_activities`
- `user_interview_responses`
- `blog_analytics_summary`
- `blog_comments`
- `blog_content_links`
- `blog_likes`
- `blog_post_associations`
- `blog_post_tags`
- `blog_views`
- `brainstorm_sessions`
- `brainstorm_favorites`
- `chat_sessions`
- `world_collaborators`
- `world_roles`
- `brainstorm_stories`
- `forum_threads`
- `published_stories`
- `story_location_associations`
- `act_character_associations`
- `act_location_associations`
- `act_lore_item_associations`
- `chat_messages`
- `forum_posts`
- `forum_subscriptions`
- `story_character_associations`
- `story_comments`
- `story_lore_item_associations`
- `story_ratings`
- `user_transactions`
- `forum_votes`
- `scene_character_associations`
- `scene_location_associations`
- `scene_lore_item_associations`

## Extra Tables In Database
- None

## Existing Tables With Drift
### `acts`
- Missing columns: `ai_summary`, `current_image_id`, `image_prompt_definition`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `ai_call_logs`
- Missing columns: `input_prompt`, `model_config_id`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP

### `characters`
- Missing columns: `age_category`, `core_motivation`, `core_motivations`, `first_meeting_message`, `gender`, `generated_narrative`, `genre`, `genre_specific_answers`, `importance_rating`, `is_ai_generated`, `key_relationships`, `narrative_filter_results`, `next_quest_scenario`, `physical_attributes`, `profession`, `relationships`, `short_backstory`, `species`, `visual_prompt`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `generated_images`
- Missing columns: `aspect_ratio`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `image_uuid` mismatch: type code=CHAR(32) db=UUID

### `job_statuses`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `location_connections`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `locations`
- Missing columns: `connected_elements`, `cultural_context`, `geography`, `importance_rating`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `dimension_x` mismatch: type code=FLOAT db=DOUBLE PRECISION
- Column `dimension_y` mismatch: type code=FLOAT db=DOUBLE PRECISION
- Column `dimension_z` mismatch: type code=FLOAT db=DOUBLE PRECISION
- Column `map_x` mismatch: type code=FLOAT db=DOUBLE PRECISION
- Column `map_y` mismatch: type code=FLOAT db=DOUBLE PRECISION
- Column `map_z` mismatch: type code=FLOAT db=DOUBLE PRECISION
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `lore_items`
- Missing columns: `importance_rating`, `related_elements`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `prompts`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `scenes`
- Missing columns: `ai_summary`, `image_prompt_definition`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `stories`
- Missing columns: `ai_summary`, `current_image_id`, `image_blob_path`, `image_prompt_definition`, `primary_conflict_type`, `story_genre`, `story_tone`, `story_type`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `story_classes`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `uploaded_documents`
- Column `processed_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `uploaded_at` mismatch: type code=DATETIME db=TIMESTAMP

### `users`
- Missing columns: `auth_provider`, `bonus1`, `bonus10`, `bonus2`, `bonus3`, `bonus4`, `bonus5`, `bonus6`, `bonus7`, `bonus8`, `bonus9`, `interview_data`, `is_admin`, `profile_picture_url`, `provider_data`, `provider_id`, `referral_count`, `referred_by_user_id`, `reset_token`, `reset_token_expires`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `hashed_password` mismatch: nullable code=True db=False
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

### `worlds`
- Missing columns: `current_image_id`, `image_blob_path`, `image_prompt_definition`, `is_free_chat_enabled`, `is_shadow`, `short_description`, `world_builder_data`
- Column `created_at` mismatch: type code=DATETIME db=TIMESTAMP
- Column `updated_at` mismatch: type code=DATETIME db=TIMESTAMP

