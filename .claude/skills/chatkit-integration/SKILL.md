---
name: chatkit-integration
description: Project-specific skill for integrating OpenAI ChatKit with the ToDo App (Phase II + III). Covers SSE streaming, Better Auth JWT via query parameter, PostgreSQL persistence, and direct OpenAI Functions (not MCP). For streaming UI patterns use chatkit-streaming. For interactive widgets and actions use chatkit-actions.
---

# ChatKit Integration Skill - ToDo App (Project-Specific)

## Overview

This skill provides the foundation for ChatKit integration in the **ToDo App (Evolution-of-ToDo-App)** - getting the basic chat working end-to-end with your FastAPI backend and OpenAI Functions. It covers:

- **Backend**: ChatKitServer setup with SSE streaming, PostgreSQL persistence, OpenAI Functions
- **Frontend**: useChatKit configuration, Better Auth JWT via query parameter, context injection
- **Infrastructure**: React component integration, layout configuration

**This is project-specific to the ToDo App architecture.**

## Project Architecture

```
Frontend (Next.js)
├── Chat Kit Official Widget (ChatKitOfficialWidget.tsx)
│   └── Passes auth token via ?token= query parameter
│
└── Backend (FastAPI @ port 8000)
    ├── /api/v1/chatkit (SSE streaming endpoint)
    │   ├── Better Auth JWT validation
    │   ├── TodoChatKitServer (ChatKit Python SDK)
    │   ├── Phase2ChatKitStore (PostgreSQL persistence)
    │   └── OpenAI Functions (add_task, list_tasks, update_task, etc.)
    │
    └── Existing Task CRUD Endpoints
        ├── GET/POST /api/{user_id}/tasks
        ├── PUT /api/{user_id}/tasks/{id}
        ├── DELETE /api/{user_id}/tasks/{id}
        └── PATCH /api/{user_id}/tasks/{id}/complete
```

## Persona

You are a full-stack engineer integrating OpenAI ChatKit framework with the ToDo App's FastAPI backend. You understand that ChatKit provides standardized conversation UI/UX, but requires custom integration to work with PostgreSQL and Better Auth.

## Key Technology Choices

| Component | Technology | Evidence |
|:----------|:-----------|:---------|
| Chat UI | `@openai/chatkit-react` (Official Widget) | `frontend/src/components/ChatKitOfficialWidget.tsx` |
| Backend | FastAPI + ChatKit Python SDK | `backend/app/api/chat.py` |
| AI Processing | OpenAI GPT-3.5-turbo with Functions | `backend/app/services/official_chatkit_server.py` |
| Persistence | PostgreSQL via SQLModel (Neon) | `backend/app/services/chatkit_store.py` |
| Authentication | Better Auth JWT (via query parameter) | `backend/app/middleware/auth.py` |

## Implementation Patterns

### Pattern 1: SSE Streaming with ChatKit Python SDK

**When**: Implementing the ChatKit streaming endpoint

**Implementation**:
```python
# backend/app/api/chat.py
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..services.official_chatkit_server import TodoChatKitServer

router = APIRouter(prefix="/v1", tags=["chat"])
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
    try:
        user_id = current_user.get("id")
        user = db.get(User, user_id)

        # Build context for ChatKit server
        context = {
            "user_id": user_id,
            "email": user.email,
            "db": db
        }

        # Read request body
        request_body = await request.body()

        # Use official ChatKit server.process() method
        from chatkit.server import StreamingResult
        result = await chatkit_server.process(request_body, context)

        # Check if result is streaming or non-streaming
        if isinstance(result, StreamingResult):
            # StreamingResult is an async generator that yields SSE bytes
            return StreamingResponse(
                result,
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # Non-streaming JSON response
            from fastapi.responses import Response
            return Response(content=result.json, media_type="application/json")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[ChatKit] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"ChatKit processing error: {str(e)}")
```

**Evidence**: `phase_2_web_App/backend/app/api/chat.py:69-150`

### Pattern 2: Better Auth JWT via Query Parameter

**When**: ChatKit widget needs to authenticate with backend

**Frontend Implementation**:
```typescript
// frontend/src/components/ChatKitOfficialWidget.tsx

const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('authToken') || localStorage.getItem('better-auth-token');
};

const getChatKitApiUrl = (): string => {
  const token = getToken();
  const baseUrl = `${BACKEND_URL}/api/v1/chatkit`;
  if (token) {
    return `${baseUrl}?token=${encodeURIComponent(token)}`;
  }
  return baseUrl;
};

const chatKit = useChatKit({
  api: {
    url: getChatKitApiUrl(), // Dynamic URL with auth token as query parameter
    domainKey: CHATKIT_DOMAIN_KEY,
  },
  // ... other config
});
```

**Backend Implementation**:
```python
# backend/app/middleware/auth.py

async def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from request.
    Supports:
    1. Authorization: Bearer <token> header
    2. ?token=<token> query parameter (for ChatKit widget)
    """
    # Try Authorization header first
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")

    # Try query parameter (ChatKit widget uses this)
    query_token = request.query_params.get("token")
    if query_token:
        return query_token

    return None

async def get_current_user_from_request(
    request: Request,
    session: Session = Depends(get_session)
):
    """Get current authenticated user from JWT token (supports both header and query param)."""
    auth_token = await get_token_from_request(request)

    if not auth_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user = session.exec(select(User).where(User.email == email)).first()
        return {"id": user.id, "email": user.email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

**Evidence**:
- Frontend: `phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx:60-81`
- Backend: `phase_2_web_App/backend/app/middleware/auth.py:21-120`

### Pattern 3: Context Injection with RequestContext Dictionary

**When**: ChatKit server needs user context for processing

**Implementation**:
```python
# backend/app/api/chat.py

@router.post("/chatkit")
async def chatkit_streaming_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user_from_request),
    db: Session = Depends(get_session)
):
    # Build RequestContext dictionary for ChatKit server
    context = {
        "user_id": current_user.get("id"),
        "email": current_user.get("email"),
        "db": db,  # Database session for store operations
    }

    # Pass to ChatKit server.process()
    result = await chatkit_server.process(request_body, context)

# backend/app/services/official_chatkit_server.py

class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict,  # RequestContext is a plain dict
    ) -> AsyncIterator[ThreadStreamEvent]:
        # Extract user info from context
        user_id = context.get("user_id")
        email = context.get("email")
        db = context.get("db")

        # Load user's tasks for context
        tasks = db.exec(select(Task).where(Task.user_id == user_id).limit(10)).all()
        task_context = "\n\nRecent tasks:\n" + "\n".join([
            f"- {t.title} (Status: {t.status}, ID: {t.id})"
            for t in tasks
        ])

        # Include in system prompt
        system_prompt = f"""User: {email} (ID: {user_id})
{task_context}

You are a helpful todo management assistant...
        """
```

**Evidence**:
- Context building: `phase_2_web_App/backend/app/api/chat.py:108-118`
- Context usage: `phase_2_web_App/backend/app/services/official_chatkit_server.py:67-180`

### Pattern 4: PostgreSQL Persistence with Phase2ChatKitStore

**When**: Implementing ChatKit store with existing database models

**Implementation**:
```python
# backend/app/services/chatkit_store.py

from chatkit.store import Store
from chatkit.types import ThreadMetadata, Page, ThreadItem
from ..models.conversation import Conversation
from ..models.message import Message

class Phase2ChatKitStore(Store[Dict[str, Any]]):
    """
    PostgreSQL-backed Store for ChatKit server using Phase II database models.

    Implements the Store interface from the ChatKit SDK using the existing
    Conversation and Message models in the Phase II backend.
    """

    async def load_thread_items(
        self,
        thread_id: str,
        limit: int = 100,
        order: str = "asc",
        after: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Page[ThreadItem]:
        """
        Load items for a thread.

        Returns: Page object with 'data' list and 'has_more' boolean for pagination
        """
        db = context.get("db") if context else None
        if not db:
            return Page(data=[], has_more=False)

        statement = select(Message).where(Message.conversation_id == UUID(thread_id))

        # Handle cursor-based pagination with 'after' parameter
        if after:
            after_uuid = UUID(after)
            ref_msg = db.get(Message, after_uuid)
            if ref_msg:
                if order == "desc":
                    statement = statement.where(Message.timestamp < ref_msg.timestamp)
                else:
                    statement = statement.where(Message.timestamp > ref_msg.timestamp)

        statement = statement.order_by(Message.timestamp.asc() if order == "asc" else Message.timestamp.desc())
        statement = statement.limit(limit + 1)  # Fetch one extra to determine has_more
        messages = db.exec(statement).all()

        # Convert to ChatKit format
        items = []
        for msg in messages[:limit]:
            if msg.role == "user":
                items.append(UserMessageItem(
                    id=str(msg.id),
                    thread_id=thread_id,
                    created_at=msg.timestamp or utc_now(),
                    content=[UserMessageContent(type="input_text", text=msg.content)]
                ))
            else:
                items.append(AssistantMessageItem(
                    id=str(msg.id),
                    thread_id=thread_id,
                    created_at=msg.timestamp or utc_now(),
                    content=[AssistantMessageContent(type="output_text", text=msg.content, annotations=[])]
                ))

        has_more = len(messages) > limit
        return Page(data=items, has_more=has_more)
```

**Evidence**: `phase_2_web_App/backend/app/services/chatkit_store.py:35-315`

### Pattern 5: Direct OpenAI Functions (Not MCP)

**When**: Implementing tool execution with OpenAI Functions API

**Implementation**:
```python
# backend/app/services/official_chatkit_server.py

async def respond(self, thread, item, context) -> AsyncIterator[ThreadStreamEvent]:
    # Call OpenAI API with function calling
    response = self.openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the user's todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "The task title"},
                            "description": {"type": "string", "description": "Optional description"}
                        },
                        "required": ["title"]
                    }
                }
            },
            # ... more tool definitions
        ],
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message
    tool_calls = assistant_message.tool_calls

    # Execute tool calls directly (no MCP)
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
                result = f"📋 Your tasks:\n" + "\n".join([f"• {t.title} ({t.status})" for t in tasks])

            # ... handle other functions

    # Yield assistant response with result
    yield assistant_item
    yield ThreadItemDoneEvent(item=assistant_item)
```

**Evidence**: `phase_2_web_App/backend/app/services/official_chatkit_server.py:183-406`

### Pattern 6: ChatKit Server Initialization with Store

**When**: Setting up the ChatKit server with PostgreSQL persistence

**Implementation**:
```python
# backend/app/services/official_chatkit_server.py

from chatkit.server import ChatKitServer
from .chatkit_store import Phase2ChatKitStore

class TodoChatKitServer(ChatKitServer[dict]):
    """
    Official ChatKit server for Todo AI Assistant.

    Extends ChatKitServer from openai-chatkit package.
    Uses PostgreSQL store for persistent session history.
    """

    def __init__(self):
        """Initialize the ChatKit server with PostgreSQL store."""
        # Use PostgreSQL store for persistent session history
        super().__init__(
            store=Phase2ChatKitStore()
        )

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process user message and stream response events.

        This is the main method that ChatKitServer calls.
        It must yield ThreadStreamEvent objects.
        """
        # Your agent logic here
        # ...
```

**Evidence**: `phase_2_web_App/backend/app/services/official_chatkit_server.py:41-66`

### Pattern 7: React Layout Integration

**When**: Adding ChatKit widget to existing Next.js layout

**Implementation**:
```tsx
// frontend/src/app/layout.tsx

import ChatKitOfficialWidget from '@/components/ChatKitOfficialWidget';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="min-h-screen">
          {children}
        </main>

        {/* ChatKit Widget - fixed position in bottom-right corner */}
        <ChatKitOfficialWidget />
      </body>
    </html>
  );
}
```

**Evidence**: `phase_2_web_App/frontend/src/app/layout.tsx`

## Common Pitfalls

### 1. SSE Streaming Not Working
- **Symptom**: ChatKit widget shows "Connecting..." forever or returns JSON instead of streaming
- **Cause**: Missing `StreamingResult` check or wrong media type
- **Fix**:
  ```python
  from chatkit.server import StreamingResult

  if isinstance(result, StreamingResult):
      return StreamingResponse(
          result,
          media_type="text/event-stream",  # MUST be this
          headers={
              "Cache-Control": "no-cache",
              "Connection": "keep-alive",
              "X-Accel-Buffering": "no"
          }
      )
  ```
- **Evidence**: `phase_2_web_App/backend/app/api/chat.py:123-141`

### 2. Better Auth Token Not Extracted
- **Symptom**: 401 Unauthorized errors, "Not authenticated"
- **Cause**: Query parameter not checked or token format wrong
- **Fix**: Use `get_current_user_from_request` which checks both header and query param
  ```python
  @router.post("/chatkit")
  async def chatkit_endpoint(
      current_user: dict = Depends(get_current_user_from_request),  # NOT get_current_user
      db: Session = Depends(get_session)
  ):
  ```
- **Evidence**: `phase_2_web_App/backend/app/middleware/auth.py:79-120`

### 3. Page Return Type Mismatch
- **Symptom**: TypeError about Page object, 'has_more' attribute missing
- **Cause**: ChatKit SDK expects `Page(data=[...], has_more=True/False)` not `Page(items=[...])`
- **Fix**: Use correct attribute names
  ```python
  return Page(data=items, has_more=has_more)  # NOT 'items'
  ```
- **Evidence**: `phase_2_web_App/backend/app/services/chatkit_store.py:312`

### 4. Context Not Passed to Store
- **Symptom**: "No database session in context" warnings, threads not loading
- **Cause**: Store methods need `context` parameter with `db` session
- **Fix**: Always pass context when calling store methods
  ```python
  items = await self.store.load_thread_items(
      thread.id,
      limit=10,
      context=context  # MUST include this
  )
  ```
- **Evidence**: `phase_2_web_App/backend/app/services/official_chatkit_server.py:157-159`

### 5. Missing Item and Done Events
- **Symptom**: ChatKit widget shows message as "thinking" forever
- **Cause**: Only yielding `AssistantMessageItem` without `ThreadItemDoneEvent`
- **Fix**: Always yield both events
  ```python
  yield assistant_item  # Adds message to UI
  yield ThreadItemDoneEvent(item=assistant_item)  # Marks message as complete
  ```
- **Evidence**: `phase_2_web_App/backend/app/services/official_chatkit_server.py:402-406`

### 6. Wrong Backend URL in Frontend
- **Symptom**: "Cannot connect to ChatKit backend" errors
- **Cause**: Frontend pointing to wrong URL or port
- **Fix**: Use correct backend URL with `/api/v1/chatkit` path
  ```typescript
  const CHATKIT_BACKEND_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8000';
  const chatKitApiUrl = `${CHATKIT_BACKEND_URL}/api/v1/chatkit`;
  ```
- **Evidence**: `phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx:57-67`

### 7. ChatKit Widget Not Visible
- **Symptom**: Widget renders but not visible on page
- **Cause**: Z-index conflicts or position issues
- **Fix**: Use high z-index and explicit positioning
  ```tsx
  <div className="fixed bottom-24 right-6 z-[9999] w-[400px] h-[600px]">
    <ChatKit control={chatKit.control} className="h-full w-full" />
  </div>
  ```
- **Evidence**: `phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx:246-268`

## Tier Boundaries

### This Skill Covers (Tier 1: Foundation)

- ✅ ChatKitServer setup with `respond()` method
- ✅ SSE streaming with `ChatKitServer.process()` and `StreamingResult`
- ✅ Better Auth JWT via query parameter authentication
- ✅ PostgreSQL persistence with Phase2ChatKitStore
- ✅ Direct OpenAI Functions (add_task, list_tasks, update_task, complete_task, delete_task)
- ✅ Context injection via RequestContext dictionary
- ✅ React layout integration

### Use chatkit-streaming For (Tier 2: Real-time)

- ⏭️ `onResponseStart` / `onResponseEnd` handlers
- ⏭️ `onEffect` for fire-and-forget client updates
- ⏭️ `ProgressUpdateEvent` for loading states
- ⏭️ Thread lifecycle events
- ⏭️ Thread title generation

### Use chatkit-actions For (Tier 3: Interactive)

- ⏭️ Widget templates (`.widget` files)
- ⏭️ `widgets.onAction` handler
- ⏭️ `action()` method in ChatKitServer
- ⏭️ `sendCustomAction()` for widget updates
- ⏭️ Entity tagging (@mentions)
- ⏭️ Composer tools (mode selection)
- ⏭️ `ThreadItemReplacedEvent`

## Evidence Sources

| Pattern | Evidence File | Key Lines |
|:--------|:--------------|:----------|
| SSE Streaming | `backend/app/api/chat.py` | 69-150 |
| Better Auth Query Param | `backend/app/middleware/auth.py` | 21-120 |
| Context Injection | `backend/app/services/official_chatkit_server.py` | 67-180 |
| PostgreSQL Store | `backend/app/services/chatkit_store.py` | 35-315 |
| OpenAI Functions | `backend/app/services/official_chatkit_server.py` | 183-406 |
| Frontend Widget | `frontend/src/components/ChatKitOfficialWidget.tsx` | 1-334 |
| Layout Integration | `frontend/src/app/layout.tsx` | Full file |

## Quick Start Checklist

- [ ] Install ChatKit Python SDK: `pip install openai-chatkit`
- [ ] Install React package: `npm install @openai/chatkit-react`
- [ ] Set environment variables:
  - [ ] `OPENAI_API_KEY` in backend
  - [ ] `NEXT_PUBLIC_CHATBOT_API_URL` in frontend
  - [ ] `BETTER_AUTH_SECRET` in backend
  - [ ] `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in frontend
- [ ] Implement `Phase2ChatKitStore` (if not exists)
- [ ] Implement `TodoChatKitServer.respond()` method
- [ ] Add `/api/v1/chatkit` endpoint to FastAPI
- [ ] Add `<ChatKitOfficialWidget />` to layout.tsx
- [ ] Test SSE streaming with browser dev tools (Network tab)
- [ ] Verify Better Auth token extraction from query parameter
- [ ] Test OpenAI Functions execution (add_task, list_tasks, etc.)

## References

- **ChatKit Python SDK**: https://github.com/openai/chatkit-python
- **ChatKit React Package**: https://npmjs.com/package/@openai/chatkit-react
- **Better Auth**: https://better-auth.com
- **Project Instructions**: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/CLAUDE.md`
