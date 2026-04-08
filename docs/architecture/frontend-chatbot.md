# Frontend Chatbot Architecture Document

## 1. Overview

The Chatbot frontend is a narrow, chat-first UI surface that provides a simple conversational interface. It is intentionally designed to be independent of storytelling and care-circle workflows, serving as a clean conversation surface before deeper app behaviors are integrated.

### Key Characteristics
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom design tokens
- **State Management**: React useState (local state only, no server integration yet)
- **Testing**: Playwright E2E tests (pending)
- **Current Status**: Local UI prototype with canned responses

### Accuracy Review
- Reviewed against:
  - `frontendv1/app/chatbot/page.tsx`
  - `frontendv1/components/chatbot/chatbot-workspace.tsx`
- This document is accurate in describing the current chatbot frontend as a prototype surface.
- The current implementation is intentionally narrow:
  - single route
  - local message state
  - canned replies
  - no live backend chat integration yet
- Any API sections in this file should be read as future-facing integration planning rather than active frontend behavior.

---

## 2. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Chatbot Frontend                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Chatbot Page (app/chatbot/page.tsx)           │   │
│  │                                                                      │   │
│  │  <PageHeader                                                         │   │
│  │    eyebrow="Chatbot"                                                 │   │
│  │    title="A narrow conversation surface..."                          │   │
│  │  />                                                                  │   │
│  │  <ChatbotWorkspace />                                                │   │
│  └──────────────────────────────┬───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    ChatbotWorkspace Component                        │   │
│  │                  (components/chatbot/chatbot-workspace.tsx)          │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────┐      ┌──────────────────────────────┐  │   │
│  │  │   Sidebar Panel         │      │   Conversation Panel         │  │   │
│  │  │                         │      │                              │  │   │
│  │  │  - App description      │      │  - Header                    │  │   │
│  │  │  - Starter Prompts      │      │  - Message List              │  │   │
│  │  │    (clickable buttons)  │      │    - Assistant messages      │  │   │
│  │  │                         │      │    - User messages           │  │   │
│  │  │                         │      │  - Input Form                │  │   │
│  │  │                         │      │    - Textarea                │  │   │
│  │  │                         │      │    - Submit Button           │  │   │
│  │  └─────────────────────────┘      └──────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Current State Management                      │   │
│  │                                                                      │   │
│  │  const [draft, setDraft] = useState("");                             │   │
│  │  const [messages, setMessages] = useState<ChatMessage[]>([...]);     │   │
│  │                                                                      │   │
│  │  // Canned replies for prototyping                                   │   │
│  │  const cannedReplies = [                                             │   │
│  │    "I can help with that...",                                        │   │
│  │    "Start with the key point...",                                    │   │
│  │    "That works well as a short exchange..."                          │   │
│  │  ];                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Shared Platform Integration                   │   │
│  │                                                                      │   │
│  │  - Surface ID: "chatbot"                                             │   │
│  │  - Owner Scope: "user"                                               │   │
│  │  - Requires Auth: true                                               │   │
│  │  - App Shell: Inherited from shared AppShell                         │   │
│  │  - Session: Checked via AppProviders                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Future Backend Integration                    │   │
│  │                                                                      │   │
│  │  - WebSocket connection to /api/v1/story-chat/ws/...                 │   │
│  │  - REST API for session management                                   │   │
│  │  - Streaming AI responses                                            │   │
│  │  - Cost tracking display                                             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Route Structure

| Route | Auth Required | Component | Description |
|-------|---------------|-----------|-------------|
| `/chatbot` | Yes | `ChatbotPage` → `ChatbotWorkspace` | Main chatbot interface |

---

## 4. Data Model (Frontend Types)

```typescript
// Chat Message
interface ChatMessage {
  id: number;
  role: 'assistant' | 'user';
  text: string;
}

// Future: Chat Session (when backend integrated)
interface ChatSession {
  id: number;
  title: string;
  focusArea: string | null;
  createdAt: string;
  updatedAt: string;
}

// Future: WebSocket Message Types
type WSMessageType =
  | { type: 'session_info'; session: ChatSession }
  | { type: 'response_start' }
  | { type: 'text_chunk'; content: string }
  | { type: 'response_complete' }
  | { type: 'error'; message: string }
  | { type: 'pong' };

// Future: Client Message Types
type ClientMessageType =
  | { type: 'send_message'; content: string; targetElement?: string; targetElementId?: string }
  | { type: 'ping' };
```

---

## 5. API Endpoints (Future Integration)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/story-chat/stories/:storyId/sessions` | User | Create chat session |
| GET | `/api/v1/story-chat/stories/:storyId/sessions` | User | List sessions for story |
| GET | `/api/v1/story-chat/stories/:storyId/sessions/:sessionId` | User | Get session with messages |
| DELETE | `/api/v1/story-chat/stories/:storyId/sessions/:sessionId` | User | Delete session |
| WS | `/api/v1/story-chat/ws/stories/:storyId/sessions/:sessionId/chat` | User | WebSocket chat connection |
| GET | `/api/v1/auth/ws-ticket` | User | Get WebSocket auth ticket |

---

## 6. Component Architecture

### 6.1 Page Component

| Component | File | Purpose |
|-----------|------|---------|
| `ChatbotPage` | `app/chatbot/page.tsx` | Page wrapper with header |

### 6.2 Workspace Component

| Component | File | Purpose |
|-----------|------|---------|
| `ChatbotWorkspace` | `components/chatbot/chatbot-workspace.tsx` | Main chat UI with sidebar and conversation panel |

### 6.3 Component Details: ChatbotWorkspace

```typescript
interface ChatbotWorkspaceProps {
  // Currently no props - self-contained
}

// Internal State:
// - draft: string (current input)
// - messages: ChatMessage[] (conversation history)

// Internal Functions:
// - submitMessage(text): Add user message + canned reply
// - handleSubmit(event): Form submission handler
```

### 6.4 Starter Prompts

```typescript
const starterPrompts = [
  "Summarize a care update for a family member.",
  "Help me outline a short story scene.",
  "Turn notes into a calm conversational response."
];
```

### 6.5 Canned Replies (Prototype)

```typescript
const cannedReplies = [
  "I can help with that. Give me the goal, the audience, and the tone you want.",
  "Start with the key point, then add the minimum context needed to keep it clear.",
  "That works well as a short exchange. If you want, I can turn it into a fuller draft next."
];
```

---

## 7. Platform Integration

The Chatbot frontend integrates with the shared platform through:

1. **Surface Resolution**: `resolveSurfaceId()` maps `/chatbot/*` paths to `"chatbot"` surface ID.

2. **Platform Context**:
   - `surface_id`: `"chatbot"`
   - `app_id`: `"chatbot"`
   - `owner_scope`: `"user"`
   - `requires_auth`: `true`

3. **App Membership**: Chatbot surface requires authentication (`granted: isAuthenticated`).

4. **Shared Shell**: Uses `AppShell` for consistent navigation, theme, and maintenance gating.

5. **Default Auth Destination**: When auth is required, redirects to `/chatbot` after login.

---

## 8. Unit Tests

### 8.1 Existing Tests
- **None currently** - Chatbot-specific tests are pending

### 8.2 Recommended Unit Tests

```typescript
// components/chatbot/__tests__/chatbot-workspace.test.tsx
describe('ChatbotWorkspace', () => {
  it('renders with initial assistant message');
  it('displays starter prompts in sidebar');
  it('adds user message to conversation on submit');
  it('adds assistant reply after user message');
  it('clears input after submission');
  it('does not submit empty messages');
  it('cycles through canned replies');
  it('submits starter prompt on click');
});

// app/chatbot/__tests__/page.test.tsx
describe('ChatbotPage', () => {
  it('renders PageHeader with correct title and eyebrow');
  it('renders ChatbotWorkspace component');
});
```

---

## 9. Integration Tests

### 9.1 Recommended Playwright E2E Test Scenarios

| Scenario | Steps | Expected |
|----------|-------|----------|
| Chatbot Page Load | Navigate to /chatbot | Page renders with header and workspace |
| Send Message | Type message → Click Send | User message appears, assistant reply follows |
| Starter Prompt Click | Click a starter prompt | Prompt submitted, reply shown |
| Empty Submit Prevention | Click Send with empty input | No message added |
| Multiple Messages | Send 3 messages | All messages visible in order |

### 9.2 Future Integration Tests (with Backend)

| Scenario | Steps | Expected |
|----------|-------|----------|
| WebSocket Connection | Login → Open chatbot | WS connects, session_info received |
| Streaming Response | Send message | Response streams in chunks |
| Session Persistence | Refresh page | Previous messages restored |
| Error Handling | Simulate WS disconnect | Error message shown, reconnect attempted |

---

## 10. Suggestions and Improvements

### 10.1 Immediate Improvements
1. **Add Backend Integration**: Connect to actual AI backend via WebSocket for real responses.
2. **Implement Session Management**: Add ability to create, list, and switch between chat sessions.
3. **Add Message Timestamps**: Display when each message was sent.
4. **Implement Typing Indicator**: Show "Assistant is typing..." while waiting for response.

### 10.2 Architecture Improvements
1. **Extract Chat Hook**: Create `useChat()` hook for reusable chat logic.
2. **Add WebSocket Client**: Implement WebSocket connection with auto-reconnect and ping/pong.
3. **Implement Streaming UI**: Add streaming text animation for AI responses.
4. **Add Message Actions**: Allow copying, editing, or regenerating responses.

### 10.3 Testing Improvements
1. **Add Component Unit Tests**: Use Vitest + React Testing Library for `ChatbotWorkspace`.
2. **Add E2E Tests**: Create Playwright tests for chatbot page and interactions.
3. **Mock WebSocket**: Use MSW or `mock-socket` for WebSocket testing.
4. **Add Accessibility Tests**: Ensure keyboard navigation and screen reader support.

### 10.4 Performance Improvements
1. **Virtualize Message List**: Use virtual scrolling for long conversations.
2. **Debounce Input**: Add debounce to input for better performance.
3. **Lazy Load Heavy Components**: If adding file upload or rich text, lazy load them.

### 10.5 UX Improvements
1. **Add Conversation History**: Sidebar showing previous conversations.
2. **Add Export Functionality**: Allow exporting conversation as text/PDF.
3. **Add Keyboard Shortcuts**: Enter to send, Shift+Enter for new line.
4. **Add Markdown Rendering**: Support basic markdown in AI responses.
5. **Add Code Block Highlighting**: If code is shared, highlight syntax.

### 10.6 Security Considerations
1. **Input Sanitization**: Sanitize user input before sending to backend.
2. **Rate Limiting**: Implement client-side rate limiting to prevent abuse.
3. **Content Filtering**: Add client-side content warnings for inappropriate content.
4. **Session Timeout**: Auto-disconnect after inactivity.

### 10.7 Future Feature Ideas
1. **Multi-Model Support**: Allow switching between different AI models.
2. **Context Injection**: Allow attaching documents or context to conversations.
3. **Voice Input**: Add speech-to-text for hands-free input.
4. **Conversation Branching**: Allow branching conversations for exploring alternatives.
5. **Shared Conversations**: Allow sharing conversations with other users.
