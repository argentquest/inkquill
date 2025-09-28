# AI Storytelling Assistant -REFACTOR_DEPS_WS_LOGGING`**
    *   **Task:** **Clean Up WebSocket Dependency Logging.**
    *   **Description:** Review `app/core/deps_ws.py` and replace any remaining `print()` statements from debugging sessions with standard `logger.debug()` or `logger.info()` calls.
 Prioritized Task Backlog
**Last Updated:** {{ currentDate }} (Replace with actual date)

This document outlines the prioritized list of development tasks, enhancements, and bug fixes for the AI Storytelling Assistant project.

---

## Ⅰ    *   **Status:** **Ready for Implementation.** This is a quick code quality improvement.
    *   **Files Affected:** `app/core/deps_ws.py`.

3.  **Task ID: `P7_01_CLEANUP_OBSOLETE_JS`**
    *   **Task:** **Clean Up Obsolete JavaScript. Immediate Priorities

These tasks focus on testing recently completed features and cleaning up remaining technical debt from recent refactoring.

1.  **Task ID: `P8_01_TEST_AI_REVIEW_CONTEXT`**
    *   **Description:** End-to-end test and verify the dynamic context population (previous act summaries, linked world elements) for the " Files.**
    *   **Description:** The monolithic `act_editor.js` and `scene_editor.js` files are now obsolete due to the new modular JavaScript structure. Delete these files and ensure no HTML templates still reference them.
    *   **Status:** **Ready for Implementation.** This is a critical cleanup to reduce technical debt.
    *   **Files Affected:** `app/static/js/act_editor.js` (delete), `app/static/js/scene_editor.js` (deleteAI Act Review" feature. The backend logic is complete, but it needs validation to ensure the AI's suggestions are contextually accurate.
    *   **Status:** **To Do.**
    *   **Files Affected:** Primarily a testing task.), all HTML templates in `app/templates/pages/`.

---

## High Priority (Next Major Features & Enhancements)

4.  **Task ID: `P8_03_ENHANCE_RAG_SEMANTIC_SEARCH`**
    *   **Task:** **Implement Semantic Ranking for RAG.**
    *   **Description:** Improve Involves `app/routers/act_ai_review.py` and reviewing AI output.

2.  **Task ID: `P8_02_REFACTOR_DEPS_WS_LOGGING`**
    *   **Description:** Review `app/core/deps_ws.py`. Remove any remaining `print()` statements used for debugging and replace them with standard `logger.debug()` calls to align with the application's logging framework.
    *   **Status:** **To Do.**
    *   **Files Affected:** `app/core/deps_ws.py`.

3. the quality of RAG results by implementing hybrid search with semantic ranking. This involves modifying the Azure AI Search query in `app/services/rag_retrieval.py` to use `query_type="semantic"` and the pre-defined `semantic_configuration_name`.  **Task ID: `P7_01_CLEANUP_OBSOLETE_JS`**
    *   **Description:** Identify and remove obsolete monolithic JavaScript files (`act_editor.js`, `scene_editor.js`) now that the modular JS structure for the editors is in place. Ensure no HTML templates still reference them.
    *   **Status:** **To Do.**
    *   **Files Affected:** `app/static/js/act_editor.js`, `app/static/js/scene_editor.js`, various `app/templates/pages/*.html` files to check for `<script>` tags.

---

## Ⅱ. High-Impact Features & Enhancements

These are the next major
    *   **Status:** **Ready for Implementation.** The search index is already configured for this.
    *   **Files Affected:** `app/services/rag_retrieval.py`.

5.  **Task ID: `P7_03_FEATURE_PROMPT_QUICK_USE`**
    *   **Task:** **Implement "Quick Use" Button in Prompt Library.**
    *   **Description:** Add a "Use" button next to each prompt in the Prompt Library UI. Clicking it should navigate the user to the relevant editor (e.g., Act or Scene Editor) and pre-fill the AI instruction input with the selected prompt's content.
    *   **Status:** New Feature. Not started.
    *   **Files Affected:** `app/templates/pages/prompt_list.html`, new/existing JavaScript for that page.

6.  **Task ID: `P6_02_ENHANCE_PERSONA_IN_PROMPTS`**
    *   **Task:** **Deepen Character/Persona Integration in AI Prompts.**
    *   **Description:** Enhance how Character details are passed to the AI during features and quality-of-life improvements to work on once the immediate priorities are complete.

4.  **Task ID: `P8_03_ENHANCE_RAG_SEMANTIC_SEARCH`**
    *   **Description:** Implement and utilize semantic search (or hybrid search with semantic ranking) for RAG retrieval. This involves modifying the search queries in `app/services/rag_retrieval.py` to use `query_type="semantic"` and a `semantic_configuration_name narrative generation. Instead of just a simple context string, consider passing a more structured summary of traits, motivations, and relationships to make the AI more "character-aware."
    *   **Status:** New Feature. A strategic enhancement for generation quality.
    *   **Files Affected:** `app/routers/ai_assisted_writing.py`, `app/routers/ai_scene_writing.py`, relevant prompt template files.

---

## Medium Priority (Quality of Life & Documentation)

7.  **Task ID: `P5_03_ENHANCE_PUBLISH_FILENAME`**
    *   **Task:** **Make "Publish Story" Filename Deterministic.**
    *   **`.
    *   **Status:** New Feature. Azure AI Search index is already configured for this.
    *   **Files Affected:** `app/services/rag_retrieval.py`.

5.  **Task ID: `P7_03_FEATURE_PROMPT_QUICK_USE`**
    *   **Description:** Implement a "Quick Use" feature in the Prompt Library. Add a button next to each prompt that navigates the user to an appropriate editor and pre-fills the AI instruction input with the selected prompt's content.
    *   **Status:** New Feature.
    *   **Files Affected:** `app/templates/pages/prompt_list.html`, new/existing JavaScript for that page.

6.  **Task ID:Description:** Modify the story publishing feature so that re-publishing the same story overwrites the existing HTML file in Azure Blob Storage. This requires generating a consistent filename based on `story_id` and a sanitized title, removing the random UUID.
    *   **Status:** Not started.
    *   **Files Affected:** `app/routers/story.py`.

8.  **Task ID: `P6_01_DOCS_ALEMBIC_README_UPDATE`**
    *   **Task:** **Update Alembic README.**
    *   **Description:** Update `alembic/README` to accurately reflect that `P6_02_ENHANCE_PERSONA_IN_PROMPTS`**
    *   **Description:** Deepen the integration of Character details into AI narrative generation prompts for Acts and Scenes. The goal is to make the AI more "character-aware" by passing more structured data about traits, motivations, and relationships.
    *   **Status:** New Feature / Enhancement.
    *   **Files Affected:** `app/prompts/system/`, `app/routers/ai_assisted_writing.py`, `app/routers/ai_scene_writing.py`.

---

## Ⅲ. General Backlog & Code Quality

These tasks are important for maintainability and improving the user experience but can be addressed after the higher-priority items.

7.  **Task ID: `P5_03_ENHANCE_PUBLISH_FILENAME`**
    *   **Description:** Modify the "Publish Story" feature to use a deterministic filename (e.g., based on ` the database URL is dynamically set by `env.py` from the application's core configuration, not from `alembic.ini`.
    *   **Status:** Not started. Quick documentation task.
    *   **Files Affected:** `alembic/README`.

9.  **Task ID: `P2_03_FEATURE_USER_GUIDE_REVIEW`**
story_id` and a sanitized title) so that re-publishing a story overwrites the existing file instead of creating a new one with a UUID.
    *   **Status:** Enhancement.
    *   **Files Affected:** `app/routers/story.py`.

8.  **Task ID: `P4_02_FEATURE_RAG_PREVIEW_EDITORS`**
    *   **Description:** In the Act/Scene editors, display a preview of the RAG context snippets *before* the main AI narrative generation begins. This requires the WebSocket to send a dedicated message with the RAG results first.
    *   **Status:** New Feature.
    *   **Files Affected:** `app/routers/ai_assisted_writing.py`, `app/routers/ai_scene_writing.py`, `app/    *   **Task:** **Review and Update User Guide.**
    *   **Description:** Thoroughly review the content of `app/templates/pages/user_guide.html` to ensure it accurately reflects all current application features, including world-building, job tracking, and the new import features.
    *   **Status:** Not started. Important for usability.
    *   **Files Affected:** `app/templates/pages/user_guide.html`.

---

## Completed or Obsolete Tasks

*   **Task ID: `P0_02_WEBSOCKET_ACT_EDITOR_403` - DONE**
    *   **Description:** Resolve 403 Forbidden error for WebSocket connection.
    *   **Resolution:** All startup `ImportError` and `NameError` issues related to dependencies have been resolved,static/js/` editor modules.

9.  **Task ID: `P3_05_SECURITY_TOKENPAYLOAD_REVIEW`**
    *   **Description:** Review the `TokenPayload` Pydantic schema and its usage in `app/core/security.py`. Consider if more explicit validation of claims (like `type`) is needed after decoding.
    *   **Status:** Code Quality.
    *   **Files Affected:** `app/schemas/token.py`, `app/core/security.py`.

10. **Task ID: `P3_06_CLEANUP_DIAGNOSTIC_SCRIPTS`**
    *   **Description:** Review all `maintest_*.py` and `test_*.py` scripts in the `app/` directory. Delete which was the root cause of the server failing before the WebSocket could authenticate.

*   **Task ID: `P0_03_REFACTOR_ACT_ROUTER_VERIFY` - DONE**
    *   **Description:** Verify the Act router refactor.
    *   **Resolution:** The AI Review logic was successfully moved to its own router (`act_ai_review.py`) and is functional.

*   **Task ID: `P3_02_REFACTOR_SK_SETUP_VERIFY` - DONE**
    *   **Description:** Finalize and verify Semantic Kernel refactoring.
    *   **Resolution:** The refactor into `sk_kernel_instance.py` and the `sk_plugins/` directory is complete and the application starts correctly.

*   **Task ID: `P5_02_REFACTOR_DOC_PROCESSOR_CHUNKER` - DONE**
    *   **Description:** Refactor document processing and chunking.
    *   **Resolution:** The monolithic `document_processor.py` was deleted and its logic was refactored into a dedicated blob service obsolete files and evaluate if the remaining scripts are still valuable or if their functionality should be moved to formal tests.
    *   **Status:** Housekeeping.
    *   **Files Affected:** All `*test*.py` files in `app/`.

11. **Task ID: `P6_01_DOCS_ALEMBIC_README_UPDATE`**
    *   **Description:** Update `alembic/README` to accurately describe how the database URL is dynamically sourced from the main app config.
    *   **Status:** Documentation.
    *   **Files Affected:** `alembic/README`.

---

## ✅ Completed / Resolved Tasks

*   **Task ID: `P0_02_WEBSOCKET_ACT_EDITOR (`azure_blob_service.py`) and a new RAG ingestion module (`rag_ingestion.py`).

*   **Task ID: `P7_02_CLEANUP_OBSOLETE_CRUD_DOC` - DONE**
    *   **Description:** Review and remove obsolete `create_document_record` function.
    *   **Resolution:** This function was removed during the refactoring of `document_processor.py`, and all calls now correctly use the schema-based creation function.

*   **Task ID: `P3_05_SECURITY_TOKENPAYLOAD_REVIEW_403` & `P3_04_STABILITY_PROMPT_FILE_HANDLING` & Startup Errors**
    *   **Resolution:** All application startup errors, including various `ImportError` and `NameError` issues related to dependency injection and module loading, have been resolved. The application now starts cleanly.

*   **Task ID: `P3_02_REFACTOR_SK_SETUP_VERIFY`**
    *   **Resolution:** The` - DONE**
    *   **Description:** Review `TokenPayload` usage.
    *   **Resolution:** The `decode_access_token` function in `security.py` now correctly returns the full payload dictionary, and the dependencies in `deps.py` and `deps_ws.py` correctly handle this dictionary. This approach is sound.