# Implementation Plan: OpenAI ChatKit Integration for Todo Chatbot

**Branch**: `001-chatkit-integration` | **Date**: 2026-02-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-chatkit-integration/spec.md`

## Summary

This plan defines the integration of the official OpenAI ChatKit widget into the existing Phase II Todo web application. The integration adds an AI-powered conversational interface that enables users to manage tasks through natural language commands while preserving all existing Phase II functionality.

**Technical Approach**:
- Frontend: Replace custom chat widget with official `@openai/chatkit-react` widget
- Backend: Add ChatKit WebSocket endpoint to Phase II backend, integrating OpenAI Agents SDK with MCP tools
- Database: Add Conversation and Message tables to Neon PostgreSQL for chat history persistence
- Authentication: Use existing Better Auth JWT tokens

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript/JavaScript ES2022+ (frontend)
**Primary Dependencies**:
- Frontend: `@openai/chatkit-react` (official ChatKit widget), Next.js 16+
- Backend: FastAPI, OpenAI Agents SDK (`openai>=1.0.0`), MCP SDK (`mcp>=1.25`), SQLModel
- Storage: Neon PostgreSQL (existing for tasks, adding conversations/messages)
- Testing: pytest (backend), Jest/Vitest (frontend - existing)
- Target Platform: Web browser (Chrome, Firefox, Safari, Edge), Linux server (backend)
- Project Type: Web application (frontend + backend)
- Performance Goals:
  - Chat response time: <3 seconds (90th percentile)
  - WebSocket message latency: <500ms
  - Support 100 concurrent chat sessions
- Constraints:
  - Must not modify existing Phase II task CRUD endpoints
  - Must use existing Better Auth authentication
  - Chat widget must be non-intrusive (collapsible/floating)
  - Backend must remain stateless and restart-safe
- Scale/Scope: Single-page application overlay, ~5 new database tables/models, ~3 new API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Statelessness

| Requirement | Compliance | Notes |
|-------------|------------|-------|
| No server-side session state | PASS | All conversation state stored in database |
| Restart-safe | PASS | ChatKit uses thread_id for session continuity |
| Horizontal scalability | PASS | Stateless WebSocket handler with database backing |

### Separation of Concerns

| Requirement | Compliance | Notes |
|-------------|------------|-------|
| MCP tools isolated from UI | PASS | Tools in `src/mcp_tools/` package |
| Frontend-backend contract defined | PASS | REST API for session, WebSocket for chat |
| No business logic in UI layer | PASS | ChatKit widget handles UI only |

### API Contract Design

| Requirement | Compliance | Notes |
|-------------|------------|-------|
| Idempotent operations | PASS | MCP tools use database transactions |
| Error taxonomy defined | PASS | Standardized error responses in Phase 0 |
| Retry semantics clear | PASS | WebSocket reconnection with thread_id resume |

### Data Model Isolation

| Requirement | Compliance | Notes |
|-------------|------------|-------|
| No leakage between domains | PASS | Conversations isolated by user_id |
| Database schema migration path | PASS | Alembic migrations for new tables |

## Project Structure

### Documentation (this feature)

```text
specs/001-chatkit-integration/
├── plan.md              # This file
├── spec.md              # Feature specification (complete)
├── data-model.md        # Database schema (Phase 1 output)
├── quickstart.md        # Developer onboarding (Phase 1 output)
├── contracts/           # API contracts (Phase 1 output)
│   ├── chatkit-api.md
│   └── mcp-tools.md
└── tasks.md             # Implementation tasks (/sp.tasks output)
```

### Source Code (repository root)

```text
# Phase II Integration (modified existing)

phase_2_web_App/
├── frontend/
│   └── src/
│       ├── app/
│       │   └── layout.tsx              # MODIFIED: Add ChatKitProvider
│       ├── components/
│       │   └── ChatKitOfficialWidget.tsx   # MODIFIED: Use official @openai/chatkit
│       └── lib/
│           └── chatkit.ts              # NEW: ChatKit client configuration
│
└── backend/
    └── app/
        ├── main.py                     # MODIFIED: Add ChatKit router
        ├── models/
        │   ├── task.py                 # EXISTING: No changes
        │   ├── conversation.py         # NEW: Conversation model
        │   └── message.py              # NEW: Message model
        ├── api/
        │   ├── tasks.py                # EXISTING: No changes
        │   └── v1/
        │       └── chatkit.py          # NEW: ChatKit endpoints
        ├── services/
        │   ├── chat_service.py         # NEW: Conversation/message CRUD
        │   └── mcp_tools.py            # NEW: MCP tool implementations
        └── agents/
            └── todo_agent.py           # NEW: OpenAI Agents SDK integration

# Phase III Reference (existing, may be reused)

phase_3_chatbot/
└── backend/
    └── src/                            # Reference implementations
        ├── mcp_tools/server.py         # Reference MCP server
        ├── agents/todo_agent.py        # Reference agent
        └── services/chatkit_server.py  # Reference ChatKit server
```

**Structure Decision**: Web application structure with separate frontend and backend directories. The ChatKit integration modifies existing Phase II code rather than creating a separate application, ensuring the chat widget works as an overlay to the existing todo interface.

## Phase 0: Research and Architecture

### 0.1 Official ChatKit Documentation Review

**Objective**: Understand official ChatKit package requirements and protocols

**Tasks**:
1. Review `@openai/chatkit-react` documentation
2. Understand ChatKit protocol message format
3. Identify required server endpoints
4. Document WebSocket event types
5. Verify session creation flow

**Deliverables**: `research/chatkit-protocol.md`

### 0.2 OpenAI Agents SDK Integration Research

**Objective**: Define integration pattern for OpenAI Agents SDK with MCP tools

**Tasks**:
1. Review OpenAI Agents SDK documentation
2. Understand tool calling protocol
3. Define agent instructions format
4. Document conversation history handling
5. Identify streaming response patterns

**Deliverables**: `research/agents-sdk-integration.md`

### 0.3 MCP Tools Specification

**Objective**: Define MCP tool interfaces for task operations

**Tasks**:
1. Define tool schemas for 5 operations (add, list, update, complete, delete)
2. Document input/output formats
3. Define error handling patterns
4. Specify natural language task matching logic
5. Document user_id injection pattern

**Deliverables**: `contracts/mcp-tools.md`

### 0.4 Architecture Decision Records

**Objective**: Document key architectural decisions

**Tasks**:
1. WebSocket vs SSE for chat streaming
2. Conversation history retention policy
3. Task identification strategy (ID vs natural language)
4. Authentication token propagation
5. Error recovery and reconnection strategy

**Deliverables**: `contracts/adr.md`

## Phase 1: Design

### 1.1 Database Schema Design

**Objective**: Define Conversation and Message tables

**Tables**:

```sql
-- Conversation table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(200) DEFAULT 'New Conversation',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Message table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool_call')),
    content TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
```

**Deliverables**: `data-model.md`

### 1.2 API Contract Design

**Objective**: Define REST and WebSocket endpoints

**Endpoints**:

1. `POST /api/v1/chatkit/session` - Create chat session
   - Request: `{ "thread_id": "optional-existing-id" }`
   - Response: `{ "client_secret": "...", "thread_id": "...", "user_id": "..." }`

2. `GET /api/v1/chatkit/ws` - WebSocket endpoint (upgrade)
   - Protocol: ChatKit WebSocket protocol
   - Events: message, tool_call_started, tool_call_completed, error, conversation_done

3. `GET /api/v1/conversations/{thread_id}/messages` - Load conversation history
   - Response: `{ "messages": [{ "role": "...", "content": "...", "timestamp": "..." }] }`

**Deliverables**: `contracts/chatkit-api.md`

### 1.3 MCP Tools Implementation Design

**Objective**: Design MCP tool implementations

**Tools**:

1. `add_task(user_id, title, description?, due_date?)`
2. `list_tasks(user_id, status?, limit?)`
3. `update_task(user_id, task_id?, task_title?, new_title?, new_description?, new_due_date?, new_status?)`
4. `complete_task(user_id, task_id?, task_title?)`
5. `delete_task(user_id, task_id?, task_title?, delete_completed?)`

**Implementation Pattern**:
- Each tool is a pure function
- Tools accept user_id as first parameter
- Tools call existing Phase II task endpoints
- Return structured results with success/error status

**Deliverables**: `contracts/mcp-tools.md`

### 1.4 Frontend Integration Design

**Objective**: Design ChatKit widget integration

**Components**:

1. `ChatKitProvider` (app-level wrapper)
2. `ChatInterface` (floating widget)
3. `useChatKit` hook (for custom interactions if needed)

**Integration Points**:
- Wrap app in ChatKitProvider in layout.tsx
- Pass authToken from existing AuthContext
- Connect to backend WebSocket endpoint
- Handle connection errors and reconnection

**Deliverables**: `contracts/frontend-integration.md`

### 1.5 Developer Quickstart

**Objective**: Create onboarding documentation

**Content**:
1. Prerequisites (Node.js, Python, PostgreSQL)
2. Environment setup
3. Running locally (frontend + backend)
4. Testing the chat widget
5. Common troubleshooting

**Deliverables**: `quickstart.md`

## Phase 2: Implementation Tasks

*(Detailed tasks will be generated by `/sp.tasks` command)*

**High-level task breakdown**:

1. Database setup (migrations, models)
2. Backend MCP tools implementation
3. Backend ChatKit endpoint implementation
4. OpenAI Agents SDK integration
5. Frontend ChatKit widget integration
6. Authentication wiring
7. Testing (unit, integration, E2E)
8. Documentation

## Complexity Tracking

> No constitution violations - this table is not required.

All architecture decisions comply with the project constitution:
- Statelessness: ChatKit protocol is stateless, thread_id provides continuity
- Separation of Concerns: MCP tools, agent, and WebSocket handler are separate
- API Contracts: REST for session management, WebSocket for chat streaming
- Data Model Isolation: Conversations/messages isolated by user_id

## Dependencies

**External Dependencies**:
- `@openai/chatkit-react` - Official ChatKit frontend package
- `openai>=1.0.0` - OpenAI API and Agents SDK
- `mcp>=1.25` - Official MCP SDK for tools
- Existing Phase II dependencies (FastAPI, SQLModel, etc.)

**Internal Dependencies**:
- Phase II backend authentication middleware
- Phase II task CRUD endpoints
- Phase II Better Auth JWT tokens
- Phase II frontend AuthContext

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| ChatKit protocol changes | Medium | Use official package, version pin |
| OpenAI API rate limits | Medium | Implement retry logic, caching |
| WebSocket connection drops | Low | Auto-reconnect with thread_id resume |
| Conversation history growth | Low | 30-day retention policy |
| Token expiration during chat | Low | Refresh token on 401 errors |

## Success Metrics

From spec.md, the following success criteria will be validated:

- SC-001: Task creation in under 10 seconds
- SC-002: 95% command interpretation accuracy
- SC-003: 30% time savings vs form-based
- SC-004: 100% conversation history accuracy (30 days)
- SC-005: 3-second response time (90th percentile)
- SC-006: All 5 task operations work via chat
- SC-007: 100% ambiguous request clarification
- SC-008: Zero security incidents

## Next Steps

1. Review and approve this plan
2. Execute `/sp.tasks` to generate detailed implementation tasks
3. Begin Phase 0 research
