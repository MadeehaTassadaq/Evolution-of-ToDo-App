# Data Model: Todo AI Chatbot

## Overview
This document defines the data models for the Todo AI Chatbot feature, including entities, relationships, and validation rules derived from the functional requirements.

## Entity: Conversation
**Description**: Represents a user's ongoing dialogue with the chatbot, including metadata like creation time, last activity, and status.

**Fields**:
- `id`: string (UUID) - Primary key, unique identifier for the conversation
- `user_id`: string - Foreign key referencing the user who owns this conversation
- `title`: string (max 200) - Display title for the conversation (default: "New Conversation")
- `status`: string (max 20) - Current status of the conversation (default: "active", values: "active", "archived", "deleted")
- `created_at`: datetime - Timestamp when the conversation was created
- `updated_at`: datetime - Timestamp when the conversation was last updated

**Relationships**:
- One-to-many: Conversation → Message (conversation has many messages)

**Validation Rules**:
- `user_id` must exist in the users table
- `status` must be one of the allowed values
- `title` must not exceed 200 characters

## Entity: Message
**Description**: Individual exchanges within a conversation, containing user input, AI responses, timestamps, and message types (user/assistant/tool).

**Fields**:
- `id`: string (UUID) - Primary key, unique identifier for the message
- `conversation_id`: string - Foreign key referencing the conversation this message belongs to
- `role`: string (max 20) - Role of the message sender (values: "user", "assistant", "tool")
- `content`: text - The actual content of the message
- `metadata_`: JSON - Optional metadata for the message (tool calls, parameters, etc.)
- `timestamp`: datetime - Timestamp when the message was created

**Relationships**:
- Many-to-one: Message → Conversation (message belongs to one conversation)

**Validation Rules**:
- `conversation_id` must exist in the conversations table
- `role` must be one of the allowed values ("user", "assistant", "tool")
- `content` must not be empty

## Entity: Todo (Existing)
**Description**: Represents a todo item, reused from existing application.

**Fields**:
- `id`: integer - Primary key
- `title`: string - Title of the todo
- `description`: text (optional) - Detailed description of the todo
- `status`: string - Status of the todo ("pending", "completed")
- `due_date`: string (optional) - Due date in ISO format
- `user_id`: string - ID of the user who owns this todo
- `created_at`: datetime - Timestamp when the todo was created
- `updated_at`: datetime - Timestamp when the todo was last updated

**Validation Rules**:
- `title` must not be empty
- `status` must be one of the allowed values
- `user_id` must be valid

## State Transitions

### Conversation State Transitions
- `active` → `archived`: When user chooses to archive the conversation
- `active` → `deleted`: When user chooses to delete the conversation
- `archived` → `active`: When user chooses to unarchive the conversation

### Todo State Transitions
- `pending` → `completed`: When user marks a task as completed
- `completed` → `pending`: When user reopens a completed task (optional functionality)

## Indexes
- `conversations.user_id`: Index on user_id for efficient user-based queries
- `conversations.created_at`: Index on creation time for chronological ordering
- `messages.conversation_id`: Index on conversation_id for efficient conversation retrieval
- `messages.timestamp`: Index on timestamp for chronological ordering
- `messages.role`: Index on role for efficient filtering by message type
