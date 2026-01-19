---
id: 008
title: Fix Natural Language Task Completion
stage: green
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: 004-chatkit-mcp-chatbot
branch: 004-chatkit-mcp-chatbot
user: madeeha
command: implement plan
labels: ["natural-language", "task-completion", "bug-fix", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/services/todo_service.py
  - backend/src/services/todo_tools.py
  - backend/src/api/v1/chatkit.py
  - backend/src/agents/todo_agent.py
tests:
  - Manual verification: "complete the groceries task" should work
---

## Prompt

Implement the following plan:

# Implementation Plan: Fix Natural Language Task Completion

**Branch**: `004-chatkit-mcp-chatbot`
**Date**: 2026-01-19
**Issue**: Chatbot cannot complete tasks by title (natural language) - only by UUID

## Problem Summary

The chatbot cannot respond to natural language commands like "complete the groceries task" because:
1. `TodoService` only has `get_todo_by_id()` - no title lookup
2. `TodoTools.complete_task()` only accepts `task_id: UUID` - no `task_title` parameter
3. `chatkit.py` uses `TodoTools` for tool execution, not the MCP server which does support title lookup

## Implementation Tasks

### Task 1: Add `get_todo_by_title` to TodoService
### Task 2: Update `TodoTools.complete_task` to Support Title
### Task 3: Update `TodoTools.update_task` to Support Title
### Task 4: Update `TodoTools.delete_task` to Support Title
### Task 5: Fix `SessionLocal` Bug in chatkit.py
### Task 6: Fix `eval()` Security Vulnerability

## Response snapshot

Successfully implemented all 6 tasks:

1. **TodoService.get_todo_by_title()** - Added new method with case-insensitive partial matching for natural language support (exact match first, then contains match)

2. **TodoTools.complete_task()** - Updated to accept optional `task_id` OR `task_title`, with title-based lookup when title provided

3. **TodoTools.update_task()** - Updated with same pattern as complete_task for title-based lookup

4. **TodoTools.delete_task()** - Updated with same pattern for title-based lookup

5. **chatkit.py SessionLocal fix** - Replaced all `SessionLocal()` calls with `Session(engine)` to fix undefined name error

6. **todo_agent.py security fix** - Replaced `eval()` with `json.loads()` to prevent code injection vulnerability

7. **Tool definitions updated** - Modified OpenAI tool schemas in todo_agent.py to include `task_title` parameter with appropriate descriptions for natural language use

## Outcome

- Impact: High - Users can now complete/update/delete tasks using natural language like "complete the groceries task"
- Tests: Manual verification required
- Files: 4 files modified
- Next prompts: Test with actual chatbot, verify partial matching works correctly
- Reflection: The plan was comprehensive and implementation was straightforward

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual verification pending
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add disambiguation when multiple tasks match the same title search
