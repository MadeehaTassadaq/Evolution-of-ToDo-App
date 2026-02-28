# Tasks: OpenAI ChatKit Integration for Todo Chatbot

**Input**: Design documents from `/specs/001-chatkit-integration/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT explicitly requested in the feature specification. Test tasks are not included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **web application** with separate frontend and backend:
- Frontend: `phase_2_web_App/frontend/src/`
- Backend: `phase_2_web_App/backend/app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install frontend ChatKit package in phase_2_web_App/frontend/ (npm install @openai/chatkit-react)
- [ ] T002 Install backend dependencies in phase_2_web_App/backend/ (pip install openai mcp)
- [ ] T003 [P] Add OPENAI_API_KEY to phase_2_web_App/backend/.env
- [ ] T004 [P] Add NEXT_PUBLIC_CHATKIT_URL to phase_2_web_App/frontend/.env.local
- [ ] T005 [P] Create phase_2_web_App/backend/app/models/__init__.py for model exports

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Layer

- [ ] T006 Create phase_2_web_App/backend/app/models/conversation.py with Conversation SQLModel
- [ ] T007 [P] Create phase_2_web_App/backend/app/models/message.py with Message SQLModel
- [ ] T008 Create Alembic migration in phase_2_web_App/backend/alembic/versions/ for conversations and messages tables
- [ ] T009 Run database migration (alembic upgrade head) to create conversations and messages tables

### Backend Services Layer

- [ ] T010 Create phase_2_web_App/backend/app/services/chat_service.py with ChatService class (conversation/message CRUD)
- [ ] T011 [P] Create phase_2_web_App/backend/app/services/mcp_tools.py with MCP tools base classes
- [ ] T012 Create phase_2_web_App/backend/app/agents/todo_agent.py with TodoAgent class using OpenAI SDK

### API Routing

- [ ] T013 Create phase_2_web_App/backend/app/api/v1/__init__.py for v1 API module
- [ ] T014 Create phase_2_web_App/backend/app/api/v1/chatkit.py with session endpoint (POST /api/v1/chatkit/session)
- [ ] T015 [P] Add WebSocket handler stub in phase_2_web_App/backend/app/api/v1/chatkit.py for /api/v1/chatkit/ws

### Backend Integration

- [ ] T016 Modify phase_2_web_App/backend/app/main.py to include ChatKit router at /api/v1
- [ ] T017 [P] Update phase_2_web_App/backend/app/middleware/auth.py to handle WebSocket authentication

### Frontend Foundation

- [ ] T018 Create phase_2_web_App/frontend/src/lib/chatkit.ts with ChatKit client configuration
- [ ] T019 [P] Create phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx with ChatKitProvider wrapper
- [ ] T020 Update phase_2_web_App/frontend/src/app/layout.tsx to import and render ChatKitOfficialWidget

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks through natural language chat commands

**Independent Test**: User types "Add a task to buy groceries" into chat widget → task appears in main todo list

### MCP Tool: add_task

- [ ] T021 [P] [US1] Implement add_task MCP tool in phase_2_web_App/backend/app/services/mcp_tools.py (calls existing POST /api/tasks endpoint)
- [ ] T022 [P] [US1] Add add_task tool schema to TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T023 [US1] Wire add_task tool execution in chatkit WebSocket handler in phase_2_web_App/backend/app/api/v1/chatkit.py

### WebSocket Message Processing

- [ ] T024 [P] [US1] Implement message parsing in WebSocket handler in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T025 [P] [US1] Implement OpenAI agent invocation in phase_2_web_App/backend/app/agents/todo_agent.py (process_message method)
- [ ] T026 [US1] Implement tool_call_started event streaming in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T027 [US1] Implement tool_call_completed event streaming in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T028 [US1] Implement conversation_done event streaming in phase_2_web_App/backend/app/api/v1/chatkit.py

### Frontend Chat Widget

- [ ] T029 [US1] Replace custom ChatKitOfficialWidget with official @openai/chatkit Chat component in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx
- [ ] T030 [US1] Wire authToken from AuthContext to ChatKitProvider in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx
- [ ] T031 [US1] Configure ChatKit serverUrl in phase_2_web_App/frontend/src/lib/chatkit.ts

### Conversation Persistence

- [ ] T032 [US1] Implement conversation creation in ChatService in phase_2_web_App/backend/app/services/chat_service.py
- [ ] T033 [P] [US1] Implement message persistence in ChatService in phase_2_web_App/backend/app/services/chat_service.py
- [ ] T034 [US1] Save user messages to database in WebSocket handler in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T035 [US1] Save assistant responses to database in WebSocket handler in phase_2_web_App/backend/app/api/v1/chatkit.py

**Checkpoint**: User can create tasks via chat - MVP is functional!

---

## Phase 4: User Story 2 - View and Search Tasks via Conversation (Priority: P2)

**Goal**: Users can view and filter their tasks through natural language

**Independent Test**: User asks "Show me all my tasks" → chat displays task list

### MCP Tool: list_tasks

- [ ] T036 [P] [US2] Implement list_tasks MCP tool in phase_2_web_App/backend/app/services/mcp_tools.py (calls existing GET /api/tasks endpoint)
- [ ] T037 [P] [US2] Add list_tasks tool schema to TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T038 [US2] Add status filtering to list_tasks tool in phase_2_web_App/backend/app/services/mcp_tools.py (all/pending/completed)

### Agent Response Formatting

- [ ] T039 [US2] Implement format_tasks_for_response method in TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T040 [P] [US2] Add task count summary to list_tasks response in phase_2_web_App/backend/app/services/mcp_tools.py

**Checkpoint**: User can view tasks via chat independently

---

## Phase 5: User Story 3 - Complete and Modify Tasks via Chat (Priority: P3)

**Goal**: Users can mark tasks complete and modify task details through conversation

**Independent Test**: User types "Mark buy groceries as complete" → task status updates in main list

### MCP Tool: complete_task

- [ ] T041 [P] [US3] Implement complete_task MCP tool in phase_2_web_App/backend/app/services/mcp_tools.py (calls existing PATCH /api/tasks/{id}/complete endpoint)
- [ ] T042 [P] [US3] Add complete_task tool schema to TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T043 [US3] Add natural language task matching to complete_task in phase_2_web_App/backend/app/services/mcp_tools.py (by title)

### MCP Tool: update_task

- [ ] T044 [P] [US3] Implement update_task MCP tool in phase_2_web_App/backend/app/services/mcp_tools.py (calls existing PUT /api/tasks/{id} endpoint)
- [ ] T045 [P] [US3] Add update_task tool schema to TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T046 [US3] Add natural language task matching to update_task in phase_2_web_App/backend/app/services/mcp_tools.py (by title)

### User Confirmation for Destructive Actions

- [ ] T047 [US3] Add confirmation prompt to TodoAgent for task modifications in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T048 [US3] Implement clarification question when multiple tasks match in phase_2_web_App/backend/app/agents/todo_agent.py

**Checkpoint**: User can complete and modify tasks via chat independently

---

## Phase 6: User Story 4 - Conversation History and Context (Priority: P4)

**Goal**: Chat remembers previous conversations and maintains context across sessions

**Independent Test**: User has conversation, closes chat, reopens → sees previous messages

### Conversation History Loading

- [ ] T049 [P] [US4] Implement get_conversation_by_id in ChatService in phase_2_web_App/backend/app/services/chat_service.py
- [ ] T050 [P] [US4] Implement get_full_conversation_history in ChatService in phase_2_web_App/backend/app/services/chat_service.py
- [ ] T051 [US4] Add GET /api/v1/conversations/{thread_id}/messages endpoint in phase_2_web_App/backend/app/api/v1/chatkit.py

### Thread ID Persistence

- [ ] T052 [US4] Implement thread_id storage in frontend localStorage in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx
- [ ] T053 [P] [US4] Pass thread_id to ChatKitProvider on mount in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx
- [ ] T054 [US4] Update thread_id after conversation_done event in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx

### Context Loading in Agent

- [ ] T055 [US4] Pass conversation history to TodoAgent.process_message in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T056 [P] [US4] Update TodoAgent system prompt to include conversation context in phase_2_web_App/backend/app/agents/todo_agent.py

**Checkpoint**: User can resume conversations - chat has memory

---

## Phase 7: User Story 5 - Multi-Step Task Operations (Priority: P5)

**Goal**: Users can perform complex bulk operations through single commands

**Independent Test**: User types "Complete all my shopping tasks" → multiple tasks updated

### MCP Tool: delete_task (with bulk operations)

- [ ] T057 [P] [US5] Implement delete_task MCP tool in phase_2_web_App/backend/app/services/mcp_tools.py (calls existing DELETE /api/tasks/{id} endpoint)
- [ ] T058 [P] [US5] Add delete_task tool schema to TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T059 [US5] Add delete_completed parameter for bulk delete in phase_2_web_App/backend/app/services/mcp_tools.py
- [ ] T060 [US5] Implement natural language matching for delete_task in phase_2_web_App/backend/app/services/mcp_tools.py

### Multi-Tool Orchestration

- [ ] T061 [US5] Implement sequential tool execution in TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T062 [P] [US5] Add tool result aggregation for bulk operations in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T063 [US5] Format bulk operation summaries in TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py

### Advanced Query Handling

- [ ] T064 [US5] Add "What should I focus on today?" intent detection in TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py
- [ ] T065 [P] [US5] Implement priority-based task filtering in list_tasks for focus queries in phase_2_web_App/backend/app/services/mcp_tools.py

**Checkpoint**: User can perform complex multi-step operations via chat

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Error Handling

- [ ] T066 [P] Implement standardized error responses in WebSocket handler in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T067 [P] Add error event streaming for tool failures in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T068 Add user-friendly error messages in TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py

### WebSocket Reliability

- [ ] T069 [P] Implement WebSocket ping/pong keep-alive in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T070 [P] Add automatic reconnection logic in ChatKitOfficialWidget in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx
- [ ] T071 Implement exponential backoff for reconnection attempts in phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx

### Performance

- [ ] T072 [P] Add database query optimization (indexes) in phase_2_web_App/backend/alembic/versions/
- [ ] T073 [P] Implement response streaming for long agent responses in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T074 Add request rate limiting to ChatKit endpoints in phase_2_web_App/backend/app/main.py

### Security

- [ ] T075 [P] Add user_id validation for conversation access in ChatService in phase_2_web_App/backend/app/services/chat_service.py
- [ ] T076 [P] Sanitize user input in WebSocket handler to prevent injection in phase_2_web_App/backend/app/api/v1/chatkit.py
- [ ] T077 Add CORS configuration for ChatKit WebSocket in phase_2_web_App/backend/app/main.py

### Documentation

- [ ] T078 [P] Update README.md with ChatKit feature description in phase_2_web_App/
- [ ] T079 [P] Add environment variable documentation to .env.example in phase_2_web_App/backend/
- [ ] T080 Update quickstart.md with any setup changes discovered during implementation in specs/001-chatkit-integration/quickstart.md

### Validation

- [ ] T081 Run quickstart.md validation checklist (all steps work)
- [ ] T082 [P] Test all 5 user stories independently per spec.md acceptance scenarios
- [ ] T083 Verify constitution compliance (statelessness, separation of concerns, API contracts, data model isolation)

**Checkpoint**: Production-ready ChatKit integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): No dependencies on other user stories
  - User Story 2 (P2): No dependencies on other user stories
  - User Story 3 (P3): No dependencies on other user stories
  - User Story 4 (P4): No dependencies on other user stories
  - User Story 5 (P5): No dependencies on other user stories
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

All user stories are **independently implementable** after Foundational phase:

- **User Story 1 (P1)**: Can start after Foundational - Core task creation
- **User Story 2 (P2)**: Can start after Foundational - Task viewing
- **User Story 3 (P3)**: Can start after Foundational - Task modification
- **User Story 4 (P4)**: Can start after Foundational - Conversation history
- **User Story 5 (P5)**: Can start after Foundational - Advanced operations

### Within Each User Story

- Models before services (applicable to Foundational phase)
- Services before endpoints
- MCP tools before agent integration
- Agent integration before WebSocket streaming
- Core implementation before frontend integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T003, T004, T005 can run in parallel

**Foundational Phase (Phase 2)**:
- T006, T007 can run in parallel (different models)
- T011, T015, T017, T019 can run in parallel after T010 completes

**User Story 1 (Phase 3)**:
- T021, T022, T024, T025, T029, T032, T033 can run in parallel
- T026, T027, T028, T030, T031, T034, T035 depend on parallel tasks

**User Story 2 (Phase 4)**:
- T036, T037 can run in parallel
- T039, T040 can run in parallel

**User Story 3 (Phase 5)**:
- T041, T042, T044, T045 can run in parallel
- T043, T046, T047, T048 depend on parallel tasks

**User Story 4 (Phase 6)**:
- T049, T050, T053, T056 can run in parallel

**User Story 5 (Phase 7)**:
- T057, T058, T062, T065 can run in parallel

**Polish Phase (Phase 8)**:
- T066, T067, T069, T070, T072, T073, T075, T076, T078, T079, T082 can run in parallel

**Cross-Story Parallelization**:
- Once Foundational phase completes, all 5 user stories can be developed in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# After Foundational phase, launch these in parallel:

# MCP tool and agent setup:
Task T021: "Implement add_task MCP tool in phase_2_web_App/backend/app/services/mcp_tools.py"
Task T022: "Add add_task tool schema to TodoAgent in phase_2_web_App/backend/app/agents/todo_agent.py"

# Message processing:
Task T024: "Implement message parsing in WebSocket handler in phase_2_web_App/backend/app/api/v1/chatkit.py"
Task T025: "Implement OpenAI agent invocation in phase_2_web_App/backend/app/agents/todo_agent.py"

# Frontend:
Task T029: "Replace custom ChatKitOfficialWidget with official @openai/chatkit Chat component"

# Persistence:
Task T032: "Implement conversation creation in ChatService in phase_2_web_App/backend/app/services/chat_service.py"
Task T033: "Implement message persistence in ChatService in phase_2_web_App/backend/app/services/chat_service.py"
```

---

## Parallel Example: Foundational Phase

```bash
# After Setup phase, launch these in parallel:

# Models:
Task T006: "Create phase_2_web_App/backend/app/models/conversation.py with Conversation SQLModel"
Task T007: "Create phase_2_web_App/backend/app/models/message.py with Message SQLModel"

# Services base:
Task T011: "Create phase_2_web_App/backend/app/services/mcp_tools.py with MCP tools base classes"
Task T015: "Add WebSocket handler stub in phase_2_web_App/backend/app/api/v1/chatkit.py"
Task T017: "Update phase_2_web_App/backend/app/middleware/auth.py to handle WebSocket authentication"
Task T019: "Create phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx with ChatKitProvider wrapper"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete **Phase 1: Setup** (T001-T005)
2. Complete **Phase 2: Foundational** (T006-T020) - CRITICAL
3. Complete **Phase 3: User Story 1** (T021-T035)
4. **STOP and VALIDATE**: Test creating tasks via chat independently
5. Deploy/demo MVP

**Result**: Users can create tasks through natural language chat

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Infrastructure ready
2. **Add US1** (Phase 3) → Task creation via chat → Deploy MVP
3. **Add US2** (Phase 4) → View tasks via chat → Deploy
4. **Add US3** (Phase 5) → Modify tasks via chat → Deploy
5. **Add US4** (Phase 6) → Conversation history → Deploy
6. **Add US5** (Phase 7) → Advanced operations → Deploy
7. **Polish** (Phase 8) → Production-ready

### Parallel Team Strategy

With multiple developers after Foundational phase:

1. **Developer A**: User Story 1 (T021-T035)
2. **Developer B**: User Story 2 (T036-T040)
3. **Developer C**: User Story 3 (T041-T048)
4. **Developer D**: User Story 4 (T049-T056)
5. **Developer E**: User Story 5 (T057-T065)

All stories complete independently and integrate seamlessly.

---

## Summary

- **Total Tasks**: 83
- **Setup Tasks**: 5
- **Foundational Tasks**: 15
- **User Story 1 (P1) Tasks**: 15
- **User Story 2 (P2) Tasks**: 5
- **User Story 3 (P3) Tasks**: 8
- **User Story 4 (P4) Tasks**: 8
- **User Story 5 (P5) Tasks**: 9
- **Polish Tasks**: 18

**Parallel Opportunities**: 35 tasks marked with [P] can run in parallel within their phases

**Independent Test Criteria**:
- US1: Create task via chat → appears in task list
- US2: Ask for tasks → displays in chat
- US3: Modify/complete task via chat → updates in list
- US4: Reopen chat → shows history
- US5: Bulk operation → multiple tasks affected

**Suggested MVP Scope**: Phases 1-3 (Setup + Foundational + User Story 1) = 35 tasks

**Format Validation**: All tasks follow the checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
