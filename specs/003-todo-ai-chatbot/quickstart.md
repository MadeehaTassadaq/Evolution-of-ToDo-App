# Quickstart Guide: Todo AI Chatbot

## Overview
This guide provides instructions for setting up and running the Todo AI Chatbot feature. It covers environment setup, dependencies, and initial configuration.

## Prerequisites
- Python 3.11 or higher
- pip package manager
- uv (Python package manager)
- Access to OpenAI API (API key)
- Neon PostgreSQL database instance

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd phase_3_chatbot/backend
```

### 2. Set up Python Environment
```bash
# Install uv if not already installed
pip install uv

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv pip install -r requirements.txt
# Or if using pyproject.toml
uv pip install -e .
```

## Configuration

### 1. Environment Variables
Create a `.env` file in the backend directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database_name
NEON_DATABASE_URL=your_neon_database_connection_string
JWT_SECRET_KEY=your_jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_ORIGIN=http://localhost:3000
ENVIRONMENT=development
```

### 2. Database Setup
Run the database migrations to create the required tables:

```bash
python run_migrations.py
```

Or if using alembic directly:

```bash
alembic revision --autogenerate -m "Create conversation and message tables"
alembic upgrade head
```

## Running the Application

### 1. Start the Backend Server
```bash
# Activate your virtual environment
source .venv/bin/activate

# Run the FastAPI application
uvicorn main:app --reload --port 8000
```

### 2. Verify the Service
Visit `http://localhost:8000/health` to verify the service is running.

## API Usage

### 1. Authenticate
First, authenticate using your existing Better Auth session to obtain a JWT token.

### 2. Send a Chat Message
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries tomorrow",
    "conversation_id": null
  }'
```

### 3. Get Conversation History
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/<conversation-id>/messages?limit=50&offset=0" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Testing

### 1. Run Unit Tests
```bash
pytest tests/unit/
```

### 2. Run Integration Tests
```bash
pytest tests/integration/
```

### 3. Run All Tests
```bash
pytest
```

## Development

### 1. Adding New MCP Tools
To add new tools for the AI agent:

1. Create the tool function in `mcp_server/tools/todo_tools.py`
2. Register the tool with the server using the `@server.tool` decorator
3. Update the agent's tool definitions in `agents/todo_agent.py`

### 2. Data Model Changes
When modifying data models:

1. Update the model class in `database/models/`
2. Create a new alembic migration: `alembic revision --autogenerate -m "Description of changes"`
3. Apply the migration: `alembic upgrade head`

## Troubleshooting

### Common Issues

1. **OpenAI API Connection Errors**
   - Verify your `OPENAI_API_KEY` is set correctly
   - Check your internet connection
   - Ensure your OpenAI account is in good standing

2. **Database Connection Errors**
   - Verify your database URL is correct
   - Check that your database server is running
   - Ensure your database credentials are valid

3. **Authentication Errors**
   - Verify your JWT token is valid and not expired
   - Check that you're using the correct authentication headers
