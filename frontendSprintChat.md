# Sprint Chat 01: Independent Chat Application Foundation

## Goal

Establish `chatbot` as an independent frontend application with a simple chat-first UI, shared platform access patterns, and explicit turn-level cost visibility requirements for later backend integration.

## In Scope

- `chatbot` route-tree foundation
- chat-first shell and landing experience
- session list and active conversation workspace layout
- composer, transcript, and turn-state handling
- loading, empty, and error states for conversation turns
- cost/usage presentation hooks per assistant turn
- Playwright coverage for chat entry and conversation behavior

## Route Backlog

| React Route | Source Legacy Surface | Priority | Notes |
|---|---|---|---|
| `/chatbot` | net-new | P0 | Chat application landing and default session route |
| `/chatbot/sessions` | net-new | P0 | Session list and resume entry |
| `/chatbot/sessions/:sessionId` | net-new | P0 | Active conversation workspace |
| `/chatbot/history` | net-new | P1 | Usage and prior conversation access |
| `/chatbot/settings` | net-new | P2 | Model and behavior preferences once needed |

## Shared Components

- `ChatbotShell`
- `ChatSessionRail`
- `ChatTranscript`
- `ChatComposer`
- `ChatTurnCostBadge`
- `ChatEmptyState`
- `ChatErrorState`

## Backend/API Dependencies

- authenticated session and app-entry guard behavior
- chatbot session create/list/get/delete endpoints
- chatbot send-message endpoint with turn identifiers
- per-turn token usage and calculated cost fields in responses
- billing transaction visibility for AI conversation turns

## UI Behavior Capture Targets

- initial chat landing behavior
- session create and resume flow
- transcript append behavior for user and assistant turns
- pending, streaming, retry, and failed-turn states
- per-turn token and cost presentation
- route reload and session restoration behavior

## Risks and Decisions

- Keep `chatbot` independent from storytelling and care-circle assumptions.
- Do not couple the chat UI to world-specific or story-specific context models.
- Token, cost, and transaction feedback should be surfaced per turn without turning the UI into an admin console.
- Start with route-level usability and reliable turn handling before adding advanced model controls.

## Task List

- [ ] Define the `chatbot` top-level route tree.
- [ ] Build the chatbot landing route and shell foundation.
- [ ] Build the session list rail and active conversation layout.
- [ ] Implement composer submission, assistant pending state, and transcript append behavior.
- [ ] Add per-turn cost and token display hooks in the transcript UI.
- [ ] Add empty, loading, and failed-turn states for the chat experience.
- [ ] Add Playwright coverage for chat entry, sending a turn, and session restore behavior.
- [ ] Capture transcript, composer, and per-turn usage behavior in `uiBehaviorCapture.md`.
- [ ] Verify chat turn responses align with backend cost-tracking and billing contracts.

## Exit Criteria

- chatbot exists as an independent application on the shared platform
- a user can open a session and complete a basic chat turn flow
- per-turn cost and token data have defined frontend integration points

## Exit Verification

| Criterion | Verification Method | Evidence |
|---|---|---|
| chatbot exists as an independent application on the shared platform | Browser verification and code review confirm chatbot routes resolve under their own app boundary and shell | To be recorded during implementation |
| a user can open a session and complete a basic chat turn flow | Playwright covers entry, send, response, and session restore behavior | To be recorded during implementation |
| per-turn cost and token data have defined frontend integration points | Code review and UI verification confirm turn-level usage placeholders or live data bindings are present in the transcript UI | To be recorded during implementation |

## Implementation Status

- Planning only.
- This sprint defines the dedicated chat application track and should remain independent from the storytelling and care-circle sprints.
