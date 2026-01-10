# Implementation Tasks: Todo AI Chatbot (Agentic, MCP-based)

**Feature**: Phase III: Todo AI Chatbot (Agentic, MCP-based)
**Date**: 2026-01-10
**Branch**: `003-todo-ai-chatbot`
**Spec**: [specs/003-todo-ai-chatbot/spec.md](../specs/003-todo-ai-chatbot/spec.md)

## Implementation Strategy

Build a complete isolated Todo AI Chatbot system under /phase_3_chatbot with:
- Backend API with OpenAI Agents integration
- MCP server for task operations
- Frontend ChatKit UI
- Database layer with conversation persistence
- All components stateless and restart-safe

**MVP Scope**: User Story 1 (Natural Language Todo Management) with minimal viable UI

## Dependencies

- User Story 1 [US1] (P1) - Natural Language Todo Management
- User Story 2 [US2] (P2) - Persistent Conversation Context
- User Story 3 [US3] (P3) - Secure Authenticated Access

## Parallel Execution Examples

- Database models (Conversation, Message) can be built in parallel with MCP server
- Backend API can be developed in parallel with frontend UI (after auth integration)
- Agent configuration can proceed once MCP tools are available

---

## Phase 1: Project Structure Setup

**Goal**: Create isolated Phase III project structure with all required directories

- [X] T001 Create root directory structure: phase_3_chatbot/
- [X] T002 Create backend directory: phase_3_chatbot/backend
- [X] T003 Create MCP server directory: phase_3_chatbot/mcp_server
- [X] T004 Create frontend directory: phase_3_chatbot/frontend
- [X] T005 Create database directory: phase_3_chatbot/database
- [X] T006 Create specs directory: phase_3_chatbot/specs
- [X] T007 [P] Create phase_3_chatbot/specs/architecture.md documenting folder responsibilities
- [X] T008 [P] Set up initial pyproject.toml in phase_3_chatbot/backend with required dependencies
- [X] T009 [P] Set up initial pyproject.toml in phase_3_chatbot/mcp_server with MCP SDK dependencies
- [X] T010 [P] Set up package.json in phase_3_chatbot/frontend with ChatKit dependencies

---

## Phase 2: Database Layer (Stateless Persistence)

**Goal**: Implement SQLModel database models for conversation persistence with no in-memory state

- [X] T011 Create SQLModel base class in phase_3_chatbot/database/models/base.py
- [X] T012 Create Conversation model in phase_3_chatbot/database/models/conversation.py
- [X] T013 Create Message model in phase_3_chatbot/database/models/message.py
- [X] T014 [P] Define foreign key relationships: Conversation → User, Message → Conversation
- [X] T015 [P] Add indexes for performance: (user_id, created_at), (conversation_id, timestamp)
- [X] T016 Create Alembic migration script for Conversation table in phase_3_chatbot/database/migrations/
- [X] T017 Create Alembic migration script for Message table in phase_3_chatbot/database/migrations/
- [X] T018 [P] Create database session management in phase_3_chatbot/database/session.py
- [ ] T019 Verify restart-safe persistence by testing conversation recovery after simulated server restart

---

## Phase 3: MCP Server Implementation

**Goal**: Build MCP server with stateless tools for task operations that agent can call

- [X] T020 Initialize MCP server application in phase_3_chatbot/mcp_server/main.py
- [X] T021 [P] Create add_task MCP tool in phase_3_chatbot/mcp_server/tools/todo_tools.py
- [X] T022 [P] Create list_tasks MCP tool in phase_3_chatbot/mcp_server/tools/todo_tools.py
- [X] T023 [P] Create update_task MCP tool in phase_3_chatbot/mcp_server/tools/todo_tools.py
- [X] T024 [P] Create complete_task MCP tool in phase_3_chatbot/mcp_server/tools/todo_tools.py
- [X] T025 [P] Create delete_task MCP tool in phase_3_chatbot/mcp_server/tools/todo_tools.py
- [X] T026 [P] Implement structured error responses for all MCP tools
- [X] T027 [P] Add input validation to all MCP tools with explicit parameters
- [X] T028 [P] Create specs/mcp-tools.spec.md documenting all MCP tool specifications
- [X] T029 Document tool versioning strategy in phase_3_chatbot/specs/mcp-tools.spec.md

---

## Phase 4: [US1] Natural Language Todo Management

**Goal**: Enable users to manage todos via natural language through AI agent

**Independent Test**: Can send natural language commands to chat endpoint and verify appropriate todo operations are performed

**Acceptance**:
- Given a user has access to the chatbot, when they send a natural language command to create a task, then the system should parse the command and create the appropriate task in their todo list
- Given a user has existing tasks, when they ask to see their tasks in natural language, then the system should return their tasks in a conversational format
- Given a user has tasks, when they request to update or complete a task via natural language, then the system should identify the correct task and update its status appropriately

- [ ] T030 [US1] Set up FastAPI application in phase_3_chatbot/backend/main.py
- [ ] T031 [US1] Create chat service in phase_3_chatbot/backend/services/chat_service.py
- [ ] T032 [US1] Implement conversation lookup/creation in ChatService
- [ ] T033 [US1] Implement message history fetching in ChatService
- [ ] T034 [US1] Implement user message storage in ChatService
- [ ] T035 [US1] Implement assistant response storage in ChatService
- [ ] T036 [US1] Integrate OpenAI Agents SDK in phase_3_chatbot/backend/agents/todo_agent.py
- [ ] T037 [US1] Configure agent system prompt for todo management
- [ ] T038 [US1] Connect agent to MCP tools for task operations
- [ ] T039 [US1] Create POST /api/{user_id}/chat endpoint in phase_3_chatbot/backend/api/v1/chat.py
- [ ] T040 [US1] Implement request validation for chat endpoint
- [ ] T041 [US1] Implement response formatting for chat endpoint
- [ ] T042 [US1] Add tool call metadata capture to chat endpoint
- [ ] T043 [US1] Create specs/agent.spec.md documenting agent behavior
- [ ] T044 [US1] Test natural language task creation functionality

---

## Phase 5: [US2] Persistent Conversation Context

**Goal**: Maintain conversation context across multiple requests and server restarts

**Independent Test**: Can have conversation across multiple API calls with context maintained, and can continue after server restart

**Acceptance**:
- Given a user is in an ongoing conversation with the chatbot, when they make subsequent requests, then the system should maintain context from previous exchanges
- Given a server restart occurs, when a user continues their conversation, then the system should reconstruct the conversation context from the database and continue appropriately

- [ ] T045 [US2] Enhance conversation replay logic in ChatService to fetch full history
- [ ] T046 [US2] Implement conversation context reconstruction for agent from database
- [ ] T047 [US2] Create GET /api/{user_id}/conversations/{conversation_id}/messages endpoint
- [ ] T048 [US2] Add pagination support to message history endpoint
- [ ] T049 [US2] Test conversation persistence across server restarts
- [ ] T050 [US2] Verify conversation context is correctly reconstructed after restart

---

## Phase 6: [US3] Secure Authenticated Access

**Goal**: Enforce Better Auth authentication and user data isolation

**Independent Test**: Authenticated requests work properly, unauthenticated requests are rejected, users only see their own data

**Acceptance**:
- Given a user makes an authenticated request to the chat endpoint, when they ask about their tasks, then they should only see their own tasks and not others'
- Given an unauthenticated request is made to the chat endpoint, when the request is processed, then it should be rejected with appropriate authentication error

- [ ] T051 [US3] Set up Better Auth integration in phase_3_chatbot/backend/auth/
- [ ] T052 [US3] Create authentication dependency in phase_3_chatbot/backend/api/deps.py
- [ ] T053 [US3] Add authentication middleware to FastAPI app
- [ ] T054 [US3] Implement user_id verification in chat endpoint
- [ ] T055 [US3] Add authorization checks to prevent cross-user data access
- [ ] T056 [US3] Test authentication with valid and invalid tokens
- [ ] T057 [US3] Verify user data isolation between different users

---

## Phase 7: Frontend Chat UI (ChatKit)

**Goal**: Create user interface using OpenAI ChatKit for natural language interaction

- [ ] T058 Set up Next.js project in phase_3_chatbot/frontend
- [ ] T059 Install and configure OpenAI ChatKit in frontend
- [ ] T060 Integrate Better Auth session management in frontend
- [ ] T061 Connect frontend to backend /api/{user_id}/chat endpoint
- [ ] T062 Implement message history rendering in UI
- [ ] T063 Display tool action confirmations in UI
- [ ] T064 Handle loading and error states in UI
- [ ] T065 Configure domain allowlist support for ChatKit

---

## Phase 8: Statelessness & Safety Validation

**Goal**: Verify all statelessness constraints and safety requirements are met

- [ ] T066 Verify server restart does not break existing conversations
- [ ] T067 Verify horizontal scalability assumptions (no shared memory/state)
- [ ] T068 Confirm no in-memory session usage in any component
- [ ] T069 Verify MCP tools are idempotent where applicable
- [ ] T070 Create specs/stateless.md with compliance checklist
- [ ] T071 Test concurrent user sessions without interference

---

## Phase 9: Documentation & Finalization

**Goal**: Complete documentation and prepare for review

- [ ] T072 Write README.md in phase_3_chatbot with setup instructions
- [ ] T073 Document environment variables setup (OpenAI API key, DB connection)
- [ ] T074 Document request lifecycle: frontend → backend → agent → MCP → DB
- [ ] T075 Document agent ↔ MCP ↔ DB flow in specs/
- [ ] T076 Prepare Phase III review checklist
- [ ] T077 Verify Phase II app remains untouched by Phase III changes
- [ ] T078 Test complete end-to-end functionality: natural language → agent → MCP tools → DB → response

---

## Task Breakdown Summary

- **Total Tasks**: 78
- **Setup Tasks**: 10 (T001-T010)
- **Database Tasks**: 9 (T011-T019)
- **MCP Server Tasks**: 10 (T020-T029)
- **US1 (Natural Language Todo Management)**: 15 (T030-T044)
- **US2 (Persistent Conversation Context)**: 7 (T045-T050)
- **US3 (Secure Authenticated Access)**: 7 (T051-T057)
- **Frontend Tasks**: 8 (T058-T065)
- **Validation Tasks**: 6 (T066-T071)
- **Documentation Tasks**: 6 (T072-T078)