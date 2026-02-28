# Test Plan: ChatKit Integration

## Test Environment

- **Frontend**: `http://localhost:3000` or `http://localhost:3001`
- **Phase II Backend**: `http://localhost:8000`
- **Phase III Backend**: `http://localhost:7860`
- **Database**: Neon PostgreSQL (shared)

## Pre-Test Checklist

### Backend Health Checks

```bash
# Phase II Backend (Task CRUD)
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

# Phase III Backend (ChatKit)
curl http://localhost:7860/health
# Expected: {"status":"healthy","service":"todo-ai-chatbot-backend",...}

# Phase III ChatKit Endpoint (should require auth)
curl http://localhost:7860/api/v1/chatkit/history
# Expected: {"detail":"Not authenticated"}
```

### Frontend Environment Check

Open browser DevTools (F12) → Console:
```javascript
// Check environment variables
console.log('ChatKit URL:', process.env.NEXT_PUBLIC_CHATKIT_URL);
console.log('Domain Key:', process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY);
console.log('Chatbot Enabled:', process.env.NEXT_PUBLIC_ENABLE_CHATBOT);

// Check auth token
console.log('Auth Token:', localStorage.getItem('authToken') || localStorage.getItem('better-auth-token'));
```

## Test Scenarios

### TC-001: Initial Page Load

**Steps:**
1. Navigate to `http://localhost:3000`
2. Login with existing account or register new one
3. Wait for page to fully load

**Expected Results:**
- [ ] Page loads without errors
- [ ] ChatKit widget appears in bottom-right corner
- [ ] Widget shows greeting message
- [ ] Widget shows suggested prompts

**Actual Results:**
-

### TC-002: Add Task via Chat

**Steps:**
1. Click on ChatKit widget
2. Type: "Add a task to buy groceries"
3. Press Enter

**Expected Results:**
- [ ] AI acknowledges the request
- [ ] Tool call event shows "add_task" starting
- [ ] Tool call event shows successful completion
- [ ] AI confirms task was added
- [ ] Task appears in main todo list (refresh page to verify)

**Test Data:**
- Task title: "buy groceries"
- Expected status: "pending"

### TC-003: List All Tasks

**Steps:**
1. Click on ChatKit widget
2. Type: "Show me all my tasks"
3. Press Enter

**Expected Results:**
- [ ] AI calls list_tasks tool
- [ ] All tasks are displayed in chat
- [ ] Tasks show correct status indicators
- [ ] Task details are accurate

### TC-004: List Pending Tasks

**Steps:**
1. Click on ChatKit widget
2. Type: "What do I need to do?"
3. Press Enter

**Expected Results:**
- [ ] AI calls list_tasks with status_filter="pending"
- [ ] Only pending tasks are shown
- [ ] Completed tasks are not displayed

### TC-005: Complete Task by Title

**Steps:**
1. Create a task titled "Test Task"
2. Click on ChatKit widget
3. Type: "Mark the Test Task as complete"
4. Press Enter

**Expected Results:**
- [ ] AI calls complete_task with task_title="Test Task"
- [ ] Tool executes successfully
- [ ] AI confirms task was completed
- [ ] Task status changes to "completed" in database

### TC-006: Update Task

**Steps:**
1. Create a task titled "Meeting"
2. Click on ChatKit widget
3. Type: "Change the Meeting task to Team Meeting tomorrow"
4. Press Enter

**Expected Results:**
- [ ] AI calls update_task
- [ ] Task title is updated to "Team Meeting tomorrow"
- [ ] AI confirms the update

### TC-007: Delete Task

**Steps:**
1. Create a task titled "Delete Me"
2. Click on ChatKit widget
3. Type: "Delete the Delete Me task"
4. Press Enter

**Expected Results:**
- [ ] AI calls delete_task with task_title="Delete Me"
- [ ] Task is removed from database
- [ ] AI confirms deletion
- [ ] Task no longer appears in list

### TC-008: Natural Language Variations

**Test various phrasings for the same intent:**

**Add Task:**
- [ ] "Create a task called..."
- [ ] "I need to..."
- [ ] "Remind me to..."
- [ ] "Add to my list..."

**List Tasks:**
- [ ] "What are my tasks?"
- [ ] "Show my todo list"
- [ ] "What's on my list?"
- [ ] "List everything I need to do"

**Complete Task:**
- [ ] "Finish task..."
- [ ] "Done with..."
- [ ] "Mark ... as done"
- [ ] "Complete the ... task"

### TC-009: Error Handling - Task Not Found

**Steps:**
1. Click on ChatKit widget
2. Type: "Complete the nonexistent task"
3. Press Enter

**Expected Results:**
- [ ] AI attempts to find task
- [ ] Returns appropriate error message
- [ ] Suggests listing tasks first

### TC-010: Error Handling - Empty Input

**Steps:**
1. Click on ChatKit widget
2. Type: "Add a task" (without title)
3. Press Enter

**Expected Results:**
- [ ] AI asks for task title
- [ ] No error occurs in backend

### TC-011: Thread Persistence

**Steps:**
1. Start a conversation, add a few tasks
2. Note the conversation ID
3. Refresh the page
4. Click on ChatKit widget
5. Ask: "What did we just talk about?"

**Expected Results:**
- [ ] Conversation history is preserved
- [ ] Thread ID remains the same
- [ ] AI remembers context

### TC-012: Authentication Flow

**Steps:**
1. Logout from the app
2. Navigate to home page
3. Verify ChatKit widget is hidden
4. Login again
5. Verify ChatKit widget appears

**Expected Results:**
- [ ] Widget hidden when not authenticated
- [ ] Widget appears after login
- [ ] No authentication errors in console

### TC-013: Multi-User Isolation

**Steps:**
1. User A creates tasks via chat
2. Logout User A
3. Login as User B
4. Ask AI to list tasks

**Expected Results:**
- [ ] User B sees only their own tasks
- [ ] User A's tasks are not visible
- [ ] No data leakage between users

### TC-014: Concurrent Operations

**Steps:**
1. Open app in two different browsers
2. Login as same user in both
3. Add task in Browser A
4. List tasks in Browser B

**Expected Results:**
- [ ] Both browsers can operate independently
- [ ] No conflicts occur
- [ ] Database handles concurrent operations

### TC-015: Special Characters in Task Title

**Steps:**
1. Click on ChatKit widget
2. Type: "Add a task: Buy milk & eggs (urgent!)"
3. Press Enter

**Expected Results:**
- [ ] Task is created with special characters
- [ ] Task can be completed by referencing partial title
- [ ] No SQL injection or parsing errors

## Performance Tests

### PT-001: Response Time

**Test:** Add a simple task
**Expected:** Response within 3 seconds

### PT-002: Large Task List

**Test:** Create 50+ tasks, then list them
**Expected:** Response within 5 seconds

### PT-003: Concurrent Users

**Test:** 5 users adding tasks simultaneously
**Expected:** All operations complete successfully

## Security Tests

### ST-001: SQL Injection

**Test:** Input: "Add task: '; DROP TABLE todos; --"
**Expected:** Safe handling, no database damage

### ST-002: XSS Prevention

**Test:** Input: "Add task: <script>alert('xss')</script>"
**Expected:** Script not executed, safely stored

### ST-003: Auth Token Validation

**Test:** Use expired JWT token
**Expected:** 401 Unauthorized response

## Logging and Debugging

### Enable Debug Logging

**Phase III Backend:**
```python
# In chatkit_server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```javascript
// ChatKit widget already logs to console
// Check for [ChatKit Widget] prefix
```

### Log Locations

- **Phase II Backend**: Console output
- **Phase III Backend**: Console output
- **Frontend**: Browser DevTools Console

## Test Results Summary

| Test Case | Status | Notes |
|:----------|:-------|:------|
| TC-001 | ☐ PASS ☐ FAIL | |
| TC-002 | ☐ PASS ☐ FAIL | |
| TC-003 | ☐ PASS ☐ FAIL | |
| TC-004 | ☐ PASS ☐ FAIL | |
| TC-005 | ☐ PASS ☐ FAIL | |
| TC-006 | ☐ PASS ☐ FAIL | |
| TC-007 | ☐ PASS ☐ FAIL | |
| TC-008 | ☐ PASS ☐ FAIL | |
| TC-009 | ☐ PASS ☐ FAIL | |
| TC-010 | ☐ PASS ☐ FAIL | |
| TC-011 | ☐ PASS ☐ FAIL | |
| TC-012 | ☐ PASS ☐ FAIL | |
| TC-013 | ☐ PASS ☐ FAIL | |
| TC-014 | ☐ PASS ☐ FAIL | |
| TC-015 | ☐ PASS ☐ FAIL | |

## Bug Report Template

```
Bug Report: [Short Description]

**Test Case:** TC-XXX

**Steps to Reproduce:**
1.
2.
3.

**Expected Behavior:**

**Actual Behavior:**

**Environment:**
- Browser:
- OS:
- Frontend URL:
- Backend Port:

**Error Messages:**
(Browser console errors)
(Backend logs)

**Screenshots:**
(Attach if applicable)
```
