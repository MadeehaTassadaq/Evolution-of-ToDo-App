# Quickstart Guide: Todo AI Chatbot Backend

## Overview
This guide provides essential information for developers to quickly understand and begin working on the stateless AI chatbot backend that integrates OpenAI Agents SDK with the existing Phase II Todo FastAPI application.

## Prerequisites

### System Requirements
- Python 3.11+
- uv package manager
- PostgreSQL (or Neon PostgreSQL for cloud deployment)
- OpenAI API key
- Existing Phase II Todo application backend

### Environment Setup
```bash
# Clone the repository
git clone <repo-url>
cd Evolution-of-ToDo-App

# Navigate to backend directory
cd backend

# Install dependencies with uv
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Set up environment variables
cp .env.example .env
# Edit .env to include your OpenAI API key and database connection
```

## Key Architecture Components

### 1. Conversation Management
- **Models**: `Conversation` and `Message` models in `src/models/`
- **Service**: `ChatService` in `src/services/chat_service.py` handles conversation logic
- **API**: `chat.py` in `src/api/v1/` provides `/api/{user_id}/chat` endpoint

### 2. AI Agent Integration
- **Agent**: `TodoAgent` in `src/agents/todo_agent.py` orchestrates OpenAI Agent
- **Tools**: MCP tool interfaces in `src/tools/` connect to external MCP server

### 3. Data Flow
1. User sends natural language message to `/api/{user_id}/chat`
2. System fetches conversation history from database
3. OpenAI Agent processes message with conversation context
4. Agent calls MCP tools for todo operations if needed
5. Assistant response is stored in database
6. Response is returned to user

## Running the Application

### Development Mode
```bash
# Start the backend server
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# The chat endpoint will be available at:
# POST http://localhost:8000/api/{user_id}/chat
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/unit/
uv run pytest tests/integration/
```

## Key Endpoints

### Chat Endpoint
```
POST /api/{user_id}/chat
```

**Headers**:
- `Authorization: Bearer <token>` (Better Auth token)

**Request Body**:
```json
{
  "message": "Add a task to buy groceries tomorrow",
  "conversation_id": "optional-uuid-here"
}
```

**Response**:
```json
{
  "conversation_id": "uuid-of-conversation",
  "response": "I've added the task 'buy groceries' for tomorrow.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "result": "Task created successfully"
    }
  ]
}
```

## Development Workflow

### 1. Adding New MCP Tool Integration
1. Define the tool interface in `src/tools/todo_tools.py`
2. Update the agent's tool configuration in `src/agents/todo_agent.py`
3. Ensure the agent never directly modifies database state
4. Test the integration through the chat endpoint

### 2. Modifying Conversation Logic
1. Update the `Conversation` or `Message` models as needed
2. Update the `ChatService` methods to handle new logic
3. Ensure all changes maintain statelessness
4. Update relevant tests

### 3. Enhancing Agent Behavior
1. Modify system prompts in `src/agents/todo_agent.py`
2. Adjust tool calling behavior as needed
3. Ensure agent responses are properly persisted
4. Test with various natural language inputs

## Testing Strategy

### Unit Tests
- Test individual service methods in isolation
- Focus on business logic and data validation
- Located in `backend/tests/unit/`

### Integration Tests
- Test API endpoints with real database connections
- Verify end-to-end chat functionality
- Located in `backend/tests/integration/`

### Contract Tests
- Verify API contract compliance
- Test error handling and edge cases
- Located in `backend/tests/contract/`

## Common Tasks

### Creating a New Conversation
```python
from src.services.chat_service import ChatService
from sqlmodel import Session

# In your service or endpoint
chat_service = ChatService(session)
conversation = chat_service.create_conversation(user_id)
```

### Processing a Chat Message
```python
response = chat_service.process_message(
    user_id=user_id,
    message_text="Add a task to buy groceries",
    conversation_id=conversation_id  # Optional, creates new if not provided
)
```

### Retrieving Conversation History
```python
messages = chat_service.get_conversation_history(
    conversation_id=conversation_id,
    limit=50,  # Optional limit
    offset=0   # Optional offset for pagination
)
```

## Troubleshooting

### Common Issues
1. **OpenAI API Errors**: Verify your API key is set in environment variables
2. **Database Connection**: Ensure PostgreSQL is running and connection string is correct
3. **Authentication**: Confirm Better Auth tokens are properly configured
4. **MCP Tools Unavailable**: Check that MCP server is running and accessible

### Debugging the Agent
- Enable detailed logging in `src/agents/todo_agent.py`
- Check the message history being passed to the agent
- Verify tool configurations are correct
- Monitor tool call execution and responses

## Next Steps

1. Review the detailed API contracts in `specs/003-todo-ai-chatbot/contracts/`
2. Examine the complete data model in `specs/003-todo-ai-chatbot/data-model.md`
3. Explore the implementation plan in `specs/003-todo-ai-chatbot/plan.md`
4. Check existing tests for examples of expected behavior