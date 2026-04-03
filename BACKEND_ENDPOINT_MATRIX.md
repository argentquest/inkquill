# Backend Endpoint → Frontend Usage Matrix

> **Generated:** 2026-03-31
> **Purpose:** Maps every backend API and WebSocket endpoint to its frontend usage. Endpoints with no frontend reference are flagged for investigation.
> **Legend:**
> - ✅ **Used** — confirmed referenced in a JS file or documented in frontendboth.md
> - ⚠️ **Partial** — endpoint exists and is logical but not explicitly traced to a specific JS file
> - ❌ **Not Found** — no reference in JS files or frontend docs; needs investigation
> - 🔒 **Admin-Only** — used only from admin UI pages
> - 📡 **Backend-Internal** — called server-to-server or by background tasks, not by the browser

---

## Table of Contents
1. [Authentication & OAuth](#1-authentication--oauth)
2. [Users](#2-users)
3. [Dashboard](#3-dashboard)
4. [Worlds](#4-worlds)
5. [Characters](#5-characters)
6. [Locations](#6-locations)
7. [Lore Items](#7-lore-items)
8. [Location Connections](#8-location-connections)
9. [Stories](#9-stories)
10. [Basic Stories](#10-basic-stories)
11. [Story Classes](#11-story-classes)
12. [Acts](#12-acts)
13. [Scenes](#13-scenes)
14. [Associations](#14-associations)
15. [AI-Assisted Writing (WebSocket)](#15-ai-assisted-writing-websocket)
16. [AI Text Transform](#16-ai-text-transform)
17. [AI Model Configuration](#17-ai-model-configuration)
18. [LLM Models](#18-llm-models)
19. [Image Generation](#19-image-generation)
20. [Prompts](#20-prompts)
21. [Documents](#21-documents)
22. [World Chat](#22-world-chat)
23. [Story Chat](#23-story-chat)
24. [Public World Chat](#24-public-world-chat)
25. [World Builder](#25-world-builder)
26. [World Importer](#26-world-importer)
27. [Story Wizard API](#27-story-wizard-api)
28. [Published Stories](#28-published-stories)
29. [Billing](#29-billing)
30. [Admin Billing](#30-admin-billing)
31. [Referrals](#31-referrals)
32. [Forum](#32-forum)
33. [Blog](#33-blog)
34. [Maintenance](#34-maintenance)
35. [Welcome Interview](#35-welcome-interview)
36. [Batch Operations](#36-batch-operations)
37. [Act AI Review](#37-act-ai-review)
38. [Admin: CTA Content](#38-admin-cta-content)
39. [Social / OG / Analytics](#39-social--og--analytics)
40. [Summary: Unused Endpoints](#40-summary-unused-endpoints)

---

## 1. Authentication & OAuth

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/auth/register` | `auth_forms.js` — register form submission |
| ✅ | POST | `/api/v1/auth/login` | `auth_forms.js` — login form submission |
| ❌ | POST | `/api/v1/auth/token` | OAuth2 token endpoint — no browser JS calls found; likely only used by API clients or Swagger UI |
| ❌ | POST | `/api/v1/auth/refresh` | Token refresh — not called explicitly in JS; browser relies on HttpOnly cookie auto-renewal; **no 401 interceptor found — sessions expire silently** |
| ✅ | POST | `/api/v1/auth/logout` | `main.js` / nav — logout button in user dropdown |
| ✅ | GET | `/api/v1/auth/ws-ticket` | `act_websocket_handler.js`, `scene_websocket_handler.js`, `world_chat_main.js`, `story_chat.js` — fetched before every WebSocket open |
| 🔒 | POST | `/api/v1/auth/impersonate` | Admin dashboard — admin user impersonation |
| 🔒 | POST | `/api/v1/auth/stop-impersonation` | Admin dashboard — stop impersonation |
| ✅ | POST | `/api/v1/auth/password-reset/request` | `auth_forms.js` — forgot password form |
| ✅ | POST | `/api/v1/auth/password-reset/confirm` | `auth_forms.js` — reset password form |
| ✅ | GET | `/api/v1/auth/google` | `_google_signin_button.html` — initiates Google OAuth redirect |
| ✅ | GET | `/api/v1/auth/google/callback` | Handled server-side after Google redirect; no direct JS call needed |

---

## 2. Users

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/users/me` | My account page (`/ui/account`) — loads profile data |
| ❌ | GET | `/api/v1/users/{user_id}` | No frontend reference found — may only be used by admin views or is unused |
| 🔒 | GET | `/api/v1/users/` | Admin: user management page — list all users |
| 🔒 | PATCH | `/api/v1/users/{user_id}/toggle-active` | Admin: user management page — activate/deactivate user |
| 🔒 | PATCH | `/api/v1/users/{user_id}/edit` | Admin: user management page — edit user details |

---

## 3. Dashboard

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ❌ | GET | `/api/v1/dashboard/summary` | **No frontend reference found.** The main dashboard (`index.html`) appears to use server-rendered Jinja2 data, not this API. Investigate whether this endpoint is called anywhere or can be removed. |

---

## 4. Worlds

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/worlds/` | `world_crud.js` — worlds list page |
| ✅ | POST | `/api/v1/worlds/` | `world_form_handler.js` — create world form |
| ⚠️ | GET | `/api/v1/worlds/has-non-shadow-worlds` | Story wizard / story form — checks if user has a valid world before proceeding; not explicitly traced to a named JS file |
| ✅ | GET | `/api/v1/worlds/{world_id}` | `world_crud.js`, world detail page init |
| ✅ | PUT | `/api/v1/worlds/{world_id}` | `world_form_handler.js` — edit world form |
| ✅ | DELETE | `/api/v1/worlds/{world_id}` | `world_crud.js` — delete world button |
| ⚠️ | GET | `/api/v1/worlds/{world_id}/stories` | World detail page — stories list; may be server-rendered or JS-loaded |

---

## 5. Characters

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/worlds/{world_id}/characters` | `character_form_handler.js` — create character form |
| ✅ | GET | `/api/v1/worlds/{world_id}/characters` | `character_crud.js` — character list page; `_link_character_modal.html` — link popup |
| ✅ | GET | `/api/v1/characters/{character_id}` | `character_form_handler.js` — edit character page load |
| ✅ | PUT | `/api/v1/characters/{character_id}` | `character_form_handler.js` — update character |
| ✅ | DELETE | `/api/v1/characters/{character_id}` | `character_crud.js` — delete character |

---

## 6. Locations

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/worlds/{world_id}/locations` | `location_form_handler.js` — create location |
| ✅ | GET | `/api/v1/worlds/{world_id}/locations` | `location_crud.js` — location list page; `_link_location_modal.html` — link popup |
| ✅ | GET | `/api/v1/locations/{location_id}` | `location_form_handler.js` — edit location page load |
| ✅ | PUT | `/api/v1/locations/{location_id}` | `location_form_handler.js` — update location |
| ✅ | DELETE | `/api/v1/locations/{location_id}` | `location_crud.js` — delete location |

---

## 7. Lore Items

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/worlds/{world_id}/lore-items` | `lore_item_form_handler.js` — create lore item |
| ✅ | GET | `/api/v1/worlds/{world_id}/lore-items` | `lore_item_crud.js` — lore list page; `_link_lore_item_modal.html` — link popup |
| ✅ | GET | `/api/v1/lore-items/{lore_item_id}` | `lore_item_form_handler.js` — edit lore item page load |
| ✅ | PUT | `/api/v1/lore-items/{lore_item_id}` | `lore_item_form_handler.js` — update lore item |
| ✅ | DELETE | `/api/v1/lore-items/{lore_item_id}` | `lore_item_crud.js` — delete lore item |

---

## 8. Location Connections

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | POST | `/api/v1/worlds/{world_id}/location-connections` | `world_map.js` — likely wired when user connects two pins on the map |
| ⚠️ | GET | `/api/v1/worlds/{world_id}/location-connections` | `world_map.js` — loads connections to render map edges |
| ❌ | GET | `/api/v1/location-connections/{connection_id}` | **No frontend reference found** — individual connection fetch appears unused |
| ⚠️ | PUT | `/api/v1/location-connections/{connection_id}` | `world_map.js` — updating a connection label or type |
| ⚠️ | DELETE | `/api/v1/location-connections/{connection_id}` | `world_map.js` — removing a connection from the map |

---

## 9. Stories

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/stories/` | `story_crud.js` — stories list page |
| ✅ | POST | `/api/v1/stories/` | `story_form_handler.js` — create story form |
| ✅ | GET | `/api/v1/stories/{story_id}` | `story_crud.js` — story detail page |
| ✅ | PUT | `/api/v1/stories/{story_id}` | `story_form_handler.js` — edit story form |
| ✅ | DELETE | `/api/v1/stories/{story_id}` | `story_crud.js` — delete story |
| ❌ | GET | `/api/v1/stories/{story_id}/outline` | **No frontend reference found.** Story detail renders act/scene tree server-side. This endpoint is likely a React-rewrite-ready endpoint not yet consumed by the current frontend. |
| ⚠️ | POST | `/api/v1/stories/{story_id}/publish` | Story detail page — publish button; exact JS call site needs verification |
| ✅ | POST | `/api/v1/stories/generate` | `story_generation_modal.js` — story wizard AI generation step |

---

## 10. Basic Stories

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/stories/basic/` | `basic_story_form.html` — create basic story form submission |
| ✅ | GET | `/api/v1/stories/basic/{story_id}` | Basic story editor page — loads story content on init |

---

## 11. Story Classes

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/story-classes/` | `story_class_crud.js` — create story class |
| ✅ | GET | `/api/v1/story-classes/` | `story_class_crud.js` — story classes list; also story form dropdown population |
| ✅ | GET | `/api/v1/story-classes/{class_id}` | `story_class_crud.js` — edit story class load |
| ✅ | PUT | `/api/v1/story-classes/{class_id}` | `story_class_crud.js` — update story class |
| ✅ | DELETE | `/api/v1/story-classes/{class_id}` | `story_class_crud.js` — delete story class |

---

## 12. Acts

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/stories/{story_id}/acts` | Story detail page — "Add Act" button |
| ✅ | GET | `/api/v1/stories/{story_id}/acts` | Story detail page — act list rendering |
| ✅ | GET | `/api/v1/acts/{act_id}` | `act_editor_main.js` — act editor page load |
| ✅ | PUT | `/api/v1/acts/{act_id}` | `act_save_handler.js` — debounced auto-save; `act_form_handler.js` — metadata update |
| ✅ | DELETE | `/api/v1/acts/{act_id}` | `act_crud.js` — delete act button |
| ✅ | POST | `/api/v1/acts/{act_id}/review` | `act_review_components/api_handler_review.js` — AI review submission |
| ❌ | POST | `/api/v1/acts/{act_id}/compile-scenes` | **No frontend reference found.** Compiles all scenes into act content. Not wired to any UI button in current frontend. |

---

## 13. Scenes

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/acts/{act_id}/scenes` | Act editor or story detail — "Add Scene" button |
| ✅ | GET | `/api/v1/acts/{act_id}/scenes` | Story detail page — scene list nested under each act |
| ❌ | POST | `/api/v1/acts/{act_id}/scenes/generate-scenes` | **No frontend reference found.** Batch scene generation from act description — not wired to any UI. Likely a planned/incomplete feature. |
| ✅ | GET | `/api/v1/scenes/{scene_id}` | `scene_editor_main.js` — scene editor page load |
| ✅ | PUT | `/api/v1/scenes/{scene_id}` | `scene_save_handler.js` — debounced auto-save |
| ✅ | DELETE | `/api/v1/scenes/{scene_id}` | `scene_crud.js` — delete scene button |

---

## 14. Associations

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ❌ | GET | `/api/v1/associations/roles/{container_type}/{element_type}` | **No frontend reference found.** Role suggestions — intended for enhanced association modals but not wired in current UI. |
| ✅ | POST | `/api/v1/associations/story/{story_id}/character/{character_id}` | `story_associations_handler.js` — link character via `_link_character_modal.html` |
| ✅ | GET | `/api/v1/associations/story/{story_id}/characters` | `story_associations_handler.js` — displays linked characters in editor sidebar |
| ⚠️ | PUT | `/api/v1/associations/story/{story_id}/character/{character_id}` | Role update — not wired in current UI; association panel shows roles but editing not documented |
| ✅ | DELETE | `/api/v1/associations/story/{story_id}/character/{character_id}` | `story_associations_handler.js` — unlink character |
| ✅ | POST | `/api/v1/associations/story/{story_id}/location/{location_id}` | `story_associations_handler.js` — link location via `_link_location_modal.html` |
| ✅ | GET | `/api/v1/associations/story/{story_id}/locations` | `story_associations_handler.js` — displays linked locations |
| ✅ | DELETE | `/api/v1/associations/story/{story_id}/location/{location_id}` | `story_associations_handler.js` — unlink location |
| ✅ | POST | `/api/v1/associations/story/{story_id}/lore-item/{lore_item_id}` | `story_associations_handler.js` — link lore item via `_link_lore_item_modal.html` |
| ✅ | GET | `/api/v1/associations/story/{story_id}/lore-items` | `story_associations_handler.js` — displays linked lore items |
| ✅ | DELETE | `/api/v1/associations/story/{story_id}/lore-item/{lore_item_id}` | `story_associations_handler.js` — unlink lore item |

---

## 15. AI-Assisted Writing (WebSocket)

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | WebSocket | `/ws/stories/{story_id}/acts/{act_id}/generate` | `act_websocket_handler.js` — opens on "Generate" click; ticket fetched first from `/api/v1/auth/ws-ticket` |
| ✅ | WebSocket | `/ws/stories/{story_id}/acts/{act_id}/scenes/{scene_id}/generate` | `scene_websocket_handler.js` — scene editor AI generation |
| ✅ | WebSocket | `/ws/worlds/{world_id}/chat` | `world_chat_main.js` + `world_chat_message_handler.js` |
| ✅ | WebSocket | `/ws/story-chat/stories/{story_id}/sessions/{session_id}` | `story_chat.js` |

---

## 16. AI Text Transform

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | GET | `/api/v1/ai-text/operations` | Likely populates transform operation options in editor toolbars; not explicitly traced in frontendboth.md |
| ⚠️ | POST | `/api/v1/ai-text/estimate-cost` | Likely shows cost preview before transform; not confirmed in frontend docs |
| ⚠️ | POST | `/api/v1/ai-text/transform` | `modules/ai_quill_toolbar.js` — AI toolbar operations (expand, rewrite, etc.) in Quill editors |

> **Note:** These endpoints are not documented in frontendboth.md. Verify their call sites in `ai_quill_toolbar.js` and update the frontend docs.

---

## 17. AI Model Configuration

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/ai-models/` | `ai_model_selector.js` — populates all three AI model selector variants on page load |
| ⚠️ | GET | `/api/v1/ai-models/user-available` | May be used by model selector as a user-filtered alternative; unclear which JS file uses which endpoint |
| ❌ | GET | `/api/v1/ai-models/cost-logs/recent` | **No frontend reference found.** Debug/developer endpoint not exposed in any user-facing page. Consider adding to admin view. |

---

## 18. LLM Models

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | GET | `/api/v1/llm-models/` | Possible use in AI models info page (`/ui/ai-models`) or admin model config; overlap with `/api/v1/ai-models/` is unclear — **these two endpoints need deduplication review**. |

---

## 19. Image Generation

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/image-generation/generate` | `image_generator.js` — image generation modal form submission |
| ✅ | GET | `/api/v1/image-generation/{world_id}/{entity_type}/{entity_id}/images` | Character/location/lore form pages — loads existing images for entity |
| ✅ | POST | `/api/v1/image-generation/{world_id}/{entity_type}/{entity_id}/set-current` | Image modal — "Set as profile image" button |
| ✅ | DELETE | `/api/v1/image-generation/{image_id}` | Image modal or image management — delete image |
| ✅ | GET | `/api/v1/image-jobs/{id}` | `image_job_monitor.js` — polls every 2s until job completes |

> **⚠️ Path Discrepancy:** `frontendboth.md` documents the generate endpoint as `/api/v1/images/generate` and image fetch as `/api/v1/images/{id}`. The actual router uses `/api/v1/image-generation/`. **Verify and update frontendboth.md — the frontend JS may be calling the wrong path.**

---

## 20. Prompts

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/prompts/` | `prompt_form_handler.js` — create prompt |
| ✅ | GET | `/api/v1/prompts/my-prompts` | `prompt_crud.js` — prompt library list; `act_prompt_manager.js`, `scene_prompt_selector.js` — editor prompt selection |
| ⚠️ | PUT | `/api/v1/prompts/{id}` | `prompt_form_handler.js` — edit prompt form (implied by CRUD) |
| ⚠️ | DELETE | `/api/v1/prompts/{id}` | `prompt_crud.js` — delete prompt button |
| ❌ | GET | `/api/v1/prompts/story-options` | **No frontend reference found.** Returns genre, tone, conflict options. Should be wired into story wizard and story form pickers — **HIGH PRIORITY gap**. |
| ❌ | GET | `/api/v1/prompts/character-roles` | **No frontend reference found.** Should populate role dropdowns in character form or association modals. |
| ❌ | GET | `/api/v1/prompts/art-styles` | **No frontend reference found.** Should populate style selector in image generation modal. |

---

## 21. Documents

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/documents/` | `document_crud.js` — document manager page list |
| ✅ | POST | `/api/v1/documents/upload` | `document_upload.js` — file upload with progress indicator |
| ✅ | DELETE | `/api/v1/documents/{id}` | `document_crud.js` — delete document button |

---

## 22. World Chat

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | GET | `/api/v1/world-chat/chat/samples` | World chat page — loads suggested starter messages; likely in `world_chat_main.js` |
| ✅ | POST | `/api/v1/world-chat/sessions/{world_id}` | `world_chat_session_manager.js` — create new session |
| ✅ | GET | `/api/v1/world-chat/sessions/{world_id}` | `world_chat_session_manager.js` — load sessions list in sidebar |
| ✅ | GET | `/api/v1/world-chat/sessions/{world_id}/{session_id}` | `world_chat_session_manager.js` — load session message history |
| ❌ | POST | `/api/v1/world-chat/sessions/{world_id}/{session_id}/send-message` | **Likely superseded by WebSocket.** World chat uses WebSocket for real-time messaging. This REST endpoint may be a fallback or legacy route — verify if it is ever called. |

---

## 23. Story Chat

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/story-chat/stories/{story_id}/sessions` | `story_chat.js` — create story chat session |
| ✅ | GET | `/api/v1/story-chat/stories/{story_id}/sessions` | `story_chat.js` — list sessions in sidebar |
| ✅ | GET | `/api/v1/story-chat/stories/{story_id}/sessions/{session_id}` | `story_chat.js` — load session message history |

---

## 24. Public World Chat

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | GET | `/api/v1/public/worlds/{world_id}/chat/info` | `public_world_chat.html` page init — loads world name/description for anonymous display |
| ⚠️ | POST | `/api/v1/public/worlds/{world_id}/chat/sessions` | Public world chat page — create anonymous session |
| ⚠️ | GET | `/api/v1/public/worlds/{world_id}/chat/sessions/{session_id}` | Public world chat page — load session history |
| ⚠️ | POST | `/api/v1/public/worlds/{world_id}/chat/sessions/{session_id}/messages` | Public world chat page — send message (REST-based for anonymous, no WebSocket auth) |

---

## 25. World Builder

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | Various | `/api/v1/world-builder/*` | World builder wizard page (`/ui/worlds/{id}/builder`) — AI-guided world building. Full endpoint list not catalogued in frontendboth.md; needs verification against `world_builder_service.py`. |

---

## 26. World Importer

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/worlds/import/create-from-document` | `world_importer_form_handler.js`, `world_importer_from_doc_handler.js` — import world from document or book |
| ⚠️ | Various | Other import/status endpoints | May include job status polling for background import tasks; not fully documented |

---

## 27. Story Wizard API

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ⚠️ | GET | `/api/story-wizard/validate-connection` | Story wizard page — validates AI connection on page load |
| ✅ | POST | `/api/story-wizard/generate-concepts` | `story_generation_modal.js` — generates concept options in brainstorm step |
| ✅ | POST | `/api/story-wizard/generate-outline` | `story_generation_modal.js` — generates act outline from selected concept |

> **Note:** These use prefix `/api/story-wizard/` (not `/api/v1/`). Confirm this routing prefix is intentional.

---

## 28. Published Stories

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/published-stories/` | Published stories gallery page — loads story cards |
| ✅ | GET | `/api/v1/published-stories/{story_id}` | Published story reader page — loads story content |
| ⚠️ | POST | `/api/v1/published-stories/{story_id}/rate` | Published story page — star rating widget |
| ✅ | POST | `/api/v1/published-stories/{story_id}/comments` | Published story page — comment form submission |
| ✅ | GET | `/api/v1/published-stories/{story_id}/comments` | Published story page — loads comment thread |

---

## 29. Billing

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/billing/balance` | `main.js` — called on **every page load** to populate coin badge in top nav |
| ⚠️ | GET | `/api/v1/billing/account` | My account page — loads subscription info; may be server-rendered instead of JS fetch |
| ⚠️ | GET | `/api/v1/billing/transactions` | `billing_dashboard.js` — transaction history table |
| ❌ | GET | `/api/v1/billing/packages` | **No frontend reference found.** Returns available coin packages for purchase. Billing dashboard should surface these — **HIGH PRIORITY gap** in the purchase flow. |
| ❌ | POST | `/api/v1/billing/add-credits` | **No frontend reference found.** Credits may be added via Stripe webhook only. If this is a manual shortcut, it should be moved to admin billing. |

---

## 30. Admin Billing

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| 🔒 | GET | `/api/v1/admin/billing/dashboard` | Admin billing page (`/ui/admin/billing`) |
| 🔒 | GET | `/api/v1/admin/billing/transactions` | Admin billing page — all transactions view |
| 🔒 | GET | `/api/v1/admin/billing/users` | Admin billing page — user accounts with billing info |
| 🔒 | POST | `/api/v1/admin/billing/adjust-credits` | Admin billing page — manual credit adjustment form |

---

## 31. Referrals

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/referrals/stats` | `referral_tracking.js` — referrals page stats display |
| ✅ | GET | `/api/v1/referrals/history` | `referral_tracking.js` — referral history table |
| ⚠️ | GET | `/api/v1/referrals/rewards` | `referral_tracking.js` — reward history section |

---

## 32. Forum

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/forum/categories/` | Forum home page — category cards |
| ✅ | GET | `/api/forum/categories/{category_id}` | Forum category page |
| ✅ | GET | `/api/forum/categories/slug/{slug}` | Forum category page via URL slug |
| 🔒 | POST | `/api/forum/categories/` | Admin: create category |
| 🔒 | PUT | `/api/forum/categories/{category_id}` | Admin: update category |
| 🔒 | DELETE | `/api/forum/categories/{category_id}` | Admin: delete category |
| ✅ | GET | `/api/forum/threads/` | Forum category page — thread list |
| ✅ | GET | `/api/forum/threads/{thread_id}` | Forum thread page |
| ✅ | POST | `/api/forum/threads/` | Forum category page — "New Thread" button |
| ⚠️ | PUT | `/api/forum/threads/{thread_id}` | Forum thread page — edit thread title (author or admin) |
| ⚠️ | DELETE | `/api/forum/threads/{thread_id}` | Forum thread page — delete thread |
| 🔒 | POST | `/api/forum/threads/{thread_id}/pin` | Admin: pin thread |
| 🔒 | POST | `/api/forum/threads/{thread_id}/lock` | Admin: lock thread |
| ✅ | GET | `/api/forum/posts/thread/{thread_id}` | Forum thread page — post list |
| ⚠️ | GET | `/api/forum/posts/user/{user_id}` | User profile page — may show user's posts; not confirmed |
| ⚠️ | GET | `/api/forum/posts/{post_id}` | Direct post fetch — likely used internally for editing |
| ✅ | POST | `/api/forum/posts/` | Forum thread page — reply form |
| ⚠️ | PUT | `/api/forum/posts/{post_id}` | Forum thread page — inline post edit |
| ⚠️ | DELETE | `/api/forum/posts/{post_id}` | Forum thread page — delete post |
| ✅ | POST | `/api/forum/posts/{post_id}/vote` | Forum thread page — upvote/downvote button |
| ❌ | GET | `/api/forum/posts/user/{user_id}/stats` | **No frontend reference found.** User post stats not displayed anywhere in documented UI. |

---

## 33. Blog

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/blog/posts` | Blog index page — post listing |
| ✅ | GET | `/api/blog/posts/{slug}` | Blog post detail page |
| ✅ | POST | `/api/blog/posts` | Blog editor — create post |
| ✅ | PUT | `/api/blog/posts/{post_id}` | Blog editor — update post |
| ✅ | POST | `/api/blog/posts/{post_id}/publish` | Blog editor — publish post |
| ✅ | DELETE | `/api/blog/posts/{post_id}` | Blog admin list — delete post |
| ✅ | GET | `/api/blog/my-posts` | Blog editor / admin list — user's own posts |
| ✅ | GET | `/api/blog/categories` | Blog index / editor — category filter and selector |
| 🔒 | POST | `/api/blog/categories` | Admin: create category |
| 🔒 | PUT | `/api/blog/categories/{category_id}` | Admin: update category |
| 🔒 | DELETE | `/api/blog/categories/{category_id}` | Admin: delete category |
| ⚠️ | GET | `/api/blog/categories/{category_id}` | Blog filtering — load single category details |
| ⚠️ | GET | `/api/blog/tags` | Blog index / editor — tag filter and selector |
| 🔒 | POST | `/api/blog/tags` | Admin: create tag |
| 🔒 | PUT | `/api/blog/tags/{tag_id}` | Admin: update tag |
| 🔒 | DELETE | `/api/blog/tags/{tag_id}` | Admin: delete tag |
| ✅ | POST | `/api/blog/comments` | Blog post page — comment form |
| ✅ | GET | `/api/blog/comments/{post_id}` | Blog post page — comment thread |
| ⚠️ | PUT | `/api/blog/comments/{comment_id}` | Blog post page — edit comment |
| ⚠️ | DELETE | `/api/blog/comments/{comment_id}` | Blog post page — delete comment |
| ✅ | GET | `/api/blog/search` | Blog index — search field |
| ❌ | POST | `/api/blog/subscriptions` | **No frontend reference found.** Email subscription not documented or visible in any page. |
| ❌ | DELETE | `/api/blog/subscriptions` | **No frontend reference found.** |
| ❌ | GET | `/api/blog/subscriptions/status` | **No frontend reference found.** |
| ✅ | POST | `/api/blog/media/upload` | Blog editor — media / image upload |
| ⚠️ | DELETE | `/api/blog/media/{media_id}` | Blog editor — remove uploaded media |
| ⚠️ | GET | `/api/blog/media/{post_id}` | Blog editor — load existing post media |
| ⚠️ | POST | `/api/blog/engagement/like` | Blog post page — like button |
| ⚠️ | POST | `/api/blog/engagement/unlike` | Blog post page — unlike button |
| ⚠️ | GET | `/api/blog/engagement/{post_id}/stats` | Blog post page — like / view count display |
| ❌ | GET | `/api/blog/analytics/posts` | **No frontend reference found.** Blog analytics not visible in any documented page. |
| ❌ | GET | `/api/blog/analytics/dashboard` | **No frontend reference found.** |

---

## 34. Maintenance

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | GET | `/api/v1/maintenance/status` | `maintenance.js` — checks on every page load to show maintenance banner |
| 🔒 | POST | `/api/v1/maintenance/enable` | Admin maintenance page — enable maintenance mode |
| 🔒 | POST | `/api/v1/maintenance/disable` | Admin maintenance page — disable maintenance mode |

---

## 35. Welcome Interview

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ❌ | GET | `/api/v1/interview/questions/{interview_id}` | **No frontend reference found.** Separate from the welcome interview flow — may be a duplicate system or unused. Reconcile with `/ui/welcome-interview/api/analyze`. |
| ❌ | POST | `/api/v1/interview/submit` | **No frontend reference found.** Same concern as above. |
| ✅ | POST | `/ui/welcome-interview/api/analyze` | `interview.js` — welcome interview form submission and AI analysis |

> **Note:** Two separate interview router systems exist (`/api/v1/interview/*` and `/ui/welcome-interview/api/*`). Only the second is confirmed used. Investigate whether `/api/v1/interview/*` is a legacy or duplicate.

---

## 36. Batch Operations

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| 📡 | POST | `/api/v1/batch/characters` | **No browser JS reference.** Used by world importer background jobs, not direct frontend calls. |
| 📡 | GET | `/api/v1/batch/characters` | Same — backend/importer use only. |
| 📡 | POST | `/api/v1/batch/locations` | Same — backend/importer use only. |
| 📡 | GET | `/api/v1/batch/locations` | Same — backend/importer use only. |
| 📡 | POST | `/api/v1/batch/lore-items` | Same — backend/importer use only. |
| 📡 | GET | `/api/v1/batch/lore-items` | Same — backend/importer use only. |

> **Assessment:** All 6 batch endpoints are likely consumed by `app/processing/importer_jobs.py`, not by browser JS. They are correctly unexposed in the frontend.

---

## 37. Act AI Review

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | POST | `/api/v1/acts/{act_id}/ai/review` | `act_review_components/api_handler_review.js` — submits act content for AI review, receives inline highlight suggestions |

---

## 38. Admin: CTA Content

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| 🔒 | GET | `/admin/cta-content` | Admin CTA manager page |
| 🔒 | GET | `/admin/cta-content/{cta_id}` | Admin CTA manager — edit form load |
| 🔒 | POST | `/admin/cta-content` | Admin CTA manager — create CTA |
| 🔒 | PUT | `/admin/cta-content/{cta_id}` | Admin CTA manager — update CTA |
| 🔒 | POST | `/admin/cta-content/{cta_id}/toggle-active` | Admin CTA manager — activate/deactivate |
| 🔒 | DELETE | `/admin/cta-content/{cta_id}` | Admin CTA manager — delete CTA |
| ❌ | GET | `/admin/debug/user-info` | **No frontend reference found. SECURITY: verify this endpoint has proper admin auth protection before deploying.** |

---

## 39. Social / OG / Analytics

| Status | Method | Endpoint | Frontend Location |
|---|---|---|---|
| ✅ | Various | Social sharing endpoints | `social_sharing.js` — opens share dialogs for published stories and images |
| 📡 | Various | `/social-preview/*` | OG preview images — called by social media crawlers, not browser JS |
| 📡 | Various | `/og-debug/*` | Open Graph debug — developer tool only |
| 📡 | Various | `/bot-analytics/*` | Bot/crawler detection — server-side middleware, not browser-callable |

---

## 40. Summary: Unused Endpoints

### Confirmed Backend-Internal (not browser-facing, not bugs)

| Endpoint | Reason |
|---|---|
| `POST /api/v1/auth/token` | OAuth2 machine client / Swagger UI only |
| All `POST/GET /api/v1/batch/*` | Used by importer background jobs, not browser JS |
| Social preview / OG endpoints | Called by social crawlers only |
| Bot analytics endpoints | Server-side middleware only |

---

### ❌ Gaps Requiring Action

| Priority | Endpoint | Issue | Recommendation |
|---|---|---|---|
| 🔴 HIGH | `GET /api/v1/billing/packages` | Purchase flow broken — no UI to show coin packages | Wire into `billing_dashboard.js` |
| 🔴 HIGH | `GET /api/v1/prompts/story-options` | Genre/tone/conflict pickers not populated from API | Wire into `story_generation_modal.js` and story form |
| 🔴 HIGH | `POST /api/v1/auth/refresh` | No 401 interceptor in JS — sessions expire silently with no recovery | Add Fetch wrapper / interceptor in `main.js` |
| 🔴 HIGH | `GET /admin/debug/user-info` | Potentially unprotected debug endpoint | Verify admin auth guard; remove or restrict |
| 🟡 MEDIUM | `GET /api/v1/dashboard/summary` | Dashboard built via server-render; this API is unreachable from browser | Either wire into JS or remove the endpoint |
| 🟡 MEDIUM | `GET /api/v1/stories/{story_id}/outline` | No UI call — appears to be a React-ready endpoint | Document as React rewrite target; no action in current frontend |
| 🟡 MEDIUM | `POST /api/v1/acts/{act_id}/compile-scenes` | Useful feature (compile scenes → act) but no UI button | Add button to act editor or story detail page |
| 🟡 MEDIUM | `POST /api/v1/acts/{act_id}/scenes/generate-scenes` | Batch scene generation with no UI entry point | Add "Generate Scenes" button on act in story detail |
| 🟡 MEDIUM | `GET /api/v1/prompts/art-styles` | Image generation modal style selector not API-driven | Wire into `modules/image_generation_modal.js` |
| 🟡 MEDIUM | `GET /api/v1/prompts/character-roles` | Character/association role picker not populated from API | Wire into character form and `_link_character_modal.html` |
| 🟡 MEDIUM | `GET /api/v1/llm-models/` | Unclear overlap with `/api/v1/ai-models/` | Audit and deduplicate |
| 🟡 MEDIUM | `GET /api/v1/interview/questions/{interview_id}` + `POST /submit` | Two interview systems exist — only one is wired | Reconcile or remove the unwired one |
| 🟡 MEDIUM | `GET /api/blog/analytics/posts` + `dashboard` | Author blog analytics has no visible UI | Add analytics section to blog editor |
| 🟡 MEDIUM | `POST /api/v1/billing/add-credits` | Unclear if Stripe webhook or this endpoint handles credit addition | Clarify flow; remove if Stripe webhook is sole path |
| 🟢 LOW | `GET /api/v1/ai-models/cost-logs/recent` | Debug endpoint with no UI | Add to admin panel or keep as developer tool |
| 🟢 LOW | `GET /api/v1/associations/roles/{container_type}/{element_type}` | Role suggestions unused | Wire into link-element modals for richer UX |
| 🟢 LOW | `PUT /api/v1/associations/story/{story_id}/character/{character_id}` | Role update on existing association not exposed | Add inline edit to association chips in editor |
| 🟢 LOW | `GET /api/v1/location-connections/{connection_id}` | Individual connection fetch not used | Remove if `world_map.js` never calls it |
| 🟢 LOW | `POST /api/v1/world-chat/sessions/{world_id}/{session_id}/send-message` | REST fallback may be superseded by WebSocket | Verify and remove if WebSocket is the only path |
| 🟢 LOW | `GET /api/forum/posts/user/{user_id}/stats` | Forum stats not displayed in any page | Add to user profile or remove |
| 🟢 LOW | `POST/DELETE/GET /api/blog/subscriptions` | Email subscription feature has no UI entry point | Build subscription UI or remove endpoints |
| 🟢 LOW | `GET /api/v1/users/{user_id}` | No public user profile page | Add profile page or remove endpoint |

---

### ⚠️ Path Discrepancy Between frontendboth.md and Actual Router

| frontendboth.md Documents | Actual Router Path | Action |
|---|---|---|
| `POST /api/v1/images/generate` | `POST /api/v1/image-generation/generate` | Verify JS file and update docs |
| `GET /api/v1/images/{id}` | `GET /api/v1/image-generation/{image_id}` | Same |
| `GET /api/v1/image-jobs/{id}` | Path unclear in catalog | Locate in `image_generation.py` and confirm |
| `POST /api/v1/associations/` (generic) | Multiple specific sub-paths per entity type | frontendboth.md oversimplified — docs already corrected in this file |
