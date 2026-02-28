# Comprehensive Plan: ChatKit UI with OpenAI Agents SDK and MCP Tools in Phase III

## Executive Summary

This document provides a comprehensive implementation plan for integrating OpenAI ChatKit widget UI with the OpenAI Agents SDK and MCP tools in the Phase III chatbot backend.

**Current Status:**
- ✅ Phase II (Web App): Fully functional - Next.js frontend + FastAPI backend on port 8000
- ✅ Phase III (Chatbot): Backend implementation complete - OpenAI Agents SDK + Todo tools on port 7860
- ✅ Database: Shared Neon PostgreSQL database
- 🔧 Integration: Frontend environment variable updated to point to Phase III backend

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                              │
│                    Port 3000/3001                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────┐    ┌─────────────────────────────────────┐   │
│  │  Todo UI Components  │    │      ChatKit Widget                 │   │
│  │  - Task list         │    │  - Floating widget (bottom-right)   │   │
│  │  - Add/Edit forms    │    │  - Natural language interface       │   │
│  │  - Status toggle     │    │  - OpenAI domain key auth           │   │
│  └─────────┬───────────┘    └─────────────────┬───────────────────┘   │
│            │                                   │                         │
│            │ REST API                          │ WebSocket/SSE           │
└────────────┼───────────────────────────────────┼─────────────────────────┘
             │                                   │
             ▼                                   ▼
┌──────────────────────────┐      ┌──────────────────────────────────────┐
│  Phase II Backend        │      │  Phase III Backend                   │
│  Port 8000               │      │  Port 7860                           │
├──────────────────────────┤      ├──────────────────────────────────────┤
│  - Task CRUD endpoints   │      │  - /api/v1/chatkit (SSE streaming)   │
│  - JWT Authentication     │      │  - OpenAI Agents SDK integration     │
│  - Better Auth           │      │  - TodoTools (MCP-compatible)        │
│  - SQLModel ORM          │      │  - TodoAgent (AI orchestration)      │
└──────────┬───────────────┘      └──────────────┬───────────────────────┘
           │                                     │
           └──────────────┬──────────────────────┘
                          ▼
                ┌─────────────────────┐
                │  Neon PostgreSQL    │
                │  - users table      │
                │  - todos table      │
                │  - conversations    │
                │  - messages         │
                └─────────────────────┘
```

## Component Details

### 1. Frontend Components

#### 1.1 ChatKit Widget (`ChatKitOfficialWidget.tsx`)
- **Location**: `phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx`
- **Package**: `@openai/chatkit-react`
- **Key Features**:
  - Floating widget in bottom-right corner
  - Dark theme
  - Custom greeting and prompts
  - Authentication-aware (only shows when logged in)
  - Thread persistence via localStorage

**Configuration:**
```typescript
const CHATKIT_SERVER_URL = process.env.NEXT_PUBLIC_CHATKIT_URL || 'http://localhost:7860';
const CHATKIT_DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || '';
```

#### 1.2 Environment Variables (`.env.local`)
```bash
# Phase 2 Web App Backend API (Todo CRUD)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Phase 3 Chatbot Backend API (for ChatKit Widget)
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:7860

# Better Auth URL
NEXT_PUBLIC_AUTH_URL=http://localhost:8000

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_699dd137050c8194b8ac6b936da88aa408d6ecf59a4d7a47

# Enable/disable features
NEXT_PUBLIC_ENABLE_CHATBOT=true

# ChatKit endpoint is on Phase III backend (port 7860)
NEXT_PUBLIC_CHATKIT_URL=http://localhost:7860
```

### 2. Phase III Backend Components

#### 2.1 Main Application (`main.py`)
- **Location**: `phase_3_chatbot/backend/main.py`
- **Port**: 7860
- **Key Setup**:
  - FastAPI application with lifespan management
  - CORS configured for frontend origins
  - Rate limiting with slowapi
  - Router includes `/v1/chatkit`, `/v1/chat`, `/v1/auth`

#### 2.2 ChatKit API Endpoint (`src/api/v1/chatkit.py`)
**Endpoints:**
- `POST /api/v1/chatkit` - Main streaming endpoint
- `POST /api/v1/chatkit/session` - Session creation
- `GET /api/v1/chatkit/history` - Conversation history
- `GET /api/v1/chatkit/conversations` - List conversations

**Streaming Protocol (SSE):**
```python
async def event_stream() -> AsyncIterator[str]:
    async for event in chatkit_server.process_request(request_body, context):
        event_type = event.get("event", "message")
        event_data = json.dumps(event.get("data", {}))
        yield f"event: {event_type}\ndata: {event_data}\n\n"
```

#### 2.3 ChatKit Server (`src/services/chatkit_server.py`)
**Classes:**
- `ChatKitStore`: PostgreSQL-backed persistence
- `ChatKitServer`: Main server implementation

**Key Methods:**
- `process_request()`: Handles incoming chat requests
- `_stream_agent_response()`: Streams AI responses with tool calls

#### 2.4 Todo Agent (`src/agents/todo_agent.py`)
**Purpose**: AI orchestration using OpenAI API

**Features:**
- Uses OpenAI Chat Completions API
- Function calling for tool operations
- Natural language understanding
- Tool result processing

**System Prompt:**
```
You are a helpful todo management assistant. Your job is to help users manage their tasks through natural language.

You can help with:
- Adding new tasks
- Listing existing tasks (pending, completed, or all)
- Updating task details
- Marking tasks as completed
- Deleting tasks
```

#### 2.5 Todo Tools (`src/services/todo_tools.py`)
**Purpose**: MCP-compatible tool implementations

**Available Tools:**
1. `add_task(user_id, title, description, due_date)`
2. `list_tasks(user_id, status_filter)`
3. `update_task(user_id, task_id, task_title, title, description, status, priority, due_date)`
4. `complete_task(user_id, task_id, task_title)`
5. `delete_task(user_id, task_id, task_title)`

**Key Features:**
- Database-backed operations
- UUID handling for user_id and task_id
- Natural language lookup via `task_title`
- Error handling with recoverable flags

### 3. Database Schema

#### 3.1 Tables
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'pending',
    priority VARCHAR,
    due_date TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR,  -- 'user', 'assistant', 'tool_call'
    content TEXT,
    metadata JSONB,
    timestamp TIMESTAMP
);
```

## Data Flow

### User Message Flow

```
1. User types in ChatKit Widget
   ↓
2. Widget sends POST to http://localhost:7860/api/v1/chatkit
   Request body: { "thread_id": "...", "message": "add task buy groceries" }
   Headers: { "Authorization": "Bearer <JWT_TOKEN>" }
   ↓
3. Backend authenticates user via JWT
   ↓
4. Request routed to ChatKitServer.process_request()
   ↓
5. TodoAgent.process_message() calls OpenAI API
   ↓
6. OpenAI returns response with tool_calls
   Example: { "name": "add_task", "arguments": { "user_id": "...", "title": "buy groceries" } }
   ↓
7. ChatKitServer executes tool via TodoTools
   ↓
8. TodoTools performs database operation
   ↓
9. Result streamed back via SSE
   Events:
   - tool_call_started
   - tool_call_completed
   - message_delta (AI response)
   - conversation_done
   ↓
10. Widget displays AI response and tool results
```

### Authentication Flow

```
1. User logs in via Phase II Backend (port 8000)
   ↓
2. Better Auth issues JWT token
   ↓
3. Token stored in localStorage as 'authToken' or 'better-auth-token'
   ↓
4. ChatKit Widget reads token from localStorage
   ↓
5. Widget includes token in Authorization header for all requests
   ↓
6. Phase III Backend validates token using shared BETTER_AUTH_SECRET
   ↓
7. User ID extracted and used for all operations
```

## Natural Language Examples

| User Input | AI Interpretation | Tools Called |
|:-----------|:------------------|:-------------|
| "Add a task to buy groceries" | Create new task | `add_task(user_id, title="buy groceries")` |
| "Show me all my tasks" | List all tasks | `list_tasks(user_id, status_filter="all")` |
| "What do I need to do?" | List pending tasks | `list_tasks(user_id, status_filter="pending")` |
| "Mark the groceries task as complete" | Complete specific task | `complete_task(user_id, task_title="groceries")` |
| "Delete task 3" | Delete by ID | `delete_task(user_id, task_id=<UUID>)` |
| "Change the meeting task to tomorrow" | Update task | `update_task(user_id, task_title="meeting", due_date="<tomorrow>")` |

## Implementation Checklist

### Phase III Backend Setup ✅
- [x] FastAPI application configured
- [x] CORS middleware configured
- [x] Database session management
- [x] ChatKit SSE endpoint implemented
- [x] OpenAI Agents SDK integration
- [x] TodoTools (MCP-compatible) implemented
- [x] TodoAgent with tool calling
- [x] Authentication service

### Frontend Integration ✅
- [x] @openai/chatkit-react installed
- [x] ChatKit widget component created
- [x] Widget integrated into layout
- [x] Environment variables configured
- [x] Authentication token handling

### Testing Required
- [ ] End-to-end chat flow
- [ ] All tool operations (add, list, update, complete, delete)
- [ ] Authentication between Phase II and Phase III
- [ ] Error handling scenarios
- [ ] Thread persistence across sessions

## Environment Setup

### Phase III Backend Requirements
```bash
# Install dependencies
cd phase_3_chatbot/backend
pip install -r requirements.txt

# Required packages:
# - fastapi
# - uvicorn
# - openai
# - sqlmodel
# - python-dotenv
# - pydantic
# - slowapi
```

### Frontend Requirements
```bash
# Install dependencies
cd phase_2_web_App/frontend
npm install

# Required packages:
# - @openai/chatkit-react
# - next
# - react
```

## Running the Application

### Terminal 1: Phase II Backend (Task CRUD)
```bash
cd phase_2_web_App/backend
python app.py
# Running on http://localhost:8000
```

### Terminal 2: Phase III Backend (ChatKit + AI)
```bash
cd phase_3_chatbot/backend
python main.py
# Running on http://localhost:7860
```

### Terminal 3: Frontend
```bash
cd phase_2_web_App/frontend
npm run dev
# Running on http://localhost:3000 or http://localhost:3001
```

## Troubleshooting

### Issue: ChatKit widget doesn't appear
**Solution**:
1. Check that user is logged in
2. Verify `NEXT_PUBLIC_ENABLE_CHATBOT=true`
3. Check browser console for errors
4. Verify auth token in localStorage

### Issue: "Connection refused" errors
**Solution**:
1. Ensure Phase III backend is running on port 7860
2. Check `NEXT_PUBLIC_CHATKIT_URL` points to port 7860
3. Verify CORS configuration allows frontend origin

### Issue: Authentication errors
**Solution**:
1. Verify BETTER_AUTH_SECRET matches between Phase II and Phase III
2. Check that JWT token is valid and not expired
3. Ensure token format includes "Bearer " prefix

### Issue: Tools not executing
**Solution**:
1. Check database connection
2. Verify user_id is valid UUID
3. Check backend logs for tool execution errors
4. Ensure OpenAI API key is valid

## Next Steps

1. **Testing**: Comprehensive testing of all tool operations
2. **Error Handling**: Improve error messages for users
3. **Enhancements**:
   - Add task priorities
   - Add due date reminders
   - Support for task categories/tags
4. **Production Deployment**:
   - Update environment variables for production
   - Deploy Phase III backend (e.g., Railway, Render)
   - Update frontend CHATKIT_URL to production endpoint
5. **Documentation**: Create user guide for ChatKit commands

## References

- [OpenAI ChatKit Documentation](https://openai.github.io/chatkit-js/)
- [OpenAI Agents SDK](https://github.com/openai/agents-sdk)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
