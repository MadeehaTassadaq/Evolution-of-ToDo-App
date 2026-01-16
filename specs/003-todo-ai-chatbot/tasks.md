# Implementation Tasks: Todo AI Chatbot (Agentic, MCP-based)

**Feature**: Todo AI Chatbot — Backend & Agent Orchestration
**Date**: 2026-01-13
**Branch**: `003-todo-ai-chatbot`
**Spec**: [specs/003-todo-ai-chatbot/spec.md](../specs/003-todo-ai-chatbot/spec.md)

## Implementation Strategy

Build a complete AI chatbot system that integrates OpenAI Agents SDK to interpret natural language commands for todo management. The system will persist all conversation state in the database, reconstruct context per request, and delegate all task operations to MCP tools. The solution extends the existing Phase II Todo FastAPI backend with new models (Conversation, Message), services (ChatService), API endpoints (/api/{user_id}/chat), and agent orchestration components while maintaining strict stateless architecture and horizontal scalability.

**MVP Scope**: User Story 1 (Natural Language Todo Management) with minimal viable UI

## Dependencies

- User Story 1 [US1] (P1) - Natural Language Todo Management
- User Story 2 [US2] (P2) - Persistent Conversation Context
- User Story 3 [US3] (P3) - Secure Authenticated Access

## Parallel Execution Examples

- Database models (Conversation, Message) can be built in parallel with agent integration
- API endpoints can be developed in parallel with service layer (after auth integration)
- Agent configuration can proceed once MCP tools are available

---

## Phase 1: Project Setup & Environment

**Goal**: Create project structure and configure dependencies according to implementation plan

- [x] T001 Update pyproject.toml with required dependencies (FastAPI, SQLModel, OpenAI Agents SDK, python-jose)
- [x] T002 [P] Install and configure required dependencies using uv
- [x] T003 Create backend/src/models directory structure
- [x] T004 Create backend/src/services directory structure
- [x] T005 Create backend/src/api directory structure
- [x] T006 Create backend/src/agents directory structure
- [x] T007 Create backend/tests/unit directory structure
- [x] T008 Create backend/tests/integration directory structure
- [x] T009 Create backend/tests/contract directory structure
- [x] T010 [P] Create Alembic migration files for conversation and message tables

---

## Phase 2: Foundational Components

**Goal**: Implement core components that all user stories depend on

- [x] T011 Create SQLModel base class in backend/database/models/base.py
- [x] T012 [P] Create Conversation model in backend/database/models/conversation.py
- [x] T013 [P] Create Message model in backend/database/models/message.py
- [x] T014 [P] Define foreign key relationships: Conversation → User, Message → Conversation
- [x] T015 [P] Add indexes for performance: (user_id, created_at), (conversation_id, timestamp)
- [x] T016 Create Alembic migration script for Conversation table
- [x] T017 Create Alembic migration script for Message table
- [x] T018 [P] Create database session management in backend/database/session.py
- [x] T019 Create TodoService in backend/services/todo_service.py to handle existing todo operations
- [x] T020 [P] Create auth dependency in backend/api/deps.py for Better Auth integration

---

## Phase 3: [US1] Natural Language Todo Management

**Goal**: Enable users to manage todos via natural language through AI agent

**Independent Test**: Can send natural language commands to chat endpoint and verify that the appropriate todo operations are performed, delivering the core value of AI-powered todo management.

**Acceptance**:
- Given a user has access to the chatbot, When they send a natural language command to create a task, Then the system should parse the command and create the appropriate task in their todo list
- Given a user has existing tasks, When they ask to see their tasks in natural language, Then the system should return their tasks in a conversational format
- Given a user has tasks, When they request to update or complete a task via natural language, Then the system should identify the correct task and update its status appropriately

- [x] T021 [US1] Create ChatService in backend/services/chat_service.py
- [x] T022 [US1] Implement conversation lookup/creation in ChatService
- [x] T023 [US1] Implement message history fetching in ChatService
- [x] T024 [US1] Implement user message storage in ChatService
- [x] T025 [US1] Implement assistant response storage in ChatService
- [x] T026 [US1] Create TodoTools in backend/services/todo_tools.py with add_task function
- [x] T027 [US1] [P] Create TodoTools with list_tasks function in backend/services/todo_tools.py
- [x] T028 [US1] [P] Create TodoTools with update_task function in backend/services/todo_tools.py
- [x] T029 [US1] [P] Create TodoTools with complete_task function in backend/services/todo_tools.py
- [x] T030 [US1] [P] Create TodoTools with delete_task function in backend/services/todo_tools.py
- [x] T031 [US1] Create TodoAgent in backend/agents/todo_agent.py
- [x] T032 [US1] Configure agent system prompt for todo management in TodoAgent
- [x] T033 [US1] Connect agent to backend todo tools for task operations
- [x] T034 [US1] Create POST /api/v1/chat endpoint in backend/api/v1/chat.py
- [x] T035 [US1] Implement request validation for chat endpoint
- [x] T036 [US1] Implement response formatting for chat endpoint
- [x] T037 [US1] Add tool call metadata capture to chat endpoint
- [ ] T038 [US1] [P] Create unit tests for TodoAgent in backend/tests/unit/test_todo_agent.py
- [ ] T039 [US1] [P] Create unit tests for ChatService in backend/tests/unit/test_chat_service.py
- [ ] T040 [US1] [P] Create integration tests for chat API in backend/tests/integration/test_chat_api.py
- [ ] T041 [US1] Test natural language task creation functionality

---

## Phase 4: [US2] Persistent Conversation Context

**Goal**: Maintain conversation context across multiple requests and server restarts

**Independent Test**: Can have conversation across multiple API calls with context maintained, and can continue after server restart

**Acceptance**:
- Given a user is in an ongoing conversation with the chatbot, When they make subsequent requests, Then the system should maintain context from previous exchanges
- Given a server restart occurs, When a user continues their conversation, Then the system should reconstruct the conversation context from the database and continue appropriately

- [x] T042 [US2] Enhance conversation replay logic in ChatService to fetch full history
- [x] T043 [US2] Implement conversation context reconstruction for agent from database
- [x] T044 [US2] Create GET /api/v1/conversations/{conversation_id}/messages endpoint
- [x] T045 [US2] Add pagination support to message history endpoint
- [x] T046 [US2] Implement conversation history formatting for agent consumption
- [ ] T047 [US2] [P] Create unit tests for conversation persistence in backend/tests/unit/test_conversation_model.py
- [ ] T048 [US2] [P] Create integration tests for conversation persistence
- [ ] T049 [US2] Test conversation persistence across server restarts
- [ ] T050 [US2] Verify conversation context is correctly reconstructed after restart

---

## Phase 5: [US3] Secure Authenticated Access

**Goal**: Enforce Better Auth authentication and user data isolation

**Independent Test**: Authenticated requests work properly, unauthenticated requests are rejected, users only see their own data

**Acceptance**:
- Given a user makes an authenticated request to the chat endpoint, When they ask about their tasks, Then they should only see their own tasks and not others'
- Given an unauthenticated request is made to the chat endpoint, When the request is processed, Then it should be rejected with appropriate authentication error

- [x] T051 [US3] Create authentication service in backend/services/auth_service.py
- [x] T052 [US3] Implement user_id verification in chat endpoint
- [x] T053 [US3] Add authorization checks to prevent cross-user data access
- [x] T054 [US3] Add conversation ownership verification in ChatService
- [ ] T055 [US3] [P] Create unit tests for authentication in backend/tests/unit/test_auth_service.py
- [ ] T056 [US3] [P] Create integration tests for authentication
- [ ] T057 [US3] Test authentication with valid and invalid tokens
- [ ] T058 [US3] Verify user data isolation between different users

---

## Phase 6: Error Handling & Resilience

**Goal**: Ensure system handles error conditions gracefully

- [ ] T059 Add error handling for OpenAI API failures in TodoAgent
- [ ] T060 [P] Add error handling for database connection issues
- [ ] T061 [P] Add error handling for tool execution failures
- [ ] T062 [P] Create error response formatting for chat endpoint
- [ ] T063 [P] Implement graceful degradation when MCP tools unavailable
- [ ] T064 Add comprehensive logging for debugging
- [ ] T065 [P] Create error contract tests in backend/tests/contract/test_error_contract.py

---

## Phase 7: Statelessness & Safety Validation

**Goal**: Verify all statelessness constraints and safety requirements are met

- [ ] T066 Verify server restart does not break existing conversations
- [ ] T067 Verify horizontal scalability assumptions (no shared memory/state)
- [ ] T068 Confirm no in-memory session usage in any component
- [ ] T069 Verify MCP tools are idempotent where applicable
- [ ] T070 [P] Create stateless compliance tests
- [ ] T071 Test concurrent user sessions without interference

---

## Phase 8: Documentation & Finalization

**Goal**: Complete documentation and prepare for review

- [ ] T072 Update README.md in backend with chatbot setup instructions
- [ ] T073 Document environment variables setup (OpenAI API key, DB connection)
- [ ] T074 Document request lifecycle: user → API → agent → tools → DB
- [ ] T075 Create agent behavior specification in specs/agent-behavior.md
- [ ] T076 [P] Prepare Phase III review checklist
- [ ] T077 Verify Phase II app remains untouched by Phase III changes
- [ ] T078 Test complete end-to-end functionality: natural language → agent → tools → DB → response

---

## Task Breakdown Summary

- **Total Tasks**: 78
- **Setup Tasks**: 10 (T001-T010)
- **Foundational Tasks**: 10 (T011-T020)
- **US1 (Natural Language Todo Management)**: 21 (T021-T041)
- **US2 (Persistent Conversation Context)**: 10 (T042-T050)
- **US3 (Secure Authenticated Access)**: 8 (T051-T058)
- **Error Handling Tasks**: 7 (T059-T065)
- **Validation Tasks**: 3 (T066-T071)
- **Documentation Tasks**: 7 (T072-T078)