# Business Logic Layer and Service Boundaries

## Table of Contents
- [Business Logic Architecture](#business-logic-architecture)
- [Story Management System](#story-management-system)
- [World Building System](#world-building-system)
- [Content Generation Services](#content-generation-services)
- [Community Features](#community-features)
- [Billing and Administration](#billing-and-administration)
- [Service Boundaries and Integration](#service-boundaries-and-integration)

## Business Logic Architecture

The business logic layer implements the core domain functionality of the storytelling platform, organized into distinct service boundaries with clear responsibilities and well-defined interfaces.

### Service Architecture Overview

```mermaid
graph TB
    subgraph "API Layer"
        ROUTERS[API Routers]
    end
    
    subgraph "Business Logic Services"
        STORY_SVC[Story Management Service]
        WORLD_SVC[World Building Service]
        CONTENT_SVC[Content Generation Service]
        COMMUNITY_SVC[Community Service]
        BILLING_SVC[Billing Service]
        ADMIN_SVC[Administration Service]
    end
    
    subgraph "CRUD Layer"
        STORY_CRUD[Story CRUD]
        WORLD_CRUD[World CRUD]
        CHARACTER_CRUD[Character CRUD]
        LOCATION_CRUD[Location CRUD]
        LORE_CRUD[Lore CRUD]
        USER_CRUD[User CRUD]
        FORUM_CRUD[Forum CRUD]
        BILLING_CRUD[Billing CRUD]
    end
    
    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        SEARCH[Azure AI Search]
        BLOB[Azure Blob Storage]
    end
    
    %% Connections
    ROUTERS --> STORY_SVC
    ROUTERS --> WORLD_SVC
    ROUTERS --> CONTENT_SVC
    ROUTERS --> COMMUNITY_SVC
    ROUTERS --> BILLING_SVC
    ROUTERS --> ADMIN_SVC
    
    STORY_SVC --> STORY_CRUD
    WORLD_SVC --> WORLD_CRUD
    WORLD_SVC --> CHARACTER_CRUD
    WORLD_SVC --> LOCATION_CRUD
    WORLD_SVC --> LORE_CRUD
    CONTENT_SVC --> STORY_CRUD
    CONTENT_SVC --> WORLD_CRUD
    COMMUNITY_SVC --> FORUM_CRUD
    COMMUNITY_SVC --> USER_CRUD
    BILLING_SVC --> BILLING_CRUD
    
    STORY_CRUD --> POSTGRES
    WORLD_CRUD --> POSTGRES
    CHARACTER_CRUD --> POSTGRES
    LOCATION_CRUD --> POSTGRES
    LORE_CRUD --> POSTGRES
    USER_CRUD --> POSTGRES
    FORUM_CRUD --> POSTGRES
    BILLING_CRUD --> POSTGRES
    
    CONTENT_SVC --> SEARCH
    CONTENT_SVC --> BLOB
    
    %% Styling
    classDef api fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef business fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef crud fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class ROUTERS api
    class STORY_SVC,WORLD_SVC,CONTENT_SVC,COMMUNITY_SVC,BILLING_SVC,ADMIN_SVC business
    class STORY_CRUD,WORLD_CRUD,CHARACTER_CRUD,LOCATION_CRUD,LORE_CRUD,USER_CRUD,FORUM_CRUD,BILLING_CRUD crud
    class POSTGRES,SEARCH,BLOB data
```

### Service Design Principles

#### Domain-Driven Design
- **Bounded Contexts**: Each service represents a distinct business domain
- **Aggregate Roots**: Clear entity hierarchies and ownership
- **Domain Events**: Asynchronous communication between services
- **Ubiquitous Language**: Consistent terminology across service boundaries

#### Service Responsibilities
- **Single Responsibility**: Each service has one primary business purpose
- **High Cohesion**: Related functionality grouped together
- **Loose Coupling**: Minimal dependencies between services
- **Interface Segregation**: Clean, focused service interfaces

## Story Management System

### Service Boundaries

The Story Management System handles all aspects of story creation, organization, and lifecycle management.

#### Core Responsibilities
- **Story CRUD Operations**: Create, read, update, delete stories
- **Story Structure Management**: Acts, scenes, and narrative organization
- **Story Publishing**: Public story sharing and distribution
- **Story Associations**: Links to world elements (characters, locations, lore)
- **Story Metadata**: Tags, categories, and classification

### Story Service Architecture

```mermaid
graph TB
    subgraph "Story Management Service"
        STORY_API[Story API Router]
        BASIC_STORY_API[Basic Story API Router]
        STORY_ACT_API[Story Act API Router]
        SCENE_API[Scene API Router]
        PUBLISHED_API[Published Stories API]
    end
    
    subgraph "Story CRUD Operations"
        STORY_CRUD[Story CRUD<br/>- create_story<br/>- get_story_for_user<br/>- update_story<br/>- delete_story]
        ACT_CRUD[Act CRUD<br/>- create_act<br/>- get_acts_by_story<br/>- update_act<br/>- delete_act]
        SCENE_CRUD[Scene CRUD<br/>- create_scene<br/>- create_multiple_scenes<br/>- update_scene<br/>- delete_scene]
        PUBLISHED_CRUD[Published Story CRUD<br/>- create_published_story<br/>- get_published_stories<br/>- update_published_story]
    end
    
    subgraph "Story Data Models"
        STORY_MODEL[Story Model<br/>- title, description<br/>- world_id, user_id<br/>- story_class_id<br/>- current_image_id]
        ACT_MODEL[Act Model<br/>- title, description<br/>- story_id, act_number<br/>- narrative_text<br/>- metadata]
        SCENE_MODEL[Scene Model<br/>- title, description<br/>- act_id, scene_number<br/>- narrative_text<br/>- metadata]
        PUBLISHED_MODEL[Published Story Model<br/>- story_id, user_id<br/>- published_at<br/>- view_count, rating]
    end
    
    %% Connections
    STORY_API --> STORY_CRUD
    BASIC_STORY_API --> STORY_CRUD
    STORY_ACT_API --> ACT_CRUD
    SCENE_API --> SCENE_CRUD
    PUBLISHED_API --> PUBLISHED_CRUD
    
    STORY_CRUD --> STORY_MODEL
    ACT_CRUD --> ACT_MODEL
    SCENE_CRUD --> SCENE_MODEL
    PUBLISHED_CRUD --> PUBLISHED_MODEL
    
    %% Styling
    classDef api fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef crud fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef model fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class STORY_API,BASIC_STORY_API,STORY_ACT_API,SCENE_API,PUBLISHED_API api
    class STORY_CRUD,ACT_CRUD,SCENE_CRUD,PUBLISHED_CRUD crud
    class STORY_MODEL,ACT_MODEL,SCENE_MODEL,PUBLISHED_MODEL model
```

### Story Management Patterns

#### Story Creation Flow
```python
async def create_story(db: AsyncSession, story: StoryCreate, user_id: int) -> Story:
    logger.info(f"User ID {user_id} creating new story: '{story.title}', linking to world_id: {story.world_id}")
    db_story = Story(**story.model_dump(), user_id=user_id)
    db.add(db_story)
    await db.flush()
    await db.refresh(db_story, attribute_names=['OwnerUser', 'world', 'published_version'])
    return db_story
```

#### Hierarchical Structure Management
- **Story → Acts → Scenes**: Three-level hierarchy with automatic numbering
- **Association Management**: Links to world elements through association tables
- **Metadata Tracking**: Creation timestamps, modification history, user ownership

#### Story Publishing Workflow
1. **Content Validation**: Ensure story meets publishing requirements
2. **File Generation**: Create downloadable formats (PDF, EPUB)
3. **Blob Storage**: Upload generated files to Azure Blob Storage
4. **Public Index**: Add to published stories catalog
5. **Analytics Tracking**: Monitor views, ratings, and engagement

## World Building System

### Service Architecture

The World Building System manages the creation and organization of fictional universes with their constituent elements.

#### Core Components
- **World Management**: World creation, settings, and organization
- **Character System**: Character profiles, relationships, and development
- **Location System**: Geographic and spatial organization
- **Lore Management**: History, mythology, and world knowledge
- **World Associations**: Cross-references between world elements

### World Service Components

```mermaid
graph TB
    subgraph "World Building APIs"
        WORLD_API[World API Router]
        CHARACTER_API[Character API Router]
        LOCATION_API[Location API Router]
        LORE_API[Lore Item API Router]
        WORLD_IMPORTER[World Importer API]
        WORLD_BUILDER[World Builder API]
    end
    
    subgraph "World CRUD Layer"
        WORLD_CRUD[World CRUD<br/>- create_world<br/>- get_world_for_user<br/>- update_world<br/>- delete_world]
        CHARACTER_CRUD[Character CRUD<br/>- create_character<br/>- get_characters_by_world<br/>- update_character<br/>- generate_backstory]
        LOCATION_CRUD[Location CRUD<br/>- create_location<br/>- get_locations_by_world<br/>- create_location_connection<br/>- update_location]
        LORE_CRUD[Lore CRUD<br/>- create_lore_item<br/>- get_lore_by_world<br/>- update_lore_item<br/>- delete_lore_item]
    end
    
    subgraph "Background Processing"
        RAG_PROCESSOR[RAG Text Processor<br/>- generate_and_index_world_element_rag_text_task<br/>- convert_to_rag_text<br/>- index_in_search]
        IMAGE_PROCESSOR[Image Processor<br/>- generate_character_image<br/>- generate_location_image<br/>- process_async]
    end
    
    %% Connections
    WORLD_API --> WORLD_CRUD
    CHARACTER_API --> CHARACTER_CRUD
    LOCATION_API --> LOCATION_CRUD
    LORE_API --> LORE_CRUD
    WORLD_IMPORTER --> WORLD_CRUD
    WORLD_BUILDER --> WORLD_CRUD
    
    CHARACTER_CRUD --> RAG_PROCESSOR
    LOCATION_CRUD --> RAG_PROCESSOR
    LORE_CRUD --> RAG_PROCESSOR
    
    CHARACTER_CRUD --> IMAGE_PROCESSOR
    LOCATION_CRUD --> IMAGE_PROCESSOR
    
    %% Styling
    classDef api fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef crud fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef processor fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class WORLD_API,CHARACTER_API,LOCATION_API,LORE_API,WORLD_IMPORTER,WORLD_BUILDER api
    class WORLD_CRUD,CHARACTER_CRUD,LOCATION_CRUD,LORE_CRUD crud
    class RAG_PROCESSOR,IMAGE_PROCESSOR processor
```

### World Building Patterns

#### World Element Creation Pattern
```python
async def create_character(
    db: AsyncSession, 
    character_in: CharacterCreate, 
    world_id: int,
    user_id: int, 
    background_tasks: BackgroundTasks,
    model_config_id: Optional[int] = None
) -> Character:
    # Create character entity
    db_character = Character(**character_in.model_dump(), world_id=world_id)
    db.add(db_character)
    await db.flush()
    await db.commit()
    
    # Schedule background processing
    background_tasks.add_task(
        generate_and_index_world_element_rag_text_task,
        character_id=db_character.id,
        model_config_id=model_config_id
    )
    
    return db_character
```

#### Background Processing Integration
- **RAG Text Generation**: Convert world elements to searchable text
- **Vector Indexing**: Add to AI search index for RAG operations
- **Image Generation**: Create visual representations asynchronously
- **Cross-Reference Updates**: Update related elements and associations

## Content Generation Services

### AI-Powered Content Creation

The Content Generation Services provide AI-assisted writing and creative tools throughout the platform.

#### Service Components
- **AI Assisted Writing**: Real-time writing assistance and suggestions
- **Scene Writing**: AI-powered scene generation and enhancement
- **Story Wizard**: Guided story creation with AI assistance
- **Image Generation**: Visual content creation for stories and worlds
- **Brainstorm Service**: Creative ideation and concept development

### Content Generation Architecture

```mermaid
graph TB
    subgraph "Content Generation APIs"
        AI_WRITING[AI Assisted Writing]
        AI_SCENE[AI Scene Writing]
        STORY_WIZARD[Story Wizard API]
        IMAGE_GEN[Image Generation API]
        BRAINSTORM[Brainstorm API]
    end
    
    subgraph "AI Services Integration"
        SK_PLUGINS[Semantic Kernel Plugins<br/>- Story Analysis<br/>- Storytelling<br/>- World Building<br/>- Structure Analysis]
        AI_CLIENTS[AI Client Factory<br/>- Azure OpenAI<br/>- OpenRouter<br/>- RunPod<br/>- OpenAI Direct]
        COST_TRACKING[Cost Tracking Service<br/>- Usage monitoring<br/>- Billing integration<br/>- Token calculation]
    end
    
    subgraph "Content Processing"
        TEXT_PROCESSOR[Text Processing<br/>- Chunking<br/>- Embedding generation<br/>- RAG indexing]
        IMAGE_PROCESSOR[Image Processing<br/>- Generation requests<br/>- Storage management<br/>- Metadata tracking]
        ASYNC_JOBS[Async Job Processing<br/>- Background tasks<br/>- Job status tracking<br/>- Error handling]
    end
    
    %% Connections
    AI_WRITING --> SK_PLUGINS
    AI_SCENE --> SK_PLUGINS
    STORY_WIZARD --> SK_PLUGINS
    IMAGE_GEN --> AI_CLIENTS
    BRAINSTORM --> SK_PLUGINS
    
    SK_PLUGINS --> AI_CLIENTS
    AI_CLIENTS --> COST_TRACKING
    
    AI_WRITING --> TEXT_PROCESSOR
    IMAGE_GEN --> IMAGE_PROCESSOR
    STORY_WIZARD --> ASYNC_JOBS
    
    %% Styling
    classDef api fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef ai fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef processing fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class AI_WRITING,AI_SCENE,STORY_WIZARD,IMAGE_GEN,BRAINSTORM api
    class SK_PLUGINS,AI_CLIENTS,COST_TRACKING ai
    class TEXT_PROCESSOR,IMAGE_PROCESSOR,ASYNC_JOBS processing
```

### Content Generation Patterns

#### AI-Assisted Writing Flow
1. **Context Gathering**: Collect relevant story/world context
2. **RAG Retrieval**: Find relevant background information
3. **Prompt Construction**: Build context-aware prompts
4. **AI Generation**: Generate content using appropriate model
5. **Post-Processing**: Format and validate generated content
6. **Cost Tracking**: Log usage and update user balance

#### Async Content Generation
```python
# Background task pattern for long-running operations
background_tasks.add_task(
    generate_and_process_content,
    content_type="character_backstory",
    entity_id=character.id,
    user_id=current_user.id,
    model_config_id=model_config.id
)
```

## Community Features

### Forum and Social System

The Community Features provide social interaction, discussion, and content sharing capabilities.

#### Core Components
- **Forum System**: Categories, threads, and posts
- **User Profiles**: Public profiles and activity tracking
- **Content Sharing**: Story publishing and discovery
- **Social Features**: Ratings, comments, and favorites
- **Moderation Tools**: Content moderation and user management

### Community Service Architecture

```mermaid
graph TB
    subgraph "Community APIs"
        FORUM_CAT[Forum Categories API]
        FORUM_THREAD[Forum Threads API]
        FORUM_POST[Forum Posts API]
        PUBLISHED[Published Stories API]
        SOCIAL[Social Sharing API]
        PUBLIC_CHAT[Public World Chat API]
    end
    
    subgraph "Community CRUD"
        FORUM_CRUD[Forum CRUD<br/>- create_forum_category<br/>- create_forum_thread<br/>- create_forum_post<br/>- vote_on_post]
        PUBLISHED_CRUD[Published Story CRUD<br/>- create_published_story<br/>- get_published_stories<br/>- rate_story<br/>- comment_on_story]
        SOCIAL_CRUD[Social CRUD<br/>- create_social_share<br/>- track_engagement<br/>- update_analytics]
    end
    
    subgraph "Community Features"
        MODERATION[Content Moderation<br/>- Automated filtering<br/>- User reporting<br/>- Admin tools]
        ANALYTICS[Community Analytics<br/>- Engagement tracking<br/>- Popular content<br/>- User activity]
        NOTIFICATIONS[Notification System<br/>- Forum subscriptions<br/>- Content updates<br/>- Social interactions]
    end
    
    %% Connections
    FORUM_CAT --> FORUM_CRUD
    FORUM_THREAD --> FORUM_CRUD
    FORUM_POST --> FORUM_CRUD
    PUBLISHED --> PUBLISHED_CRUD
    SOCIAL --> SOCIAL_CRUD
    PUBLIC_CHAT --> FORUM_CRUD
    
    FORUM_CRUD --> MODERATION
    PUBLISHED_CRUD --> ANALYTICS
    SOCIAL_CRUD --> NOTIFICATIONS
    
    %% Styling
    classDef api fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef crud fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef features fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    
    class FORUM_CAT,FORUM_THREAD,FORUM_POST,PUBLISHED,SOCIAL,PUBLIC_CHAT api
    class FORUM_CRUD,PUBLISHED_CRUD,SOCIAL_CRUD crud
    class MODERATION,ANALYTICS,NOTIFICATIONS features
```

## Billing and Administration

### Billing Service Architecture

The Billing Service manages user accounts, credits, transactions, and usage tracking.

#### Core Responsibilities
- **User Account Management**: Credit balances and account status
- **Transaction Processing**: Credit purchases and usage deductions
- **Cost Tracking**: AI usage monitoring and billing
- **Package Management**: Credit packages and pricing
- **Admin Tools**: Billing administration and reporting

### Billing Service Components

```python
class BillingService:
    """Comprehensive billing service for user account and transaction management."""
    
    async def get_or_create_user_account(self, db: AsyncSession, user_id: int) -> UserAccount:
        """Get existing account or create new one with default balance."""
        
    async def create_transaction(self, db: AsyncSession, transaction_data: UserTransactionCreate) -> UserTransaction:
        """Create transaction and update account balance."""
        
    async def deduct_credits(self, db: AsyncSession, user_id: int, amount: float, description: str) -> bool:
        """Deduct credits from user account with validation."""
        
    async def get_user_balance(self, db: AsyncSession, user_id: int) -> float:
        """Get current user credit balance."""
```

### Administrative Services

#### Admin Service Boundaries
- **User Management**: Account administration and user support
- **Content Moderation**: Content review and policy enforcement
- **System Monitoring**: Performance metrics and health checks
- **Billing Administration**: Transaction management and reporting
- **Maintenance Tools**: System maintenance and configuration

## Service Boundaries and Integration

### Inter-Service Communication Patterns

#### Direct Database Access
```python
# Services access data through CRUD layer
story_service = StoryService()
world_service = WorldService()

# Story service can access world data for validation
world = await world_service.get_world_for_user(db, world_id, user_id)
if world:
    story = await story_service.create_story(db, story_data, user_id)
```

#### Event-Driven Integration
```python
# Background tasks for async processing
background_tasks.add_task(
    update_related_content,
    entity_type="character",
    entity_id=character.id,
    change_type="created"
)
```

#### Shared Utilities and Dependencies
- **Authentication**: Shared user authentication across all services
- **Database Sessions**: Common database session management
- **Error Handling**: Consistent error handling patterns
- **Logging**: Centralized logging and monitoring
- **Configuration**: Shared configuration management

### Service Integration Principles

#### Loose Coupling
- Services communicate through well-defined interfaces
- Minimal direct dependencies between service implementations
- Async processing for non-critical cross-service operations

#### Data Consistency
- Transactional boundaries within individual services
- Eventual consistency for cross-service operations
- Compensation patterns for distributed transactions

#### Error Isolation
- Service failures don't cascade to other services
- Graceful degradation when dependencies are unavailable
- Circuit breaker patterns for external service calls

---
**Document Information:**
- Last Updated: 2025-07-14
- Version: 1.0.0
- Author: Architecture Team
- Reviewers: Business Logic Team