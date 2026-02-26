---
id: 009
title: Fix Task Completion Error Handling
stage: green
date: 2026-01-20
surface: agent
model: claude-opus-4-5-20251101
feature: 004-chatkit-mcp-chatbot
branch: 004-chatkit-mcp-chatbot
user: madeeha
command: implement plan
labels: ["bugfix", "error-handling", "chatbot", "task-completion"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase_3_chatbot/backend/src/api/v1/chat.py
  - phase_3_chatbot/backend/src/agents/todo_agent.py
  - phase_3_chatbot/backend/src/mcp_tools/server.py
tests:
  - Manual verification required via API/UI
---

## Prompt

Implement the following plan:

# Fix: Task Completion Not Working in ToDo Chatbot

## Problem Summary
When users ask the chatbot to mark a task as completed, it returns **"Unknown error"** instead of actually completing the task or showing the real error message.

**Confirmed symptom:** Shows "Unknown error" message

## Root Causes Identified

### Issue 1: Error Key Mismatch (Critical Bug)
The chat endpoint accesses errors using `result.get('error', 'Unknown error')` but `todo_tools.py` returns errors with `error_message` key.

### Issue 2: Agent System Prompt Lacks Title-based Guidance
The system prompt doesn't explicitly tell the agent to use `task_title` parameter when users refer to tasks by name.

### Issue 3: MCP Server Schema Inconsistency
The MCP server schema still requires `task_id`, but `task_title` is a valid alternative.

## Response snapshot

Implemented all three fixes as planned:

**Fix 1: Corrected error key access in chat.py (4 locations)**
- Changed `result.get('error', 'Unknown error')` to `result.get('error_message', result.get('error', 'Unknown error'))`
- Also enhanced complete_task success message to include task title

**Fix 2: Enhanced agent system prompt in todo_agent.py**
- Added explicit guidance for task identification using `task_title` parameter
- Added examples showing how to use task_title for natural language requests

**Fix 3: Updated MCP server schema in server.py**
- Changed `required: ["task_id"]` to `required: []` for complete_task, update_task, and delete_task
- Updated descriptions to clarify task_title usage for natural language matching

## Outcome

- Impact: Critical bugfix - users will now see actual error messages instead of "Unknown error"
- Tests: Manual verification via API or UI required
- Files: 3 files modified (chat.py, todo_agent.py, server.py)
- Next prompts: Test the chatbot with various task completion scenarios
- Reflection: Error key mismatch is a common integration bug - consider adding type checking or shared response schemas

## Evaluation notes (flywheel)

- Failure modes observed: Error key mismatch between services caused silent failures
- Graders run and results (PASS/FAIL): Not yet verified
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run end-to-end test with chatbot to verify fix
