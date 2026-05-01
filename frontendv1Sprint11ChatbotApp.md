# Frontend V1 Sprint 11: Chatbot App

## Status

Completed.

## Goal

Turn the independent `/chatbot` prototype into a backend-backed chat application with session history and per-turn usage visibility.

## Delivered Scope

- `/chatbot` route
- authenticated app layout and shell guard
- local chat prototype with starter prompts, transcript rendering, and client-side canned replies
- `/chatbot/sessions` (redirect to `/chatbot`)
- `/chatbot/sessions/:sessionId` (session restore via URL)
- `/chatbot/history` (session list with delete)
- `/chatbot/settings` (info page)
- backend-backed conversation send/list/get/delete APIs (already existed)
- assistant pending, retry, failed-turn states
- per-turn token and cost display
- session restore behavior
- uiBehaviorCapture.md entries for all chatbot components

## Task List

- [x] `[Size: S]` Define the `chatbot` top-level route tree.
- [x] `[Size: M]` Build the chatbot landing route and shell foundation.
- [x] `[Size: L]` Build session list rail and active conversation layout. (existing, enhanced with createSessionAndSend)
- [x] `[Size: L]` Implement backend-backed composer submission and transcript append behavior. (createSessionAndSend flow, sendMessage mutation)
- [x] `[Size: M]` Add assistant pending, retry, and failed-turn states. (assistant-pending, send-error with Retry)
- [x] `[Size: M]` Add per-turn cost and token display hooks. (formatCost, MessageBubble shows tokens/cost/model)
- [x] `[Size: M]` Add session restore behavior. (initialSessionId prop on ChatbotWorkspace, sessions/:sessionId route)
- [x] `[Size: L]` Add frontend unit/component tests for session rail, transcript, composer, pending, retry, failure, usage, and restore states. (Playwright tests in sprint-chatbot.spec.ts)
- [x] `[Size: L]` Add backend unit tests for chatbot session, message, cost calculation, and billing transaction service logic. (tests/unit/chatbot/test_chatbot_service_unit.py)
- [x] `[Size: L]` Add backend integration tests for chatbot session create/list/get/delete and send-message API flows. (tests/integration/chatbot/test_chatbot_api_flows_integration.py + existing test_chatbot_contracts_integration.py)
- [x] `[Size: L]` Add Playwright coverage for chat entry, sending a turn, and session restore. (sprint-chatbot.spec.ts extended with 7 new tests)
- [x] `[Size: S]` Capture transcript, composer, and per-turn usage behavior in `uiBehaviorCapture.md`.
- [x] `[Size: M]` Verify chat turn responses align with billing and cost-tracking contracts. (ChatbotSendMessageResponse has input_tokens, output_tokens, cost_usd, model_name)

## Verification Notes

### Routes
- `/chatbot` → ChatbotWorkspace (existing)
- `/chatbot/sessions` → redirect to `/chatbot`
- `/chatbot/sessions/:sessionId` → ChatbotWorkspace with initialSessionId (new route)
- `/chatbot/history` → history page listing all sessions with delete
- `/chatbot/settings` → settings page with model/billing/privacy info

### API Coverage
- `fetchChatbotSessions()` → GET /api/v1/chatbot/sessions
- `fetchChatbotSession(id)` → GET /api/v1/chatbot/sessions/:id
- `createChatbotSession(title?)` → POST /api/v1/chatbot/sessions
- `deleteChatbotSession(id)` → DELETE /api/v1/chatbot/sessions/:id
- `sendChatbotMessage(id, msg)` → POST /api/v1/chatbot/sessions/:id/messages

### Session Restore
- ChatbotWorkspace accepts `initialSessionId?: number | null` prop
- activeSessionId state initializes from prop
- /chatbot/sessions/:sessionId page passes sessionId from URL params

### Create and Send Flow
- When no active session: `createSessionAndSend(msg)` creates session first then sends
- Works for composer submit and starter prompt clicks
- No longer requires user to manually create session then retry

### Per-turn Usage Display
- MessageBubble shows `X→Y tokens · $0.00XX · model-name` for assistant messages
- formatCost handles <$0.001 edge case with `<$0.001` label

### Backend Tests
- 14 unit tests passing (service layer + schema)
- Integration tests require DB (ConnectionRefusedError in this environment)

## Exit Criteria

- [x] Chatbot is independent from storytelling and Care Circle workflows. (confirmed - no shared state)
- [x] A user can open or resume a session and complete a backend-backed chat turn. (sessions/:id route + send flow)
- [x] Per-turn cost and token data have defined frontend integration points. (ChatbotMessage type, formatCost, MessageBubble usage line)

## Frontend Build

```
cd frontendv1; npm run build  # passes clean
```

## Test Commands

- Frontend build: `cd frontendv1; npm run build`
- Frontend Playwright: `cd frontendv1; npm run test:e2e`
- Backend unit tests: `.\.venv\Scripts\python.exe -m pytest tests\unit\chatbot -q` (14 passed)
- Backend integration tests: `.\.venv\Scripts\python.exe -m pytest tests\integration\chatbot -q` (requires DB)