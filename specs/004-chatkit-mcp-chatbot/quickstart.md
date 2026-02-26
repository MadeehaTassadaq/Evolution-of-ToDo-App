# Quickstart: Todo AI Chatbot with ChatKit + MCP

**Feature**: 004-chatkit-mcp-chatbot
**Date**: 2026-01-14

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (Neon account configured)
- OpenAI API key

## Environment Setup

### 1. Clone and Navigate

```bash
cd Evolution-of-ToDo-App/phase_3_chatbot
```

### 2. Backend Setup

```bash
cd backend

# Create/activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies (including new packages)
uv add openai-chatkit openai-agents mcp

# Verify installation
python -c "import chatkit; import agents; import mcp; print('All packages installed')"
```

### 3. Environment Variables

Create/update `.env` in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host/database

# Authentication
JWT_SECRET_KEY=your-secure-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Frontend
FRONTEND_ORIGIN=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies (ChatKit already added)
npm install

# Verify ChatKit installation
npm list @openai/chatkit-react
```

## Running the Application

### Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

### Start Frontend

```bash
cd frontend
npm run dev
```

**Expected output**:
```
▲ Next.js 14.x.x
- Local: http://localhost:3000
```

## Verification Steps

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{"status": "healthy", "service": "todo-ai-chatbot-backend"}
```

### 2. Register a Test User

```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "TestPass123"}'
```

**Expected**:
```json
{"user_id": "...", "username": "testuser", "message": "User registered successfully"}
```

### 3. Login

```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "TestPass123"}'
```

**Expected**:
```json
{"access_token": "eyJ...", "token_type": "bearer", "user_id": "...", "username": "testuser"}
```

### 4. Test ChatKit Endpoint (after implementation)

```bash
TOKEN="your-access-token"
curl -X POST http://localhost:8000/api/v1/chatkit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"action": "create_thread"}'
```

## Project Structure

```
phase_3_chatbot/
├── backend/
│   ├── main.py                 # FastAPI app entry
│   ├── api/
│   │   ├── router.py           # Route registration
│   │   └── v1/
│   │       ├── auth.py         # Auth endpoints
│   │       └── chatkit.py      # ChatKit endpoint (NEW)
│   ├── services/
│   │   ├── auth_service.py     # JWT handling
│   │   ├── chatkit_server.py   # ChatKitServer impl (NEW)
│   │   └── chatkit_store.py    # DB-backed Store (NEW)
│   ├── agents/
│   │   └── todo_agent.py       # OpenAI Agent config (UPDATE)
│   ├── mcp_tools/
│   │   └── server.py           # MCP tool definitions (NEW)
│   └── database/
│       ├── session.py          # DB connection
│       └── models/             # SQLModel entities
├── frontend/
│   ├── app/
│   │   ├── page.js             # ChatKit integration (UPDATE)
│   │   └── login/page.js       # Login page
│   └── components/
│       └── ChatKitPanel.tsx    # ChatKit wrapper (NEW)
└── specs/
    └── 004-chatkit-mcp-chatbot/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        └── contracts/
```

## Development Workflow

1. **Start both servers** (backend + frontend)
2. **Open browser** at http://localhost:3000
3. **Register/Login** to get authentication token
4. **Chat interface** loads with ChatKit UI
5. **Type natural language commands** like "Add a task to buy groceries"
6. **Observe** tool calls and task management

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: chatkit` | Run `uv add openai-chatkit` |
| 401 on ChatKit endpoint | Check Authorization header format |
| Database connection error | Verify DATABASE_URL in .env |
| CORS errors in browser | Check FRONTEND_ORIGIN matches |
| OpenAI API errors | Verify OPENAI_API_KEY is valid |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement ChatKit server (`services/chatkit_server.py`)
3. Implement MCP tools (`mcp_tools/server.py`)
4. Update frontend to use ChatKit component
5. Test end-to-end flow
