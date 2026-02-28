# ChatKit API Contract

**Phase**: 1 - Design
**Date**: 2026-02-26
**Status**: Draft

## Overview

This document defines the API contract between the ChatKit frontend widget and the backend service. It includes REST endpoints for session management and WebSocket protocol for real-time chat.

## Base URL

**Development**: `http://localhost:8000`
**Production**: `https://api.example.com`

All endpoints are prefixed with `/api/v1`.

## Authentication

All requests require JWT authentication via the `Authorization` header:

```http
Authorization: Bearer <jwt-token>
```

The JWT token is obtained from the existing Better Auth system and passed to ChatKit endpoints.

---

## REST Endpoints

### 1. Create Chat Session

Creates a new chat session or resumes an existing one.

**Endpoint**: `POST /api/v1/chatkit/session`

**Request Headers**:
```http
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "thread_id": "optional-existing-conversation-id"
}
```

**Parameters**:
- `thread_id` (optional): UUID of existing conversation to resume. If omitted, creates new conversation.

**Response** (200 OK):
```json
{
  "client_secret": "sha256-hash-of-session-data",
  "thread_id": "conversation-uuid",
  "user_id": "user-uuid",
  "mode": "custom_backend"
}
```

**Error Responses**:

401 Unauthorized:
```json
{
  "detail": "Invalid authentication token"
}
```

500 Internal Server Error:
```json
{
  "detail": "Failed to create session"
}
```

**Notes**:
- `client_secret` is a hash for session validation (not a secret key)
- `thread_id` should be stored by frontend for session continuity
- Same `thread_id` can be used to resume conversation later

---

### 2. Get Conversation History

Retrieves message history for a conversation.

**Endpoint**: `GET /api/v1/conversations/{thread_id}/messages`

**Request Headers**:
```http
Authorization: Bearer <jwt-token>
```

**Path Parameters**:
- `thread_id`: UUID of the conversation

**Query Parameters**:
- `limit` (optional): Maximum number of messages to return (default: 100)
- `after` (optional): Cursor for pagination (message ID)

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": "msg-uuid-1",
      "role": "user",
      "content": "Add a task to buy groceries",
      "timestamp": "2026-02-26T10:00:00Z"
    },
    {
      "id": "msg-uuid-2",
      "role": "assistant",
      "content": "I've added 'Buy groceries' to your task list.",
      "timestamp": "2026-02-26T10:00:01Z"
    },
    {
      "id": "msg-uuid-3",
      "role": "tool_call",
      "content": null,
      "metadata": {
        "tool_name": "add_task",
        "tool_result": {
          "success": true,
          "task_id": "task-uuid"
        }
      },
      "timestamp": "2026-02-26T10:00:01Z"
    }
  ],
  "has_more": false
}
```

**Error Responses**:

403 Forbidden:
```json
{
  "detail": "Access denied to this conversation"
}
```

404 Not Found:
```json
{
  "detail": "Conversation not found"
}
```

**Notes**:
- Messages are ordered chronologically (oldest first)
- `role` can be: `user`, `assistant`, or `tool_call`
- `content` is null for `tool_call` messages (see `metadata` instead)
- `has_more` indicates if more messages available (pagination)

---

## WebSocket Protocol

### 3. Chat WebSocket Endpoint

Real-time bidirectional communication for chat messages.

**Endpoint**: `WS /api/v1/chatkit/ws`

**Connection**:
```
ws://localhost:8000/api/v1/chatkit/ws
```

**Secure WebSocket (Production)**:
```
wss://api.example.com/api/v1/chatkit/ws
```

**Connection Handshake**:

The WebSocket connection includes the JWT token in the initial handshake:

```http
Authorization: Bearer <jwt-token>
```

**Note**: Browser WebSocket API doesn't support custom headers. The token is passed via query parameter or subprotocol:
- Query parameter: `ws://host/api/v1/chatkit/ws?token=<jwt>`
- Or: Use REST session endpoint to get temporary connection token

### Client → Server Messages

#### Message Format

```json
{
  "type": "message",
  "thread_id": "conversation-uuid-or-null",
  "content": "User's message text"
}
```

**Fields**:
- `type`: Always "message" for user messages
- `thread_id`: Conversation ID (null for new conversation)
- `content`: The user's message text

**Example**:
```json
{
  "type": "message",
  "thread_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "Complete the groceries task"
}
```

### Server → Client Events

All server events follow this structure:
```json
{
  "event": "event-type",
  "data": { /* event-specific data */ }
}
```

#### Event: message_delta

Streaming text response from the AI.

```json
{
  "event": "message_delta",
  "data": {
    "delta": {
      "content": "I've marked"
    },
    "type": "text"
  }
}
```

Multiple deltas are sent as the response streams:
```json
{"event":"message_delta","data":{"delta":{"content":"I've "},"type":"text"}}
{"event":"message_delta","data":{"delta":{"content":"marked "},"type":"text"}}
{"event":"message_delta","data":{"delta":{"content":"the "},"type":"text"}}
{"event":"message_delta","data":{"delta":{"content":"task "},"type":"text"}}
{"event":"message_delta","data":{"delta":{"content":"as "},"type":"text"}}
{"event":"message_delta","data":{"delta":{"content":"complete."},"type":"text"}}
```

#### Event: tool_call_started

Indicates an MCP tool is being executed.

```json
{
  "event": "tool_call_started",
  "data": {
    "tool_name": "complete_task",
    "parameters": {
      "user_id": "user-uuid",
      "task_title": "groceries"
    }
  }
}
```

**Tool Names**: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`

#### Event: tool_call_completed

Indicates a tool execution completed successfully.

```json
{
  "event": "tool_call_completed",
  "data": {
    "tool_name": "complete_task",
    "result": {
      "success": true,
      "task_id": "task-uuid",
      "title": "Buy groceries",
      "status": "completed",
      "message": "Task marked as completed"
    }
  }
}
```

#### Event: tool_call_error

Indicates a tool execution failed.

```json
{
  "event": "tool_call_error",
  "data": {
    "tool_name": "complete_task",
    "error": "Task not found: groceries"
  }
}
```

#### Event: conversation_done

Indicates the conversation turn is complete.

```json
{
  "event": "conversation_done",
  "data": {
    "conversation_id": "conv-uuid",
    "thread_id": "conv-uuid"
  }
}
```

**Note**: `conversation_id` and `thread_id` are the same value. Frontend should store this for session continuity.

#### Event: error

General error event.

```json
{
  "event": "error",
  "data": {
    "error": "Error message description",
    "code": "ERROR_CODE"
  }
}
```

**Error Codes**:
- `AUTH_FAILED`: Invalid authentication
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error
- `TOOL_ERROR`: MCP tool execution failed

### Connection Lifecycle

```
1. WebSocket Open
   ↓
2. Client sends: {"type":"message","thread_id":null,"content":"..."}
   ↓
3. Server streams events:
   - message_delta (text response)
   - tool_call_started (if tool used)
   - tool_call_completed (tool result)
   - conversation_done (end)
   ↓
4. Connection stays open for next message
   ↓
5. Repeat from step 2 for new messages
```

### Error Handling

#### Connection Errors

If the WebSocket connection fails:
- Frontend should automatically reconnect
- Use exponential backoff: 1s, 2s, 4s, 8s, max 30s
- Preserve `thread_id` to resume conversation

#### Message Errors

If a message processing fails:
- Server sends `error` event
- Frontend displays error to user
- Connection remains open for retry

### Ping/Pong (Keep-Alive)

To keep connections alive, use WebSocket ping/pong:

**Server** sends ping every 30 seconds:
```
PING
```

**Client** responds with:
```
PONG
```

If no pong received after 60 seconds, server closes connection.

---

## Data Types

### UUID Format

All IDs use UUID v4 format:
```
123e4567-e89b-12d3-a456-426614174000
```

### Timestamp Format

All timestamps use ISO 8601 format with timezone:
```
2026-02-26T10:00:00Z
```

---

## Rate Limiting

**Endpoint**: Rate limits apply to prevent abuse.

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /chatkit/session | 10 requests | 1 minute |
| WebSocket connections | 5 connections | 1 minute |
| GET /conversations/*/messages | 60 requests | 1 minute |

**Rate Limit Response** (429 Too Many Requests):
```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 30
}
```

---

## CORS Configuration

**Allowed Origins** (development):
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:3001`

**Production**: Configure specific frontend domain.

**Allowed Headers**:
- `Authorization`
- `Content-Type`

**Allowed Methods**:
- GET, POST, OPTIONS
- WebSocket upgrades

---

## Security Considerations

1. **Token Validation**: All JWT tokens validated against Better Auth secret
2. **User Isolation**: All conversation/message access scoped to authenticated user
3. **Input Sanitization**: All user input sanitized before processing
4. **SQL Injection Prevention**: Use parameterized queries (SQLModel)
5. **XSS Prevention**: Output encoding in all responses

---

## Browser Compatibility

| Browser | WebSocket Support |
|---------|------------------|
| Chrome 16+ | ✅ Full support |
| Firefox 11+ | ✅ Full support |
| Safari 7+ | ✅ Full support |
| Edge (all) | ✅ Full support |
| IE 11 | ❌ Not supported |

**Note**: Application targets modern browsers only. IE11 not supported.
