# Backend Chatbot Architecture Document

## 1. Overview

The Backend Chatbot architecture provides conversational AI capabilities across two distinct contexts:
- **World Chat**: Authenticated users chat about their created worlds, characters, locations, and lore with AI assistance.
- **Public World Chat**: Anonymous and authenticated users can engage with pre-configured public worlds for free (with balance limits).
- **Story Chat**: Authenticated users chat about their stories with AI, discussing plot, characters, themes, and development ideas.

The chatbot backend is designed to be flexible, supporting both REST and WebSocket communication patterns, with full cost tracking and billing integration.

### Key Characteristics
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (async via SQLAlchemy)
- **ORM**: SQLAlchemy 2.0 (async)
- **Real-time**: WebSocket support for streaming responses
- **Architecture**: Router → Service → CRUD → Model layers
- **Testing**: pytest (unit + integration)

### Accuracy Review
- Reviewed against the active router set under `app/routers/`, especially:
  - `world_chat.py`
  - `public_world_chat.py`
  - `story_chat.py`
  - `ws_context_manager.py`
- The backend chatbot domain is real, but this document should be treated as a domain-level map rather than a line-by-line implementation contract.
- Current repository state supports both HTTP and WebSocket chat routes, but route details, request shapes, and supporting services should be verified against router code before using this document for implementation work.
- Cross-cutting concerns such as auth, billing, anonymous access, and cost tracking live in shared backend services and are not isolated into a single chatbot-only stack.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Backend Chatbot                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        World Chat (Authenticated)                    │   │
│  │                                                                      │   │
│  │  GET    /api/v1/world-chat/chat/samples                              │   │
│  │  POST   /api/v1/world-chat/sessions/{world_id}                       │   │
│  │  GET    /api/v1/world-chat/sessions/{world_id}                       │   │
│  │  GET    /api/v1/world-chat/sessions/{world_id}/{session_id}          │   │
│  │  POST   /api/v1/world-chat/sessions/{world_id}/{session_id}/messages │   │
│  │  DELETE /api/v1/world-chat/sessions/{world_id}/{session_id}          │   │
│  │  GET    /api/v1/world-chat/world-context/{world_id}                  │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Public World Chat (Anonymous + Auth)          │   │
│  │                                                                      │   │
│  │  GET    /public/chat/samples                                         │   │
│  │  GET    /public/worlds                                               │   │
│  │  GET    /public/worlds/{world_id}                                    │   │
│  │  POST   /public/worlds/{world_id}/chat                               │   │
│  │  POST   /public/chat/{session_id}/message                            │   │
│  │  GET    /public/chat/{session_id}/messages                           │   │
│  │  GET    /public/user/balance                                         │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Story Chat (Authenticated + WebSocket)        │   │
│  │                                                                      │   │
│  │  POST   /api/v1/story-chat/stories/{story_id}/sessions               │   │
│  │  GET    /api/v1/story-chat/stories/{story_id}/sessions               │   │
│  │  GET    /api/v1/story-chat/stories/{story_id}/sessions/{session_id}  │   │
│  │  DELETE /api/v1/story-chat/stories/{story_id}/sessions/{session_id}  │   │
│  │  WS     /api/v1/story-chat/ws/stories/{story_id}/sessions/{id}/chat  │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│            ┌────────────────────┼────────────────────┐                      │
│            ▼                    ▼                    ▼                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐       │
│  │  Service Layer  │  │  CRUD Layer     │  │  Model Layer         │       │
│  │                 │  │                 │  │                      │       │
│  │  WorldChatSvc   │  │  chat_session   │  │  - ChatSession       │       │
│  │  StoryChatSvc   │  │  chat_message   │  │  - ChatMessage       │       │
│  │  WorldContext   │  │  chat_sample    │  │  - StoryChatSession  │       │
│  │  AnonymousUser  │  │  world          │  │  - StoryChatMessage  │       │
│  │  Billing        │  │  character      │  │  - ChatSample        │       │
│  │                 │  │  location       │  │                      │       │
│  │                 │  │  lore_item      │  │                      │       │
│  └─────────────────┘  └─────────────────┘  └──────────────────────┘       │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        AI Integration                                │   │
│  │                                                                      │   │
│  │  - Semantic Kernel (Microsoft)                                       │   │
│  │  - AI Model Cache (model configurations)                             │   │
│  │  - Cost Tracker (token usage, billing)                               │   │
│  │  - Streaming responses (WebSocket)                                   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Anonymous User Flow                           │   │
│  │                                                                      │   │
│  │  1. Request arrives without auth cookie                              │   │
│  │  2. Generate browser fingerprint (MD5 of UA + headers)               │   │
│  │  3. Create anonymous user with IP + fingerprint                      │   │
│  │  4. Set anon_session and anon_user_id cookies (7 days)               │   │
│  │  5. Initialize balance (500 coins)                                   │   │
│  │  6. Check balance before each AI call                                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. API Endpoints

### 3.1 World Chat (Authenticated)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/world-chat/chat/samples` | User | Get chat sample suggestions |
| POST | `/api/v1/world-chat/sessions/{world_id}` | User | Create chat session for world |
| GET | `/api/v1/world-chat/sessions/{world_id}` | User | List chat sessions for world |
| GET | `/api/v1/world-chat/sessions/{world_id}/{session_id}` | User | Get session with messages |
| POST | `/api/v1/world-chat/sessions/{world_id}/{session_id}/messages` | User | Send message in session |
| DELETE | `/api/v1/world-chat/sessions/{world_id}/{session_id}` | User | Delete chat session |
| GET | `/api/v1/world-chat/world-context/{world_id}` | User | Get complete world context |

### 3.2 Public World Chat (Anonymous + Authenticated)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/public/chat/samples` | None | Get chat sample suggestions |
| GET | `/public/worlds` | None | Get public worlds list |
| GET | `/public/worlds/{world_id}` | None | Get world details |
| POST | `/public/worlds/{world_id}/chat` | Optional | Start chat session |
| POST | `/public/chat/{session_id}/message` | Optional | Send message |
| GET | `/public/chat/{session_id}/messages` | Optional | Get session messages |
| GET | `/public/user/balance` | None | Get anonymous user balance |

### 3.3 Story Chat (Authenticated + WebSocket)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/story-chat/stories/{story_id}/sessions` | User | Create story chat session |
| GET | `/api/v1/story-chat/stories/{story_id}/sessions` | User | List story chat sessions |
| GET | `/api/v1/story-chat/stories/{story_id}/sessions/{session_id}` | User | Get session with messages |
| DELETE | `/api/v1/story-chat/stories/{story_id}/sessions/{session_id}` | User | Delete story chat session |
| WS | `/api/v1/story-chat/ws/stories/{story_id}/sessions/{session_id}/chat` | User | WebSocket chat connection |

---

## 4. Data Model

### 4.1 Chat Session Model

```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("worlds.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.2 Chat Message Model

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    full_context: Mapped[Optional[Dict]] = mapped_column(JSON)
    element_type: Mapped[Optional[str]] = mapped_column(String(50))
    element_id: Mapped[Optional[int]] = mapped_column(Integer)
    cost_log_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_call_logs.id", ondelete="SET NULL"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 4.3 Story Chat Session Model

```python
class StoryChatSession(Base):
    __tablename__ = "story_chat_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    focus_area: Mapped[Optional[str]] = mapped_column(String(50))  # 'plot', 'characters', 'world', 'general'
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 4.4 Story Chat Message Model

```python
class StoryChatMessage(Base):
    __tablename__ = "story_chat_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("story_chat_sessions.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text)
    target_element: Mapped[Optional[str]] = mapped_column(String(50))
    target_element_id: Mapped[Optional[int]] = mapped_column(Integer)
    full_context: Mapped[Optional[Dict]] = mapped_column(JSON)
    story_context: Mapped[Optional[Dict]] = mapped_column(JSON)
    cost_log_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_call_logs.id", ondelete="SET NULL"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 4.5 Chat Sample Model

```python
class ChatSample(Base):
    __tablename__ = "chat_samples"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    prompt_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

---

## 5. Service Architecture

### 5.1 WorldChatService

```python
class WorldChatService:
    def __init__(self, db: AsyncSession, blob_service_client: LocalStorageClient = None):
        self.db = db
        self.blob_service_client = blob_service_client
    
    async def create_chat_session(self, world_id: int, user_id: int) -> int:
        """Create a new chat session for a world"""
    
    async def send_message(self, session_id: int, user_id: int, request: SendMessageRequest) -> SendMessageResponse:
        """Send a message and get AI response"""
    
    async def _load_world_context(self, world_id: int) -> WorldContextData:
        """Load world context for AI prompt"""
    
    async def _generate_ai_response(self, session_id: int, user_id: int, message: str, world_context: WorldContextData) -> str:
        """Generate AI response using Semantic Kernel"""
```

### 5.2 StoryChatService

```python
class StoryChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cost_tracker = CostTrackerService(db)
    
    async def create_session(self, story_id: int, user_id: int, session_data: StoryChatSessionCreate) -> StoryChatSessionRead:
        """Create a new story chat session"""
    
    async def get_sessions(self, story_id: int, user_id: int) -> List[StoryChatSessionRead]:
        """Get all chat sessions for a story"""
    
    async def get_session_with_messages(self, story_id: int, session_id: int, user_id: int) -> Optional[StoryChatSessionWithMessages]:
        """Get a chat session with all its messages"""
    
    async def delete_session(self, story_id: int, session_id: int, user_id: int) -> bool:
        """Delete a chat session"""
    
    async def send_message(self, story_id: int, session_id: int, user_id: int, request: SendStoryChatMessageRequest) -> AsyncGenerator[str, None]:
        """Send a message and get AI response (streaming)"""
    
    async def _load_story_context(self, story_id: int) -> Story:
        """Load complete story context"""
    
    async def _build_ai_context(self, story: Story, session: StoryChatSession, request: SendStoryChatMessageRequest) -> Dict[str, Any]:
        """Build comprehensive context for AI conversation"""
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt for story chat AI"""
    
    async def _stream_ai_response(self, kernel, messages, ai_config) -> AsyncGenerator[str, None]:
        """Stream AI response chunks"""
```

### 5.3 WorldContextLoader

```python
class WorldContextLoader:
    def __init__(self, db: AsyncSession, blob_service_client: LocalStorageClient):
        self.db = db
        self.blob_service_client = blob_service_client
    
    async def load_full_world_context(self, world_id: int, user_id: int) -> Dict[str, Any]:
        """Load complete world context for AI"""
    
    async def _load_characters(self, world_id: int) -> List[Dict]:
        """Load characters for world"""
    
    async def _load_locations(self, world_id: int) -> List[Dict]:
        """Load locations for world"""
    
    async def _load_lore_items(self, world_id: int) -> List[Dict]:
        """Load lore items for world"""
```

### 5.4 AnonymousUserService

```python
class AnonymousUserService:
    async def create_anonymous_user(self, db: AsyncSession, ip_address: str, browser_fingerprint: str, user_agent: str) -> Tuple[User, str]:
        """Create a new anonymous user"""
    
    async def is_anonymous_user(self, user: User) -> bool:
        """Check if user is anonymous"""
    
    def _generate_anonymous_username(self) -> str:
        """Generate a unique anonymous username"""
```

---

## 6. WebSocket Architecture

### 6.1 Connection Manager

```python
class StoryChatConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            self.active_connections.pop(connection_id)
    
    async def send_json_message(self, data: Dict, connection_id: str):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json(data)
    
    async def send_text_chunk(self, text: str, connection_id: str):
        """Send a text chunk for streaming responses"""
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_json({
                "type": "text_chunk",
                "content": text
            })
```

### 6.2 WebSocket Message Types

**Client → Server:**
```json
{
  "type": "send_message",
  "content": "What happens next in the story?",
  "target_element": "scene",
  "target_element_id": 42
}
```

```json
{
  "type": "ping"
}
```

**Server → Client:**
```json
{
  "type": "session_info",
  "session": {
    "id": 1,
    "title": "Plot Discussion",
    "focus_area": "plot",
    "story_title": "My Story"
  }
}
```

```json
{
  "type": "response_start"
}
```

```json
{
  "type": "text_chunk",
  "content": "The protagonist discovers..."
}
```

```json
{
  "type": "response_complete"
}
```

```json
{
  "type": "error",
  "message": "AI response error: ..."
}
```

```json
{
  "type": "pong"
}
```

### 6.3 WebSocket Authentication Flow

```
1. Client requests WebSocket ticket via GET /api/v1/auth/ws-ticket
2. Server returns short-lived JWT ticket (5 min expiry)
3. Client connects to WS endpoint with ticket as query parameter
4. Server validates ticket and authenticates user
5. WS connection established, session begins
```

---

## 7. AI Context Building

### 7.1 Story Chat Context

```python
context = {
    'story': {
        'id': story.id,
        'title': story.title,
        'description': story.short_description,
        'type': story.story_type,
        'genre': story.story_genre,
        'tone': story.story_tone
    },
    'session': {
        'focus_area': session.focus_area,
        'title': session.title
    },
    'request': {
        'target_element': request.target_element,
        'target_element_id': request.target_element_id
    },
    'acts': [
        {
            'id': act.id,
            'title': act.title,
            'act_number': act.act_number,
            'content': act.content,  # Full or preview based on targeting
            'scenes': [...]
        }
    ],
    'world': {...},  # For advanced stories
    'characters': [...],  # Limited to 10
    'locations': [...],  # Limited to 10
    'lore_items': [...]  # Limited to 5
}
```

### 7.2 System Prompt Templates

- **Basic Story Chat**: Focused on writing assistance, plot development, character arcs
- **Advanced Story Chat**: Includes world-building context, character sheets, locations, lore

---

## 8. Unit Tests

### 8.1 Existing Tests

| Test File | Coverage |
|-----------|----------|
| `tests/integration/story/test_chat_endpoints_integration.py` | Story chat REST endpoints |
| `tests/unit/story/test_story_and_ai_text_transform_unit.py` | AI text transform unit tests |

### 8.2 Test Coverage Summary

| Area | Unit Tests | Integration Tests |
|------|------------|-------------------|
| World Chat REST | ❌ | Partial |
| World Chat Service | ❌ | ❌ |
| Story Chat REST | Partial | ✅ |
| Story Chat Service | ❌ | Partial |
| Story Chat WebSocket | ❌ | ❌ |
| Public World Chat | ❌ | ❌ |
| Anonymous User Chat | ❌ | ❌ |
| Chat Samples | ❌ | Partial |

### 8.3 Recommended Additional Tests

```python
# tests/unit/chat/test_world_chat_service_unit.py
def test_create_chat_session_returns_session_id():
def test_send_message_returns_response():
def test_load_world_context_includes_characters():
def test_send_message_with_element_target():

# tests/unit/chat/test_story_chat_service_unit.py
def test_create_session_validates_story_access():
def test_build_ai_context_includes_acts():
def test_build_system_prompt_for_basic_story():
def test_build_system_prompt_for_advanced_story():
def test_stream_ai_response_yields_chunks():

# tests/unit/chat/test_anonymous_user_unit.py
def test_create_anonymous_user_generates_username():
def test_is_anonymous_user_returns_true():
def test_generate_browser_fingerprint_is_consistent():

# tests/unit/chat/test_connection_manager_unit.py
def test_connect_adds_to_active_connections():
def test_disconnect_removes_from_active_connections():
def test_send_json_message_handles_disconnected():
```

---

## 9. Integration Tests

### 9.1 Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| World Chat Session | Login → Create world → Create session → Send message | AI response returned, cost deducted |
| Story Chat Session | Login → Create story → Create session → Send message | AI response returned with story context |
| Story Chat WebSocket | Login → Get WS ticket → Connect → Send message | Streaming response received |
| Public World Chat | Visit public world → Start chat → Send message | AI response returned, balance checked |
| Anonymous User Flow | Visit without auth → Start chat → Send message | Anonymous user created, balance initialized |
| Insufficient Balance | Deplete balance → Send message | 402 Payment Required returned |

---

## 10. Suggestions and Improvements

### 10.1 Immediate Improvements
1. **Add WebSocket Tests**: Test WebSocket connection, message exchange, and streaming.
2. **Add World Chat Unit Tests**: Test WorldChatService methods in isolation.
3. **Implement Chat History Pagination**: Add cursor-based pagination for message retrieval.
4. **Add Message Edit/Delete**: Allow users to edit or delete their messages.

### 10.2 Architecture Improvements
1. **Implement Chat Session Archival**: Archive old sessions to reduce database load.
2. **Add Chat Analytics**: Track chat usage patterns, popular topics, and engagement.
3. **Implement Multi-Model Support**: Allow users to select different AI models per session.
4. **Add Chat Export**: Allow exporting chat history as text or JSON.

### 10.3 Testing Improvements
1. **Add WebSocket Mock Tests**: Use mock WebSocket for testing client behavior.
2. **Add Load Tests**: Test chat under concurrent user load.
3. **Add Streaming Tests**: Test streaming response handling.
4. **Add Anonymous User Tests**: Test anonymous user creation and balance management.

### 10.4 Performance Improvements
1. **Implement Message Caching**: Cache recent messages to reduce database queries.
2. **Add Connection Pooling**: Optimize WebSocket connection handling.
3. **Implement Response Streaming**: Use true streaming for AI responses.
4. **Add Context Compression**: Compress AI context to reduce token usage.

### 10.5 Security Considerations
1. **Rate Limit Chat Messages**: Prevent abuse with per-session rate limiting.
2. **Validate User Input**: Sanitize messages before sending to AI.
3. **Add Content Filtering**: Filter inappropriate content in AI responses.
4. **Secure WebSocket Connections**: Ensure WSS in production.

### 10.6 Scalability Considerations
1. **Horizontal WebSocket Scaling**: Use Redis pub/sub for multi-instance WS.
2. **Message Queue for AI Calls**: Use Celery/Redis for async AI processing.
3. **Database Read Replicas**: Route message reads to replicas.
4. **Session Affinity**: Use sticky sessions for WebSocket connections.

### 10.7 Future Feature Ideas
1. **Multi-User Chat**: Support collaborative chat sessions.
2. **Voice Chat**: Add speech-to-text and text-to-speech.
3. **Chat Templates**: Pre-configured chat templates for different scenarios.
4. **AI Personality Selection**: Allow selecting different AI personalities.
5. **Chat Summarization**: Auto-summarize long conversations.
6. **Context Memory**: Persistent memory across chat sessions.
