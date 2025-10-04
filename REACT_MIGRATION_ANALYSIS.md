# React Frontend Migration Analysis

**FastAPI AI Storytelling Application - Complete Migration Plan**

## Executive Summary

This document provides a comprehensive analysis for migrating the current server-rendered Jinja2 + JavaScript frontend to a modern React SPA with TypeScript, Ant Design, and TanStack Query. The application is a sophisticated AI-powered storytelling platform with real-time WebSocket features, RAG (Retrieval Augmented Generation) capabilities, and complex world-building tools.

**Key Statistics:**
- **78 Router Files** (API + View routers)
- **36 Schema Files** defining request/response models
- **50+ JavaScript Files** for frontend logic
- **100+ HTML Templates** (Jinja2-based)
- **2 WebSocket Endpoints** for real-time AI assistance
- **REST API Endpoints:** 200+ endpoints across all routers

---

## 1. Current Backend API Analysis

### 1.1 Core Authentication & User Management

#### Authentication Router (`app/routers/auth.py`)

**Endpoints:**
```
POST   /api/v1/auth/register                    - User registration with referral tracking
POST   /api/v1/auth/login                       - Login (sets HttpOnly cookie)
GET    /api/v1/auth/ws-ticket                   - Get WebSocket authentication ticket
POST   /api/v1/auth/impersonate                 - Admin: impersonate user
POST   /api/v1/auth/stop-impersonation          - Admin: stop impersonation
POST   /api/v1/auth/password-reset/request      - Request password reset
POST   /api/v1/auth/password-reset/confirm      - Confirm password reset with token
POST   /api/v1/auth/ws-ticket                   - Generate WebSocket ticket
```

**Current Auth Flow:**
- Uses **HttpOnly cookies** for JWT tokens (access_token cookie)
- Token expires in configured minutes (AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
- WebSocket authentication via temporary tickets (5-minute expiry)
- Referral tracking via cookies and middleware

**Issues for React Migration:**
- HttpOnly cookies work but limit client-side token management
- No refresh token mechanism
- WebSocket ticket system needs client-side coordination

#### Users Router (`app/routers/users.py`)

**Endpoints:**
```
GET    /api/v1/users/me                         - Get current user profile
GET    /api/v1/users/{user_id}                  - Get user by ID
GET    /api/v1/users/                           - List all users (admin only)
PATCH  /api/v1/users/{user_id}/toggle-active    - Toggle user active status (admin)
PATCH  /api/v1/users/{user_id}/edit             - Edit user details (admin)
```

### 1.2 World Building & Content Management

#### Worlds Router (`app/routers/world.py`)

**Endpoints:**
```
POST   /api/v1/worlds/                          - Create new world
GET    /api/v1/worlds/                          - List user's worlds
GET    /api/v1/worlds/has-non-shadow-worlds     - Check if user has non-shadow worlds
GET    /api/v1/worlds/{world_id}                - Get single world
PUT    /api/v1/worlds/{world_id}                - Update world
DELETE /api/v1/worlds/{world_id}                - Delete world (if no stories)
GET    /api/v1/worlds/{world_id}/stories        - List stories for world
GET    /api/v1/worlds/{world_id}/images         - List images for world
POST   /api/v1/worlds/{world_id}/set-current-image/{image_id} - Set current image
POST   /api/v1/worlds/{world_id}/stories/generate - Generate story from world elements
POST   /api/v1/worlds/dev/reload-kernel         - Reload semantic kernel (dev only)
```

#### Characters Router (`app/routers/character.py`)

**Three separate routers for different contexts:**

**World Characters Router** (`/api/v1/worlds/{world_id}/characters`):
```
POST   /worlds/{world_id}/characters/           - Create character for world
GET    /worlds/{world_id}/characters/           - List characters in world
```

**Characters Router** (`/api/v1/characters`):
```
GET    /characters/{character_id}               - Get single character
PUT    /characters/{character_id}               - Update character
DELETE /characters/{character_id}               - Delete character
GET    /characters/{character_id}/images        - List images for character
POST   /characters/{character_id}/set-current-image/{image_id} - Set current image
GET    /characters/{character_id}/generated-rag-content - Get AI-generated RAG content
```

**Story Characters Router** (`/api/v1/stories/{story_id}/characters`):
```
POST   /stories/{story_id}/characters/          - Link character to story
DELETE /stories/{story_id}/characters/{character_id} - Unlink character from story
GET    /stories/{story_id}/characters/          - List characters for story
```

#### Locations Router (`app/routers/location.py`)
Similar structure to Characters with three routers:
- World Locations: `/api/v1/worlds/{world_id}/locations`
- Locations: `/api/v1/locations`
- Story Locations: `/api/v1/stories/{story_id}/locations`

#### Lore Items Router (`app/routers/lore_item.py`)
Similar structure to Characters with three routers:
- World Lore Items: `/api/v1/worlds/{world_id}/lore-items`
- Lore Items: `/api/v1/lore-items`
- Story Lore Items: `/api/v1/stories/{story_id}/lore-items`

#### Location Connections Router (`app/routers/location_connection.py`)
```
POST   /api/v1/worlds/{world_id}/location-connections/ - Create connection
GET    /api/v1/worlds/{world_id}/location-connections/ - List connections
GET    /api/v1/location-connections/{connection_id}    - Get single connection
PUT    /api/v1/location-connections/{connection_id}    - Update connection
DELETE /api/v1/location-connections/{connection_id}    - Delete connection
```

### 1.3 Story Management

#### Stories Router (`app/routers/story.py`)

**Core Story Endpoints:**
```
POST   /api/v1/stories/                         - Create new story
GET    /api/v1/stories/                         - List user's stories
GET    /api/v1/stories/{story_id}               - Get single story
PUT    /api/v1/stories/{story_id}               - Update story
DELETE /api/v1/stories/{story_id}               - Delete story
POST   /api/v1/stories/{story_id}/publish       - Compile & publish story to HTML
GET    /api/v1/stories/{story_id}/images        - List story images
POST   /api/v1/stories/{story_id}/set-current-image/{image_id} - Set current image
POST   /api/v1/stories/{story_id}/upgrade       - Upgrade basic story to advanced
```

#### Acts Router (`app/routers/act.py`)

**Two separate routers:**

**Story Acts Router** (`/api/v1/stories/{story_id}/acts`):
```
POST   /stories/{story_id}/acts/                - Create act for story
GET    /stories/{story_id}/acts/                - List acts for story
```

**Acts Router** (`/api/v1/acts`):
```
GET    /acts/{act_id}                           - Get single act
PUT    /acts/{act_id}                           - Update act
DELETE /acts/{act_id}                           - Delete act
GET    /acts/{act_id}/images                    - List images for act
POST   /acts/{act_id}/set-current-image/{image_id} - Set current image
```

#### Scenes Router (`app/routers/scene.py`)

**Two separate routers:**

**Act Scenes Router** (`/api/v1/acts/{act_id}/scenes`):
```
POST   /acts/{act_id}/scenes/                   - Create scene for act
GET    /acts/{act_id}/scenes/                   - List scenes for act
```

**Scenes Router** (`/api/v1/scenes`):
```
GET    /scenes/{scene_id}                       - Get single scene
PUT    /scenes/{scene_id}                       - Update scene
DELETE /scenes/{scene_id}                       - Delete scene
GET    /scenes/{scene_id}/images                - List images for scene
POST   /scenes/{scene_id}/set-current-image/{image_id} - Set current image
```

#### Basic Stories Router (`app/routers/basic_stories.py`)
```
POST   /api/v1/basic-stories/                   - Create basic story
GET    /api/v1/basic-stories/                   - List basic stories
GET    /api/v1/basic-stories/{story_id}         - Get basic story
PUT    /api/v1/basic-stories/{story_id}         - Update basic story
DELETE /api/v1/basic-stories/{story_id}         - Delete basic story
POST   /api/v1/basic-stories/{story_id}/generate - AI generate content
```

#### Associations Router (`app/routers/associations.py`)
```
POST   /api/v1/associations/story/{story_id}/character - Link character to story
DELETE /api/v1/associations/story/{story_id}/character/{character_id} - Unlink
POST   /api/v1/associations/story/{story_id}/location - Link location to story
DELETE /api/v1/associations/story/{story_id}/location/{location_id} - Unlink
POST   /api/v1/associations/story/{story_id}/lore-item - Link lore item to story
DELETE /api/v1/associations/story/{story_id}/lore-item/{lore_item_id} - Unlink
# Similar endpoints for act and scene associations
```

### 1.4 AI-Powered Features

#### WebSocket Endpoints

**Act AI Writing** (`app/routers/ai_assisted_writing.py`):
```
WEBSOCKET /ws/stories/{story_id}/acts/{act_id}/generate
```

**Message Protocol:**
```javascript
// Client → Server
{
  "user_instruction": string,
  "current_act_content": string,  // HTML content
  "generation_mode": "Continue/Append" | "Rewrite" | "Edit Selected",
  "selected_text": string,
  "model_config_id": number | null
}

// Server → Client
{
  "type": "narrative_generation_start_act" |
          "narrative_content_chunk_act" |
          "narrative_generation_end_act" |
          "metadata_result_act" |
          "error_act",
  "data": string  // chunk or JSON metadata
}
```

**Scene AI Writing** (`app/routers/ai_scene_writing.py`):
```
WEBSOCKET /ws/stories/{story_id}/acts/{act_id}/scenes/{scene_id}/generate
```

**Message Protocol:**
```javascript
// Client → Server
{
  "user_instruction_for_scene": string,
  "scene_current_content": string,  // HTML content
  "generation_mode": "Continue/Append" | "Rewrite" | "Edit Selected",
  "selected_text": string,
  "model_config_id": number | null
}

// Server → Client
{
  "type": "narrative_generation_start" |
          "narrative_content_chunk" |
          "narrative_generation_end" |
          "metadata_result" |
          "error",
  "data": string  // chunk or JSON metadata
}
```

**WebSocket Authentication:**
1. Client requests ticket: `GET /api/v1/auth/ws-ticket`
2. Receives short-lived JWT (5 min expiry)
3. Connects to WebSocket with ticket as query param or in handshake
4. Dependency `get_current_user_from_ws_ticket` validates ticket

#### World Chat (`app/routers/world_chat.py`)
```
GET    /api/v1/world-chat/chat/samples         - Get chat sample prompts
POST   /api/v1/world-chat/sessions/{world_id}  - Create chat session
GET    /api/v1/world-chat/sessions/{world_id}  - List chat sessions
GET    /api/v1/world-chat/sessions/{world_id}/{session_id} - Get session with messages
POST   /api/v1/world-chat/sessions/{world_id}/{session_id}/messages - Send message
DELETE /api/v1/world-chat/sessions/{world_id}/{session_id} - Delete session
GET    /api/v1/world-chat/world-context/{world_id} - Get world context data
```

#### Story Chat (`app/routers/story_chat.py`)
```
POST   /api/v1/story-chat/sessions             - Create story chat session
GET    /api/v1/story-chat/sessions/{story_id}  - List sessions for story
GET    /api/v1/story-chat/sessions/{story_id}/{session_id} - Get session
POST   /api/v1/story-chat/sessions/{story_id}/{session_id}/messages - Send message
DELETE /api/v1/story-chat/sessions/{story_id}/{session_id} - Delete session
```

#### World Builder (`app/routers/world_builder.py`)
```
GET    /api/v1/world-builder/genres            - Get available genres
GET    /api/v1/world-builder/questions/{genre} - Get questions for genre
POST   /api/v1/world-builder/analyze           - Analyze answers & generate world
POST   /api/v1/world-builder/generate          - Generate world elements
POST   /api/v1/world-builder/refine            - Refine generated elements
PUT    /api/v1/world-builder/save/{world_id}   - Save world elements to DB
```

#### Story Wizard (`app/routers/story_wizard_api.py`)
```
POST   /api/v1/story-wizard/chat               - Chat with story wizard
POST   /api/v1/story-wizard/generate-report    - Generate story report
POST   /api/v1/story-wizard/create-story       - Create story from wizard
```

#### AI Model Configuration (`app/routers/ai_model_config.py`)
```
GET    /api/v1/ai-model-configs/               - List AI model configs
GET    /api/v1/ai-model-configs/{config_id}    - Get single config
POST   /api/v1/ai-model-configs/               - Create config (admin)
PUT    /api/v1/ai-model-configs/{config_id}    - Update config (admin)
DELETE /api/v1/ai-model-configs/{config_id}    - Delete config (admin)
GET    /api/v1/ai-model-configs/default/{operation_type} - Get default config
```

#### AI Text Transform (`app/routers/ai_text_transform.py`)
```
POST   /api/v1/ai-text-transform/transform     - Transform text with AI
POST   /api/v1/ai-text-transform/translate     - Translate text
POST   /api/v1/ai-text-transform/summarize     - Summarize text
POST   /api/v1/ai-text-transform/expand        - Expand text
```

#### Act AI Review (`app/routers/act_ai_review.py`)
```
POST   /api/v1/acts/{act_id}/ai-review         - Get AI review for act
POST   /api/v1/acts/{act_id}/ai-suggestions    - Get AI suggestions
```

### 1.5 Document & Image Management

#### Document Upload (`app/routers/document_upload.py`)
```
POST   /api/v1/documents/upload                - Upload document
GET    /api/v1/documents/                      - List documents
GET    /api/v1/documents/{document_id}         - Get document
DELETE /api/v1/documents/{document_id}         - Delete document
POST   /api/v1/documents/{document_id}/process - Process document for RAG
GET    /api/v1/documents/world/{world_id}      - List documents for world
```

#### Image Generation (`app/routers/image_generation.py`)
```
POST   /api/v1/images/generate                 - Generate image with DALL-E
POST   /api/v1/images/generate/{element_type}/{element_id} - Generate for element
GET    /api/v1/images/job/{job_id}             - Get generation job status
GET    /api/v1/images/element/{element_type}/{element_id} - Get images for element
GET    /api/v1/images/admin/jobs               - Admin: list all jobs
POST   /api/v1/images/admin/jobs/{job_id}/retry - Admin: retry failed job
```

#### World Importer (`app/routers/world_importer.py`)
```
POST   /api/v1/world-importer/import/from-book - Import world from book
POST   /api/v1/world-importer/import/create-from-document - Create world from doc
GET    /api/v1/world-importer/import/job-status/{job_id} - Get import job status
```

### 1.6 Publishing & Sharing

#### Published Stories (`app/routers/published_stories.py`)
```
GET    /api/v1/published-stories/              - List public stories
GET    /api/v1/published-stories/user/{user_id} - List user's published stories
GET    /api/v1/published-stories/{story_id}    - Get published story
PUT    /api/v1/published-stories/{story_id}    - Update published story
DELETE /api/v1/published-stories/{story_id}    - Unpublish story
POST   /api/v1/published-stories/{story_id}/toggle-visibility - Toggle public/private
```

#### Social Sharing (`app/routers/social_sharing.py`)
```
POST   /api/v1/social/share                    - Create shareable link
GET    /api/v1/social/share/{share_id}         - Get share by ID
POST   /api/v1/social/track-click/{share_id}   - Track share click
GET    /api/v1/social/analytics/{user_id}      - Get sharing analytics
```

#### Social Preview (`app/routers/social_preview.py`)
```
GET    /api/v1/social-preview/world/{world_id} - Get OG preview for world
GET    /api/v1/social-preview/story/{story_id} - Get OG preview for story
GET    /api/v1/social-preview/character/{character_id} - Get OG preview for character
```

### 1.7 Community Features

#### Forum (`app/routers/forum_*.py`)
```
# Categories
GET    /api/v1/forum/categories/               - List categories
POST   /api/v1/forum/categories/               - Create category (admin)
GET    /api/v1/forum/categories/{category_id}  - Get category
PUT    /api/v1/forum/categories/{category_id}  - Update category (admin)

# Threads
GET    /api/v1/forum/threads/                  - List threads
POST   /api/v1/forum/threads/                  - Create thread
GET    /api/v1/forum/threads/{thread_id}       - Get thread
PUT    /api/v1/forum/threads/{thread_id}       - Update thread
DELETE /api/v1/forum/threads/{thread_id}       - Delete thread
POST   /api/v1/forum/threads/{thread_id}/pin   - Pin thread (mod)

# Posts
GET    /api/v1/forum/posts/                    - List posts
POST   /api/v1/forum/posts/                    - Create post
GET    /api/v1/forum/posts/{post_id}           - Get post
PUT    /api/v1/forum/posts/{post_id}           - Update post
DELETE /api/v1/forum/posts/{post_id}           - Delete post
```

### 1.8 Blog Platform

#### Blog (`app/routers/blog.py`)
```
GET    /api/v1/blog/posts/                     - List blog posts
POST   /api/v1/blog/posts/                     - Create post (author)
GET    /api/v1/blog/posts/{post_id}            - Get post
PUT    /api/v1/blog/posts/{post_id}            - Update post
DELETE /api/v1/blog/posts/{post_id}            - Delete post
POST   /api/v1/blog/posts/{post_id}/publish    - Publish post
POST   /api/v1/blog/posts/{post_id}/unpublish  - Unpublish post
```

#### Blog Categories & Tags
```
GET    /api/v1/blog/categories/                - List categories
POST   /api/v1/blog/categories/                - Create category
GET    /api/v1/blog/tags/                      - List tags
POST   /api/v1/blog/tags/                      - Create tag
```

#### Blog Engagement
```
POST   /api/v1/blog/posts/{post_id}/like       - Like post
DELETE /api/v1/blog/posts/{post_id}/like       - Unlike post
GET    /api/v1/blog/posts/{post_id}/likes      - Get like count
POST   /api/v1/blog/posts/{post_id}/view       - Track view
```

#### Blog AI Writing
```
POST   /api/v1/blog/ai/generate-outline        - Generate blog outline
POST   /api/v1/blog/ai/expand-section          - Expand blog section
POST   /api/v1/blog/ai/suggest-title           - Suggest blog title
POST   /api/v1/blog/ai/improve-seo             - Improve SEO
```

### 1.9 Billing & Administration

#### Billing (`app/routers/billing.py`)
```
GET    /api/v1/billing/balance                 - Get user credit balance
GET    /api/v1/billing/transactions            - List transactions
POST   /api/v1/billing/purchase                - Purchase credits
GET    /api/v1/billing/packages                - List credit packages
GET    /api/v1/billing/ai-costs/last           - Get last AI costs
GET    /api/v1/billing/ai-costs/summary        - Get cost summary
```

#### Admin Billing (`app/routers/admin_billing.py`)
```
GET    /api/v1/admin/billing/users             - List users with balances
GET    /api/v1/admin/billing/transactions      - All transactions
POST   /api/v1/admin/billing/adjust-balance    - Adjust user balance
GET    /api/v1/admin/billing/ai-costs          - AI cost analytics
```

#### Maintenance (`app/routers/maintenance.py`)
```
GET    /api/v1/maintenance/status              - Get maintenance status
POST   /api/v1/maintenance/enable              - Enable maintenance mode (admin)
POST   /api/v1/maintenance/disable             - Disable maintenance mode (admin)
PUT    /api/v1/maintenance/message             - Update maintenance message (admin)
```

#### Admin News (`app/routers/admin_news.py`)
```
GET    /api/v1/news/                           - List news items
GET    /api/v1/news/{news_id}                  - Get news item
POST   /api/v1/admin/news/                     - Create news (admin)
PUT    /api/v1/admin/news/{news_id}            - Update news (admin)
DELETE /api/v1/admin/news/{news_id}            - Delete news (admin)
```

#### Referrals (`app/routers/referrals.py`)
```
GET    /api/v1/referrals/my-code               - Get user's referral code
GET    /api/v1/referrals/stats                 - Get referral stats
GET    /api/v1/referrals/conversions           - List conversions
POST   /api/v1/referrals/track                 - Track referral visit
```

### 1.10 Other Features

#### Interview (`app/routers/interview.py`)
```
POST   /api/v1/interview/start                 - Start interview
POST   /api/v1/interview/answer                - Submit answer
POST   /api/v1/interview/complete              - Complete interview
GET    /api/v1/interview/results/{session_id}  - Get results
```

#### Welcome Interview (`app/routers/welcome_interview.py`)
```
POST   /api/v1/welcome-interview/analyze       - Analyze welcome interview
GET    /api/v1/welcome-interview/bonus-status  - Check bonus eligibility
POST   /api/v1/welcome-interview/claim-bonus   - Claim welcome bonus
```

#### Brainstorm (`app/routers/brainstorm.py`)
```
POST   /api/v1/brainstorm/session              - Create brainstorm session
POST   /api/v1/brainstorm/{session_id}/message - Send brainstorm message
GET    /api/v1/brainstorm/{session_id}         - Get session
```

#### Story Classes (`app/routers/story_class.py`)
```
GET    /api/v1/story-classes/                  - List story classes
POST   /api/v1/story-classes/                  - Create class (admin)
GET    /api/v1/story-classes/{class_id}        - Get class
PUT    /api/v1/story-classes/{class_id}        - Update class (admin)
DELETE /api/v1/story-classes/{class_id}        - Delete class (admin)
```

#### Prompts (`app/routers/prompt.py`)
```
GET    /api/v1/prompts/                        - List prompts
POST   /api/v1/prompts/                        - Create prompt
GET    /api/v1/prompts/{prompt_id}             - Get prompt
PUT    /api/v1/prompts/{prompt_id}             - Update prompt
DELETE /api/v1/prompts/{prompt_id}             - Delete prompt
```

---

## 2. Current Frontend Structure Analysis

### 2.1 Template Organization

**Total Templates:** 100+ Jinja2 HTML files

**Main Categories:**

1. **Pages** (`app/templates/pages/`):
   - World building: `world_builder.html`, `world_map.html`, `character_generator.html`
   - Story management: `story_wizard.html`, `act_form.html`, `scene_form.html`
   - User: `edit_user.html`, `register.html`, `forgot_password.html`
   - Admin: `admin_news_form.html`, `admin_help_editor.html`, `admin_image_jobs.html`
   - Forum: `forum_home.html`, `forum_category.html`, `forum_thread.html`
   - Lists: `character_list_for_world.html`, `location_list_for_world.html`, `lore_item_list_for_world.html`

2. **Blog Templates** (`app/templates/blog/`):
   - `home_new.html`, `post_list.html`, `post_detail.html`
   - `author_dashboard.html`, `author.html`

3. **Components** (`app/templates/components/`):
   - Cards: `basic_card.html`, `status_card.html`, `action_card.html`
   - Modals: `base_modal.html`, `confirmation_modal.html`, `success_modal.html`
   - Forms: `input.html`, `textarea.html`, `select.html`
   - Buttons: `button.html`, `button_group.html`
   - Other: `alert.html`, `breadcrumb.html`, `progress_bar.html`, `badge.html`

4. **Partials** (`app/templates/partials/`):
   - `_navbar.html`, `_topbar.html`, `_breadcrumbs.html`, `_alerts.html`
   - `_ai_model_selector.html`, `_ai_model_card_selector.html`, `_ai_model_button_selector.html`
   - `_link_character_modal.html`, `_link_location_modal.html`, `_link_lore_item_modal.html`
   - `interview.html`, `interview_simple.html`, `interview_full.html`
   - `_social_sharing.html`, `_google_signin_button.html`

5. **Basic Story** (`app/templates/basic_story/`):
   - `create.html`, `detail.html`

6. **Help Content** (`app/templates/help/`):
   - `forum_home.html`, `import_book.html`, `import_document.html`
   - `lore_item_detail.html`, `lore_item_list.html`, `prompts.html`

7. **Email Templates** (`app/templates/emails/`):
   - `base.html`, `welcome.html`, `password_reset.html`
   - `story_completion.html`, `maintenance.html`

### 2.2 JavaScript Architecture

**Total JS Files:** 50+ files

**Key JavaScript Modules:**

1. **CRUD Operations:**
   - `world_crud.js`, `character_crud.js`, `location_crud.js`, `lore_item_crud.js`
   - `story_crud.js`, `act_crud.js`, `scene_crud.js`
   - `prompt_crud.js`, `story_class_crud.js`, `document_crud.js`

2. **Form Handlers:**
   - `world_form_handler.js`, `character_form_handler.js`, `location_form_handler.js`
   - `story_form_handler.js`, `act_form_handler.js`, `lore_item_form_handler.js`
   - `prompt_form_handler.js`, `world_importer_form_handler.js`

3. **AI & WebSocket:**
   - `act_websocket_handler.js` - Handles WebSocket for act AI generation
   - `scene_websocket_handler.js` - Handles WebSocket for scene AI generation
   - `act_ai_processor.js` - Processes AI responses for acts
   - `scene_ai_processor.js` - Processes AI responses for scenes
   - `ai_model_selector.js` - AI model selection UI

4. **UI Updaters:**
   - `act_ui_updater.js` - Updates act editor UI
   - `scene_ui_updater.js` - Updates scene editor UI

5. **World Chat:**
   - `world_chat_main.js` - Main chat UI controller
   - `world_chat_session_manager.js` - Session management
   - `world_chat_context_loader.js` - Context loading
   - `world_chat_message_handler.js` - Message handling

6. **Story Features:**
   - `story_chat.js` - Story-specific chat
   - `story_generation_modal.js` - Story generation UI
   - `story_associations_handler.js` - Manage story associations

7. **AI Review:**
   - `act_review_components/quill_manager_review.js`
   - `act_review_components/text_highlighter_review.js`
   - `act_review_components/ui_updater_review.js`
   - `act_review_components/api_handler_review.js`

8. **Editors & Tools:**
   - `act_main.js` - Main act editor logic
   - `act_prompt_manager.js` - Prompt management for acts
   - `scene_prompt_selector.js` - Prompt selection for scenes
   - `act_save_handler.js`, `scene_save_handler.js` - Auto-save handlers

9. **Other:**
   - `world_map.js` - Interactive world map
   - `document_upload.js` - Document upload UI
   - `import_world_handler.js` - World import UI
   - `billing_dashboard.js` - Billing UI
   - `admin_users.js`, `edit_user.js` - Admin UI
   - `maintenance.js` - Maintenance mode UI
   - `social-sharing.js` - Social sharing UI
   - `help-panel.js` - Help panel UI
   - `sidebar.js` - Sidebar navigation
   - `notifications.js` - Notification system
   - `utils.js` - Utility functions

10. **Page-Specific:**
    - `pages/story-wizard.js` - Story wizard logic
    - `analytics_tracking_examples.js` - GA4 tracking examples

### 2.3 Current UI Patterns

**Tabler Premium Features in Use:**

1. **Hero Headers** (gradient backgrounds):
   - Used across all major pages
   - Gradient: `linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%)`
   - White text with actions in header area

2. **Card Components:**
   - Enhanced cards with hover effects
   - `translateY(-4px)` on hover
   - Animated gradient borders
   - Status badges with gradient backgrounds

3. **Forms:**
   - Tabler form controls with focus states
   - Enhanced input styling
   - Floating labels support

4. **Modals:**
   - Enhanced modal headers with gradients
   - Center-aligned titles
   - Proper sizing with `modal-xl`

5. **Buttons:**
   - Consistent button styling
   - `btn btn-warning` for help buttons (yellow/orange)
   - `btn btn-primary` for main actions
   - `btn btn-light` for gradient backgrounds
   - Icon + text pattern with `me-1` spacing

6. **Animations:**
   - `fadeInUp` animations with staggered delays
   - Smooth transitions with `cubic-bezier(0.4, 0, 0.2, 1)`
   - 0.2-0.3s hover transitions

7. **Empty States:**
   - Large avatars (`avatar-xl`) with icons
   - Descriptive text
   - Primary action buttons
   - Status bars (`card-status-top`)

### 2.4 Key JavaScript Dependencies

**From Templates Analysis:**

1. **Rich Text Editor:**
   - Quill.js - Used in act/scene editors
   - Custom toolbar configurations
   - Markdown conversion support

2. **UI Framework:**
   - Tabler Premium CSS/JS
   - Bootstrap 5 (via Tabler)
   - Font Awesome icons

3. **HTTP:**
   - Native `fetch` API
   - No Axios or other HTTP library

4. **Utilities:**
   - Markdownify for HTML to Markdown conversion
   - DOMPurify for sanitization (possibly)

5. **WebSocket:**
   - Native WebSocket API
   - Custom connection managers

6. **Analytics:**
   - Google Analytics 4 (gtag.js)
   - Custom event tracking

---

## 3. Backend Refactoring Requirements

### 3.1 Authentication Changes

**Current Issues:**
- HttpOnly cookie approach limits React SPA flexibility
- No refresh token mechanism
- Token stored in cookie not accessible to React

**Required Changes:**

1. **New Token Endpoint:**
```python
POST /api/v1/auth/token
Request: { "username": str, "password": str }
Response: {
  "access_token": str,
  "refresh_token": str,
  "token_type": "bearer",
  "expires_in": int
}
```

2. **Refresh Token Endpoint:**
```python
POST /api/v1/auth/refresh
Request: { "refresh_token": str }
Response: {
  "access_token": str,
  "expires_in": int
}
```

3. **Update Existing Endpoints:**
- Keep `/api/v1/auth/login` for backward compatibility
- Add `/api/v1/auth/logout` that invalidates refresh token
- WebSocket ticket generation remains the same

4. **Middleware Changes:**
- Support both cookie-based and Bearer token auth
- Add `Authorization: Bearer <token>` header support
- Deprecate cookie auth over time

### 3.2 Presentation Logic Separation

**Current Issues:**
- View routers (`views_*.py`) mix presentation with data
- HTML rendering happens server-side
- Some endpoints return redirects instead of data

**Required Changes:**

1. **Remove View Routers:**
   - All `views_*.py` files can be eliminated
   - Keep only API routers

2. **Convert Redirect Endpoints:**
```python
# OLD (view router)
@router.post("/create-world")
async def create_world(form_data):
    # ... create world ...
    return RedirectResponse(url=f"/ui/worlds/{world.id}")

# NEW (API router)
@router.post("/api/v1/worlds")
async def create_world(world_data: WorldCreate):
    # ... create world ...
    return WorldRead.from_orm(world)  # Return JSON
```

3. **Separate Concerns:**
   - API routers: Return JSON only
   - React: Handle routing, navigation, UI rendering
   - Backend: Business logic, data validation, persistence

### 3.3 New Endpoints Needed

1. **Batch Operations:**
```python
# Get multiple entities in one request
POST /api/v1/batch/characters
Request: { "ids": [1, 2, 3] }
Response: { "characters": [...] }

POST /api/v1/batch/locations
POST /api/v1/batch/lore-items
```

2. **Optimized List Endpoints:**
```python
# Current: Multiple round trips
GET /api/v1/worlds/{world_id}
GET /api/v1/worlds/{world_id}/characters
GET /api/v1/worlds/{world_id}/locations
GET /api/v1/worlds/{world_id}/lore-items

# New: Single request with nested data
GET /api/v1/worlds/{world_id}?include=characters,locations,lore_items
Response: {
  "id": 1,
  "name": "...",
  "characters": [...],
  "locations": [...],
  "lore_items": [...]
}
```

3. **Search & Filter:**
```python
GET /api/v1/search?q=dragon&type=character,location
GET /api/v1/worlds/{world_id}/search?q=castle
```

4. **Dashboard Data:**
```python
GET /api/v1/dashboard/summary
Response: {
  "worlds_count": 5,
  "stories_count": 12,
  "characters_count": 45,
  "recent_activity": [...],
  "ai_credits_remaining": 1000
}
```

### 3.4 WebSocket Refactoring

**Current Implementation:**
- Ticket-based auth (good, keep this)
- Custom connection managers (good pattern)
- Message protocols defined but not documented

**Improvements Needed:**

1. **Standardize Message Format:**
```typescript
// All WS messages should follow this structure
interface WebSocketMessage<T = any> {
  type: string;
  data?: T;
  error?: {
    code: string;
    message: string;
  };
  metadata?: {
    timestamp: number;
    sequence?: number;
  };
}
```

2. **Add Reconnection Support:**
```python
# Server should support resuming from last sequence
{
  "type": "resume",
  "data": {
    "last_sequence": 42
  }
}
```

3. **Heartbeat/Keepalive:**
```python
# Add ping/pong for connection health
{
  "type": "ping",
  "metadata": { "timestamp": 1234567890 }
}
```

### 3.5 Response Format Standardization

**Current State:**
- Most endpoints return Pydantic models (good)
- Some return dicts or plain strings
- Error responses not consistent

**Standardize All Responses:**

```typescript
// Success Response
interface ApiResponse<T> {
  success: true;
  data: T;
  meta?: {
    pagination?: {
      total: number;
      page: number;
      per_page: number;
    };
  };
}

// Error Response
interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  };
}
```

**Implementation:**
```python
# Create response wrapper
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: Optional[dict] = None

class ApiError(BaseModel):
    success: bool = False
    error: dict

# Use in endpoints
@router.get("/worlds/")
async def list_worlds() -> ApiResponse[List[WorldRead]]:
    worlds = await crud_world.get_worlds_by_user(...)
    return ApiResponse(
        data=worlds,
        meta={"pagination": {"total": len(worlds)}}
    )
```

### 3.6 CORS Configuration

**Current:**
```python
# app/main.py
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o).strip() for o in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
```

**Update for React SPA:**
```python
# .env
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://app.yourdomain.com

# More specific headers for production
CORS_ALLOW_HEADERS=Content-Type,Authorization,X-Request-ID
CORS_EXPOSE_HEADERS=X-Total-Count,X-Page,X-Per-Page
```

---

## 4. React Architecture Design

### 4.1 Project Structure

```
react-app/
├── public/
│   ├── index.html
│   └── assets/
│       └── images/
├── src/
│   ├── main.tsx                    # Entry point
│   ├── App.tsx                     # Root component
│   ├── vite-env.d.ts              # TypeScript declarations
│   │
│   ├── api/                        # API client layer
│   │   ├── client.ts              # Axios instance with interceptors
│   │   ├── endpoints/             # Typed API endpoints
│   │   │   ├── auth.ts
│   │   │   ├── worlds.ts
│   │   │   ├── characters.ts
│   │   │   ├── stories.ts
│   │   │   ├── acts.ts
│   │   │   ├── scenes.ts
│   │   │   ├── chat.ts
│   │   │   └── ...
│   │   ├── websocket/             # WebSocket clients
│   │   │   ├── base.ts            # Base WS client class
│   │   │   ├── actWriter.ts       # Act AI writing WS
│   │   │   └── sceneWriter.ts     # Scene AI writing WS
│   │   └── types.ts               # Shared API types
│   │
│   ├── components/                 # Reusable components
│   │   ├── common/                # Generic components
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Modal/
│   │   │   ├── Form/
│   │   │   ├── Table/
│   │   │   ├── Empty/
│   │   │   └── Loading/
│   │   ├── layout/                # Layout components
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   └── PageHeader/
│   │   ├── features/              # Feature-specific components
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── PasswordResetForm.tsx
│   │   │   ├── world/
│   │   │   │   ├── WorldCard.tsx
│   │   │   │   ├── WorldForm.tsx
│   │   │   │   ├── WorldStats.tsx
│   │   │   │   └── WorldMap.tsx
│   │   │   ├── character/
│   │   │   │   ├── CharacterCard.tsx
│   │   │   │   ├── CharacterForm.tsx
│   │   │   │   ├── CharacterList.tsx
│   │   │   │   └── CharacterGenerator.tsx
│   │   │   ├── story/
│   │   │   │   ├── StoryCard.tsx
│   │   │   │   ├── StoryForm.tsx
│   │   │   │   ├── StoryWizard/
│   │   │   │   └── StoryPublisher.tsx
│   │   │   ├── editor/
│   │   │   │   ├── ActEditor/
│   │   │   │   │   ├── index.tsx
│   │   │   │   │   ├── Toolbar.tsx
│   │   │   │   │   ├── AIAssistant.tsx
│   │   │   │   │   └── EditorContent.tsx
│   │   │   │   ├── SceneEditor/
│   │   │   │   └── RichTextEditor/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── ChatSamples.tsx
│   │   │   ├── ai/
│   │   │   │   ├── ModelSelector.tsx
│   │   │   │   ├── StreamingText.tsx
│   │   │   │   ├── PromptLibrary.tsx
│   │   │   │   └── GenerationStatus.tsx
│   │   │   └── associations/
│   │   │       ├── LinkCharacterModal.tsx
│   │   │       ├── LinkLocationModal.tsx
│   │   │       └── LinkLoreItemModal.tsx
│   │   └── index.ts               # Component exports
│   │
│   ├── pages/                      # Page components (routes)
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── ForgotPassword.tsx
│   │   ├── dashboard/
│   │   │   └── Dashboard.tsx
│   │   ├── worlds/
│   │   │   ├── WorldList.tsx
│   │   │   ├── WorldDetail.tsx
│   │   │   ├── WorldCreate.tsx
│   │   │   ├── WorldEdit.tsx
│   │   │   └── WorldBuilder.tsx
│   │   ├── characters/
│   │   │   ├── CharacterList.tsx
│   │   │   ├── CharacterDetail.tsx
│   │   │   ├── CharacterCreate.tsx
│   │   │   └── CharacterGenerator.tsx
│   │   ├── locations/
│   │   │   ├── LocationList.tsx
│   │   │   ├── LocationDetail.tsx
│   │   │   └── LocationCreate.tsx
│   │   ├── lore/
│   │   │   ├── LoreItemList.tsx
│   │   │   ├── LoreItemDetail.tsx
│   │   │   └── LoreItemCreate.tsx
│   │   ├── stories/
│   │   │   ├── StoryList.tsx
│   │   │   ├── StoryDetail.tsx
│   │   │   ├── StoryCreate.tsx
│   │   │   └── StoryWizard.tsx
│   │   ├── acts/
│   │   │   ├── ActDetail.tsx
│   │   │   ├── ActEditor.tsx
│   │   │   └── ActReview.tsx
│   │   ├── scenes/
│   │   │   ├── SceneDetail.tsx
│   │   │   └── SceneEditor.tsx
│   │   ├── chat/
│   │   │   ├── WorldChat.tsx
│   │   │   └── StoryChat.tsx
│   │   ├── documents/
│   │   │   └── DocumentManager.tsx
│   │   ├── billing/
│   │   │   └── BillingDashboard.tsx
│   │   ├── admin/
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── UserManagement.tsx
│   │   │   ├── NewsManagement.tsx
│   │   │   └── MaintenanceMode.tsx
│   │   ├── forum/
│   │   │   ├── ForumHome.tsx
│   │   │   ├── CategoryView.tsx
│   │   │   └── ThreadView.tsx
│   │   ├── blog/
│   │   │   ├── BlogHome.tsx
│   │   │   ├── BlogPost.tsx
│   │   │   └── BlogEditor.tsx
│   │   └── account/
│   │       ├── MyAccount.tsx
│   │       └── Settings.tsx
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── useAuth.ts             # Authentication state
│   │   ├── useWebSocket.ts        # WebSocket connection
│   │   ├── useActWriter.ts        # Act AI writing
│   │   ├── useSceneWriter.ts      # Scene AI writing
│   │   ├── useDebounce.ts         # Debounced values
│   │   ├── useLocalStorage.ts     # Local storage sync
│   │   ├── useMediaQuery.ts       # Responsive breakpoints
│   │   ├── usePermissions.ts      # Permission checks
│   │   └── usePagination.ts       # Pagination logic
│   │
│   ├── store/                      # State management (Zustand)
│   │   ├── authStore.ts           # Auth state
│   │   ├── worldStore.ts          # Current world context
│   │   ├── editorStore.ts         # Editor state
│   │   ├── uiStore.ts             # UI state (modals, drawers)
│   │   └── index.ts
│   │
│   ├── routes/                     # Routing configuration
│   │   ├── index.tsx              # Route definitions
│   │   ├── ProtectedRoute.tsx     # Auth guard
│   │   ├── AdminRoute.tsx         # Admin guard
│   │   └── PublicRoute.tsx        # Public only
│   │
│   ├── services/                   # Business logic services
│   │   ├── auth.service.ts
│   │   ├── storage.service.ts     # localStorage/sessionStorage
│   │   ├── analytics.service.ts   # GA4 tracking
│   │   └── notification.service.ts # Toast notifications
│   │
│   ├── utils/                      # Utility functions
│   │   ├── format.ts              # Date, number formatting
│   │   ├── validation.ts          # Form validation
│   │   ├── markdown.ts            # Markdown processing
│   │   ├── constants.ts           # App constants
│   │   └── helpers.ts             # Generic helpers
│   │
│   ├── styles/                     # Global styles
│   │   ├── theme.ts               # Ant Design theme
│   │   ├── global.css             # Global CSS
│   │   ├── variables.css          # CSS variables (Tabler-inspired)
│   │   └── animations.css         # Animations
│   │
│   ├── types/                      # TypeScript types
│   │   ├── models/                # Data models
│   │   │   ├── user.ts
│   │   │   ├── world.ts
│   │   │   ├── character.ts
│   │   │   ├── story.ts
│   │   │   ├── act.ts
│   │   │   └── scene.ts
│   │   ├── api.ts                 # API request/response types
│   │   ├── websocket.ts           # WebSocket message types
│   │   └── index.ts
│   │
│   └── config/                     # App configuration
│       ├── api.config.ts          # API endpoints
│       ├── routes.config.ts       # Route paths
│       └── env.ts                 # Environment variables
│
├── .env.development               # Dev environment
├── .env.production                # Prod environment
├── tsconfig.json                  # TypeScript config
├── vite.config.ts                 # Vite config
├── package.json
└── README.md
```

### 4.2 Technology Stack

**Core:**
- **React** 18+ with TypeScript
- **Vite** for build tooling (faster than CRA)
- **React Router** v6 for routing

**UI Framework:**
- **Ant Design** 5.x (replacement for Tabler Premium)
- **Ant Design Pro Components** for advanced features
- Custom theme matching current color scheme

**State Management:**
- **Zustand** for global state (lightweight alternative to Redux)
- **TanStack Query** (React Query) for server state

**Forms:**
- **Ant Design Form** with built-in validation
- **React Hook Form** for complex forms (optional)

**Rich Text:**
- **Quill** (keep current editor)
- **@vueup/vue-quill** wrapper for React

**HTTP & WebSocket:**
- **Axios** for HTTP requests
- Native **WebSocket** API with custom hooks

**Utilities:**
- **date-fns** for date formatting
- **lodash-es** for utilities
- **react-markdown** for markdown rendering
- **dompurify** for sanitization

**Development:**
- **ESLint** + **Prettier** for code quality
- **Vitest** for unit tests
- **Playwright** for E2E tests

### 4.3 Tabler to Ant Design Mapping

| Tabler Component | Ant Design Equivalent | Notes |
|-----------------|----------------------|-------|
| Hero Header (gradient) | `<PageHeader>` + custom CSS | Use Ant Design PageHeader with custom gradient background |
| Card (enhanced) | `<Card>` + custom styles | Add hover effects via CSS |
| Modal | `<Modal>` | Very similar API |
| Button | `<Button>` | Use `type` prop for variants |
| Form | `<Form>` | More powerful with built-in validation |
| Input | `<Input>`, `<Input.TextArea>` | Multiple input types |
| Select | `<Select>` | Enhanced with search, tags, etc. |
| Table | `<Table>` | Feature-rich with sorting, filtering |
| Badge | `<Badge>`, `<Tag>` | Both available |
| Alert | `<Alert>` | Same purpose |
| Progress | `<Progress>` | Multiple types |
| Breadcrumb | `<Breadcrumb>` | Same |
| Dropdown | `<Dropdown>` | Same |
| Drawer | `<Drawer>` | Side panel |
| Tooltip | `<Tooltip>` | Same |
| Popover | `<Popover>` | Same |
| Empty State | `<Empty>` | Built-in component |
| Spin | `<Spin>` | Loading spinner |
| Skeleton | `<Skeleton>` | Loading placeholder |

**Custom Components Needed:**

1. **Gradient Hero Header:**
```tsx
interface HeroHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  stats?: Array<{ label: string; value: string }>;
}

const HeroHeader: React.FC<HeroHeaderProps> = ({ title, subtitle, actions, stats }) => {
  return (
    <div className="hero-header">
      <div className="hero-content">
        <h1>{title}</h1>
        {subtitle && <p className="subtitle">{subtitle}</p>}
        {stats && (
          <div className="stats">
            {stats.map((stat, i) => (
              <div key={i} className="stat">
                <span className="value">{stat.value}</span>
                <span className="label">{stat.label}</span>
              </div>
            ))}
          </div>
        )}
        {actions && <div className="actions">{actions}</div>}
      </div>
    </div>
  );
};
```

2. **Enhanced Card:**
```tsx
import { Card as AntCard } from 'antd';
import './EnhancedCard.css';  // Hover effects

interface EnhancedCardProps extends React.ComponentProps<typeof AntCard> {
  hoverable?: boolean;
  gradient?: boolean;
}

const EnhancedCard: React.FC<EnhancedCardProps> = ({
  hoverable = true,
  gradient = false,
  className,
  ...props
}) => {
  const classes = cn(
    'enhanced-card',
    hoverable && 'enhanced-card-hoverable',
    gradient && 'enhanced-card-gradient',
    className
  );

  return <AntCard className={classes} {...props} />;
};
```

### 4.4 State Management Strategy

**Global State (Zustand):**

```typescript
// authStore.ts
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  isAuthenticated: boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),

  login: async (username, password) => {
    const { access_token, refresh_token, user } = await authApi.login(username, password);
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    set({ accessToken: access_token, refreshToken: refresh_token, user });
  },

  logout: async () => {
    await authApi.logout();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ accessToken: null, refreshToken: null, user: null });
  },

  refreshAuth: async () => {
    const { access_token } = await authApi.refresh(get().refreshToken!);
    localStorage.setItem('access_token', access_token);
    set({ accessToken: access_token });
  },

  get isAuthenticated() {
    return !!get().accessToken;
  }
}));
```

**Server State (TanStack Query):**

```typescript
// useWorlds.ts
export const useWorlds = () => {
  return useQuery({
    queryKey: ['worlds'],
    queryFn: () => worldApi.list(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useWorld = (worldId: number) => {
  return useQuery({
    queryKey: ['worlds', worldId],
    queryFn: () => worldApi.get(worldId),
    enabled: !!worldId,
  });
};

export const useCreateWorld = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: WorldCreate) => worldApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] });
    },
  });
};

export const useUpdateWorld = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: WorldUpdate }) =>
      worldApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['worlds'] });
      queryClient.invalidateQueries({ queryKey: ['worlds', id] });
    },
  });
};
```

### 4.5 WebSocket Integration

**Base WebSocket Hook:**

```typescript
// useWebSocket.ts
interface UseWebSocketOptions {
  url: string;
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnect?: boolean;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
  reconnect = true,
  reconnectAttempts = 5,
  reconnectInterval = 3000,
}: UseWebSocketOptions) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectCount = useRef(0);

  const connect = useCallback(() => {
    const socket = new WebSocket(url);

    socket.onopen = () => {
      setIsConnected(true);
      reconnectCount.current = 0;
      onOpen?.();
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    };

    socket.onerror = (error) => {
      onError?.(error);
    };

    socket.onclose = () => {
      setIsConnected(false);
      onClose?.();

      // Reconnect logic
      if (reconnect && reconnectCount.current < reconnectAttempts) {
        setTimeout(() => {
          reconnectCount.current++;
          connect();
        }, reconnectInterval);
      }
    };

    setWs(socket);
  }, [url, onMessage, onError, onOpen, onClose, reconnect, reconnectAttempts, reconnectInterval]);

  useEffect(() => {
    connect();
    return () => {
      ws?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((data: any) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify(data));
    }
  }, [ws, isConnected]);

  return { ws, isConnected, sendMessage };
};
```

**Act Writer Hook:**

```typescript
// useActWriter.ts
interface ActWriterMessage {
  user_instruction: string;
  current_act_content: string;
  generation_mode: 'Continue/Append' | 'Rewrite' | 'Edit Selected';
  selected_text?: string;
  model_config_id?: number;
}

interface ActWriterResponse {
  type: 'narrative_generation_start_act' | 'narrative_content_chunk_act' |
        'narrative_generation_end_act' | 'metadata_result_act' | 'error_act';
  data?: string;
}

export const useActWriter = (storyId: number, actId: number) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  const [metadata, setMetadata] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Get WebSocket ticket
  const { data: ticket } = useQuery({
    queryKey: ['ws-ticket'],
    queryFn: () => authApi.getWsTicket(),
    staleTime: 4 * 60 * 1000, // Refresh before 5min expiry
    refetchInterval: 4 * 60 * 1000,
  });

  const wsUrl = ticket
    ? `${WS_BASE_URL}/ws/stories/${storyId}/acts/${actId}/generate?ticket=${ticket.ticket}`
    : null;

  const handleMessage = useCallback((data: ActWriterResponse) => {
    switch (data.type) {
      case 'narrative_generation_start_act':
        setIsGenerating(true);
        setGeneratedContent('');
        setError(null);
        break;
      case 'narrative_content_chunk_act':
        setGeneratedContent(prev => prev + (data.data || ''));
        break;
      case 'narrative_generation_end_act':
        setIsGenerating(false);
        break;
      case 'metadata_result_act':
        setMetadata(JSON.parse(data.data || '{}'));
        break;
      case 'error_act':
        setError(data.data || 'Unknown error');
        setIsGenerating(false);
        break;
    }
  }, []);

  const { sendMessage, isConnected } = useWebSocket({
    url: wsUrl || '',
    onMessage: handleMessage,
    reconnect: true,
  });

  const generate = useCallback((message: ActWriterMessage) => {
    if (isConnected) {
      sendMessage(message);
    }
  }, [isConnected, sendMessage]);

  return {
    generate,
    isGenerating,
    generatedContent,
    metadata,
    error,
    isConnected,
  };
};
```

### 4.6 Authentication Flow

**Login Flow:**

```typescript
// Login.tsx
const Login: React.FC = () => {
  const navigate = useNavigate();
  const login = useAuthStore(state => state.login);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success('Login successful!');
      navigate('/dashboard');
    } catch (error) {
      message.error('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form form={form} onFinish={onFinish}>
      <Form.Item name="username" rules={[{ required: true }]}>
        <Input placeholder="Username" />
      </Form.Item>
      <Form.Item name="password" rules={[{ required: true }]}>
        <Input.Password placeholder="Password" />
      </Form.Item>
      <Form.Item>
        <Button type="primary" htmlType="submit" loading={loading} block>
          Login
        </Button>
      </Form.Item>
    </Form>
  );
};
```

**Protected Route:**

```typescript
// ProtectedRoute.tsx
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
```

**Token Refresh Interceptor:**

```typescript
// api/client.ts
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// Request interceptor - add auth header
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        await useAuthStore.getState().refreshAuth();
        const newToken = useAuthStore.getState().accessToken;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

---

## 5. Migration Roadmap

### Phase 1: Core Infrastructure (Weeks 1-3)

**Week 1: Project Setup & Authentication**

**Backend Tasks:**
- [ ] Create new token-based auth endpoints (`/api/v1/auth/token`, `/api/v1/auth/refresh`)
- [ ] Add Bearer token support to existing middleware
- [ ] Update CORS configuration for React dev server
- [ ] Test dual auth (cookie + Bearer) for backward compatibility

**Frontend Tasks:**
- [ ] Initialize React + TypeScript + Vite project
- [ ] Set up Ant Design with custom theme (Tabler color scheme)
- [ ] Configure routing with React Router
- [ ] Implement auth store (Zustand)
- [ ] Create auth API client (Axios)
- [ ] Build Login, Register, Forgot Password pages
- [ ] Implement ProtectedRoute and AdminRoute guards
- [ ] Set up token refresh interceptor

**Deliverables:**
- Working authentication flow
- Protected routing
- Ant Design theme matching current design

**Week 2: API Client & State Management**

**Backend Tasks:**
- [ ] Standardize all API responses with `ApiResponse<T>` wrapper
- [ ] Add batch endpoints for common operations
- [ ] Create dashboard summary endpoint
- [ ] Document all API endpoints (OpenAPI/Swagger)

**Frontend Tasks:**
- [ ] Set up TanStack Query with dev tools
- [ ] Create typed API client for all endpoints
- [ ] Implement global stores (auth, UI, world context)
- [ ] Build reusable hooks (useWorlds, useCharacters, etc.)
- [ ] Create base components (Button, Card, Modal, etc.)
- [ ] Set up error boundary and loading states

**Deliverables:**
- Complete API client layer
- TanStack Query integration
- Core component library

**Week 3: Layout & Navigation**

**Frontend Tasks:**
- [ ] Build main layout components (Header, Sidebar, Footer)
- [ ] Implement navigation system
- [ ] Create PageHeader component (gradient hero)
- [ ] Build breadcrumb system
- [ ] Implement responsive design (mobile menu)
- [ ] Create notification system (toasts)
- [ ] Build dashboard page

**Deliverables:**
- Complete app layout
- Responsive navigation
- Dashboard with summary stats

### Phase 2: World Building & Content Management (Weeks 4-7)

**Priority 1: Core World Features (Week 4)**

**Backend Tasks:**
- [ ] Add `?include=` query param support for nested data
- [ ] Optimize world detail endpoint with related entities
- [ ] Add search/filter endpoints

**Frontend Tasks:**
- [ ] Build World List page with cards
- [ ] Build World Detail page
- [ ] Create World Create/Edit forms
- [ ] Implement world image management
- [ ] Build world context switcher
- [ ] Create world stats display

**Deliverables:**
- Complete world CRUD
- World context management

**Priority 2: Characters, Locations, Lore (Week 5-6)**

**Frontend Tasks:**
- [ ] Build Character List/Detail/Create/Edit pages
- [ ] Build Location List/Detail/Create/Edit pages
- [ ] Build Lore Item List/Detail/Create/Edit pages
- [ ] Implement image galleries for all elements
- [ ] Create association modals (link to stories)
- [ ] Build Character Generator UI
- [ ] Implement World Map visualization

**Deliverables:**
- Complete world element management
- Working associations system
- Character generator

**Priority 3: Document Management (Week 7)**

**Frontend Tasks:**
- [ ] Build Document Manager UI
- [ ] Implement upload with progress
- [ ] Create document viewer
- [ ] Build import workflows (book → world)
- [ ] Show RAG processing status

**Deliverables:**
- Document upload & management
- Import world from documents

### Phase 3: Story Writing & AI Features (Weeks 8-11)

**Priority 1: Story Management (Week 8)**

**Frontend Tasks:**
- [ ] Build Story List/Detail pages
- [ ] Create Story Create/Edit forms
- [ ] Implement story-world associations
- [ ] Build story publishing UI
- [ ] Create story preview/sharing

**Deliverables:**
- Complete story CRUD
- Story publishing

**Priority 2: Act & Scene Editors (Week 9-10)**

**Backend Tasks:**
- [ ] Ensure WebSocket endpoints support reconnection
- [ ] Add heartbeat/keepalive to WebSocket
- [ ] Standardize WS message format

**Frontend Tasks:**
- [ ] Build Act Editor with Quill integration
- [ ] Implement Scene Editor with Quill
- [ ] Create WebSocket hooks (useActWriter, useSceneWriter)
- [ ] Build AI Assistant panel (toolbar)
- [ ] Implement streaming text display
- [ ] Add AI model selector
- [ ] Create generation history
- [ ] Build metadata display (AI suggestions)
- [ ] Implement auto-save functionality
- [ ] Add keyboard shortcuts

**Deliverables:**
- Fully functional Act Editor with AI
- Fully functional Scene Editor with AI
- WebSocket-based streaming generation

**Priority 3: AI Tools & Wizards (Week 11)**

**Frontend Tasks:**
- [ ] Build Story Wizard (interview flow)
- [ ] Build World Builder Wizard
- [ ] Create AI Text Transform UI
- [ ] Implement Act AI Review
- [ ] Build Prompt Library UI
- [ ] Create brainstorming interface

**Deliverables:**
- Story Wizard
- World Builder Wizard
- AI tools suite

### Phase 4: Chat, Community & Advanced Features (Weeks 12-14)

**Priority 1: Chat Features (Week 12)**

**Frontend Tasks:**
- [ ] Build World Chat UI
- [ ] Implement Story Chat
- [ ] Create chat session management
- [ ] Build message list with infinite scroll
- [ ] Implement chat samples/suggestions
- [ ] Add context loading indicators

**Deliverables:**
- World Chat
- Story Chat

**Priority 2: Community Features (Week 13)**

**Frontend Tasks:**
- [ ] Build Forum Home
- [ ] Create Category/Thread views
- [ ] Implement post creation/editing
- [ ] Add forum moderation tools (admin)
- [ ] Build Blog platform (list, detail, editor)
- [ ] Implement blog engagement (likes, comments)

**Deliverables:**
- Forum system
- Blog platform

**Priority 3: Billing & Admin (Week 14)**

**Frontend Tasks:**
- [ ] Build Billing Dashboard
- [ ] Implement credit purchase flow
- [ ] Create transaction history
- [ ] Build Admin Dashboard
- [ ] Create User Management UI
- [ ] Implement Maintenance Mode toggle
- [ ] Build News Management
- [ ] Create AI Cost Analytics

**Deliverables:**
- Billing system
- Admin panel

### Phase 5: Polish & Optimization (Weeks 15-16)

**Week 15: UX Refinement**

- [ ] Implement animations (page transitions, loading states)
- [ ] Add skeleton loaders for all async content
- [ ] Create empty states for all lists
- [ ] Improve error messages and handling
- [ ] Add confirmation dialogs for destructive actions
- [ ] Implement undo/redo for editors
- [ ] Add keyboard shortcuts guide
- [ ] Build onboarding tour

**Week 16: Performance & Testing**

- [ ] Code splitting and lazy loading
- [ ] Optimize bundle size
- [ ] Implement service worker for offline support
- [ ] Add performance monitoring
- [ ] Write E2E tests (Playwright)
- [ ] Conduct accessibility audit (WCAG 2.1)
- [ ] Security audit (XSS, CSRF protection)
- [ ] Load testing

### Effort Estimates Summary

| Phase | Duration | Backend Work | Frontend Work | Key Deliverables |
|-------|----------|--------------|---------------|------------------|
| Phase 1 | 3 weeks | 40% | 60% | Auth, API client, Layout |
| Phase 2 | 4 weeks | 30% | 70% | World building, Elements |
| Phase 3 | 4 weeks | 20% | 80% | Story writing, AI features |
| Phase 4 | 3 weeks | 30% | 70% | Chat, Forum, Admin |
| Phase 5 | 2 weeks | 10% | 90% | Polish, Testing |
| **Total** | **16 weeks** | **30%** | **70%** | Full React SPA |

**Team Composition:**
- 1 Backend Developer (30% time)
- 2 Frontend Developers (full time)
- 1 QA Engineer (from week 12)

---

## 6. E2E Testing Strategy

### 6.1 Playwright Test Structure

```
e2e/
├── fixtures/
│   ├── auth.ts              # Authenticated user fixture
│   ├── world.ts             # World with elements fixture
│   └── story.ts             # Story with acts/scenes fixture
├── tests/
│   ├── auth/
│   │   ├── login.spec.ts
│   │   ├── register.spec.ts
│   │   └── password-reset.spec.ts
│   ├── worlds/
│   │   ├── crud.spec.ts
│   │   ├── elements.spec.ts
│   │   └── associations.spec.ts
│   ├── stories/
│   │   ├── crud.spec.ts
│   │   ├── wizard.spec.ts
│   │   └── publishing.spec.ts
│   ├── editors/
│   │   ├── act-editor.spec.ts
│   │   ├── scene-editor.spec.ts
│   │   └── ai-generation.spec.ts
│   ├── chat/
│   │   ├── world-chat.spec.ts
│   │   └── story-chat.spec.ts
│   └── admin/
│       └── user-management.spec.ts
├── utils/
│   ├── api.ts               # API helpers
│   ├── db.ts                # DB seeding helpers
│   └── helpers.ts
└── playwright.config.ts
```

### 6.2 Critical User Flows

**Flow 1: Complete Story Creation Journey**

```typescript
// e2e/tests/stories/complete-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Complete Story Creation Journey', () => {
  test('user can create world, add elements, create story, write act, and publish', async ({ page, context }) => {
    // Setup: Login
    await page.goto('/login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');

    // Step 1: Create World
    await page.click('text=Create World');
    await page.fill('[name="name"]', 'Test Fantasy World');
    await page.fill('[name="description"]', 'A magical realm for testing');
    await page.click('button:has-text("Create World")');
    await expect(page.locator('text=Test Fantasy World')).toBeVisible();

    // Step 2: Add Character
    await page.click('text=Characters');
    await page.click('text=Add Character');
    await page.fill('[name="name"]', 'Hero Protagonist');
    await page.fill('[name="description"]', 'The brave hero');
    await page.click('button:has-text("Create Character")');

    // Step 3: Create Story
    await page.click('text=Stories');
    await page.click('text=Create Story');
    await page.fill('[name="title"]', 'Epic Quest');
    await page.selectOption('[name="world_id"]', { label: 'Test Fantasy World' });
    await page.click('button:has-text("Create Story")');

    // Step 4: Link Character to Story
    await page.click('text=Link Elements');
    await page.click('text=Hero Protagonist');
    await page.fill('[name="role"]', 'Protagonist');
    await page.click('button:has-text("Link Character")');

    // Step 5: Create Act
    await page.click('text=Add Act');
    await page.fill('[name="title"]', 'Act 1: The Beginning');
    await page.fill('[name="act_summary"]', 'Hero discovers their destiny');
    await page.click('button:has-text("Create Act")');

    // Step 6: Write Act Content with AI
    await page.click('text=Edit Act');
    await page.waitForSelector('.ql-editor'); // Quill editor

    // Type instruction for AI
    await page.fill('[data-testid="ai-instruction"]', 'Write an exciting opening scene');
    await page.click('button:has-text("Generate")');

    // Wait for AI generation to complete
    await expect(page.locator('[data-testid="generation-status"]')).toHaveText('Complete');

    // Verify content was generated
    const editorContent = await page.locator('.ql-editor').textContent();
    expect(editorContent!.length).toBeGreaterThan(100);

    // Step 7: Save Act
    await page.click('button:has-text("Save")');
    await expect(page.locator('text=Saved successfully')).toBeVisible();

    // Step 8: Publish Story
    await page.click('text=Back to Story');
    await page.click('button:has-text("Publish")');
    await page.selectOption('[name="visibility"]', 'public');
    await page.click('button:has-text("Confirm Publish")');

    // Verify publication
    await expect(page.locator('text=Story published successfully')).toBeVisible();

    // Step 9: View Published Story
    const publishedUrl = await page.locator('[data-testid="published-url"]').textContent();
    await page.goto(publishedUrl!);
    await expect(page.locator('h1')).toHaveText('Epic Quest');
  });
});
```

**Flow 2: Real-time AI Collaboration**

```typescript
// e2e/tests/editors/ai-collaboration.spec.ts
import { test, expect } from '@playwright/test';

test.describe('AI Writing Assistance', () => {
  test('AI assistant responds to user instructions in real-time', async ({ page }) => {
    // Setup: Navigate to act editor
    await setupAuthenticatedUser(page);
    await navigateToActEditor(page, { actId: 1 });

    // Test streaming generation
    const generatedChunks: string[] = [];

    // Listen for WebSocket messages
    page.on('websocket', ws => {
      ws.on('framereceived', event => {
        const message = JSON.parse(event.payload as string);
        if (message.type === 'narrative_content_chunk_act') {
          generatedChunks.push(message.data);
        }
      });
    });

    // Trigger AI generation
    await page.fill('[data-testid="ai-instruction"]', 'Describe a thrilling battle scene');
    await page.selectOption('[data-testid="model-selector"]', 'gpt-4');
    await page.click('button:has-text("Generate")');

    // Wait for streaming to complete
    await expect(page.locator('[data-testid="generation-status"]')).toHaveText('Complete', { timeout: 30000 });

    // Verify streaming occurred
    expect(generatedChunks.length).toBeGreaterThan(5);

    // Verify editor was updated
    const editorContent = await page.locator('.ql-editor').textContent();
    expect(editorContent).toContain('battle');

    // Test metadata extraction
    await expect(page.locator('[data-testid="metadata-mood"]')).toBeVisible();
    await expect(page.locator('[data-testid="metadata-themes"]')).toBeVisible();
  });

  test('user can regenerate content', async ({ page }) => {
    await setupAuthenticatedUser(page);
    await navigateToActEditor(page, { actId: 1 });

    // Generate initial content
    await page.fill('[data-testid="ai-instruction"]', 'Write a peaceful scene');
    await page.click('button:has-text("Generate")');
    await page.waitForSelector('[data-testid="generation-status"]:has-text("Complete")');

    const firstContent = await page.locator('.ql-editor').textContent();

    // Regenerate with different instruction
    await page.click('button:has-text("Clear")');
    await page.fill('[data-testid="ai-instruction"]', 'Write an action-packed scene');
    await page.click('button:has-text("Generate")');
    await page.waitForSelector('[data-testid="generation-status"]:has-text("Complete")');

    const secondContent = await page.locator('.ql-editor').textContent();

    // Verify content changed
    expect(secondContent).not.toBe(firstContent);
  });
});
```

**Flow 3: World Chat Interaction**

```typescript
// e2e/tests/chat/world-chat.spec.ts
test.describe('World Chat', () => {
  test('user can chat with AI about their world', async ({ page }) => {
    await setupAuthenticatedUser(page);
    await page.goto('/worlds/1/chat');

    // Create new session
    await page.click('button:has-text("New Chat")');
    await expect(page.locator('[data-testid="chat-window"]')).toBeVisible();

    // Send message
    await page.fill('[data-testid="message-input"]', 'Tell me about the magic system in this world');
    await page.click('button:has-text("Send")');

    // Wait for AI response
    await expect(page.locator('[data-testid="ai-message"]').last()).toBeVisible({ timeout: 10000 });

    // Verify response includes world context
    const response = await page.locator('[data-testid="ai-message"]').last().textContent();
    expect(response!.length).toBeGreaterThan(50);

    // Test follow-up question
    await page.fill('[data-testid="message-input"]', 'How would this magic system affect combat?');
    await page.click('button:has-text("Send")');
    await expect(page.locator('[data-testid="ai-message"]').last()).toBeVisible({ timeout: 10000 });

    // Verify chat history is maintained
    const messages = await page.locator('[data-testid="message"]').count();
    expect(messages).toBe(4); // 2 user + 2 AI messages
  });
});
```

### 6.3 Test Data Management

**Seed Data Strategy:**

```typescript
// e2e/utils/db.ts
import { PrismaClient } from '@prisma/client';

export async function seedTestData() {
  const prisma = new PrismaClient();

  // Create test user
  const user = await prisma.user.create({
    data: {
      username: 'testuser',
      email: 'test@example.com',
      hashed_password: hashPassword('password123'),
      is_active: true,
    },
  });

  // Create test world with elements
  const world = await prisma.world.create({
    data: {
      user_id: user.id,
      name: 'Test World',
      description: 'A test world for E2E testing',
      characters: {
        create: [
          { name: 'Test Character 1', description: 'First test character' },
          { name: 'Test Character 2', description: 'Second test character' },
        ],
      },
      locations: {
        create: [
          { name: 'Test Location 1', description: 'First test location' },
        ],
      },
    },
  });

  // Create test story
  const story = await prisma.story.create({
    data: {
      user_id: user.id,
      world_id: world.id,
      title: 'Test Story',
      story_type: 'advanced',
      acts: {
        create: [
          {
            act_number: 1,
            title: 'Test Act 1',
            act_summary: 'First test act',
          },
        ],
      },
    },
  });

  await prisma.$disconnect();

  return { user, world, story };
}

export async function cleanTestData() {
  const prisma = new PrismaClient();

  // Delete in reverse order of dependencies
  await prisma.scene.deleteMany({ where: { act: { story: { user: { username: 'testuser' } } } } });
  await prisma.act.deleteMany({ where: { story: { user: { username: 'testuser' } } } });
  await prisma.story.deleteMany({ where: { user: { username: 'testuser' } } });
  await prisma.character.deleteMany({ where: { world: { user: { username: 'testuser' } } } });
  await prisma.location.deleteMany({ where: { world: { user: { username: 'testuser' } } } });
  await prisma.world.deleteMany({ where: { user: { username: 'testuser' } } });
  await prisma.user.deleteMany({ where: { username: 'testuser' } });

  await prisma.$disconnect();
}
```

**Test Fixtures:**

```typescript
// e2e/fixtures/auth.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  authenticatedPage: async ({ page }, use) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[name="username"]', 'testuser');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');

    await use(page);

    // Cleanup: Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('text=Logout');
  },
});
```

### 6.4 Visual Regression Testing

```typescript
// e2e/tests/visual/pages.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('dashboard matches snapshot', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveScreenshot('dashboard.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('world detail matches snapshot', async ({ page }) => {
    await page.goto('/worlds/1');
    await expect(page).toHaveScreenshot('world-detail.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });

  test('act editor matches snapshot', async ({ page }) => {
    await page.goto('/stories/1/acts/1/edit');
    await page.waitForSelector('.ql-editor');
    await expect(page).toHaveScreenshot('act-editor.png', {
      fullPage: true,
      animations: 'disabled',
    });
  });
});
```

---

## 7. Risk Assessment & Mitigation

### 7.1 Technical Risks

**Risk 1: WebSocket Complexity**
- **Impact:** High - Core feature for AI writing
- **Probability:** Medium
- **Mitigation:**
  - Build robust reconnection logic
  - Implement message queuing during disconnection
  - Add extensive error handling
  - Test under poor network conditions
  - Have fallback to polling for critical operations

**Risk 2: State Management Complexity**
- **Impact:** Medium - Could cause performance issues
- **Probability:** Low
- **Mitigation:**
  - Use proven libraries (Zustand + TanStack Query)
  - Implement proper data normalization
  - Use React DevTools to monitor state
  - Code review state management patterns

**Risk 3: Real-time Editing Conflicts**
- **Impact:** Medium - Data loss potential
- **Probability:** Low (single user editing)
- **Mitigation:**
  - Implement optimistic updates
  - Add auto-save with conflict detection
  - Show clear saving/saved states
  - Implement version history

**Risk 4: Bundle Size**
- **Impact:** Medium - Affects load time
- **Probability:** High
- **Mitigation:**
  - Code splitting by route
  - Lazy load heavy components (Quill, etc.)
  - Use bundle analyzer
  - Optimize Ant Design imports (use es modules)
  - Target <500KB initial bundle

### 7.2 Migration Risks

**Risk 1: API Incompatibility**
- **Impact:** High - Could break existing features
- **Probability:** Medium
- **Mitigation:**
  - Run backend and React frontend in parallel
  - Version API endpoints (`/api/v2/`)
  - Comprehensive E2E tests
  - Gradual rollout with feature flags

**Risk 2: Data Migration**
- **Impact:** High - Could lose user data
- **Probability:** Low
- **Mitigation:**
  - No database changes needed
  - Backend remains same
  - Only frontend changes
  - Backup production data before deployment

**Risk 3: User Adoption**
- **Impact:** High - Users resist change
- **Probability:** Medium
- **Mitigation:**
  - Beta testing with select users
  - Onboarding tour for new UI
  - Keep familiar workflows
  - Provide feedback mechanism
  - Gradual rollout option

### 7.3 Performance Risks

**Risk 1: Initial Load Time**
- **Impact:** Medium - First impression
- **Probability:** Medium
- **Mitigation:**
  - Server-side rendering (SSR) with Vite SSR
  - Preload critical resources
  - Optimize images (WebP, lazy loading)
  - CDN for static assets
  - Service worker caching

**Risk 2: Memory Leaks**
- **Impact:** Medium - App slowdown over time
- **Probability:** Low
- **Mitigation:**
  - Proper cleanup in useEffect
  - Unsubscribe from WebSockets
  - Clear timers/intervals
  - Use React DevTools Profiler
  - Regular memory profiling

---

## 8. Success Metrics

### 8.1 Technical Metrics

**Performance:**
- Initial load time: < 3 seconds
- Time to interactive: < 5 seconds
- Lighthouse score: > 90
- Bundle size: < 500KB (gzipped)
- API response time: < 500ms (p95)
- WebSocket latency: < 100ms

**Quality:**
- Test coverage: > 80%
- E2E test coverage: 100% critical flows
- Zero critical bugs in production
- < 5 minor bugs per week

**Reliability:**
- Uptime: 99.9%
- WebSocket connection success rate: > 95%
- Auto-save success rate: 99%

### 8.2 User Metrics

**Engagement:**
- Daily active users (DAU) increase: +20%
- Session duration increase: +30%
- Feature adoption rate: > 70%
- User satisfaction (NPS): > 8

**Performance:**
- Bounce rate decrease: -20%
- Page views per session: +25%
- Conversion rate (free → paid): +15%

### 8.3 Business Metrics

**Efficiency:**
- Development velocity: +40% (React components reusability)
- Bug fix time: -30%
- Feature delivery time: -25%
- Onboarding time for new developers: -50%

---

## 9. Deployment Strategy

### 9.1 Environment Setup

**Development:**
```bash
# Backend (FastAPI)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (React + Vite)
cd react-app
npm run dev  # Runs on http://localhost:5173
```

**Staging:**
```bash
# Backend: Same as production
docker-compose -f docker-compose.staging.yml up

# Frontend: Build and serve
npm run build
npm run preview
```

**Production:**
```bash
# Backend: Gunicorn + Uvicorn
docker-compose up -d

# Frontend: Static files served by Nginx
npm run build
# Deploy dist/ to CDN or static hosting
```

### 9.2 Deployment Steps

**Phase 1: Backend Preparation (Week before frontend launch)**

1. Deploy new auth endpoints
2. Enable CORS for React domain
3. Add Bearer token support
4. Deploy to staging
5. Run API tests
6. Monitor for issues

**Phase 2: Parallel Deployment (Launch week)**

1. Deploy React app to subdomain (e.g., `app.yourdomain.com`)
2. Keep existing app at main domain
3. Redirect new users to React app
4. Offer existing users option to switch
5. Monitor metrics closely

**Phase 3: Gradual Rollout (2 weeks)**

1. Week 1: 25% traffic to React app
2. Week 2: 50% traffic to React app
3. Week 3: 75% traffic to React app
4. Week 4: 100% traffic to React app
5. Deprecate old frontend

**Phase 4: Cleanup (Week after full rollout)**

1. Remove view routers from backend
2. Remove Jinja2 templates
3. Remove old JavaScript files
4. Redirect all traffic to React app
5. Update documentation

### 9.3 Rollback Plan

**If critical issues arise:**

1. **Immediate:** Redirect traffic back to old frontend
2. **Within 1 hour:** Identify and fix issue
3. **Within 4 hours:** Deploy fix or extend rollback
4. **Post-mortem:** Document issue and prevention

**Rollback Triggers:**
- Error rate > 5%
- User complaints > 10/hour
- Core feature broken (auth, AI generation, saving)
- Performance degradation > 50%

---

## 10. Post-Migration Optimization

### 10.1 Performance Optimization

**Code Splitting:**
```typescript
// routes/index.tsx
const Dashboard = lazy(() => import('@/pages/dashboard/Dashboard'));
const WorldDetail = lazy(() => import('@/pages/worlds/WorldDetail'));
const ActEditor = lazy(() => import('@/pages/acts/ActEditor'));

// Preload on hover
<Link
  to="/worlds/1"
  onMouseEnter={() => import('@/pages/worlds/WorldDetail')}
>
  View World
</Link>
```

**Image Optimization:**
- Convert to WebP format
- Implement lazy loading
- Use responsive images (srcset)
- Compress with Squoosh/ImageOptim

**Caching Strategy:**
```typescript
// TanStack Query config
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

### 10.2 SEO & Accessibility

**SEO (for public pages):**
- Server-side rendering for blog, published stories
- Meta tags for social sharing
- Structured data (JSON-LD)
- Sitemap generation
- robots.txt optimization

**Accessibility:**
- ARIA labels for all interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance (WCAG AA)
- Focus management in modals
- Skip to content links

### 10.3 Analytics & Monitoring

**Setup:**
```typescript
// services/analytics.service.ts
export const trackEvent = (category: string, action: string, label?: string) => {
  if (window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
    });
  }
};

// Usage
trackEvent('World', 'Create', worldId.toString());
trackEvent('AI', 'Generate', `act-${actId}`);
trackEvent('Story', 'Publish', storyId.toString());
```

**Error Tracking:**
- Integrate Sentry for error monitoring
- Track API errors
- Track WebSocket failures
- Track unhandled promise rejections

**Performance Monitoring:**
- Use Web Vitals library
- Track LCP, FID, CLS
- Monitor bundle size over time
- Track API response times

---

## 11. Conclusion

### 11.1 Summary

This migration plan provides a comprehensive roadmap for transitioning from a server-rendered Jinja2 + JavaScript frontend to a modern React SPA with TypeScript and Ant Design. The plan covers:

1. **Complete API Analysis:** 200+ endpoints catalogued with request/response types
2. **Backend Refactoring:** Token-based auth, response standardization, new endpoints
3. **React Architecture:** Modern tech stack with proven patterns
4. **16-Week Roadmap:** Phased approach with clear deliverables
5. **Comprehensive Testing:** E2E tests with Playwright covering critical flows
6. **Risk Mitigation:** Identified risks with mitigation strategies
7. **Deployment Strategy:** Gradual rollout with rollback plan

### 11.2 Key Benefits

**For Users:**
- Faster, more responsive interface
- Better mobile experience
- Improved real-time features
- Modern, polished UI

**For Developers:**
- Type safety with TypeScript
- Reusable component library
- Better debugging tools
- Faster development cycles

**For Business:**
- Reduced maintenance costs
- Faster feature delivery
- Better scalability
- Improved metrics (engagement, conversion)

### 11.3 Next Steps

1. **Week 1:** Review and approve this plan
2. **Week 1-2:** Set up development environment
3. **Week 2:** Begin Phase 1 (Auth & Infrastructure)
4. **Week 16:** Complete migration
5. **Week 17:** Full production rollout
6. **Week 18+:** Monitor, optimize, iterate

### 11.4 Resources Required

**Development Team:**
- 1 Backend Developer (30% allocation, 5 weeks)
- 2 Frontend Developers (100% allocation, 16 weeks)
- 1 QA Engineer (100% allocation, 6 weeks - from week 10)
- 1 DevOps Engineer (20% allocation, ongoing)

**Tools & Services:**
- Vite, React, TypeScript (free)
- Ant Design (free, but consider Pro license for support)
- TanStack Query (free)
- Playwright (free)
- Hosting for React app (CDN/static hosting)
- Monitoring tools (Sentry, etc.)

**Total Effort:** ~40 person-weeks

---

## Appendix A: API Endpoint Reference

*See Section 1 for complete endpoint documentation*

## Appendix B: Component Mapping

*See Section 4.3 for Tabler to Ant Design mapping*

## Appendix C: Code Examples

*See Sections 4.4-4.6 for detailed code examples*

## Appendix D: Testing Checklists

*See Section 6 for E2E test specifications*

---

**Document Version:** 1.0
**Last Updated:** 2025-10-04
**Author:** Claude (AI Assistant)
**Status:** Draft - Pending Review
