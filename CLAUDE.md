# Claude Code Rules - Evolution of ToDo App (Hackathon II)

This project is part of **Hackathon II - Todo Spec-Driven Development**. See `Hackathon II - Todo Spec-Driven Development.md` for full hackathon requirements.

## Project Overview

**Current Phase:** Phase III - AI-Powered Todo Chatbot Integration

**Completed Phases:**
- **Phase I (Console):** In-memory Python console todo app - ✅ COMPLETE
- **Phase II (Web):** Full-stack web app with frontend (Next.js) and backend (FastAPI) - ✅ COMPLETE

**Active Work:**
- **Phase III (Chatbot):** Integrating OpenAI ChatKit widget into the existing Phase II web app

## Project Structure

```
Evolution-of-ToDo-App/
├── phase1-console/          # ✅ Phase I: Python console app (COMPLETE)
├── phase_2_web_App/         # ✅ Phase II: Full-stack web app (COMPLETE)
│   ├── frontend/            # Next.js 16+ frontend (working)
│   └── backend/             # FastAPI backend with Neon DB (working)
├── phase_3_chatbot/         # 🚧 Phase III: Chatbot integration (IN PROGRESS)
└── Hackathon II - Todo Spec-Driven Development.md  # Hackathon requirements
```

## Phase II Status (Web App - COMPLETE)

**Working Components:**
- Frontend: Next.js 16 (App Router) at `phase_2_web_App/frontend/`
- Backend: FastAPI at `phase_2_web_App/backend/`
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

## Phase III Goal: Chatbot Integration

**Objective:** Integrate OpenAI ChatKit widget into the existing Phase II web app's frontend (bottom-right corner) that can:
- Talk in natural language to manage todos
- Use OpenAI Agents SDK for AI logic
- Use MCP tools for task operations
- Work with existing Phase II backend

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase II Frontend (Next.js)                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Existing Todo UI (Working)                               │ │
│  │  - Task list, forms, etc.                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  📢 OpenAI ChatKit Widget (Bottom-Right Corner)           │ │
│  │  - Natural language chat interface                        │ │
│  │  - Talks to ChatKit backend endpoint                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Phase II Backend (FastAPI) + ChatKit Endpoint      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Existing REST API (Working)                              │ │
│  │  - /api/{user_id}/tasks/* CRUD endpoints                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  ChatKit WebSocket Endpoint (To Add)                      │ │
│  │  - /api/v1/chatkit/ws                                     │ │
│  │  - OpenAI Agents SDK integration                          │ │
│  │  - MCP tools for task operations                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Neon PostgreSQL Database
```

## Phase III Technology Stack

| Component | Technology |
|:----------|:-----------|
| Chat UI | **@openai/chatkit-react** (Official Widget) |
| Backend | Python FastAPI + OpenAI Agents SDK |
| MCP Tools | Official MCP SDK (mcp >= 1.25) |
| ORM | SQLModel |
| Database | Neon PostgreSQL |
| Authentication | Better Auth (existing from Phase II) |

## Development Guidelines

### 1. Integration Approach (NOT Separate App)
- **DO NOT** create a separate full chatbot page
- **DO** integrate ChatKit widget into existing `phase_2_web_App/frontend/`
- Widget should appear in bottom-right corner of existing todo app
- Backend chat endpoint added to existing `phase_2_web_App/backend/`

### 2. ChatKit Widget Placement
Add to `phase_2_web_App/frontend/app/layout.js`:
```jsx
<ChatKitProvider options={{ serverUrl: 'ws://localhost:7860/api/v1/chatkit/ws', token }}>
  <ChatInterface />  // Fixed position, bottom-right
</ChatKitProvider>
```

### 3. Backend Integration
Add to existing `phase_2_web_App/backend/`:
- `/api/v1/chatkit/ws` - WebSocket endpoint for ChatKit
- OpenAI Agents SDK integration
- MCP tools that call existing task CRUD operations

### 4. MCP Tools Specification
The MCP server must expose tools that use existing Phase II task operations:

| Tool | Uses Existing Endpoint |
|:-----|:---------------------|
| add_task | POST `/api/{user_id}/tasks` |
| list_tasks | GET `/api/{user_id}/tasks` |
| update_task | PUT `/api/{user_id}/tasks/{id}` |
| complete_task | PATCH `/api/{user_id}/tasks/{id}/complete` |
| delete_task | DELETE `/api/{user_id}/tasks/{id}` |

### 5. Authentication
- Use existing Better Auth JWT tokens
- ChatKit widget passes token via WebSocket
- Backend verifies token and extracts user_id

## Current Working Directories

**Phase II (Working - Do NOT break):**
- Frontend: `phase_2_web_App/frontend/` - Next.js on port 3000/3001
- Backend: `phase_2_web_App/backend/` - FastAPI on port 8000

**Phase III (Integration target):**
- Add ChatKit widget to: `phase_2_web_App/frontend/`
- Add chat endpoint to: `phase_2_web_App/backend/`
- May use code from: `phase_3_chatbot/` as reference

## Environment Variables

**Frontend (Phase II):**
```
NEXT_PUBLIC_BETTER_AUTH_SECRET=phase2-local-development-secret-key-change-in-production-min-32-chars-please
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (Phase II + ChatKit):**
```
DATABASE_URL=postgresql://neondb_owner:npg_uetLP5DAE7fj@ep-solitary-sunset-a4oczh67-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
JWT_SECRET_KEY=phase2-local-development-secret-key-change-in-production-min-32-chars-please
OPENAI_API_KEY=your-openai-api-key
PORT=8000
```

## Running Phase II (Current Working App)

```bash
# Terminal 1: Backend
cd phase_2_web_App/backend
python app.py  # Runs on port 8000

# Terminal 2: Frontend
cd phase_2_web_App/frontend
npm run dev  # Runs on port 3000/3001
```

Access at: `http://localhost:3000` or `http://localhost:3001`

## Development Workflow for Phase III

1. **Read existing Phase II code** to understand architecture
2. **Add ChatKit widget** to existing frontend layout
3. **Add WebSocket endpoint** to existing backend
4. **Implement MCP tools** that call existing task endpoints
5. **Test natural language commands** through the widget

## Natural Language Commands to Support

| User Says | MCP Tool |
|:----------|:---------|
| "Add a task to buy groceries" | add_task |
| "Show me all my tasks" | list_tasks |
| "Mark task 3 as complete" | complete_task |
| "Delete the meeting task" | list_tasks → delete_task |
| "Change task 1 to 'Call mom tonight'" | update_task |

## Key Constraints

- **DO NOT modify existing Phase II task CRUD endpoints** - they work!
- **DO NOT create separate chatbot frontend** - use widget overlay
- **MUST use existing Better Auth** for authentication
- **MUST work with existing Neon database schema**
- **ChatKit widget should be non-intrusive** - collapsible/floating

## Hackathon Submission

**For Phase III submission:**
1. Demo video (max 90s) showing ChatKit widget working
2. GitHub repo with integrated changes
3. Published app URL (Vercel)

See `Hackathon II - Todo Spec-Driven Development.md` for full requirements.

## Success Criteria

Phase III is successful when:
- ChatKit widget appears in bottom-right corner of existing todo app
- User can chat naturally to manage todos
- All MCP tools work with existing backend
- Authentication uses existing Better Auth tokens
- No breaking changes to existing Phase II functionality

---

**Reference:** Hackathon II Spec → `Hackathon II - Todo Spec-Driven Development.md`
