# Backend Storytelling Architecture Document

## 1. Overview

The Backend Storytelling architecture provides the core creative authoring platform. It manages worlds, stories, acts, scenes, characters, locations, lore, brainstorming sessions, and story publishing. The system supports two story types:
- **Basic Stories**: Simple story creation focused on writing (acts, scenes, content).
- **Advanced Stories**: Full world-building with characters, locations, lore, and AI-assisted generation.

### Key Characteristics
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (async via SQLAlchemy)
- **ORM**: SQLAlchemy 2.0 (async)
- **AI Integration**: Semantic Kernel (Microsoft) for story generation, brainstorming, and writing assistance
- **Architecture**: Router → Service → CRUD → Model layers
- **Testing**: pytest (unit + integration)

### Accuracy Review
- Reviewed against the active storytelling/router surface in `app/routers/`, including:
  - `story.py`, `basic_stories.py`, `brainstorm.py`
  - `world.py`, `world_builder.py`, `world_importer.py`
  - `character.py`, `location.py`, `lore_item.py`
  - `scene.py`, `act.py`, `published_stories.py`
  - `ai_assisted_writing.py`, `ai_scene_writing.py`, `ai_text_transform.py`
- The domain and route breadth described here are broadly accurate.
- The AI stack line should be treated cautiously: the repository contains multiple AI-related router and service paths, and this document should not be read as proof that Semantic Kernel is the exclusive or universal runtime path for all storytelling generation.
- Use this document as a map of the storytelling domain, then confirm exact behavior in the active routers and services before making contract changes.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Backend Storytelling                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Story Management                              │   │
│  │                                                                      │   │
│  │  POST   /api/v1/stories/                                             │   │
│  │  GET    /api/v1/stories/                                             │   │
│  │  GET    /api/v1/stories/{story_id}                                   │   │
│  │  PUT    /api/v1/stories/{story_id}                                   │   │
│  │  DELETE /api/v1/stories/{story_id}                                   │   │
│  │  POST   /api/v1/stories/{story_id}/publish                           │   │
│  │  GET    /api/v1/stories/{story_id}/images                            │   │
│  │  POST   /api/v1/stories/{story_id}/set-current-image/{image_id}      │   │
│  │  POST   /api/v1/stories/{story_id}/upgrade                           │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        World Management                              │   │
│  │                                                                      │   │
│  │  POST   /api/v1/worlds/                                              │   │
│  │  GET    /api/v1/worlds/                                              │   │
│  │  GET    /api/v1/worlds/has-non-shadow-worlds                         │   │
│  │  GET    /api/v1/worlds/{world_id}                                    │   │
│  │  PUT    /api/v1/worlds/{world_id}                                    │   │
│  │  DELETE /api/v1/worlds/{world_id}                                    │   │
│  │  GET    /api/v1/worlds/{world_id}/stories                            │   │
│  │  GET    /api/v1/worlds/{world_id}/images                             │   │
│  │  POST   /api/v1/worlds/{world_id}/set-current-image/{image_id}       │   │
│  │  POST   /api/v1/worlds/{world_id}/stories/generate                   │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Act & Scene Management                        │   │
│  │                                                                      │   │
│  │  POST   /api/v1/stories/{story_id}/acts                              │   │
│  │  GET    /api/v1/stories/{story_id}/acts                              │   │
│  │  GET    /api/v1/acts/{act_id}                                        │   │
│  │  PUT    /api/v1/acts/{act_id}                                        │   │
│  │  DELETE /api/v1/acts/{act_id}                                        │   │
│  │  POST   /api/v1/acts/{act_id}/scenes                                 │   │
│  │  GET    /api/v1/acts/{act_id}/scenes                                 │   │
│  │  GET    /api/v1/scenes/{scene_id}                                    │   │
│  │  PUT    /api/v1/scenes/{scene_id}                                    │   │
│  │  DELETE /api/v1/scenes/{scene_id}                                    │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        World Elements (Characters, Locations, Lore)  │   │
│  │                                                                      │   │
│  │  POST   /api/v1/worlds/{world_id}/characters                         │   │
│  │  GET    /api/v1/worlds/{world_id}/characters                         │   │
│  │  POST   /api/v1/worlds/{world_id}/locations                          │   │
│  │  GET    /api/v1/worlds/{world_id}/locations                          │   │
│  │  POST   /api/v1/worlds/{world_id}/lore                               │   │
│  │  GET    /api/v1/worlds/{world_id}/lore                               │   │
│  │  POST   /api/v1/stories/{story_id}/characters                        │   │
│  │  POST   /api/v1/stories/{story_id}/locations                         │   │
│  │  POST   /api/v1/stories/{story_id}/lore                              │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Brainstorm & Story Generation                 │   │
│  │                                                                      │   │
│  │  GET    /ui/brainstorm/                                              │   │
│  │  GET    /ui/brainstorm/api/sessions                                  │   │
│  │  GET    /ui/brainstorm/api/favorites                                 │   │
│  │  POST   /ui/brainstorm/api/generate-concepts                        │   │
│  │  POST   /ui/brainstorm/api/save-favorite                            │   │
│  │  POST   /ui/brainstorm/api/create-story                              │   │
│  │  POST   /api/v1/worlds/{world_id}/stories/generate                   │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│            ┌────────────────────┼────────────────────┐                      │
│            ▼                    ▼                    ▼                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐       │
│  │  Service Layer  │  │  CRUD Layer     │  │  Model Layer         │       │
│  │                 │  │                 │  │                      │       │
│  │  StoryService   │  │  story          │  │  - Story             │       │
│  │  WorldService   │  │  world          │  │  - World             │       │
│  │  ActService     │  │  act            │  │  - Act               │       │
│  │  SceneService   │  │  scene          │  │  - Scene             │       │
│  │  CharacterSvc   │  │  character      │  │  - Character         │       │
│  │  LocationSvc    │  │  location       │  │  - Location          │       │
│  │  LoreSvc        │  │  lore_item      │  │  - LoreItem          │       │
│  │  BrainstormSvc  │  │  brainstorm     │  │  - BrainstormSession │       │
│  │  GenerationSvc  │  │  associations   │  │  - BrainstormFavorite│       │
│  │  PublishingSvc  │  │  published_story│  │  - PublishedStory    │       │
│  │  ImageService   │  │  generated_image│  │  - GeneratedImage    │       │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘       │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        AI Integration                                │   │
│  │                                                                      │   │
│  │  - Semantic Kernel (story generation, brainstorming, writing)        │   │
│  │  - AI Model Cache (model configurations)                             │   │
│  │  - Cost Tracker (token usage, billing)                               │   │
│  │  - Image Generation (DALL-E 3, RunPod)                               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. API Endpoints

### 3.1 Story Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/stories/` | User | Create new story |
| GET | `/api/v1/stories/` | User | List user's stories |
| GET | `/api/v1/stories/{story_id}` | User | Get single story |
| PUT | `/api/v1/stories/{story_id}` | User | Update story |
| DELETE | `/api/v1/stories/{story_id}` | User | Delete story |
| POST | `/api/v1/stories/{story_id}/publish` | User | Publish story to HTML |
| GET | `/api/v1/stories/{story_id}/images` | User | List story images |
| POST | `/api/v1/stories/{story_id}/set-current-image/{image_id}` | User | Set current story image |
| POST | `/api/v1/stories/{story_id}/upgrade` | User | Upgrade basic to advanced |

### 3.2 World Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/worlds/` | User | Create new world |
| GET | `/api/v1/worlds/` | User | List user's worlds |
| GET | `/api/v1/worlds/has-non-shadow-worlds` | User | Check if user has worlds |
| GET | `/api/v1/worlds/{world_id}` | User | Get world details |
| PUT | `/api/v1/worlds/{world_id}` | User | Update world |
| DELETE | `/api/v1/worlds/{world_id}` | User | Delete world |
| GET | `/api/v1/worlds/{world_id}/stories` | User | List stories in world |
| GET | `/api/v1/worlds/{world_id}/images` | User | List world images |
| POST | `/api/v1/worlds/{world_id}/set-current-image/{image_id}` | User | Set current world image |
| POST | `/api/v1/worlds/{world_id}/stories/generate` | User | Generate story from world |

### 3.3 Act & Scene Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/stories/{story_id}/acts` | User | Create act |
| GET | `/api/v1/stories/{story_id}/acts` | User | List story acts |
| GET | `/api/v1/acts/{act_id}` | User | Get act |
| PUT | `/api/v1/acts/{act_id}` | User | Update act |
| DELETE | `/api/v1/acts/{act_id}` | User | Delete act |
| POST | `/api/v1/acts/{act_id}/scenes` | User | Create scene |
| GET | `/api/v1/acts/{act_id}/scenes` | User | List act scenes |
| GET | `/api/v1/scenes/{scene_id}` | User | Get scene |
| PUT | `/api/v1/scenes/{scene_id}` | User | Update scene |
| DELETE | `/api/v1/scenes/{scene_id}` | User | Delete scene |

### 3.4 World Elements

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/worlds/{world_id}/characters` | User | Create character |
| GET | `/api/v1/worlds/{world_id}/characters` | User | List world characters |
| POST | `/api/v1/worlds/{world_id}/locations` | User | Create location |
| GET | `/api/v1/worlds/{world_id}/locations` | User | List world locations |
| POST | `/api/v1/worlds/{world_id}/lore` | User | Create lore item |
| GET | `/api/v1/worlds/{world_id}/lore` | User | List world lore items |

### 3.5 Brainstorm & Story Generation

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/ui/brainstorm/` | Optional | Brainstorm page |
| GET | `/ui/brainstorm/api/sessions` | User | Get brainstorm sessions |
| GET | `/ui/brainstorm/api/favorites` | User | Get brainstorm favorites |
| POST | `/ui/brainstorm/api/generate-concepts` | User | Generate story concepts |
| POST | `/ui/brainstorm/api/save-favorite` | User | Save favorite concept |
| POST | `/ui/brainstorm/api/create-story` | User | Create story from favorite |
| POST | `/api/v1/worlds/{world_id}/stories/generate` | User | Generate story from world |

---

## 4. Data Model

### 4.1 Story Model

```python
class Story(Base):
    __tablename__ = "stories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    short_description: Mapped[Optional[str]] = mapped_column(Text)
    story_type: Mapped[str] = mapped_column(String(50))  # 'basic' or 'advanced'
    story_genre: Mapped[Optional[str]] = mapped_column(String(100))
    story_tone: Mapped[Optional[str]] = mapped_column(String(100))
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    current_image_id: Mapped[Optional[int]] = mapped_column(Integer)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.2 World Model

```python
class World(Base):
    __tablename__ = "worlds"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))
    is_free_chat_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    image_prompt_definition: Mapped[Optional[str]] = mapped_column(Text)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(500))
    current_image_id: Mapped[Optional[int]] = mapped_column(Integer)
    is_shadow: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.3 Act Model

```python
class Act(Base):
    __tablename__ = "acts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    act_number: Mapped[int] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    act_summary: Mapped[Optional[str]] = mapped_column(Text)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(500))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.4 Scene Model

```python
class Scene(Base):
    __tablename__ = "scenes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    scene_number: Mapped[int] = mapped_column(Integer)
    content: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text)
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(500))
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.5 Character Model

```python
class Character(Base):
    __tablename__ = "characters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    character_type: Mapped[Optional[str]] = mapped_column(String(50))
    image_blob_path: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.6 Brainstorm Session Model

```python
class BrainstormSession(Base):
    __tablename__ = "brainstorm_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_name: Mapped[str] = mapped_column(String(255))
    concepts: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 4.7 Brainstorm Favorite Model

```python
class BrainstormFavorite(Base):
    __tablename__ = "brainstorm_favorites"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_id: Mapped[int] = mapped_column(ForeignKey("brainstorm_sessions.id", ondelete="CASCADE"))
    concept_id: Mapped[str] = mapped_column(String(100))
    concept_data: Mapped[dict] = mapped_column(JSON)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 4.8 Published Story Model

```python
class PublishedStory(Base):
    __tablename__ = "published_stories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id", ondelete="CASCADE"), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    published_url: Mapped[str] = mapped_column(String(500))
    filename: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.9 Generated Image Model

```python
class GeneratedImage(Base):
    __tablename__ = "generated_images"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    element_type: Mapped[str] = mapped_column(String(50))  # 'story', 'world', 'act', 'scene', 'character'
    associated_element_id: Mapped[int] = mapped_column(Integer)
    prompt: Mapped[str] = mapped_column(Text)
    revised_prompt: Mapped[Optional[str]] = mapped_column(Text)
    blob_path: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

---

## 5. Service Architecture

### 5.1 StoryService

```python
class StoryService:
    async def upgrade_story_to_advanced(db, story_id, user, world_id) -> ApiResponse:
        """Upgrade a Basic Story to Advanced with world-building features"""
```

### 5.2 StoryGenerationService

```python
class StoryGenerationService:
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def generate_story_from_world(world: World, request: StoryGenerationRequest) -> StoryGenerationResponse:
        """Generate a story from selected world elements"""
    
    async def _validate_elements(world_id, element_ids) -> bool:
        """Validate selected elements belong to world"""
    
    async def _generate_story_outline(elements, user_preferences) -> Dict:
        """Generate story outline using AI"""
    
    async def _create_story_and_elements(outline, world, user) -> Story:
        """Create story, acts, scenes in database"""
```

### 5.3 StoryBrainstormService

```python
class StoryBrainstormService:
    async def generate_story_concepts(user, interview_response_id, db) -> Dict:
        """Generate 15 story concepts based on interview responses"""
    
    async def save_favorite_concept(user, session_id, concept_id, db) -> BrainstormFavorite:
        """Save a story concept as favorite"""
    
    async def remove_favorite_concept(user, favorite_id, db) -> bool:
        """Remove a concept from favorites"""
    
    async def generate_three_act_story(user, favorite_id, db) -> Dict:
        """Generate three-act story structure from favorite concept"""
```

### 5.4 WorldContextLoader

```python
class WorldContextLoader:
    async def load_full_world_context(world_id, user_id) -> Dict[str, Any]:
        """Load complete world context for AI"""
```

---

## 6. Publishing Flow

```
publish_story_to_html(story_id, request)
    │
    ├── Verify story ownership
    │
    ├── Get all acts for story
    │   └── Return 400 if no acts
    │
    ├── Build HTML document
    │   ├── HTML head with styles
    │   ├── Story title and description
    │   ├── Story AI summary
    │   ├── Story image (if available)
    │   ├── Story-level elements (characters, locations, lore)
    │   └── For each act:
    │       ├── Act title and description
    │       ├── Act image (if available)
    │       ├── Act writer's intent
    │       ├── Act AI summary
    │       ├── Act-level elements
    │       └── For each scene:
    │           ├── Scene title
    │           ├── Scene image (if available)
    │           ├── Scene-level elements
    │           ├── Writer's intent
    │           ├── AI summary
    │           └── Scene content
    │
    ├── Save HTML to local storage
    │
    ├── Calculate word count
    │
    ├── Save/update PublishedStory record
    │
    ├── Send publication email
    │
    └── Return published URL
```

---

## 7. Unit Tests

### 7.1 Existing Tests

| Test File | Coverage |
|-----------|----------|
| `tests/test_stories_crud_complete.py` | Story CRUD operations |
| `tests/unit/story/test_act_ai_review_unit.py` | Act AI review unit tests |
| `tests/unit/story/test_act_router_unit.py` | Act router unit tests |
| `tests/unit/story/test_basic_story_interview_importer_unit.py` | Basic story interview |
| `tests/unit/story/test_story_and_ai_text_transform_unit.py` | Story + AI text transform |
| `tests/unit/story/test_users_prompt_world_storyclass_unit.py` | Users, prompts, world, story class |
| `tests/unit/story/test_welcome_interview_bonus_unit.py` | Welcome interview bonus |
| `tests/integration/story/test_batch_association_graph_integration.py` | Batch association graph |
| `tests/integration/story/test_world_builder_integration.py` | World builder integration |
| `tests/integration/story/test_world_content_integration.py` | World content integration |
| `tests/integration/story/test_world_story_flow_integration.py` | World-story flow integration |

### 7.2 Test Coverage Summary

| Area | Unit Tests | Integration Tests |
|------|------------|-------------------|
| Story CRUD | ✅ | ✅ |
| World CRUD | Partial | ✅ |
| Act CRUD | ✅ | Partial |
| Scene CRUD | Partial | Partial |
| Character CRUD | ❌ | Partial |
| Location CRUD | ❌ | Partial |
| Lore CRUD | ❌ | Partial |
| Story Publishing | ❌ | ❌ |
| Story Generation | ❌ | ❌ |
| Brainstorm | ❌ | ❌ |
| Image Generation | ❌ | Partial |
| Story Upgrade | ❌ | ❌ |

### 7.3 Recommended Additional Tests

```python
# tests/unit/story/test_story_service_unit.py
def test_upgrade_story_to_advanced_changes_type():
def test_upgrade_story_to_advanced_creates_world():
def test_upgrade_story_to_advanced_preserves_content():

# tests/unit/story/test_story_generation_service_unit.py
def test_generate_story_from_world_validates_elements():
def test_generate_story_from_world_creates_story():
def test_generate_story_from_world_returns_response():

# tests/unit/story/test_story_brainstorm_service_unit.py
def test_generate_story_concepts_returns_15_concepts():
def test_save_favorite_concept_creates_favorite():
def test_generate_three_act_story_creates_structure():

# tests/unit/story/test_publishing_unit.py
def test_publish_story_generates_html():
def test_publish_story_includes_acts_and_scenes():
def test_publish_story_calculates_word_count():
def test_publish_story_saves_to_storage():

# tests/unit/story/test_image_service_unit.py
def test_list_story_images_returns_images():
def test_set_current_story_image_updates_story():
def test_generate_image_creates_pending_record():
```

---

## 8. Integration Tests

### 8.1 Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Story Creation | Login → Create story → Verify | Story created with correct type |
| World Creation | Login → Create world → Verify | World created with user ownership |
| Story Publishing | Create story with acts → Publish → Verify URL | HTML file generated, URL returned |
| Story Generation | Create world → Select elements → Generate → Verify | Story created with acts/scenes |
| Brainstorm Flow | Complete interview → Generate concepts → Save favorite → Create story | Story created from concept |
| Story Upgrade | Create basic story → Upgrade → Verify advanced features | Story type changed, world created |

---

## 9. Suggestions and Improvements

### 9.1 Immediate Improvements
1. **Add Story Publishing Tests**: Test HTML generation, file saving, and email notification.
2. **Add Story Generation Tests**: Test element validation, AI integration, and story creation.
3. **Add Brainstorm Tests**: Test concept generation, favorite saving, and story creation.
4. **Add Image Generation Tests**: Test image creation, status tracking, and URL generation.

### 9.2 Architecture Improvements
1. **Implement Story Versioning**: Track story versions for rollback and comparison.
2. **Add Collaborative Editing**: Support multiple users editing the same story.
3. **Implement Story Templates**: Pre-configured story templates for different genres.
4. **Add Story Export**: Export stories as PDF, EPUB, or DOCX.

### 9.3 Testing Improvements
1. **Add Mock AI Services**: Use mock AI services for consistent testing.
2. **Add Load Tests**: Test story creation under concurrent user load.
3. **Add Publishing Tests**: Test HTML output validity and accessibility.
4. **Add Image Generation Tests**: Test image provider integration.

### 9.4 Performance Improvements
1. **Implement Story Caching**: Cache story data to reduce database queries.
2. **Add Batch Operations**: Support batch creation of acts, scenes, and elements.
3. **Optimize Publishing**: Use async file writing for large stories.
4. **Implement Lazy Loading**: Load story elements on demand.

### 9.5 Security Considerations
1. **Validate HTML Output**: Sanitize HTML to prevent XSS in published stories.
2. **Rate Limit Story Creation**: Prevent abuse with per-user rate limiting.
3. **Validate User Input**: Sanitize story content before saving.
4. **Secure File Storage**: Validate file paths and prevent directory traversal.

### 9.6 Scalability Considerations
1. **Horizontal Service Scaling**: Deploy story services independently.
2. **Database Read Replicas**: Route read queries to replicas.
3. **CDN for Published Stories**: Serve published stories via CDN.
4. **Async Image Generation**: Use Celery/Redis for async image generation.

### 9.7 Future Feature Ideas
1. **Real-time Collaboration**: Multi-user story editing with conflict resolution.
2. **AI Writing Assistant**: Inline AI suggestions while writing.
3. **Story Analytics**: Track writing progress, word count trends, and engagement.
4. **Story Marketplace**: Share and sell stories to other users.
5. **Audio Narration**: Text-to-speech for story playback.
6. **Interactive Stories**: Choose-your-own-adventure style branching.
7. **Story Translation**: Auto-translate stories to multiple languages.
8. **Reading Mode**: Distraction-free reading interface.
