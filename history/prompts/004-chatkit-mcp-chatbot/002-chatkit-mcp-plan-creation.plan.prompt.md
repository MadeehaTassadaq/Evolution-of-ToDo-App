---
id: 002
title: ChatKit MCP Chatbot Plan Creation
stage: plan
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: 004-chatkit-mcp-chatbot
branch: 004-chatkit-mcp-chatbot
user: madeeha
command: /sp.plan
labels: ["chatkit", "mcp", "architecture", "planning"]
links:
  spec: specs/004-chatkit-mcp-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-chatkit-mcp-chatbot/plan.md
  - specs/004-chatkit-mcp-chatbot/research.md
  - specs/004-chatkit-mcp-chatbot/data-model.md
  - specs/004-chatkit-mcp-chatbot/quickstart.md
  - specs/004-chatkit-mcp-chatbot/contracts/chatkit-api-contract.yaml
  - specs/004-chatkit-mcp-chatbot/contracts/mcp-tools-contract.yaml
tests:
  - N/A (planning phase)
---

## Prompt

/sp.plan

## Response snapshot

Executed the `/sp.plan` command to create implementation planning artifacts for the Todo AI Chatbot with ChatKit + MCP feature.

### Phase 0: Research (Complete)
Generated `research.md` with 6 key decisions:
1. **Frontend**: OpenAI ChatKit React (`@openai/chatkit-react`)
2. **Backend Protocol**: ChatKit Python SDK with self-hosted backend
3. **MCP Architecture**: MCP Python SDK with FastMCP for task tools
4. **Agent Framework**: OpenAI Agents SDK with MCP integration
5. **Data Persistence**: SQLModel with PostgreSQL, implementing ChatKit Store interface
6. **Authentication**: JWT integration via context injection

### Phase 1: Design (Complete)
Generated planning artifacts:
- `data-model.md`: Entity schemas for User, Task, Conversation, Message with ChatKit mappings
- `contracts/chatkit-api-contract.yaml`: OpenAPI spec for ChatKit protocol endpoint
- `contracts/mcp-tools-contract.yaml`: MCP tool definitions (add_task, list_tasks, complete_task, update_task, delete_task)
- `quickstart.md`: Setup guide with verification steps
- `plan.md`: Complete implementation plan with 5 phases

### Constitution Check
All 6 principles verified:
- Specification First: PASS
- Agentic Implementation Only: PASS
- Phase Isolation: PASS
- Traceable Tasks: PENDING (awaiting /sp.tasks)
- Testable Acceptance: PASS
- Immutable Specs: PASS

### Technical Stack
- Python 3.11 + FastAPI >=0.104.1
- openai-chatkit, openai-agents, mcp >=1.25
- PostgreSQL (Neon) via SQLModel
- Next.js frontend with @openai/chatkit-react

## Outcome

- Impact: Created complete implementation planning artifacts (7 files)
- Tests: N/A (planning phase)
- Files: 7 files created/updated
- Next prompts: `/sp.tasks` to generate implementation tasks
- Reflection: Research phase consolidated ChatKit Python SDK and MCP integration patterns from official documentation

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - 5/6 PASS, 1 PENDING
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
