# Basic/Advanced Story System - Complete Implementation

## Overview

This document describes the **fully implemented** Basic/Advanced Story system - a two-tier approach that allows users to start writing immediately with minimal setup (Basic Stories) or use full world-building features (Advanced Stories). The system includes comprehensive AI chat capabilities for story discussion and development.

## Core Concepts

### Basic Stories
- **Purpose**: Enable users to start writing immediately without world-building overhead
- **Features**: Simple creation form (title + description), automatic Act 1 creation, direct to editor
- **Restrictions**: No character/location management, no hierarchy view
- **Shadow World**: Automatically created but completely hidden from user

### Advanced Stories  
- **Purpose**: Full-featured storytelling with comprehensive world-building
- **Features**: All Basic features plus characters, locations, lore, multiple acts, world management
- **World**: Fully visible and editable world with all management tools

## Key Design Decisions

### 1. Shadow Worlds
- Every Basic Story has a hidden "shadow world" to satisfy database relationships
- Shadow worlds are marked with `is_shadow = true` in the database
- Never shown in world lists or navigation
- Become visible when story is upgraded to Advanced

### 2. Story Creation Flow

#### Basic Story (Start Writing)
1. User clicks "Start Writing" button
2. Enters only title and description
3. System automatically:
   - Creates story with `story_type = 'basic'`
   - Creates shadow world named "[Story Title] World"
   - Creates Act 1 (no act number shown)
4. Redirects directly to act editor

#### Advanced Story
1. Traditional flow with full form
2. World selection/creation
3. All configuration options available

### 3. Act Number Visibility
- **1 Act**: No act numbers shown anywhere
- **2+ Acts**: Act numbers visible for all acts
- Applies to both Basic and Advanced stories

### 4. Upgrade Process (Basic → Advanced)
1. User clicks "Upgrade to Advanced Story"
2. System prompts for world name (default: "[Story Title] World")
3. Shadow world becomes visible and fully editable
4. All features unlocked immediately
5. No downgrade option

### 5. Complete Feature Availability Matrix

| Feature | Basic Story | Advanced Story | Notes |
|---------|------------|----------------|-------|
| **Story Creation & Management** | | | |
| Title/Description | ✅ | ✅ | Instant creation vs full form |
| Auto-generated First Act | ✅ | ✅ | "Act 1" created automatically |
| Act Creation & Management | ✅ | ✅ | Full act editor access |
| Scene Writing & Management | ✅ | ✅ | Complete scene functionality |
| Story Type Badges | ✅ | ✅ | Visual indicators throughout UI |
| Story Upgrade to Advanced | ✅ | ❌ | One-way upgrade available |
| **AI Features** | | | |
| AI Writing Assistance | ✅ | ✅ | Context-free vs world-aware |
| Story Chat Discussions | ✅ | ✅ | Different AI prompts & context |
| AI Summaries (Story/Act/Scene) | ✅ | ✅ | Full summary generation |
| Context Context Integration | ❌ | ✅ | No world data vs full context |
| **Publishing & Sharing** | | | |
| Story Publishing | ✅ | ✅ | Identical publishing capabilities |
| Published Story Gallery | ✅ | ✅ | Stories show type badges |
| Story Comments & Ratings | ✅ | ✅ | Full community features |
| **World Building** | | | |
| Character Management | ❌ | ✅ | No character sheets vs full management |
| Location Management | ❌ | ✅ | No location details vs full system |
| Lore Items | ❌ | ✅ | No lore management vs full system |
| World Chat | ❌ | ✅ | No world-specific AI chat |
| Hierarchy View | ❌ | ✅ | No world overview vs full hierarchy |
| World Detail Page Access | ❌ | ✅ | Shadow world vs visible world |
| World-Story Associations | ❌ | ✅ | Auto-shadow vs manual selection |
| **Navigation & UI** | | | |
| My Stories List | ✅ | ✅ | Mixed view with type indicators |
| My Worlds List | ❌ | ✅ | Shadow worlds hidden vs visible |
| Navigation Dropdown | ✅ | ✅ | Quick creation options |
| Help System | ✅ | ✅ | Type-specific help documentation |
| **Technical Features** | | | |
| Cost Tracking | ✅ | ✅ | Full AI call logging |
| WebSocket Chat | ✅ | ✅ | Real-time story discussions |
| Image Generation | ✅ | ✅ | Story cover images |
| Document Management | ✅ | ✅ | Context document uploads |

### 6. UI/UX Differentiation
- **Visual Badges**: Basic stories show "Basic" badge on cards and lists
- **Menu Items**: Dynamic menu based on story type
- **Navigation**: "My Worlds" visible but shows only non-shadow worlds
- **Story Lists**: Basic and Advanced stories mixed with visual indicators

### 7. AI Context Handling
- **Basic Stories**: AI prompts exclude world context fields, focus on writing craft
- **Advanced Stories**: Full world context provided to AI including characters, locations, lore
- **Story Chat**: Real-time AI discussions with story-specific context and full content access

### 8. Story Chat System (NEW FEATURE)

The Story Chat System provides real-time AI conversations about stories with full context awareness:

#### Chat Features
- **Real-time WebSocket Communication**: Instant messaging with streaming AI responses
- **Session Management**: Create focused chat sessions for different topics (plot, characters, themes)
- **Full Story Context**: AI receives complete content of current and previous acts/scenes
- **Element Targeting**: Chat about specific acts or scenes with full context
- **Cost Tracking**: All AI interactions logged with token usage and costs

#### Chat Differences by Story Type

**Basic Story Chat**:
- Focus on **writing craft** and **storytelling techniques**
- Discussions about **plot development**, **pacing**, **dialogue**
- **No world-building context** - pure story content focus
- Prompts optimized for **writing improvement** and **creative flow**

**Advanced Story Chat**:
- **Comprehensive world-building** discussions
- **Character development** and **relationship dynamics**
- **Location details** and **world consistency**
- **Lore integration** and **thematic coherence**
- Full **Context context** from world elements

#### Chat Interface
- **Collapsible Chat Section**: Toggle on/off from story detail pages
- **Session Sidebar**: Manage multiple chat sessions per story
- **Focus Areas**: Plot, Characters, World, Themes, Structure, Writing Techniques
- **Message History**: Full conversation persistence
- **Target Selection**: Choose specific story elements to discuss

## Technical Implementation - COMPLETED

### Database Changes (IMPLEMENTED)
```python
# Story model
story_type: Mapped[str] = mapped_column(String(20), nullable=False, default='advanced', index=True)
chat_sessions: Mapped[List["StoryChatSession"]] = relationship(...)

# World model  
is_shadow: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

# New models for Story Chat System
class StoryChatSession(Base):
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    focus_area: Mapped[str] = mapped_column(String(50))  # plot, characters, etc.
    messages: Mapped[List["StoryChatMessage"]] = relationship(...)

class StoryChatMessage(Base):
    session_id: Mapped[int] = mapped_column(ForeignKey("story_chat_sessions.id"))
    role: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    target_element: Mapped[str] = mapped_column(String(50))  # 'act', 'scene', etc.
    target_element_id: Mapped[int] = mapped_column(Integer)
    cost_log_id: Mapped[int] = mapped_column(ForeignKey("ai_call_logs.id"))
```

### Migration Strategy
- All existing stories → `story_type = 'advanced'`
- All existing worlds → `is_shadow = false`
- No edge case handling needed

### Implementation Approach: COMPLETED

**Integration Strategy** was used instead of isolation for better code maintainability:

#### API Endpoints (IMPLEMENTED)
- `POST /api/stories/basic/create-ui` - Create Basic Story with shadow world (redirects to editor)
- `POST /api/stories/{story_id}/upgrade` - Upgrade Basic to Advanced Story
- `POST /story-chat/stories/{story_id}/sessions` - Create story chat session
- `GET /story-chat/stories/{story_id}/sessions` - List chat sessions
- `WebSocket /story-chat/ws/stories/{story_id}/sessions/{session_id}/chat` - Real-time chat

#### UI Implementation (IMPLEMENTED)
- **Navigation Dropdown**: My Stories → View All Stories, Create Basic Story, Create Advanced Story
- **Home Page**: Basic vs Advanced story creation buttons
- **Story List**: Mixed view with type badges and unified creation section
- **Story Detail**: Integrated chat section (collapsible)
- **Story Badges**: Throughout UI showing Basic/Advanced indicators

#### Code Integration Points (IMPLEMENTED)
- **StoryService**: Extended with story_type logic and upgrade mechanism
- **Templates**: Enhanced existing templates with story_type conditionals
- **AI Prompts**: Separate prompt files for Basic vs Advanced story chats
- **Help System**: Type-specific help documentation
- **WebSocket**: New story chat infrastructure alongside existing act/scene chat

#### Benefits of Integration
1. **Unified codebase** - easier maintenance
2. **Consistent UI/UX** - seamless user experience  
3. **Shared infrastructure** - cost tracking, publishing, etc.
4. **Feature parity** - both types get same core capabilities
5. **Flexible navigation** - users can mix story types

### Additional Isolated Components

#### AI Prompts (Separate Files)
- `/app/prompts/basic_story/` - New directory for Basic Story prompts
  - `basic_story_writing.yaml` - Writing assistance without world context
  - `basic_story_suggestions.yaml` - "What happens next" prompts
  - `basic_story_brainstorm.yaml` - Simple brainstorming prompts
- Existing prompts in `/app/prompts/` remain unchanged
- Prompt loader will select based on story type

#### Help System (Separate Files)
- `/app/static/help/basic_story/` - New help documentation
  - `basic_story_overview.html` - What are Basic Stories
  - `basic_story_creation.html` - How to create
  - `basic_story_writing.html` - Writing features
  - `basic_story_upgrade.html` - Upgrading to Advanced
- Existing help files remain untouched
- Help system will route based on context

#### Templates (Separate Files)
- `/app/templates/basic_story/` - New template directory
  - `create.html` - Basic Story creation form
  - `detail.html` - Basic Story detail page
  - `edit_act.html` - Simplified act editor
  - `_components/` - Basic Story specific components
- No modifications to existing templates
- Clean separation of UI code

## User Experience

### Entry Points
1. **"Start Writing"** - Prominent button leading to Basic Story
2. **Story Creation Toggle** - Switch between Basic/Advanced on form
3. **Menu Options** - Separate "Create Basic Story" and "Create Advanced Story"

### Publishing
- Basic Stories fully publishable
- Gallery shows "Basic Story" badge
- Readers can distinguish story types

### Templates
- Primary: Blank slate (default)
- Optional: Genre templates via dropdown

## Future Compatibility

Designed to support:
- Document import as Basic Stories
- Collaborative Basic Stories
- Basic Story series/connections
- No downgrade functionality planned

## Benefits

### For New Users
- Zero friction to start writing
- No overwhelming world-building decisions
- Clear upgrade path when ready

### For Experienced Users  
- Quick story creation option
- Full features still available
- Can mix Basic and Advanced stories

### For the Platform
- Lower barrier to entry
- Better new user activation
- Progressive feature disclosure

## Implementation Details from Design Sessions

### Service Layer Strategy
- **Extend StoryService** with story_type checks (not separate classes)
- **ShadowWorldMixin** for shadow-specific functionality
- **New repository methods** for shadow world operations

### API Design
- **story_type field** included in all story API responses ('basic' or 'advanced')
- **Hide shadow world fields** in API responses for Basic Stories
- **Include upgrade_available flag** in responses
- **Enforce story type checks** in Basic Story endpoints
- **Block character/location API access** for Basic Stories

### Frontend Architecture
- **No global state** for story type tracking
- **Components self-check** feature availability
- **Standard URLs** (no /basic/ prefix)
- **Cache story type** in browser storage
- **Separate components**:
  - Different act editors for Basic vs Advanced
  - BasicStoryCard and AdvancedStoryCard components
  - Hide world breadcrumbs for Basic Stories
  - Shared publishing modal

### Error Handling
- **Shadow world creation failure blocks** Basic Story creation
- **No recovery mechanisms** for failed upgrades
- **No special validation** for feature access
- **Standard error messages** (no Basic-specific messages)

### Performance Optimizations
- **Simplified queries** for Basic Story lists (fewer joins)
- **Index story_type column** for faster filtering
- **Exclude shadow worlds** from count queries
- **Standard eager loading** for both types

### Testing Approach
- **Separate test files** for Basic Story features
- **Update existing tests** to cover both story types
- **No specific tests** for upgrade process or restrictions

### Deployment Strategy
- **No feature flags** or gradual rollout
- **No user group limitations**
- **Deploy when ready** - full availability
- **No special monitoring** for Basic Story usage

## Implementation Files Created/Modified

### New Models & Schemas
- `app/models/story_chat_session.py` - Chat session database model
- `app/models/story_chat_message.py` - Chat message database model  
- `app/schemas/story_chat.py` - Pydantic schemas for chat API

### Services & Logic
- `app/services/story_chat_service.py` - Complete chat service with AI integration
- `app/services/story_service.py` - Extended with Basic/Advanced logic and upgrade mechanism
- `app/services/mixins.py` - ShadowWorldMixin for shadow world operations

### API & WebSocket Endpoints
- `app/routers/story_chat.py` - REST API and WebSocket endpoints for story chat
- `app/routers/story.py` - Added story upgrade endpoint
- `app/routers/basic_story.py` - Basic story creation endpoints

### AI Prompts (NEW)
- `app/prompts/story_chat/basic_story_chat.py` - Basic story chat prompts
- `app/prompts/story_chat/advanced_story_chat.py` - Advanced story chat prompts
- `app/prompts/basic_story/` - Directory with 14 Basic story AI prompt files

### Frontend & UI
- `app/static/js/story_chat.js` - Complete story chat interface JavaScript
- `app/static/css/story_chat.css` - Story chat interface styling
- `app/templates/pages/story_detail.html` - Added collapsible chat section
- `app/templates/partials/_navbar.html` - Updated with story creation dropdown
- `app/templates/pages/stories_list.html` - Enhanced with Basic/Advanced creation options
- `app/templates/pages/index.html` - Updated home page with story type selection

### Help Documentation (COMPREHENSIVE)
- `app/static/help/basic_story/basic_story_overview.html` - What are Basic Stories
- `app/static/help/basic_story/basic_story_creation.html` - How to create Basic Stories
- `app/static/help/basic_story/basic_story_writing.html` - Writing with Basic Stories
- `app/static/help/basic_story/basic_story_ai_features.html` - AI assistance features
- `app/static/help/basic_story/basic_story_chat.html` - Story chat capabilities
- `app/static/help/advanced_story/advanced_story_chat.html` - Advanced story chat features

### Main Help Files (UPDATED FOR BASIC/ADVANCED)
- `app/static/help/index.html` - Main help with Basic vs Advanced comparison and feature matrix
- `app/static/help/quick_start.html` - Updated with Basic (2 min) vs Advanced (30 min) paths
- `app/static/help/story_detail.html` - Updated with story type feature availability
- `app/static/help/act_editor.html` - Updated with AI assistance differentiation by story type

### Database Models Modified
- `app/models/story.py` - Added story_type field and chat_sessions relationship
- `app/models/world.py` - Added is_shadow field for shadow worlds
- `app/models/user.py` - Added story_chat_sessions relationship

## Summary

The Basic/Advanced Story system provides a **fully implemented** streamlined path for users to start writing immediately while preserving the full power of world-building for when they need it. The complete help documentation system has been updated to clearly show feature availability by story type. Key achievements:

### ✅ Core Features Delivered
- **Instant Story Creation**: Basic stories create with title → Act 1 → start writing
- **Shadow World System**: Transparent world management for Basic stories
- **Story Type Badges**: Visual differentiation throughout the entire UI
- **Upgrade Mechanism**: One-way Basic → Advanced story conversion
- **Publishing Parity**: Both story types have identical publishing capabilities

### ✅ Story Chat System
- **Real-time AI Conversations**: WebSocket-based chat about story development
- **Context-Aware AI**: Different prompts and context for Basic vs Advanced stories
- **Full Content Access**: AI receives complete story content for better assistance
- **Session Management**: Organized chat sessions with focus areas
- **Cost Tracking**: All AI interactions logged and tracked

### ✅ User Experience
- **Progressive Disclosure**: Simple start with upgrade path to advanced features
- **Visual Clarity**: Clear indicators and badges throughout the interface
- **Unified Navigation**: Seamless experience mixing both story types
- **Comprehensive Help**: Context-aware help system for all features

### ✅ Technical Architecture
- **Integrated Codebase**: Enhanced existing systems rather than separate implementations
- **Scalable Design**: WebSocket infrastructure supports future chat features
- **Cost Management**: Full AI call logging and cost tracking maintained
- **Feature Flags**: Story type controls feature availability dynamically

The system successfully delivers on the goal of providing immediate writing access for new users while maintaining full power for experienced users, with the addition of sophisticated AI chat capabilities for story development discussions.
