# Data Model: Todo AI Chatbot Backend

## Overview
This document defines the database models required for the stateless AI chatbot backend, extending the existing Phase II Todo application with conversation and message persistence capabilities.

## Entity: Conversation

### Fields
- **id** (UUID, Primary Key)
  - Unique identifier for the conversation
  - Auto-generated using UUID4
  - Required, immutable

- **user_id** (String, Foreign Key)
  - References the user who owns this conversation
  - Required, links to existing User model
  - Enforces user isolation

- **title** (String, Optional)
  - Auto-generated title based on first message or topic
  - Max length: 200 characters
  - Default: "New Conversation"

- **created_at** (DateTime)
  - Timestamp when conversation was created
  - Auto-set to current time on creation
  - Required, immutable

- **updated_at** (DateTime)
  - Timestamp when conversation was last updated
  - Auto-updated on any changes
  - Required

- **status** (String)
  - Current status of the conversation (active, archived)
  - Default: "active"
  - Required

### Relationships
- One-to-many with Message model (one Conversation to many Messages)

### Validation Rules
- user_id must reference an existing User
- created_at and updated_at use UTC timezone
- status must be one of: "active", "archived"

## Entity: Message

### Fields
- **id** (UUID, Primary Key)
  - Unique identifier for the message
  - Auto-generated using UUID4
  - Required, immutable

- **conversation_id** (UUID, Foreign Key)
  - References the conversation this message belongs to
  - Required, links to Conversation model
  - Cascading delete not allowed

- **role** (String)
  - Role of the message sender (user, assistant, tool)
  - Required
  - Must be one of: "user", "assistant", "tool"

- **content** (Text)
  - The actual message content
  - Required
  - Can contain structured data for tool messages

- **timestamp** (DateTime)
  - When the message was created
  - Auto-set to current time on creation
  - Required

- **metadata** (JSON, Optional)
  - Additional structured data about the message
  - For tool calls: contains tool name and parameters
  - For responses: may contain confidence scores

### Relationships
- Many-to-one with Conversation model (many Messages to one Conversation)

### Validation Rules
- conversation_id must reference an existing Conversation
- role must be one of: "user", "assistant", "tool"
- content must not be empty
- timestamp uses UTC timezone
- metadata must be valid JSON if provided

## Integration with Existing Models

### Relationship to User Model
- Conversation.user_id links to User.id
- Enforces that users can only access their own conversations
- Uses existing Better Auth user_id pattern

### Relationship to Task Model
- No direct relationship (agent uses MCP tools to interact with tasks)
- Messages may reference task IDs in content
- Conversation context may include task-related information

## Indexes for Performance

### Conversation Model
- Index on (user_id, created_at) for efficient user conversation queries
- Index on (user_id, status) for filtering active vs archived conversations

### Message Model
- Index on (conversation_id, timestamp) for chronological message retrieval
- Index on (conversation_id, role) for role-based queries

## State Transitions

### Conversation Status Transitions
- active → archived (when user archives conversation)
- archived → active (when user unarchives conversation)

## Constraints and Business Rules

1. **Data Isolation**: Users can only access conversations where user_id matches their own
2. **Immutability**: Messages cannot be modified after creation (only soft-delete if needed)
3. **Referential Integrity**: All foreign key relationships must reference existing records
4. **Temporal Consistency**: Message timestamps within a conversation should be chronologically ordered
5. **Size Limits**: Individual messages have reasonable size limits to prevent storage issues