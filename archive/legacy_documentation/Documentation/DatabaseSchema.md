# Database Schema (Entity Relationship Diagram - Textual Representation)

This document provides a textual representation of the application's PostgreSQL database schema, outlining tables, their columns, primary keys, and relationships.

**Note:** This is a conceptual ERD in text. For a visual diagram, you would typically use a dedicated ERD tool (e.g., dbdiagram.io, draw.io) based on this schema.

---

## Tables & Relationships

### `users` table
*   **Purpose:** Stores user account information for authentication and ownership.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `username`: VARCHAR(100), NOT NULL, UNIQUE, INDEX
    *   `email`: VARCHAR(255), UNIQUE, INDEX (nullable)
    *   `hashed_password`: VARCHAR, NOT NULL
    *   `display_name`: VARCHAR(100) (nullable)
    *   `is_active`: BOOLEAN, NOT NULL, DEFAULT FALSE
    *   `created_at`: TIMESTAMPTZ, NOT NULL, DEFAULT NOW()
    *   `updated_at`: TIMESTAMPTZ, NOT NULL, DEFAULT NOW() (on update)
*   **Relationships (Owns):** `worlds`, `stories`, `uploaded_documents`, `prompts`, `job_statuses`, `ai_call_logs`.

---

### `worlds` table
*   **Purpose:** A fictional world container for lore, characters, and locations.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `name`: VARCHAR(255), NOT NULL, INDEX
    *   `description`: TEXT (nullable)
    *   `user_id`: INTEGER, NOT NULL, INDEX, FOREIGN KEY (`users.id` ON DELETE CASCADE)
*   **Relationships:** Belongs to one `user`. Owns `characters`, `locations`, `lore_items`, and `stories`.

---

### `stories` table
*   **Purpose:** A creative story project set within a specific world.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `title`: VARCHAR(255), NOT NULL, INDEX
    *   `short_description`: TEXT (nullable)
    *   `user_id`: INTEGER, NOT NULL, INDEX, FOREIGN KEY (`users.id`)
    *   `world_id`: INTEGER, NOT NULL, INDEX, FOREIGN KEY (`worlds.id` ON DELETE RESTRICT)
*   **Relationships:** Belongs to one `user` and one `world`. Owns `acts`. Associated with `characters`, `locations`, `lore_items` via many-to-many tables.

---

### `acts` table
*   **Purpose:** A major narrative division within a story.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `title`: VARCHAR(255), NOT NULL
    *   `description`: TEXT (nullable)
    *   `act_number`: INTEGER, NOT NULL
    *   `story_id`: INTEGER, NOT NULL, FOREIGN KEY (`stories.id` ON DELETE CASCADE)
    *   `system_prompt_id`: INTEGER, FOREIGN KEY (`prompts.id` ON DELETE SET NULL) (nullable)
*   **Constraints:** `UNIQUE(story_id, act_number)`
*   **Relationships:** Belongs to one `story`. Owns `scenes`.

---

### `scenes` table
*   **Purpose:** A smaller narrative unit within an act.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `scene_number`: INTEGER, NOT NULL
    *   `title`: VARCHAR(255) (nullable)
    *   `summary`: TEXT (nullable)
    *   `content`: TEXT (nullable)
    *   `act_id`: INTEGER, NOT NULL, FOREIGN KEY (`acts.id` ON DELETE CASCADE)
*   **Constraints:** `UNIQUE(act_id, scene_number)`
*   **Relationships:** Belongs to one `act`.

---

### `characters`, `locations`, `lore_items` tables
*   **Purpose:** Define the building blocks of a World.
*   **Common Columns:** `id`, `name`/`title`, `description`, `world_id` (FK to `worlds.id` ON DELETE CASCADE).
*   **Relationships:** Each belongs to one `world` and can be associated with many `stories` via association tables.

---

### `prompts` table
*   **Purpose:** Stores reusable AI prompt templates.
*   **Columns:** `id`, `title`, `prompt_content`, `prompt_type` (ENUM), `user_id` (FK to `users.id` ON DELETE SET NULL).

---

### `uploaded_documents` table
*   **Purpose:** Tracks user-uploaded files and system-generated Context documents.
*   **Columns:** `id`, `filename`, `blob_storage_path`, `status` (ENUM), `user_id` (FK), `world_id` (FK), `source_element_type` (ENUM), `source_character_id` (FK), etc.

---

### `job_statuses` table (New)
*   **Purpose:** Tracks the state of long-running asynchronous background jobs.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `job_id`: VARCHAR(255), NOT NULL, UNIQUE
    *   `job_type`: `job_type_enum`, NOT NULL
    *   `state`: `job_state_enum`, NOT NULL, DEFAULT 'PENDING'
    *   `status_message`: VARCHAR(512) (nullable)
    *   `result_message`: TEXT (nullable)
    *   `user_id`: INTEGER, NOT NULL, FOREIGN KEY (`users.id` ON DELETE CASCADE)
    *   `world_id`: INTEGER, FOREIGN KEY (`worlds.id` ON DELETE SET NULL) (nullable)
*   **Relationships:** Belongs to one `user`. Can be linked to a `world`.

---

### `ai_call_logs` table (New)
*   **Purpose:** Logs every AI API call to track token usage, cost, and latency.
*   **Columns:**
    *   `id`: INTEGER, PRIMARY KEY
    *   `job_id`: VARCHAR(255), FOREIGN KEY (`job_statuses.job_id`) (nullable)
    *   `user_id`: INTEGER, NOT NULL, FOREIGN KEY (`users.id` ON DELETE CASCADE)
    *   `model_name`: VARCHAR(255), NOT NULL
    *   `call_type`: VARCHAR(50), NOT NULL
    *   `prompt_tokens`: INTEGER, DEFAULT 0
    *   `completion_tokens`: INTEGER, DEFAULT 0
    *   `total_tokens`: INTEGER, DEFAULT 0
    *   `calculated_cost_usd`: NUMERIC(10, 8), DEFAULT 0.0
    *   `duration_ms`: INTEGER (nullable)
*   **Relationships:** Belongs to one `user`. Can be linked to a `job_status`.

---

### Association Tables (Many-to-Many)
*   `story_character_association`
*   `story_location_association`
*   `story_lore_item_association`

---

### Enumeration Types (Enums)
*   **`document_status_enum`**: UPLOADED, PENDING, PROCESSING_TEXT, CHUNKING, PREPARING_CONTEXT, STORING_CONTEXT, COMPLETED, ERROR
*   **`prompt_type_enum`**: GENERAL, CHARACTER_DEVELOPMENT, SYSTEM, ACT, STORY, etc.
*   **`lore_item_category_enum`**: MAGIC_SYSTEM, HISTORICAL_EVENT, ARTIFACT, etc.
*   **`source_element_type_enum`**: USER_UPLOADED, CHARACTER_LORE, LOCATION_LORE, LORE_ITEM_LORE
*   **`job_type_enum` (New)**: WORLD_EXTRACTION_FROM_DOC, DOCUMENT_CONTEXT_PROCESSING, WORLD_IMPORT_FROM_TITLE
*   **`job_state_enum` (New)**: PENDING, RUNNING, COMPLETED, FAILED
