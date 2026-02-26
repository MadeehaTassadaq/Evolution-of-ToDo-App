---
id: 3
title: todo-ai-chatbot-tasks
stage: tasks
date: 2026-01-10
surface: agent
model: claude-opus-4-5-20251101
feature: todo-ai-chatbot
branch: 003-todo-ai-chatbot
user: madeeha
command: "/sp.tasks Phase III: Todo AI Chatbot (Agentic, MCP-based)"
labels: [tasks, ai, chatbot, mcp, database]
links:
  spec: ../specs/003-todo-ai-chatbot/spec.md
  plan: ../specs/003-todo-ai-chatbot/plan.md
  tasks: ../specs/003-todo-ai-chatbot/tasks.md
  ticket: null
  adr: null
  pr: null
files:
  - ../specs/003-todo-ai-chatbot/tasks.md
tests:
  - tasks_generated: true
  - task_format_valid: true
  - user_stories_mapped: true
  - dependencies_defined: true
outcome: Success
evaluation: Complete task breakdown generated for Todo AI Chatbot implementation
---

## Prompt

/sp.tasks Phase III: Todo AI Chatbot (Agentic, MCP-based)

Global Constraint:
- All Phase III code MUST live under /phase_3_chatbot
- No changes allowed outside this folder
- Backend, MCP server, frontend, and database code MUST be isolated

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 0: Project Structure Setup
━━━━━━━━━━━━━━━━━━━━━━

- Create root directory: phase_3_chatbot/
- Create subfolders:
  - phase_3_chatbot/backend
  - phase_3_chatbot/mcp_server
  - phase_3_chatbot/frontend
  - phase_3_chatbot/database
  - phase_3_chatbot/specs

- Ensure Phase II code is imported or referenced, not duplicated
- Document folder responsibilities in specs/architecture.md

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 1: Database Layer (Stateless Persistence)
━━━━━━━━━━━━━━━━━━━━━━

- Define SQLModel models:
  - Conversation
  - Message
- Reuse existing Task model via shared import or DB schema
- Add foreign key relationships:
  - Conversation → User
  - Message → Conversation
- Create migration scripts inside:
  - phase_3_chatbot/database/migrations
- Verify restart-safe persistence

Deliverable:
- DB schema supports conversation replay
- No in-memory state required

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 2: Backend Chat API (FastAPI + Agents SDK)
━━━━━━━━━━━━━━━━━━━━━━

Location:
- phase_3_chatbot/backend

Tasks:
- Create stateless POST /api/{user_id}/chat endpoint
- Enforce Better Auth authentication
- Implement conversation lookup or creation
- Fetch full message history from database
- Store incoming user message
- Construct agent input messages
- Integrate OpenAI Agents SDK runner
- Capture MCP tool calls (metadata only)
- Store assistant response
- Return structured response:
  - conversation_id
  - response
  - tool_calls

Constraints:
- No global variables
- No cached memory
- No direct DB mutation by agent

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 3: Agent Configuration & Behavior
━━━━━━━━━━━━━━━━━━━━━━

Location:
- phase_3_chatbot/backend/agent

Tasks:
- Define system prompt for Todo chatbot
- Configure tool awareness (no hardcoded logic)
- Enforce:
  - Tool-only mutations
  - Friendly confirmations
  - Graceful error handling
- Ensure agent is deterministic and restart-safe

Deliverable:
- Agent behavior spec in specs/agent.spec.md

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 4: MCP Server Implementation
━━━━━━━━━━━━━━━━━━━━━━

Location:
- phase_3_chatbot/mcp_server

Tasks:
- Initialize MCP server using Official MCP SDK
- Implement MCP tools:
  - add_task
  - list_tasks
  - update_task
  - complete_task
  - delete_task
- Enforce:
  - Stateless execution
  - Explicit parameters
  - Structured JSON outputs
- Persist all changes via database
- Implement structured error responses

Deliverables:
- MCP tool specs in specs/mcp-tools.spec.md
- Tool versioning strategy documented

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 5: Frontend Chat UI (ChatKit)
━━━━━━━━━━━━━━━━━━━━━━

Location:
- phase_3_chatbot/frontend

Tasks:
- Set up OpenAI ChatKit UI
- Integrate Better Auth session
- Connect UI to /api/{user_id}/chat endpoint
- Render message history
- Display tool action confirmations
- Handle loading and error states
- Configure domain allowlist support

Constraints:
- No business logic in frontend
- All intelligence delegated to backend agent

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 6: Statelessness & Safety Validation
━━━━━━━━━━━━━━━━━━━━━━

Tasks:
- Verify server restart does not break chats
- Verify horizontal scalability assumptions
- Verify no in-memory session usage
- Verify tools are idempotent where applicable

Deliverable:
- Stateless compliance checklist in specs/stateless.md

━━━━━━━━━━━━━━━━━━━━━━
TASK GROUP 7: Documentation & Finalization
━━━━━━━━━━━━━━━━━━━━━━

Tasks:
- Write README.md inside phase_3_chatbot
- Document setup steps (env vars, DB, ChatKit)
- Document request lifecycle
- Document agent ↔ MCP ↔ DB flow
- Prepare Phase III review checklist

━━━━━━━━━━━━━━━━━━━━━━
EXIT CRITERIA
━━━━━━━━━━━━━━━━━━━━━━

- Natural language task management works end-to-end
- Agent uses MCP tools correctly
- Conversations resume after restart
- Backend, MCP, frontend fully isolated
- Phase II app remains untouched

## Response

Generated comprehensive task breakdown for Todo AI Chatbot implementation with 78 tasks organized across 9 phases:

Phase 1: Project Structure Setup (10 tasks) - Creating isolated Phase III directory structure
Phase 2: Database Layer (9 tasks) - SQLModel models for conversation persistence
Phase 3: MCP Server Implementation (10 tasks) - MCP tools for task operations
Phase 4: US1 Natural Language Todo Management (15 tasks) - Core AI chat functionality
Phase 5: US2 Persistent Conversation Context (7 tasks) - Conversation state management
Phase 6: US3 Secure Authenticated Access (7 tasks) - Better Auth integration
Phase 7: Frontend Chat UI (8 tasks) - ChatKit interface
Phase 8: Statelessness & Safety Validation (6 tasks) - Compliance verification
Phase 9: Documentation & Finalization (6 tasks) - Documentation and review

All tasks follow the required format with proper IDs, story labels, and file paths. Tasks are organized by user stories as required, with dependencies and parallel execution opportunities identified. The implementation strategy focuses on the MVP scope of User Story 1 first.