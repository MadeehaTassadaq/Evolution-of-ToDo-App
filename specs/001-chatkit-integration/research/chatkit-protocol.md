# ChatKit Protocol Research

**Phase**: 0 - Research
**Date**: 2026-02-26
**Status**: Draft

## Overview

This document summarizes the official OpenAI ChatKit protocol requirements based on the official documentation and package specifications.

## References

- Official ChatKit Docs: https://developers.openai.com/api/docs/guides/chatkit
- GitHub Repository: https://github.com/openai/chatkit-js
- NPM Package: `@openai/chatkit-react`

## Frontend Package: `@openai/chatkit-react`

### Installation

```bash
npm install @openai/chatkit-react
```

### Key Components

#### 1. ChatKitProvider

Context provider that enables ChatKit throughout the application.

```typescript
import { ChatKitProvider } from '@openai/chatkit-react';

<ChatKitProvider options={{
  serverUrl: 'ws://localhost:8000/api/v1/chatkit/ws',
  token: authToken,
  threadId: existingThreadId  // Optional, for resuming conversations
}}>
  <App />
</ChatKitProvider>
```

**Options**:
- `serverUrl`: WebSocket endpoint URL
- `token`: Authentication token (passed via Authorization header)
- `threadId`: Optional existing conversation ID for resumption

#### 2. ChatInterface

The floating chat widget component.

```typescript
import { ChatInterface } from '@openai/chatkit-react';

<ChatInterface />
```

**Features**:
- Fixed position (bottom-right by default)
- Collapsible panel
- Auto-scrolling message list
- Typing indicators
- Built-in input handling

### Usage Pattern

```typescript
'use client';

import { ChatKitProvider, ChatInterface } from '@openai/chatkit-react';
import { useAuth } from './context/AuthContext';

export default function ChatKitWidget() {
  const { token } = useAuth();

  return (
    <ChatKitProvider options={{
      serverUrl: process.env.NEXT_PUBLIC_CHATKIT_URL,
      token: token,
    }}>
      <ChatInterface />
    </ChatKitProvider>
  );
}
```

## Backend Protocol

### WebSocket Endpoint

The backend must expose a WebSocket endpoint at the configured `serverUrl`.

**Endpoint**: `ws://localhost:8000/api/v1/chatkit/ws`
**Protocol**: WebSocket with Secure WebSocket (WSS) support for production

### Connection Flow

```
1. Frontend: WebSocket connect request with Authorization header
2. Backend: Verify JWT, extract user_id
3. Backend: Accept connection
4. Frontend: Send session initialization message
5. Backend: Load conversation history (if thread_id provided)
6. Ready for message exchange
```

### Message Format

#### Client → Server (User Message)

```json
{
  "type": "message",
  "thread_id": "uuid-or-null",
  "content": "Add a task to buy groceries"
}
```

#### Server → Client (Streaming Response)

**Text Delta** (streaming text response):
```json
{
  "event": "message_delta",
  "data": {
    "delta": {
      "content": "I've added"
    },
    "type": "text"
  }
}
```

**Tool Call Started**:
```json
{
  "event": "tool_call_started",
  "data": {
    "tool_name": "add_task",
    "parameters": {
      "title": "Buy groceries",
      "user_id": "user-uuid"
    }
  }
}
```

**Tool Call Completed**:
```json
{
  "event": "tool_call_completed",
  "data": {
    "tool_name": "add_task",
    "result": {
      "success": true,
      "task_id": "task-uuid",
      "message": "Task created successfully"
    }
  }
}
```

**Conversation Done**:
```json
{
  "event": "conversation_done",
  "data": {
    "conversation_id": "conv-uuid",
    "thread_id": "conv-uuid"
  }
}
```

**Error**:
```json
{
  "event": "error",
  "data": {
    "error": "Error message here"
  }
}
```

### Session Creation (REST)

Before WebSocket connection, the frontend creates a session via REST:

**Request**:
```http
POST /api/v1/chatkit/session
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "thread_id": "optional-existing-thread-id"
}
```

**Response**:
```json
{
  "client_secret": "session-secret-hash",
  "thread_id": "conversation-uuid",
  "user_id": "user-uuid",
  "mode": "custom_backend"
}
```

### Authentication

- JWT token passed via `Authorization: Bearer <token>` header
- Backend validates token and extracts `user_id` from claims
- All WebSocket messages scoped to authenticated user
- Connection rejected if token invalid

### Conversation History

**Endpoint**: `GET /api/v1/conversations/{thread_id}/messages`

**Response**:
```json
{
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user",
      "content": "Add a task to buy groceries",
      "timestamp": "2026-02-26T10:00:00Z"
    },
    {
      "id": "msg-uuid-2",
      "role": "assistant",
      "content": "I've added the task 'Buy groceries' to your list.",
      "timestamp": "2026-02-26T10:00:01Z"
    }
  ]
}
```

## Key Findings

### 1. No Custom Message History UI Required

The ChatKit package handles all message rendering, scrolling, and state management. The frontend only needs to:
- Wrap app in `ChatKitProvider`
- Render `<ChatInterface />`
- Pass authentication token

### 2. Custom Backend Mode

ChatKit supports "custom backend" mode where:
- Backend handles OpenAI API calls
- Backend executes tool calls
- Backend streams responses via WebSocket
- No workflowId required (unlike OpenAI-hosted mode)

### 3. Tool Calling Protocol

The backend must:
- Accept user messages
- Process with OpenAI Agents SDK
- Stream tool call events (started, completed)
- Stream text response deltas
- Send final conversation_done event

### 4. Session Continuity

- `thread_id` persists across sessions
- Frontend stores `thread_id` from first conversation
- Subsequent sessions pass `thread_id` to resume
- Backend loads conversation history for context

### 5. Error Handling

All errors must be sent as `error` events:
- Invalid authentication
- Tool execution failures
- OpenAI API errors
- Database errors

## Implementation Notes

### WebSocket vs SSE

The official ChatKit uses WebSocket (not SSE) for:
- Bidirectional communication
- Lower latency
- Better mobile support
- Native browser support

### Statelessness

The backend remains stateless:
- No in-memory session storage
- All conversation state in database
- WebSocket connection only handles message streaming
- Thread_id enables reconnect/resume

## Open Questions

1. **Rate Limiting**: How to handle rate limits on OpenAI API?
   - *Resolution*: Implement exponential backoff, return friendly error

2. **Concurrent Sessions**: Can user have multiple chat sessions?
   - *Resolution*: Yes, multiple thread_ids per user_id

3. **Message Retention**: How long to keep conversation history?
   - *Resolution*: 30 days per spec, with soft-delete
