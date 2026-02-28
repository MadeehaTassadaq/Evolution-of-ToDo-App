---
id: 002
title: chatkit-integration-plan
stage: plan
date: 2026-02-26
surface: cli
model: glm-4.6
feature: 001-chatkit-integration
branch: 001-chatkit-integration
user: madeeha
command: /sp.plan
labels: [plan, chatkit, integration]
links:
  spec: ../spec.md
  ticket:
  adr:
  pr:
files:
  - specs/001-chatkit-integration/plan.md
  - specs/001-chatkit-integration/data-model.md
  - specs/001-chatkit-integration/quickstart.md
  - specs/001-chatkit-integration/research/chatkit-protocol.md
  - specs/001-chatkit-integration/contracts/chatkit-api.md
  - specs/001-chatkit-integration/contracts/mcp-tools.md
tests:
  - Constitution validation (all checks pass)
  - Architecture design review
  - API contract completeness
  - Data model normalization
---

## Prompt

/sp.plan Components:
  - Frontend (Next.js): ChatKitOfficialWidget.tsx uses { Chat } from '@openai/chatkit'; connects to backend serverUrl.
  - Backend (FastAPI): /api/v1/chatkit/session (POST: creates session, returns client_secret and thread_id).
    - /mcp (MCP server mount for tools).
    - Agent: Use OpenAI Agents SDK with model="gpt-4o", tools from MCP, instructions: "Manage Todo list using provided tools."
  - Database: SQLModel models for Conversation (id, user_id, created_at) and Message (id, conversation_id, role, content).
- Interfaces: Frontend sends authToken to backend; backend verifies JWT, runs agent, persists messages.

## Response snapshot

Created comprehensive implementation plan for ChatKit integration.

**Plan Structure**:
- Summary: Technical approach overview
- Technical Context: Dependencies, performance goals, constraints
- Constitution Check: All gates pass (statelessness, separation of concerns, API contracts, data model isolation)
- Project Structure: Modified Phase II code paths
- Phase 0: Research tasks (ChatKit protocol, Agents SDK, MCP tools)
- Phase 1: Design tasks (database schema, API contracts, MCP implementation, frontend integration)
- Phase 2: Implementation tasks (detailed breakdown for /sp.tasks)

**Key Deliverables Created**:
1. `plan.md` - Master implementation plan
2. `data-model.md` - Database schema (conversations, messages tables)
3. `quickstart.md` - Developer onboarding guide
4. `research/chatkit-protocol.md` - ChatKit protocol documentation
5. `contracts/chatkit-api.md` - REST and WebSocket API specifications
6. `contracts/mcp-tools.md` - MCP tool definitions (add_task, list_tasks, update_task, complete_task, delete_task)

**Architecture Decisions**:
- Use official `@openai/chatkit-react` package (no custom UI)
- WebSocket for chat streaming (not SSE)
- Custom backend mode (OpenAI Agents SDK on backend)
- Stateless design with database-backed conversation persistence
- 30-day message retention policy
- MCP tools call existing Phase II task endpoints (no direct DB access)

**Integration Points**:
- Frontend: Modify `layout.tsx` to add ChatKitProvider, replace custom widget
- Backend: Add `/api/v1/chatkit/` router with WebSocket endpoint
- Database: Add conversations and messages tables to Neon PostgreSQL
- Auth: Use existing Better Auth JWT tokens

**Compliance**: All constitution checks passed - architecture is stateless, has clear separation of concerns, well-defined API contracts, and isolated data models.

## Outcome

- ✅ Impact: Complete implementation plan with all design artifacts, ready for task generation
- 🧪 Tests: Constitution validation passed (statelessness, separation of concerns, API contracts, data model isolation)
- 📁 Files: Created 6 design documents (plan, data-model, quickstart, research, 2 contracts)
- 🔁 Next prompts: /sp.tasks to generate detailed implementation tasks
- 🧠 Reflection: Plan successfully bridges user requirements with technical implementation. Key insight: Phase III reference code can be reused but needs integration into Phase II backend (not separate service). Architecture maintains statelessness by storing conversations in database and using thread_id for continuity.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL):
  - Constitution check: PASS (all 4 categories compliant)
  - Statelessness: PASS (WebSocket stateless, thread_id for continuity)
  - Separation of Concerns: PASS (MCP tools isolated from UI)
  - API Contracts: PASS (REST for session, WebSocket for chat)
  - Data Model Isolation: PASS (user-scoped conversations/messages)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
