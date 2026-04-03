# React Component Inventory

> Purpose: inventory of reusable frontend components to carry forward into the React rebuild.
>
> This is not a 1:1 conversion list. It groups legacy partials, template fragments, and recurring JS-driven UI patterns into React component candidates.

Reference sources:
- `app/templates/components/README.md`
- `app/templates/partials/`
- `app/static/js/`
- `frontendAll.md`
- `frontendRouteBacklog.md`

Suggested metadata for implementation tickets:
- owner area
- route usage
- API dependency
- state complexity
- accessibility risk

---

## 1. App Shell and Navigation

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `AppShell` | `layouts/base.html` | all app routes | overall page frame, content area, global providers | Root authenticated shell |
| `PublicShell` | `layouts/base.html` | public routes | public nav/footer/page frame | Public-only variant |
| `TopNav` | `_topbar.html`, `_horizontal_navbar.html`, `_navbar.html` | most pages | primary navigation, user menu, coin balance, theme toggle | High-priority component |
| `PageHeader` | `_page_header.html` | many pages | title, subtitle, CTA actions, supporting metadata | Shared page header pattern |
| `Breadcrumbs` | `_breadcrumbs.html`, components breadcrumb | many pages | contextual navigation trail | Should be route-driven |
| `Footer` | `_footer.html` | public and app | footer links and site info | Likely smaller in app shell |
| `CookieConsentBanner` | banner in base layout | global | consent prompt and persistence | Global state component |
| `MaintenanceBanner` | maintenance partial/banner usage | global | maintenance messaging and route restrictions | Needs environment/global app awareness |
| `UserMenu` | topbar/account dropdown | app shell | profile, billing, logout, impersonation status | |
| `CoinBalanceBadge` | topbar billing fetch | app shell | current credit/coin balance display | Poll or invalidate after billing actions |
| `ThemeToggle` | `theme-toggle.js` | global | theme switch and persistence | |
| `HelpButton` | `_help_button.html` | many pages | open help panel/modal | Trigger only, shared globally |
| `ToastCenter` | `notifications.js`, alerts partial | global | app notifications | Prefer portal-based implementation |

## 2. Forms and Field Controls

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `TextField` | components/forms/input.html | all forms | labeled text input with validation | |
| `TextareaField` | components/forms/textarea.html | all forms | multiline input with count/help text | |
| `SelectField` | components/forms/select.html | all forms | single/multi select input | |
| `RichTextEditorField` | `content_editor.html`, Quill setup files | acts, scenes, blog, help | rich text editing wrapper | Abstract away editor vendor |
| `FormActionsBar` | repeated form footer patterns | forms | save, cancel, delete, dirty-state UI | |
| `InlineValidationMessage` | auth/forms/utilities | all forms | field and form-level errors | |
| `FileUploadField` | `document_upload.js`, media flows | documents, media, image flows | upload input/dropzone | |
| `SearchSelect` | model/prompt/entity selectors | many forms | search and select related records | Could be generic headless component |
| `TagInput` | blog tags, prompts, metadata | blog, prompts | add/remove tokens | |

## 3. Buttons, Cards, Status, Feedback

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `Button` | components/buttons/button.html | everywhere | standard button variants | |
| `ButtonGroup` | components/buttons/button_group.html | editor toolbars, filters | grouped actions | |
| `AlertBanner` | components/alerts/alert.html, `_alerts.html` | forms, pages | dismissible alert | |
| `StatusBadge` | components/badges/badge.html | lists and detail pages | status/role/type labels | |
| `BasicCard` | components/cards/basic_card.html | dashboards, content cards | generic card layout | |
| `ActionCard` | components/cards/action_card.html | home, onboarding, dashboards | CTA-oriented card | |
| `MetricCard` | components/cards/status_card.html | billing, analytics, dashboards | KPI/metric display | |
| `ProgressBar` | components/progress/progress_bar.html | uploads/jobs/credits | determinate/indeterminate progress | |
| `EmptyState` | repeated empty layouts | all list pages | no-results/no-content state | |
| `LoadingState` | repeated spinners/skeletons | all pages | page/section loading UI | Prefer skeletons over spinners |
| `ErrorState` | repeated alert blocks | all pages | recoverable load failure UI | |

## 4. Modal and Overlay System

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `ModalRoot` | base modal includes | global | central modal portal and stacking | |
| `BaseModal` | components/modals/base_modal.html | many pages | generic modal layout | |
| `ConfirmationModal` | components/modals/confirmation_modal.html | delete/archive/danger actions | confirm destructive or important actions | |
| `SuccessModal` | components/modals/success_modal.html | completion states | positive confirmation flow | Likely optional if toasts cover enough |
| `StoryGenerationModal` | `_story_generation_modal.html`, `story_generation_modal.js` | story wizard, story creation | AI-assisted story generation flow | High-value bespoke modal |
| `UsePromptModal` | `_use_prompt_modal.html` | act/scene/blog/prompt workflows | apply prompt to target editor | |
| `ImageGenerationModal` | `image_generation_modal.html`, `image_generator.js` | story/world/entity/image flows | request image generation and preview status | |
| `ImagePropertiesModal` | `image_properties_modal.html` | generated image flows | edit metadata/set current image | |
| `LinkCharacterModal` | `_link_character_modal.html` | stories, acts, scenes | attach character associations | |
| `LinkLocationModal` | `_link_location_modal.html` | stories, acts, scenes | attach location associations | |
| `LinkLoreItemModal` | `_link_lore_item_modal.html` | stories, acts, scenes | attach lore associations | |
| `HelpModal` | `help-modal.js`, partials | help-enabled pages | contextual help/content | |

## 5. Domain Lists and Detail Blocks

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `WorldCard` | world list/detail templates | worlds, home | world summary card | |
| `StoryCard` | story list/published story cards | stories, public | story summary card | |
| `EntityListTable` | character/location/lore lists | world content pages | shared list/table for world entities | Could be parameterized by entity type |
| `EntityDetailHeader` | character/location/lore detail templates | element detail pages | title, metadata, actions, image | |
| `OutlineTree` | story detail act/scene nesting | story detail | render story structure | Important navigation component |
| `AssociationChipList` | story associations panel | stories/acts/scenes | list linked entities and roles | |
| `AssociationManagerPanel` | handlers + modals | stories/acts/scenes | link/unlink and show associations | |
| `DocumentTable` | document manager | documents | list documents and processing states | |
| `PublishedStoryReader` | published story pages | public published story | long-form reading layout | |
| `CommentThread` | forum/blog/published story comments | community areas | nested comments and actions | Reusable across domains if carefully abstracted |

## 6. Editor and Writing Components

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `EditorPageLayout` | act/scene/editor templates | editors | split layout with editor and side panels | |
| `AutosaveStatus` | act/scene save handlers | editors | dirty, saving, saved, error states | |
| `PromptPicker` | prompt manager/selectors | acts, scenes, blog | choose and apply prompt | |
| `AiModelSelector` | `_ai_model_selector.html`, `_ai_model_card_selector.html`, `_ai_model_button_selector.html`, `ai_model_selector.js` | editors, generation flows | choose active AI model | Use one domain model, multiple presentations |
| `EditorToolbarAiActions` | `modules/ai_quill_toolbar.js` | editors | AI rewrite/transform actions | |
| `ReviewDiffPanel` | act review scripts | act review | highlight suggestions and compare changes | |
| `BasicStoryAssistantPanel` | `basic_story_editor_ai_assistant.js` | basic story editor | assistant tools for simplified story mode | |
| `WordCountDisplay` | editor scripts | editors | live word/character count | |
| `ContextSidebar` | chat/editor sidebars | editors, chat | shows related context, entities, source docs | Important for user trust |

## 7. Chat and Streaming Components

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `ChatLayout` | chat pages | world chat, story chat, public chat | page shell for chat surfaces | |
| `ConversationList` | session manager patterns | chat pages | list/select chat sessions | |
| `MessageList` | chat handlers | chat pages | render threaded/chronological messages | |
| `MessageComposer` | chat handlers | chat pages | input, submit, disabled/loading state | |
| `StreamingMessage` | websocket handlers | chat and generation flows | partial/in-progress content rendering | |
| `ContextSourcePanel` | chat/document context display | chat pages | show documents/entities used as context | |
| `ChatSessionHeader` | chat page headers | chat pages | title, context, controls | |

## 8. Spatial, Visual, and Media Components

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `WorldMapCanvas` | `world_map.js` | world map page | render locations and connections | Probably custom canvas/SVG layer |
| `HierarchyTree` | `world_hierarchy.js` | hierarchy page | navigate nested world content | |
| `GeneratedImageGallery` | image/job scripts | stories, worlds, entities | list generated images and actions | |
| `ImageJobStatusList` | `image_job_monitor.js` | image and admin pages | pending/running/completed jobs | |
| `MediaLibraryGrid` | blog media flows | blog media, editor picker | media thumbnail grid | |
| `FilePreviewPanel` | documents/media | docs/media | preview selected file/image/document | |

## 9. Community and Publishing Components

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `ForumCategoryList` | forum templates | forum | category navigation | |
| `ForumThreadList` | forum templates | forum | list threads in category | |
| `ForumThreadView` | forum templates | forum | thread plus replies | |
| `BlogPostCard` | blog templates | blog lists | blog post teaser card | |
| `BlogPostLayout` | blog post page | blog detail | article layout | |
| `AuthorProfileHeader` | blog author pages | blog author/profile | author identity and stats | |
| `SocialSharingBar` | `_social_sharing.html`, `social-sharing.js` | published stories, blog, public pages | share actions and stats | |
| `RatingSummary` | published story pages | published stories | star/rating summary | |
| `PublicGalleryGrid` | home/public pages | published/public discovery | shared public content grid | |

## 10. Commercial, Account, Admin Components

| Proposed React Component | Legacy Source | Used On | Responsibility | Notes |
|---|---|---|---|---|
| `BillingSummaryPanel` | billing pages | billing dashboard | balance, packages, recent activity | |
| `TransactionTable` | billing/admin billing | billing, admin | transaction history table | |
| `PackageSelector` | billing flows | billing purchase flow | choose package/credits | |
| `ReferralStatsPanel` | referral pages | referrals | stats, rewards, invite tools | |
| `AdminDataTable` | admin pages | users, billing, jobs, news | generic admin table with filters/actions | |
| `AdminActionToolbar` | admin pages | admin | bulk actions and filters | |
| `CtaEditorPanel` | CTA admin pages, `cta_display.html` | admin CTA | manage CTA content and preview | |
| `NewsEditor` | news admin pages | admin news | CRUD editor for announcements/news | |
| `UserImpersonationControl` | admin auth flows | admin users | impersonate/stop impersonating | |

## 11. Components To Build First

Build order for reusable components:

1. `AppShell`
2. `TopNav`
3. `PageHeader`
4. `Breadcrumbs`
5. `Button`, `TextField`, `TextareaField`, `SelectField`
6. `AlertBanner`, `ToastCenter`, `LoadingState`, `ErrorState`, `EmptyState`
7. `FormActionsBar`
8. `BasicCard`, `MetricCard`, `StatusBadge`
9. `ModalRoot`, `BaseModal`, `ConfirmationModal`
10. `WorldCard`, `StoryCard`, `EntityListTable`
11. `AssociationManagerPanel`
12. `EditorPageLayout`, `RichTextEditorField`, `AutosaveStatus`
13. `ChatLayout`, `MessageList`, `MessageComposer`
14. domain-specific components after the base system is stable

## 12. Components That Need Behavior Notes Before Implementation

Use `uiBehaviorCapture.md` first for:
- `TopNav`
- `CoinBalanceBadge`
- `StoryGenerationModal`
- `AiModelSelector`
- `AssociationManagerPanel`
- `RichTextEditorField`
- `AutosaveStatus`
- `ChatLayout`
- `WorldMapCanvas`
- `ImageGenerationModal`
- `MediaLibraryGrid`
- `CtaEditorPanel`
