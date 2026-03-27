# Claude Code Rules - Evolution of ToDo App (Hackathon II)

This project is part of **Hackathon II - Todo Spec-Driven Development**. See `Hackathon II - Todo Spec-Driven Development.md` for full hackathon requirements.

## Project Overview

**Current Phase:** Phase III - AI-Powered Todo Chatbot Integration

**Completed Phases:**
- **Phase I (Console):** In-memory Python console todo app - ✅ COMPLETE
- **Phase II (Web):** Full-stack web app with frontend (Next.js) and backend (FastAPI) - ✅ COMPLETE
- **Phase III (Chatbot):** Integrating OpenAI ChatKit widget with OpenAI Agents SDK and MCP tools

## Project Structure

```
Evolution-of-ToDo-App/
├── phase1-console/          # ✅ Phase I: Python console app (COMPLETE)
├── phase_2_web_App/         # ✅ Phase II + III: Full-stack web app with ChatKit integration
│   ├── frontend/            # Next.js 16+ frontend with ChatKit widget (port 3000/3001)
│   │   └── src/
│   │       ├── app/
│   │       │   └── layout.tsx        # ChatKit widget placement
│   │       └── components/
│   │           └── ChatKitOfficialWidget.tsx
│   └── backend/             # FastAPI backend with ChatKit endpoint (port 8000)
│       └── app/
│           ├── api/
│           │   └── chat.py                  # /api/v1/chatkit endpoint
│           ├── services/
│           │   ├── official_chatkit_server.py  # ChatKitServer with OpenAI Agents SDK
│           │   └── chatkit_store.py            # PostgreSQL store
│           └── middleware/
│               └── auth.py                    # JWT auth
└── .claude/skills/           # Project-specific ChatKit skills
    ├── chatkit-integration/  # Core integration patterns
    ├── chatkit-streaming/    # SSE streaming patterns
    └── chatkit-actions/      # Interactive widgets (future)
```

## Phase II Status (Web App - COMPLETE)

**Working Components:**
- Frontend: Next.js 16 (App Router) at `phase_2_web_App/frontend/` - Port 3000/3001
- Backend: FastAPI at `phase_2_web_App/backend/` - Port 8000
- Database: Neon PostgreSQL via SQLModel
- Authentication: Better Auth with JWT
- All Basic CRUD operations working

**API Endpoints (Phase II):**
| Method | Endpoint | Description |
|:-------||:-----|:-----|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

## Phase III Implementation: ChatKit Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Phase II Frontend (Next.js)                          │
│  Port: 3000/3001                                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Existing Todo UI (Working)                                       │ │
│  │  - Task list, forms, Better Auth signup/login                     │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  📢 OpenAI ChatKit Widget (Bottom-Right Corner)                   │ │
│  │  - @openai/chatkit-react widget                                   │ │
│  │  - useChatKit hook from @openai/chatkit-react                      │ │
│  │  - JWT via ?token= query parameter                                 │ │
│  │  - SSE streaming (text/event-stream)                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ POST /api/v1/chatkit?token=<jwt>
┌─────────────────────────────────────────────────────────────────────────┐
│              Phase II Backend (FastAPI) - Port 8000                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Existing REST API (Working)                                      │ │
│  │  - /api/{user_id}/tasks/* CRUD endpoints                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  ChatKit HTTP Endpoint                                            │ │
│  │  - /api/v1/chatkit (POST with SSE streaming)                      │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │ OpenAI ChatKit Python SDK                                   │ │ │
│  │  │  ┌────────────────────────────────────────────────────────┐  │ │ │
│  │  │  │ TodoChatKitServer (extends ChatKitServer)             │  │ │ │
│  │  │  │  - respond() method for processing messages           │  │ │ │
│  │  │  │  - stream_agent_response() with AgentContext          │  │ │ │
│  │  │  │  - PostgreSQL store for thread persistence            │  │ │ │
│  │  │  └────────────────────────────────────────────────────────┘  │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │ OpenAI Agents SDK Integration                               │ │ │
│  │  │  - stream_agent_response(agent, context)                   │ │ │
│  │  │  - AgentContext with user_id, db, config                   │ │ │
│  │  │  - Tool execution with MCP-compatible patterns              │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────────────────┐ │ │
│  │  │ MCP Tools (Stateless, Database-Backed)                     │ │ │
│  │  │  - add_task: Create new task                                │ │ │
│  │  │  - list_tasks: Retrieve user tasks                          │ │ │
│  │  │  - update_task: Modify existing task                        │ │ │
│  │  │  - complete_task: Mark task as complete                     │ │ │
│  │  │  - delete_task: Remove task                                 │ │ │
│  │  └──────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Neon PostgreSQL Database
                    - tasks table
                    - users table
                    - conversations table
                    - messages table
```

### Phase III Technology Stack

| Component | Technology | Port/Location |
|:----------|:-----------|:--------------|
| Chat UI Widget | **@openai/chatkit-react** (Official Widget) | Frontend: Port 3000/3001 |
| Chat Backend | **Python FastAPI + OpenAI ChatKit Python SDK** | Backend: Port 8000 |
| AI Framework | **OpenAI Agents SDK** (via chatkit.agents) | Backend: Port 8000 |
| Agent Execution | **stream_agent_response() + AgentContext** | Backend: Port 8000 |
| Tools | **MCP-compatible stateless tools** (database-backed) | Backend: Port 8000 |
| Communication | **HTTP POST with SSE streaming** (`text/event-stream`) | Backend: Port 8000 |
| ORM | SQLModel | Backend: Port 8000 |
| Database | Neon PostgreSQL | Cloud-hosted |
| Authentication | Better Auth JWT (via query parameter) | Frontend + Backend |

### Key Implementation Details

**1. ChatKit Widget (Frontend - Port 3000/3001)**
- Location: `phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx`
- Widget placement: `phase_2_web_App/frontend/src/app/layout.tsx`
- Uses `useChatKit` hook from `@openai/chatkit-react`
- Connects to: `http://localhost:8000/api/v1/chatkit?token=<jwt>`

**2. ChatKit Server (Backend - Port 8000)**
- Location: `phase_2_web_App/backend/app/services/official_chatkit_server.py`
- Extends `ChatKitServer[dict]` from `openai-chatkit` package
- Implements `respond()` method for processing messages
- Uses `stream_agent_response()` from `chatkit.agents` (OpenAI Agents SDK)
- Creates `AgentContext` with user_id, database session, and configuration

**3. OpenAI Agents SDK Integration**
- Import: `from chatkit.agents import stream_agent_response, AgentContext`
- The Agents SDK provides agent execution patterns with MCP-compatible tool calling
- `AgentContext` carries user information and database session to agent

**4. MCP Tools (Stateless, Database-Backed)**
- All tools are stateless functions that accept user_id and database session
- Each operation is self-contained and persistable to Neon PostgreSQL
- Tools follow MCP patterns: pure functions with explicit parameters

**5. PostgreSQL Persistence**
- `Phase2ChatKitStore` implements the ChatKit `Store` interface
- Threads and messages persisted to `conversations` and `messages` tables
- Session history survives server restarts

## Claude Skills for ChatKit Development

When working on ChatKit features, use these three project-specific skills:

### 1. chatkit-integration (Foundation)
**When to use:** Core ChatKit integration work
- Backend: ChatKitServer setup, SSE streaming, PostgreSQL store
- Frontend: useChatKit configuration, Better Auth JWT
- Authentication: JWT via query parameter

**Location:** `.claude/skills/chatkit-integration/SKILL.md`

### 2. chatkit-streaming (Real-time)
**When to use:** SSE streaming and response lifecycle
- Response lifecycle events (onResponseStart/End)
- Tool execution streaming
- Thread state synchronization
- AssistantMessageItem creation and ThreadItemDoneEvent

**Location:** `.claude/skills/chatkit-streaming/SKILL.md`

### 3. chatkit-actions (Interactive UI)
**When to use:** Interactive widgets and buttons (FUTURE)
- Widget templates (.widget files)
- Server-side action handlers
- Entity tagging (@mentions)
- Composer tools

**Location:** `.claude/skills/chatkit-actions/SKILL.md`
**Note:** Not currently implemented - kept as reference for future enhancements

## Development Workflow

When implementing ChatKit features:

1. **Use the chatkit-integration skill** for:
   - Setting up ChatKitServer
   - Configuring SSE endpoint
   - PostgreSQL store implementation
   - Better Auth JWT integration

2. **Use the chatkit-streaming skill** for:
   - SSE event flow
   - Tool execution with streaming
   - Response lifecycle management
   - Thread persistence

3. **Refer to chatkit-actions skill** for:
   - Future interactive widget enhancements
   - Server action patterns
   - Widget templates

## Environment Variables

**Frontend (Phase II + III):**
```bash
NEXT_PUBLIC_BETTER_AUTH_SECRET=phase2-local-development-secret-key-change-in-production-min-32-chars-please
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here  # For production deployment
```

**Backend (Phase II + ChatKit):**
```bash
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-solitary-sunset-a4oczh67-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
PORT=8000
```

## Running Phase II + III (Current Working App)

```bash
# Terminal 1: Backend (Port 8000)
cd phase_2_web_App/backend
python app.py  # Runs FastAPI with ChatKit endpoint on port 8000

# Terminal 2: Frontend (Port 3000/3001)
cd phase_2_web_App/frontend
npm run dev  # Runs Next.js on port 3000 or 3001
```

Access at: `http://localhost:3000` or `http://localhost:3001`

The ChatKit widget appears in the bottom-right corner of the page.

## Natural Language Commands to Support

| User Says | MCP Tool | Database Operation |
|:----------|:---------|:-------------------|
| "Add a task to buy groceries" | add_task | INSERT INTO tasks |
| "Show me all my tasks" | list_tasks | SELECT FROM tasks WHERE user_id=? |
| "Mark task 3 as complete" | complete_task | UPDATE tasks SET status='completed' |
| "Delete the meeting task" | delete_task | DELETE FROM tasks |
| "Change task 1 to 'Call mom tonight'" | update_task | UPDATE tasks SET title='...' |

## Key Constraints

- **DO NOT modify existing Phase II task CRUD endpoints** - they work!
- **DO NOT create separate chatbot frontend** - use widget overlay in bottom-right
- **MUST use existing Better Auth** for authentication
- **MUST work with existing Neon database schema**
- **ChatKit widget should be non-intrusive** - collapsible/floating in bottom-right
- **Backend runs on port 8000** with ChatKit endpoint at `/api/v1/chatkit`
- **All tools must be stateless** and database-backed for production readiness

## Hackathon Submission

**For Phase III submission:**
1. Demo video (max 90s) showing ChatKit widget working
2. GitHub repo with integrated changes
3. Published app URL (Vercel)

See `Hackathon II - Todo Spec-Driven Development.md` for full requirements.

## Success Criteria

Phase III is successful when:
- ✅ ChatKit widget appears in bottom-right corner of existing todo app
- ✅ Backend /api/v1/chatkit endpoint on port 8000 handles SSE streaming
- ✅ User can chat naturally to manage todos
- ✅ OpenAI Agents SDK integration works via stream_agent_response()
- ✅ MCP tools execute stateless operations on PostgreSQL
- ✅ Authentication uses existing Better Auth tokens via query parameter
- ✅ No breaking changes to existing Phase II functionality

## Architecture Benefits

| Aspect | Benefit |
|:-------|:---------|
| **Port 8000 Unified** | Single FastAPI server handles both REST API and ChatKit endpoint |
| **OpenAI ChatKit SDK** | Official, maintained SDK for ChatKit integration |
| **OpenAI Agents SDK** | Standardized agent execution with AgentContext patterns |
| **MCP-Compatible Tools** | Stateless, database-backed tools following MCP patterns |
| **SSE Streaming** | Real-time response streaming without WebSocket complexity |
| **PostgreSQL Store** | Thread persistence across server restarts |
| **Better Auth JWT** | Existing authentication leveraged via query parameter |

---

**Reference:** Hackathon II Spec → `Hackathon II - Todo Spec-Driven Development.md`

**Skills Documentation:**
- chatkit-integration: `.claude/skills/chatkit-integration/SKILL.md`
- chatkit-streaming: `.claude/skills/chatkit-streaming/SKILL.md`
- chatkit-actions: `.claude/skills/chatkit-actions/SKILL.md`
