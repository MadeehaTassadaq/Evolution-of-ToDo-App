# Todo AI Chatbot API Reference

## Base URL
All API endpoints are prefixed with `/api`.

## Authentication
Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:
```
Authorization: Bearer {token}
```

## Endpoints

### Chat Operations

#### POST /api/v1/chat
Process natural language input and return AI-generated responses with potential task operations.

**Headers:**
- `Authorization: Bearer {token}` (Required)

**Request Body:**
```json
{
  "message": "string (required)",
  "conversation_id": "string (optional)"
}
```

**Response:**
```json
{
  "conversation_id": "string",
  "response": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "parameters": "object",
      "result": "object"
    }
  ],
  "timestamp": "string (ISO 8601)"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{"message": "Add a task to buy groceries", "conversation_id": "abc123"}'
```

#### GET /api/v1/conversations/{conversation_id}/messages
Retrieve message history for a specific conversation.

**Path Parameters:**
- `conversation_id` (string, required): The ID of the conversation

**Query Parameters:**
- `limit` (integer, optional): Maximum number of messages to return (default: 50, max: 100)
- `offset` (integer, optional): Number of messages to skip (default: 0)

**Headers:**
- `Authorization: Bearer {token}` (Required)

**Response:**
```json
{
  "conversation_id": "string",
  "messages": [
    {
      "id": "string",
      "role": "string (user|assistant|tool)",
      "content": "string",
      "timestamp": "string (ISO 8601)",
      "metadata": "object (optional)"
    }
  ],
  "pagination": {
    "limit": "integer",
    "offset": "integer",
    "total_count": "integer",
    "has_more": "boolean"
  }
}
```

### Authentication Operations

#### POST /api/v1/login
Authenticate a user and return an access token.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "string (default: bearer)",
  "user_id": "string",
  "username": "string"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "password123"}'
```

#### POST /api/v1/register
Register a new user account.

**Request Body:**
```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "user_id": "string",
  "username": "string",
  "message": "string"
}
```

## Error Responses

All error responses follow this format:
```json
{
  "detail": "string"
}
```

### Common Status Codes
- `200`: Success
- `400`: Bad Request - Invalid input or parameters
- `401`: Unauthorized - Invalid or missing authentication token
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource does not exist
- `500`: Internal Server Error - Unexpected server error

## Rate Limiting
API requests may be rate-limited. Exceeding the limit will result in a `429 Too Many Requests` response.

## Tool Specifications

### Available MCP Tools

#### add_task
Add a new task to the user's todo list.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `title` (string, required): The title of the task
- `description` (string, optional): Detailed description of the task
- `due_date` (string, optional): Due date in ISO format

**Response:**
```json
{
  "success": "boolean",
  "task": {
    "id": "integer",
    "title": "string",
    "description": "string",
    "status": "string (pending|completed)",
    "due_date": "string",
    "user_id": "string",
    "created_at": "string",
    "updated_at": "string"
  },
  "message": "string"
}
```

#### list_tasks
List tasks for a specific user.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `status_filter` (string, optional): Filter by status ("all", "pending", "completed")

**Response:**
```json
{
  "success": "boolean",
  "tasks": "[array of task objects]",
  "total_count": "integer"
}
```

#### update_task
Update an existing task.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `task_id` (integer, required): The ID of the task to update
- `title` (string, optional): New title
- `description` (string, optional): New description
- `status` (string, optional): New status ("pending", "completed")
- `due_date` (string, optional): New due date

**Response:**
```json
{
  "success": "boolean",
  "task": "{task object}",
  "message": "string"
}
```

#### complete_task
Mark a task as completed.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `task_id` (integer, required): The ID of the task to complete

**Response:**
```json
{
  "success": "boolean",
  "task": "{task object}",
  "message": "string"
}
```

#### delete_task
Delete a task.

**Parameters:**
- `user_id` (string, required): The ID of the user
- `task_id` (integer, required): The ID of the task to delete

**Response:**
```json
{
  "success": "boolean",
  "message": "string"
}
```

## Health Check

#### GET /
Root endpoint for basic service information.

**Response:**
```json
{
  "message": "Todo AI Chatbot Backend is running",
  "version": "string",
  "status": "operational"
}
```

#### GET /health
Detailed health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "todo-ai-chatbot-backend",
  "version": "string",
  "checks": {
    "database": "connected",
    "authentication": "enabled",
    "stateless": "true"
  }
}
```