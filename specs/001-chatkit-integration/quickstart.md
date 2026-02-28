# Quickstart: ChatKit Integration

**Feature**: OpenAI ChatKit Integration for Todo Chatbot
**Phase**: III
**Last Updated**: 2026-02-26

## Overview

This guide helps you get started with the ChatKit integration development. It covers setting up the development environment, running the application locally, and testing the chat widget.

## Prerequisites

Before starting, ensure you have:

1. **Node.js** 18+ and npm
   ```bash
   node --version  # Should be 18.x or higher
   npm --version
   ```

2. **Python** 3.13+ and pip
   ```bash
   python --version  # Should be 3.13.x
   pip --version
   ```

3. **PostgreSQL** database (Neon or local)
   - Phase II uses Neon PostgreSQL
   - Connection string in `.env` file

4. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Required for AI agent responses

## Repository Structure

```
Evolution-of-ToDo-App/
├── phase_2_web_App/          # Main web application (modified)
│   ├── frontend/             # Next.js frontend (add ChatKit widget)
│   └── backend/              # FastAPI backend (add ChatKit endpoint)
├── phase_3_chatbot/          # Reference implementations
└── specs/001-chatkit-integration/  # This feature's documentation
```

## Environment Setup

### 1. Clone and Navigate

```bash
cd Evolution-of-ToDo-App
git checkout 001-chatkit-integration
```

### 2. Backend Setup

```bash
cd phase_2_web_App/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your values:
# - DATABASE_URL=postgresql://...
# - BETTER_AUTH_SECRET=your-secret-key
# - OPENAI_API_KEY=sk-...
# - PORT=8000
```

### 3. Frontend Setup

```bash
cd phase_2_web_App/frontend

# Install dependencies
npm install

# Install ChatKit package
npm install @openai/chatkit-react

# Copy environment template
cp .env.local.example .env.local

# Edit .env.local:
# - NEXT_PUBLIC_API_URL=http://localhost:8000
# - NEXT_PUBLIC_CHATKIT_URL=http://localhost:8000
# - NEXT_PUBLIC_ENABLE_CHATBOT=true
```

## Running Locally

### Terminal 1: Start Backend

```bash
cd phase_2_web_App/backend
source venv/bin/activate
python app/main.py
```

Backend should start at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Terminal 2: Start Frontend

```bash
cd phase_2_web_App/frontend
npm run dev
```

Frontend should start at:
- App: http://localhost:3000 (or http://localhost:3001)

### Terminal 3: Run Database Migrations (if needed)

```bash
cd phase_2_web_App/backend
source venv/bin/activate
alembic upgrade head
```

## Testing the Chat Widget

1. **Open the application**
   - Navigate to http://localhost:3000
   - Sign up or log in (create a user account)

2. **Locate the chat widget**
   - Look for the floating button in the bottom-right corner
   - Green button with chat icon

3. **Start chatting**
   - Click the chat button to open the widget
   - Try these commands:
     - "Add a task to buy groceries"
     - "Show me all my tasks"
     - "Complete the groceries task"
     - "What tasks do I have pending?"

4. **Verify task operations**
   - Go to the main /tasks page
   - Confirm tasks created/modified via chat appear in the list

## Development Workflow

### 1. Making Changes

**Frontend changes** (ChatKit widget):
```bash
cd phase_2_web_App/frontend
# Edit src/components/ChatKitOfficialWidget.tsx
# Changes auto-reload via Next.js hot reload
```

**Backend changes** (ChatKit endpoint):
```bash
cd phase_2_web_App/backend
# Edit app/api/v1/chatkit.py or related files
# Restart backend server to see changes
```

### 2. Running Tests

**Backend tests**:
```bash
cd phase_2_web_App/backend
pytest tests/
```

**Frontend tests**:
```bash
cd phase_2_web_App/frontend
npm test
```

### 3. Database Migrations

After changing database models:

```bash
cd phase_2_web_App/backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Common Issues

### Issue: Chat widget doesn't appear

**Solutions**:
1. Check `NEXT_PUBLIC_ENABLE_CHATBOT=true` in frontend `.env.local`
2. Verify you're logged in (chat requires authentication)
3. Check browser console for errors
4. Ensure backend is running on port 8000

### Issue: Chat shows "Connection error"

**Solutions**:
1. Verify backend URL: `NEXT_PUBLIC_CHATKIT_URL=http://localhost:8000`
2. Check backend logs for errors
3. Ensure WebSocket endpoint is accessible: `curl http://localhost:8000/health`
4. Check CORS configuration in backend

### Issue: AI responses don't work

**Solutions**:
1. Verify `OPENAI_API_KEY` is set in backend `.env`
2. Check API key has credits: https://platform.openai.com/usage
3. Check backend logs for OpenAI API errors
4. Ensure OpenAI package is installed: `pip show openai`

### Issue: Tasks not created/updated

**Solutions**:
1. Check backend task CRUD endpoints: http://localhost:8000/docs
2. Verify database connection string is correct
3. Check JWT token is valid (browser DevTools → Application → Local Storage)
4. Look for MCP tool errors in backend logs

## Debugging

### Frontend Debugging

1. **Browser Console**: F12 → Console tab
2. **React DevTools**: Install browser extension
3. **Network Tab**: Check WebSocket connection and API calls

### Backend Debugging

1. **Enable Debug Logging**:
   ```python
   # In app/main.py
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check Database**:
   ```bash
   # Connect to PostgreSQL
   psql $DATABASE_URL

   # Query conversations
   SELECT * FROM conversations ORDER BY created_at DESC LIMIT 5;

   # Query messages
   SELECT * FROM messages WHERE conversation_id = '...';
   ```

3. **Test API Endpoints**:
   - Visit http://localhost:8000/docs for Swagger UI
   - Test endpoints interactively

## Code Locations

### Frontend Files

| File | Purpose |
|------|---------|
| `src/app/layout.tsx` | Add ChatKitProvider wrapper |
| `src/components/ChatKitOfficialWidget.tsx` | Chat widget component |
| `src/lib/chatkit.ts` | ChatKit client configuration |
| `src/context/AuthContext.tsx` | Authentication token management |

### Backend Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, include ChatKit router |
| `app/api/v1/chatkit.py` | ChatKit WebSocket endpoint |
| `app/models/conversation.py` | Conversation SQLModel |
| `app/models/message.py` | Message SQLModel |
| `app/services/chat_service.py` | Conversation/message CRUD |
| `app/services/mcp_tools.py` | MCP tool implementations |
| `app/agents/todo_agent.py` | OpenAI agent integration |

## Next Steps

1. **Complete the implementation**: Follow tasks in `specs/001-chatkit-integration/tasks.md`
2. **Read the API contract**: `specs/001-chatkit-integration/contracts/chatkit-api.md`
3. **Review data model**: `specs/001-chatkit-integration/data-model.md`
4. **Test with natural language**: Try various task commands

## Getting Help

- **Documentation**: See `specs/001-chatkit-integration/` directory
- **Issue Tracker**: GitHub issues for this repository
- **Team Contact**: @madeeha (project lead)

## Resources

- **ChatKit Docs**: https://developers.openai.com/api/docs/guides/chatkit
- **OpenAI API**: https://platform.openai.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **SQLModel Docs**: https://sqlmodel.tiangolo.com
