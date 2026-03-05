---
name: chatkit-streaming
description: Implements SSE streaming patterns for the ToDo ChatKit integration. This skill should be used when working with Server-Sent Events, response lifecycle management, tool execution streaming, and thread state synchronization in the ToDo app. Covers SSE event flow, OpenAI function calling, AssistantMessageItem creation, and ThreadItemDoneEvent completion.
---

# ChatKit SSE Streaming Skill - ToDo App Integration

## Overview

This skill provides patterns for building SSE (Server-Sent Events) streaming interfaces in the ToDo ChatKit integration. It covers the streaming layer between the frontend ChatKit widget and the FastAPI backend using the ChatKit Python SDK.

**Project**: Evolution of ToDo App - Phase III ChatKit Integration
**Architecture**: FastAPI Backend + ChatKit Python SDK + OpenAI API + Neon PostgreSQL

## Core Concepts

### SSE vs WebSocket

This implementation uses **Server-Sent Events (SSE)** for streaming, NOT WebSocket:

| Aspect | SSE (Used Here) | WebSocket |
|:-------|:----------------|:-----------|
| **Direction** | Server → Client only | Bidirectional |
| **Protocol** | HTTP text/event-stream | WebSocket protocol |
| **Client** | ChatKit React widget | Custom WebSocket client |
| **Backend** | FastAPI StreamingResponse | WebSocket server |

### Response Lifecycle (SSE)

ChatKit streams responses via SSE in real-time:

```
User sends message via ChatKit widget
    ↓
POST /api/v1/chatkit (with auth token)
    ↓
chatkit_server.process() parses request
    ↓
respond() method is called
    ↓
OpenAI processes request (with tool_calls)
    ↓
Yield AssistantMessageItem (text response)
    ↓
Yield ThreadItemDoneEvent (completion marker)
    ↓
SSE stream ends
    ↓
ChatKit widget displays message and unlocks UI
```

### SSE Event Flow

Each response consists of TWO events:

```python
# Event 1: The message content
yield AssistantMessageItem(
    id="msg_123",
    thread_id="thread_456",
    created_at=utc_now(),
    content=[AssistantMessageContent(type="output_text", text="...")]
)

# Event 2: The completion marker
yield ThreadItemDoneEvent(item=assistant_item)
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/official_chatkit_server.py:402-406`

## Implementation Patterns

### Pattern 1: SSE Endpoint Setup

**When**: Set up the FastAPI endpoint to handle ChatKit SSE streaming

**Backend Implementation**:
```python
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from ..services.official_chatkit_server import TodoChatKitServer
from ..middleware.auth import get_current_user_from_request

# Create global ChatKit server instance
chatkit_server = TodoChatKitServer()

@router.post("/chatkit")
async def chatkit_streaming_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user_from_request),
    db: Session = Depends(get_session)
):
    """
    Official ChatKit streaming endpoint using openai-chatkit Python SDK.

    Authentication:
    - Authorization: Bearer <token> header (standard)
    - ?token=<token> query parameter (for ChatKit widget)
    """
    # Extract user info
    user_id = current_user.get("id")
    user = db.get(User, user_id)

    # Build context for ChatKit server
    context = {
        "user_id": user_id,
        "email": user.email,
        "db": db
    }

    # Read request body and process
    request_body = await request.body()
    result = await chatkit_server.process(request_body, context)

    # Return SSE stream
    from chatkit.server import StreamingResult

    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    else:
        # Non-streaming JSON response
        return Response(content=result.json, media_type="application/json")
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/api/chat.py:69-141`

### Pattern 2: OpenAI Tool Execution with SSE Streaming

**When**: Execute database operations through OpenAI function calling and stream results

**Backend Implementation**:
```python
async def respond(
    self,
    thread: ThreadMetadata,
    item: UserMessageItem | None,
    context: dict,
) -> AsyncIterator[ThreadStreamEvent]:
    """Process user message and stream response events."""

    # Get user info
    user_id = context.get("user_id")
    db = context.get("db")

    # Extract user message
    user_message = ""
    if item and item.content:
        for content in item.content:
            if hasattr(content, 'text'):
                user_message = content.text
                break

    # Call OpenAI API with function tools
    response = self.openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"""You are a helpful todo management assistant.
                Available tools:
                1. add_task(title: str, description: str = None)
                2. list_tasks(status: str = None)
                3. update_task(task_id: str, title: str = None, ...)
                4. complete_task(task_id: str)
                5. delete_task(task_id: str)"""
            },
            {"role": "user", "content": user_message}
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["title"]
                    }
                }
            },
            # ... other tools
        ],
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message
    tool_calls = assistant_message.tool_calls

    final_response = ""

    # Execute tool calls
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "add_task":
                new_task = Task(
                    title=function_args.get("title", "Untitled"),
                    description=function_args.get("description", ""),
                    user_id=user_id,
                    status="pending"
                )
                db.add(new_task)
                db.commit()
                db.refresh(new_task)
                result = f"✅ Added task: {new_task.title}"

            elif function_name == "list_tasks":
                tasks = db.exec(select(Task).where(Task.user_id == user_id)).all()
                if tasks:
                    task_list = "\n".join([f"• {t.title} ({t.status})" for t in tasks])
                    result = f"📋 Your tasks:\n{task_list}"
                else:
                    result = "📋 No tasks found"

            elif function_name == "complete_task":
                task_id = UUID(function_args.get("task_id"))
                task = db.get(Task, task_id)
                if task and task.user_id == user_id:
                    task.status = "completed"
                    db.commit()
                    result = f"✅ Completed task: {task.title}"
                else:
                    result = "❌ Task not found"

            elif function_name == "delete_task":
                task_id = UUID(function_args.get("task_id"))
                task = db.get(Task, task_id)
                if task and task.user_id == user_id:
                    title = task.title
                    db.delete(task)
                    db.commit()
                    result = f"🗑️ Deleted task: {title}"
                else:
                    result = "❌ Task not found"

            elif function_name == "update_task":
                task_id = UUID(function_args.get("task_id"))
                task = db.get(Task, task_id)
                if task and task.user_id == user_id:
                    if "title" in function_args:
                        task.title = function_args["title"]
                    if "description" in function_args:
                        task.description = function_args["description"]
                    if "status" in function_args:
                        task.status = function_args["status"]
                    db.commit()
                    result = f"✅ Updated task: {task.title}"
                else:
                    result = "❌ Task not found"

            final_response = result
    else:
        final_response = assistant_message.content or "I understand. How can I help?"

    # Yield the assistant message
    assistant_id = self.store.generate_item_id("msg", thread, context)
    assistant_item = AssistantMessageItem(
        id=assistant_id,
        thread_id=thread.id,
        created_at=utc_now(),
        content=[
            AssistantMessageContent(
                type="output_text",
                text=final_response,
                annotations=[]
            )
        ],
    )

    # First yield the item (adds message to UI)
    yield assistant_item

    # Then yield the done event (marks message complete)
    yield ThreadItemDoneEvent(item=assistant_item)
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/official_chatkit_server.py:67-408`

### Pattern 3: Frontend ChatKit Widget Configuration

**When**: Configure the ChatKit widget to connect to SSE endpoint

**Frontend Implementation**:
```typescript
import { ChatKit, useChatKit } from '@openai/chatkit-react';

const CHATKIT_BACKEND_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8000';

// Helper to get auth token and build URL with query parameter
const getChatKitApiUrl = (): string => {
  const token = getToken();
  const baseUrl = `${CHATKIT_BACKEND_URL}/api/v1/chatkit`;
  if (token) {
    return `${baseUrl}?token=${encodeURIComponent(token)}`;
  }
  return baseUrl;
};

const chatKit = useChatKit({
  // SSE endpoint configuration
  api: {
    url: getChatKitApiUrl(),
    domainKey: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
  },

  // Thread persistence
  initialThread: getInitialThreadId(),
  onThreadChange: (event: { threadId: string | null }) => {
    if (event.threadId) {
      localStorage.setItem('chatkit_thread_id', event.threadId);
    } else {
      localStorage.removeItem('chatkit_thread_id');
    }
  },

  // Theme customization
  theme: 'dark',

  // Header configuration
  header: {
    enabled: true,
    title: {
      enabled: true,
      text: '🤖 Todo AI Assistant',
    },
  },

  // Start screen with suggested prompts
  startScreen: {
    greeting: 'Hi! I can help you manage your todos.',
    prompts: [
      { label: 'Add a new task', prompt: 'Add a new task', icon: 'write' },
      { label: 'Show my tasks', prompt: 'Show all my tasks', icon: 'search' },
      { label: 'Mark task complete', prompt: 'Mark a task as complete', icon: 'sparkle' },
    ],
  },

  // Error handler
  onError: ({ error }) => {
    console.error('[ChatKit Widget] Error:', error);
    if (error.message?.includes('fetch') || error.message?.includes('network')) {
      console.error('Cannot connect to ChatKit backend at:', getChatKitApiUrl());
    }
  },

  // Ready handler
  onReady: () => {
    console.log('[ChatKit Widget] Widget is ready and connected!');
  },
});

// Render the widget
return (
  <div className="fixed bottom-24 right-6 z-[9998] w-[400px] h-[600px]">
    <ChatKit control={chatKit.control} className="h-full w-full" />
  </div>
);
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx:107-244`

### Pattern 4: Error Handling with ErrorEvent

**When**: Handle errors gracefully during SSE streaming

**Backend Implementation**:
```python
from chatkit.types import ErrorEvent, ErrorCode

def _error_event(self, message: str) -> ThreadStreamEvent:
    """Create an error event for SSE streaming."""
    return ErrorEvent(
        code=ErrorCode.STREAM_ERROR,
        message=message,
        allow_retry=False
    )

# Usage in respond()
async def respond(self, thread, item, context):
    if not self.openai_client:
        yield self._error_event("OpenAI API key not configured")
        return

    user_id = context.get("user_id")
    if not user_id:
        yield self._error_event("Authentication required")
        return

    try:
        # ... processing ...
    except Exception as e:
        logger.exception(f"[ChatKitServer] Error: {e}")
        yield self._error_event(f"Processing error: {str(e)}")
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/official_chatkit_server.py:79-97, 410-417`

### Pattern 5: Thread Persistence with PostgreSQL Store

**When**: Persist thread history using the ChatKit Store interface

**Backend Implementation**:
```python
from chatkit.store import Store
from chatkit.types import Page

class Phase2ChatKitStore(Store[Dict[str, Any]]):
    """PostgreSQL-backed Store for ChatKit server."""

    async def load_thread_items(
        self,
        thread_id: str,
        limit: int = 100,
        order: str = "asc",
        after: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Page[ThreadItem]:
        """Load items for a thread with cursor-based pagination."""
        db = context.get("db")

        statement = select(Message).where(
            Message.conversation_id == UUID(thread_id)
        )

        # Handle cursor-based pagination
        if after:
            ref_msg = db.get(Message, UUID(after))
            if ref_msg:
                if order == "desc":
                    statement = statement.where(Message.timestamp < ref_msg.timestamp)
                else:
                    statement = statement.where(Message.timestamp > ref_msg.timestamp)

        statement = statement.order_by(Message.timestamp.asc())
        statement = statement.limit(limit + 1)
        messages = db.exec(statement).all()

        # Convert to ChatKit format
        items = []
        for msg in messages[:limit]:
            if msg.role == "user":
                items.append(UserMessageItem(
                    id=str(msg.id),
                    thread_id=thread_id,
                    created_at=msg.timestamp,
                    content=[UserMessageContent(type="input_text", text=msg.content)]
                ))
            else:
                items.append(AssistantMessageItem(
                    id=str(msg.id),
                    thread_id=thread_id,
                    created_at=msg.timestamp,
                    content=[AssistantMessageContent(type="output_text", text=msg.content)]
                ))

        has_more = len(messages) > limit
        return Page(data=items, has_more=has_more)
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/chatkit_store.py:226-315`

## Configuration Options

### SSE-Related useChatKit Options

```typescript
const chatkit = useChatKit({
  // === SSE Endpoint ===
  api: {
    url: string,          // SSE endpoint URL
    domainKey: string,    // Domain validation key
  },

  // === Lifecycle Events ===
  onReady: () => void,                    // ChatKit initialized
  onError: ({ error }) => void,           // SSE stream error
  onResponseStart: () => void,            // AI started responding
  onResponseEnd: () => void,              // AI finished responding

  // === Thread Events ===
  onThreadChange: ({ threadId }) => void, // Thread switched
  onThreadLoadStart: ({ threadId }) => void,
  onThreadLoadEnd: ({ threadId }) => void,

  // === Client Interaction ===
  onEffect: ({ name, data }) => void,     // Server sent effect (not used in this project)
  onClientTool: ({ name, params }) => any, // AI requests client state (not used in this project)

  // === Theme ===
  theme: 'light' | 'dark',

  // === UI Components ===
  header: {
    enabled: boolean,
    title: { enabled: boolean, text: string }
  },
  startScreen: {
    greeting: string,
    prompts: Array<{label: string, prompt: string, icon: string}>
  },
  composer: {
    placeholder: string
  }
});
```

## Natural Language Commands to Tool Mapping

| User Says | OpenAI Tool | Database Operation |
|:----------|:------------|:-------------------|
| "Add a task to buy groceries" | add_task | INSERT INTO tasks |
| "Show me all my tasks" | list_tasks | SELECT FROM tasks |
| "Mark task 3 as complete" | complete_task | UPDATE tasks SET status='completed' |
| "Delete the meeting task" | delete_task | DELETE FROM tasks |
| "Change task 1 to 'Call mom'" | update_task | UPDATE tasks SET title='...' |

## SSE Headers Configuration

Critical headers for proper SSE streaming:

```python
headers={
    "Cache-Control": "no-cache",      # Prevent caching
    "Connection": "keep-alive",       # Keep connection open
    "X-Accel-Buffering": "no"         # Disable nginx buffering
}
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/api/chat.py:131-135`

## Authentication Flow

```
Frontend: Get JWT token from localStorage
    ↓
Frontend: Build SSE URL with ?token=<jwt>
    ↓
Frontend: POST /api/v1/chatkit?token=<jwt>
    ↓
Backend: get_current_user_from_request() validates JWT
    ↓
Backend: Extract user_id from token
    ↓
Backend: Pass user_id and db session to respond()
    ↓
Backend: Execute tools with user_id scope
```

**Evidence**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/api/chat.py:84-113`

## Anti-Patterns to Avoid

### SSE-Specific Issues

1. **Missing ThreadItemDoneEvent** - Always yield done event after item, or message won't complete
2. **Blocking in respond()** - Use async/await properly, never block the event loop
3. **Not handling tool_call parsing** - Always check for tool_calls before using content
4. **Missing SSE headers** - Without proper headers, nginx/proxies may buffer responses
5. **Not validating user_id in context** - Always verify user owns the data they're accessing

### Tool Execution Issues

1. **Not committing database changes** - Always db.commit() after modifications
2. **Not checking task ownership** - Verify task.user_id == user_id before operations
3. **Invalid UUID handling** - Wrap UUID parsing in try/except for user input
4. **Missing error messages** - Return user-friendly error messages, not raw exceptions

### Store Implementation Issues

1. **Not returning Page object** - load_thread_items must return Page(data=[], has_more=bool)
2. **Not handling pagination** - Support 'after' parameter for cursor-based pagination
3. **Not filtering by user_id** - Always scope queries to the authenticated user

## References

### Evidence Sources

All patterns derived from actual project implementation:

**Backend Files**:
- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/api/chat.py` - SSE endpoint
- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/official_chatkit_server.py` - respond() method and tool execution
- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/chatkit_store.py` - PostgreSQL store implementation

**Frontend Files**:
- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx` - ChatKit widget configuration

### Database Models

- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/models/task.py` - Task model
- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/models/conversation.py` - Conversation model
- `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/models/message.py` - Message model

### External Documentation

- ChatKit Python SDK: https://github.com/openai/chatkit-python
- ChatKit React SDK: https://github.com/openai/chatkit-react
- FastAPI StreamingResponse: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- SSE Specification: https://html.spec.whatwg.org/multipage/server-sent-events.html
