---
id: 2
title: AI Chatbot Integration
stage: spec
date: 2026-01-13
surface: agent
model: claude-opus-4-5-20251101
feature: 003-todo-ai-chatbot
branch: 003-todo-ai-chatbot
user: madeeha
command: /sp.specify
labels: ["ai", "chatbot", "integration", "specification"]
links:
  spec: /home/madeeha/Documents/Evolution-of-ToDo-App/specs/003-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - /home/madeeha/Documents/Evolution-of-ToDo-App/specs/003-todo-ai-chatbot/spec.md
 - /home/madeeha/Documents/Evolution-of-ToDo-App/history/prompts/general/002-ai-chatbot-integration.general.prompt.md
tests:
 - /home/madeeha/Documents/Evolution-of-ToDo-App/specs/003-todo-ai-chatbot/tasks.md
---

## Prompt

# Specification: Phase 2 Todo Web App – AI Chatbot Integration

## Context
We already have a working Phase 2 Todo Web Application with:
- Next.js App Router frontend
- FastAPI backend
- Better Auth for authentication
- Neon serverless PostgreSQL database
- Deployed frontend (Vercel) and backend (cloud-ready)

The application includes:
- User authentication (login/signup)
- Todo CRUD functionality
- Protected routes (/tasks)

This specification adds an **AI-powered Todo Chatbot** using:
- OpenAI Agent SDK
- Existing Better Auth session
- Same Neon database
- ChatKit UI embedded in the frontend

No existing functionality should be broken.

---

## Goals
1. Integrate an AI chatbot into the existing Todo app
2. Use the **same authenticated user context**
3. Allow chatbot to:
   - Read todos
   - Create todos
   - Update todos
   - Delete todos
   - Answer questions about todos
4. Persist chat history per user
5. Embed ChatKit UI into the existing frontend

---

## Non-Goals
- No new authentication system
- No separate chatbot database
- No separate frontend app
- No replacement of existing APIs
- No experimental frameworks

---

## High-Level Architecture

Frontend (Next.js):
- Existing Todo pages remain unchanged
- Add a Chat widget using ChatKit UI
- Chat widget authenticates using Better Auth session
- Chat messages sent to FastAPI chatbot endpoint

Backend (FastAPI):
- Existing Todo APIs untouched
- Add `/api/chat` endpoint
- Use OpenAI Agent SDK
- Agent has tools to call Todo services
- Agent scoped to authenticated user
- Chat history stored in Neon DB

Database (Neon PostgreSQL):
- Existing tables remain
- Add `chat_sessions` and `chat_messages` tables

---

## Authentication & Security

- Use **existing Better Auth secret**
- Extract user identity from:
  - Session cookie
  - Authorization header (Bearer token)
- Chatbot requests MUST fail if user is unauthenticated
- Agent actions must be scoped to `user_id`

---

## Backend Requirements (FastAPI)

### New Router
Create:

## Response snapshot

I analyzed the existing project structure and found that there is already a specification for the "Todo AI Chatbot" feature in `/home/madeeha/Documents/Evolution-of-ToDo-App/specs/003-todo-ai-chatbot/spec.md`. The specification covers the AI chatbot integration with OpenAI Agents SDK, conversation persistence, and authentication requirements. The feature branch `003-todo-ai-chatbot` is already active, and implementation work appears to be in progress with changes to multiple files including agents/todo_agent.py, main.py, and services/auth_service.py.

## Outcome

- ✅ Impact: Identified existing specification and current implementation status for AI chatbot integration
- 🧪 Tests: N/A - Documentation task
- 📁 Files: Found existing spec.md and identified current implementation files
- 🔁 Next prompts: Continue with planning or implementation based on existing spec
- 🧠 Reflection: The feature is already specified and implementation is underway

## Evaluation notes (flywheel)

- Failure modes observed: None - successfully identified existing work
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with implementation based on existing specification