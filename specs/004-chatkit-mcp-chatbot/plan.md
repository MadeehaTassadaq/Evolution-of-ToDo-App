# Implementation Plan: Todo AI Chatbot with ChatKit + MCP

**Branch**: `004-chatkit-mcp-chatbot` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-chatkit-mcp-chatbot/spec.md`

## Summary

Build a production-ready AI chatbot that enables natural language task management using OpenAI ChatKit for the frontend UI, ChatKit Python SDK for the backend protocol, OpenAI Agents SDK for AI reasoning, and MCP (Model Context Protocol) for exposing task operations as tools. The backend remains stateless with all state persisted in PostgreSQL.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI >=0.104.1, openai-chatkit, openai-agents, mcp >=1.25
**Storage**: PostgreSQL (Neon) via SQLModel
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (Docker-compatible)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <5s task creation, <3s task listing, 100 concurrent users
**Constraints**: Stateless backend, streaming responses, JWT authentication
**Scale/Scope**: Single-user task management, 1000s of tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Specification First | PASS | spec.md created and approved before planning |
| Agentic Implementation Only | PASS | All code will be generated via Claude Code |
| Phase Isolation | PASS | Work confined to phase_3_chatbot directory |
| Traceable Tasks | PENDING | tasks.md to be generated via /sp.tasks |
| Testable Acceptance | PASS | Success criteria defined in spec with metrics |
| Immutable Specs | PASS | spec.md ratified, changes require new revision |

## Project Structure

### Documentation (this feature)

```text
specs/004-chatkit-mcp-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output - COMPLETE
├── data-model.md        # Phase 1 output - COMPLETE
├── quickstart.md        # Phase 1 output - COMPLETE
├── contracts/           # Phase 1 output - COMPLETE
│   ├── chatkit-api-contract.yaml
│   └── mcp-tools-contract.yaml
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
phase_3_chatbot/
├── backend/
│   ├── main.py                    # FastAPI app with lifespan
│   ├── pyproject.toml             # Dependencies
│   ├── api/
│   │   ├── router.py              # Route registration
│   │   └── v1/
│   │       ├── auth.py            # Auth endpoints (existing)
│   │       ├── chat.py            # Legacy chat (to deprecate)
│   │       └── chatkit.py         # ChatKit endpoint (NEW)
│   ├── services/
│   │   ├── auth_service.py        # JWT handling (existing)
│   │   ├── chatkit_server.py      # ChatKitServer implementation (NEW)
│   │   └── chatkit_store.py       # Database-backed Store (NEW)
│   ├── agents/
│   │   └── todo_agent.py          # Agent with MCP tools (UPDATE)
│   ├── mcp_tools/
│   │   ├── __init__.py            # MCP package init (NEW)
│   │   └── server.py              # MCP tool definitions (NEW)
│   └── database/
│       ├── session.py             # DB connection (existing)
│       └── models/
│           ├── user.py            # User model (existing)
│           ├── task.py            # Task model (verify/update)
│           ├── conversation.py    # Conversation model (verify)
│           └── message.py         # Message model (update for tool_calls)
├── frontend/
│   ├── package.json               # Dependencies (ChatKit added)
│   ├── app/
│   │   ├── page.js                # Main page with ChatKit (UPDATE)
│   │   └── login/page.js          # Login page (existing)
│   └── components/
│       └── ChatKitPanel.tsx       # ChatKit wrapper component (NEW)
└── tests/
    ├── test_chatkit.py            # ChatKit endpoint tests (NEW)
    └── test_mcp_tools.py          # MCP tool tests (NEW)
```

**Structure Decision**: Web application structure with separate frontend and backend directories, leveraging existing infrastructure while adding ChatKit and MCP components.

## Implementation Phases

### Phase 1: Backend ChatKit Infrastructure

1. Add new dependencies to `pyproject.toml`
2. Create `ChatKitServer` subclass in `services/chatkit_server.py`
3. Create database-backed `Store` in `services/chatkit_store.py`
4. Create `/api/v1/chatkit` endpoint with auth integration

### Phase 2: MCP Tools Implementation

1. Create `mcp_tools/server.py` with FastMCP
2. Implement 5 tools: add_task, list_tasks, complete_task, update_task, delete_task
3. Wire tools to existing database models
4. Add user context injection for multi-tenancy

### Phase 3: Agent Integration

1. Update `agents/todo_agent.py` to use MCP tools
2. Configure streaming response handling
3. Add tool execution logging
4. Test agent with ChatKit protocol

### Phase 4: Frontend ChatKit Integration

1. Create `ChatKitPanel.tsx` component
2. Update `page.js` to use ChatKit instead of custom UI
3. Configure authentication flow
4. Remove deprecated custom chat UI

### Phase 5: Testing & Validation

1. Write integration tests for ChatKit endpoint
2. Write unit tests for MCP tools
3. End-to-end testing with real OpenAI API
4. Validate against success criteria

## Complexity Tracking

No Constitution Check violations requiring justification.

## Dependencies

| Dependency | Purpose | Added In |
|------------|---------|----------|
| openai-chatkit | ChatKit Python SDK | Phase 1 |
| openai-agents | Agent framework | Phase 1 |
| mcp | MCP Python SDK | Phase 2 |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| ChatKit SDK instability (new in 2025) | Pin versions, use official samples as reference |
| MCP integration complexity | Start with direct tool registration as fallback |
| Streaming errors | Implement retry logic, graceful degradation |

## Success Metrics

From spec success criteria:

- SC-001: Task creation in <5 seconds ✓
- SC-002: Task listing in <3 seconds ✓
- SC-003: 90% command accuracy ✓
- SC-004: 100 concurrent users ✓
- SC-005: History loads in <2 seconds ✓

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Begin Phase 1 implementation
3. Iterate through phases with testing at each stage
