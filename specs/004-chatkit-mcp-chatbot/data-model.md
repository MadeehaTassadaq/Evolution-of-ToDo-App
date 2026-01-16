# Data Model: Todo AI Chatbot with ChatKit + MCP

**Feature**: 004-chatkit-mcp-chatbot
**Date**: 2026-01-14

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│    User     │──1:N──│  Conversation   │──1:N──│   Message   │
└─────────────┘       └─────────────────┘       └─────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐
│    Task     │
└─────────────┘
```

---

## Entities

### User

Represents an authenticated user of the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| username | String(100) | Unique, Not Null | Display name for login |
| email | String(255) | Unique, Not Null | Email address |
| hashed_password | String(255) | Not Null | Bcrypt hashed password |
| is_active | Boolean | Default: true | Account active status |
| created_at | DateTime | Not Null | Account creation timestamp |
| updated_at | DateTime | Not Null | Last modification timestamp |

**Relationships**:
- Has many Tasks
- Has many Conversations

---

### Task

A todo item belonging to a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK → User.id, Not Null | Owner of the task |
| title | String(500) | Not Null | Task title |
| description | Text | Nullable | Detailed description |
| status | Enum | Not Null, Default: 'pending' | Task status (pending/completed) |
| due_date | DateTime | Nullable | Optional due date |
| created_at | DateTime | Not Null | Task creation timestamp |
| updated_at | DateTime | Not Null | Last modification timestamp |

**Status Values**:
- `pending` - Task not yet completed
- `completed` - Task marked as done

**Validation Rules**:
- Title must be 1-500 characters
- Description max 5000 characters
- Due date must be in the future when set

---

### Conversation

A chat session (thread) belonging to a user, compatible with ChatKit's ThreadMetadata.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier (ChatKit thread_id) |
| user_id | UUID | FK → User.id, Not Null | Owner of the conversation |
| title | String(255) | Nullable | Optional conversation title |
| created_at | DateTime | Not Null | Conversation start timestamp |
| updated_at | DateTime | Not Null | Last activity timestamp |

**Relationships**:
- Belongs to User
- Has many Messages

**ChatKit Mapping**:
- `id` → ThreadMetadata.id
- `created_at` → ThreadMetadata.created_at

---

### Message

A single message in a conversation, compatible with ChatKit's ThreadItem types.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier (ChatKit item_id) |
| conversation_id | UUID | FK → Conversation.id, Not Null | Parent conversation |
| role | Enum | Not Null | Message role (user/assistant) |
| content | Text | Not Null | Message text content |
| tool_calls | JSON | Nullable | Array of tool call records |
| created_at | DateTime | Not Null | Message timestamp |

**Role Values**:
- `user` - Message from the user
- `assistant` - Response from the AI assistant

**Tool Call Structure** (JSON):
```json
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "tool_name": "add_task",
      "parameters": {"title": "Buy groceries"},
      "result": {"task_id": "uuid", "status": "created"}
    }
  ]
}
```

**ChatKit Mapping**:
- `id` → ThreadItem.id
- `role: user` → UserMessageItem
- `role: assistant` → AssistantMessageItem
- `created_at` → ThreadItem.created_at
- `content` → MessageContent.text

---

## Indexes

| Table | Index Name | Columns | Purpose |
|-------|------------|---------|---------|
| User | ix_user_username | username | Login lookup |
| User | ix_user_email | email | Email uniqueness check |
| Task | ix_task_user_id | user_id | List tasks by user |
| Task | ix_task_user_status | user_id, status | Filter tasks by status |
| Conversation | ix_conversation_user_id | user_id | List conversations by user |
| Message | ix_message_conversation_id | conversation_id | Load conversation messages |
| Message | ix_message_created_at | conversation_id, created_at | Pagination support |

---

## State Transitions

### Task Status

```
┌─────────┐     complete()    ┌───────────┐
│ pending │ ────────────────► │ completed │
└─────────┘                   └───────────┘
     ▲                              │
     │         reopen()             │
     └──────────────────────────────┘
```

**Transition Rules**:
- `pending` → `completed`: Via complete_task tool
- `completed` → `pending`: Via update_task tool (status change)

---

## Data Retention

| Entity | Retention Policy |
|--------|------------------|
| User | Indefinite (until account deletion) |
| Task | Indefinite (user can delete) |
| Conversation | 90 days of inactivity (configurable) |
| Message | Tied to Conversation lifecycle |

---

## Migration Notes

### Existing Tables
The following tables already exist and need schema verification:
- `user` - Verified with username, email, hashed_password, is_active columns
- `task` - May exist, needs verification
- `conversation` - May exist, needs verification
- `message` - May exist, needs verification

### Required Migrations
1. Ensure `task` table has all required columns
2. Add `tool_calls` JSON column to `message` table if missing
3. Add indexes for performance optimization
