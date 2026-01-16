---
id: 001
title: ChatKit MCP Chatbot Spec Creation
stage: spec
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: 004-chatkit-mcp-chatbot
branch: 004-chatkit-mcp-chatbot
user: madeeha
command: /sp.specify
labels: ["chatkit", "mcp", "todo-chatbot", "specification"]
links:
  spec: specs/004-chatkit-mcp-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-chatkit-mcp-chatbot/spec.md
  - specs/004-chatkit-mcp-chatbot/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

# Phase III Specification: Todo AI Chatbot with ChatKit + MCP

## Objective
Build a production-ready AI-powered chatbot that allows users to manage Todo tasks using natural language. The chatbot must use OpenAI ChatKit for the frontend UI, OpenAI Agents SDK for AI reasoning, and an MCP (Model Context Protocol) server to expose task operations as tools. The backend must be stateless and persist all conversation and task state in the database.

---

## Integration Decision
Use **ChatKit full protocol integration**.

- Frontend: OpenAI ChatKit UI
- Backend: FastAPI with ChatKit-compatible `/api/chat` endpoint
- AI: OpenAI Agents SDK
- Tools: MCP Server using Official MCP SDK

No custom chat UI should be maintained.

---

## Required ChatKit Functionalities

### 1. Hosted ChatKit UI
ChatKit must provide:
- Message input box
- Streaming assistant responses
- Tool call visualization (optional but supported)
- Conversation persistence via backend
- Auth-aware session handling

ChatKit UI must only communicate with:

## Response snapshot

Created feature specification for Todo AI Chatbot with ChatKit + MCP integration:

- **Branch**: `004-chatkit-mcp-chatbot`
- **Spec file**: `specs/004-chatkit-mcp-chatbot/spec.md`
- **Checklist**: `specs/004-chatkit-mcp-chatbot/checklists/requirements.md`

Defined 6 user stories with priorities:
- P1: Task creation, Task listing
- P2: Task completion, Task updates, Conversation persistence
- P3: Task deletion

15 functional requirements covering chat interface, task CRUD operations, persistence, authentication, streaming responses, and error handling.

8 measurable success criteria focused on response times, accuracy, and user experience.

All validation checklist items passed. Ready for `/sp.clarify` or `/sp.plan`.

## Outcome

- Impact: Created complete feature specification with user stories, requirements, success criteria
- Tests: N/A (specification phase)
- Files: 2 files created (spec.md, requirements.md checklist)
- Next prompts: `/sp.clarify` for refinement or `/sp.plan` for architecture planning
- Reflection: User provided detailed input which allowed spec creation without clarification questions

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed successfully
- Graders run and results (PASS/FAIL): Manual validation checklist - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
