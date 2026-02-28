# Data Model: ChatKit Integration

**Phase**: 1 - Design
**Date**: 2026-02-26
**Status**: Draft

## Overview

This document defines the database schema for the ChatKit integration. The schema adds two new tables (`conversations` and `messages`) to the existing Phase II database while keeping the existing `tasks` table unchanged.

## Entity Relationship Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    users    │1       *│conversations│1       *│  messages   │
│ (existing)  │─────────│    (new)    │─────────│   (new)     │
└─────────────┘         └─────────────┘         └─────────────┘
                                                       │
                                                       │ (references)
                                                       ▼
                                               ┌─────────────┐
                                               │    tasks    │
                                               │ (existing)  │
                                               └─────────────┘
```

## Tables

### 1. conversations

Stores chat session metadata for each user's conversation with the AI assistant.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique conversation identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner of the conversation |
| title | VARCHAR(200) | DEFAULT 'New Conversation' | Optional conversation title |
| status | VARCHAR(20) | DEFAULT 'active', CHECK (status IN ('active', 'closed')) | Conversation status |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for user's conversation list)
- `idx_conversations_status` on `status` (for filtering active conversations)

**SQL**:
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) DEFAULT 'New Conversation',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class ConversationBase(SQLModel):
    title: Optional[str] = Field(default="New Conversation", max_length=200)
    status: str = Field(default="active", max_length=20)

class Conversation(ConversationBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
```

---

### 2. messages

Stores individual messages exchanged within a conversation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Unique message identifier |
| conversation_id | UUID | FK(conversations.id), NOT NULL, ON DELETE CASCADE, INDEX | Parent conversation |
| role | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant', 'tool_call')) | Message sender/role |
| content | TEXT | NOT NULL | Message content (JSON string for tool_call) |
| metadata | JSONB | NULL | Additional metadata (tool calls, etc.) |
| timestamp | TIMESTAMPTZ | DEFAULT NOW(), INDEX | Message timestamp |

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` (for conversation history)
- `idx_messages_timestamp` on `timestamp` (for chronological ordering)

**SQL**:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool_call')),
    content TEXT NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
```

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship, Column
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4

class MessageBase(SQLModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class Message(MessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

---

### 3. tasks (Existing - No Changes)

The existing `tasks` table from Phase II remains unchanged.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique task identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Task owner |
| title | VARCHAR(500) | NOT NULL | Task title |
| description | TEXT | NULL | Detailed description |
| status | VARCHAR(20) | DEFAULT 'pending', CHECK (status IN ('pending', 'completed')) | Task status |
| priority | VARCHAR(20) | NULL | Task priority |
| due_date | TIMESTAMPTZ | NULL | Due date |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update timestamp |

**Note**: This table is NOT modified as part of ChatKit integration. MCP tools call existing Phase II endpoints to interact with tasks.

---

## Relationships

### Conversation → Messages (One-to-Many)

- A `conversation` has many `messages`
- A `message` belongs to one `conversation`
- Cascading delete: Deleting a conversation deletes all its messages

### User → Conversations (One-to-Many)

- A `user` has many `conversations`
- A `conversation` belongs to one `user`
- Cascading delete: Deleting a user deletes all their conversations

### Message → Tasks (Reference Only)

- Messages may reference tasks in `metadata` (e.g., tool_call results)
- No foreign key constraint (tasks are in separate domain)
- References made by task UUID

---

## Metadata Schema

### Tool Call Message Metadata

When `role = 'tool_call'`, the `metadata` column contains:

```json
{
  "tool_name": "add_task | list_tasks | update_task | complete_task | delete_task",
  "tool_call_id": "uuid-of-the-tool-call",
  "tool_parameters": {
    // Parameters passed to the tool
  },
  "tool_result": {
    // Result from tool execution
    "success": true | false,
    // ... other result fields
  }
}
```

### Assistant Message Metadata

When `role = 'assistant'`, the `metadata` column may contain:

```json
{
  "tool_calls": [
    {
      "name": "complete_task",
      "arguments": { "task_title": "groceries" }
    }
  ],
  "model": "gpt-4o",
  "finish_reason": "tool_calls"
}
```

---

## Data Retention

### Retention Policy

- **Conversations**: Retained for 30 days after last update
- **Messages**: Retained for 30 days after creation
- **Archived**: Conversations older than 30 days are marked `status = 'closed'`

### Cleanup Job

Scheduled job (runs daily):

```sql
-- Close conversations older than 30 days
UPDATE conversations
SET status = 'closed'
WHERE updated_at < NOW() - INTERVAL '30 days'
  AND status = 'active';

-- Archive old messages (move to cold storage or delete)
-- Implementation depends on requirements
```

---

## Migration Strategy

### Alembic Migration

```python
# alembic/versions/001_add_chatkit_tables.py

from alembic import op
import sqlalchemy as sa
from sqlmodel import SQLModel

def upgrade():
    # Create conversations table
    op.execute("""
        CREATE TABLE conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(200) DEFAULT 'New Conversation',
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # Create messages table
    op.execute("""
        CREATE TABLE messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool_call')),
            content TEXT NOT NULL,
            metadata JSONB,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        )
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_conversations_user_id ON conversations(user_id)")
    op.execute("CREATE INDEX idx_messages_conversation_id ON messages(conversation_id)")
    op.execute("CREATE INDEX idx_messages_timestamp ON messages(timestamp)")

def downgrade():
    op.execute("DROP TABLE IF EXISTS messages")
    op.execute("DROP TABLE IF EXISTS conversations")
```

---

## Query Patterns

### Get User's Active Conversations

```sql
SELECT id, title, created_at, updated_at,
       (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
FROM conversations c
WHERE user_id = $1 AND status = 'active'
ORDER BY updated_at DESC;
```

### Get Conversation Messages

```sql
SELECT id, role, content, metadata, timestamp
FROM messages
WHERE conversation_id = $1
ORDER BY timestamp ASC;
```

### Get Latest Conversation for User

```sql
SELECT id, title
FROM conversations
WHERE user_id = $1 AND status = 'active'
ORDER BY updated_at DESC
LIMIT 1;
```

---

## Performance Considerations

1. **Message Pagination**: For long conversations, use cursor-based pagination with `timestamp`
2. **Index Optimization**: Indexes on `user_id` and `conversation_id` ensure fast lookups
3. **JSONB Storage**: Metadata stored as JSONB for efficient querying of tool calls
4. **Connection Pooling**: Use connection pooling for concurrent chat sessions
5. **Cleanup Job**: Run cleanup during low-traffic hours (midnight UTC)

---

## Security

1. **User Isolation**: All queries scoped by `user_id`
2. **Access Control**: Backend validates user owns conversation before returning messages
3. **Input Validation**: `role` column uses CHECK constraint to prevent invalid values
4. **SQL Injection**: Use parameterized queries (SQLModel handles this)
5. **Cascading Deletes**: ON DELETE CASCADE prevents orphaned records
