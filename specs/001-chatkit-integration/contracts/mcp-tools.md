# MCP Tools Contract

**Phase**: 1 - Design
**Date**: 2026-02-26
**Status**: Draft

## Overview

This document defines the Model Context Protocol (MCP) tools for task management operations. These tools are called by the OpenAI Agent to perform CRUD operations on tasks.

## Tool Definitions

### Tool 1: add_task

Create a new task for the authenticated user.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id", "title"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The UUID of the authenticated user"
    },
    "title": {
      "type": "string",
      "description": "The title of the task (1-500 characters)",
      "minLength": 1,
      "maxLength": 500
    },
    "description": {
      "type": "string",
      "description": "Optional detailed description of the task",
      "maxLength": 5000
    },
    "due_date": {
      "type": "string",
      "format": "date-time",
      "description": "Optional due date for the task (ISO 8601 format)"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task_id": {
      "type": "string",
      "format": "uuid"
    },
    "title": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": ["pending"]
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "message": {
      "type": "string"
    },
    "error": {
      "type": "string"
    }
  }
}
```

**Success Response Example**:
```json
{
  "success": true,
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "status": "pending",
  "created_at": "2026-02-26T10:00:00Z",
  "message": "Task 'Buy groceries' created successfully"
}
```

**Error Response Example**:
```json
{
  "success": false,
  "error": "Title is required"
}
```

---

### Tool 2: list_tasks

List tasks for the authenticated user with optional filtering.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The UUID of the authenticated user"
    },
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "default": "all",
      "description": "Filter tasks by status"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20,
      "description": "Maximum number of tasks to return"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "task_id": {
            "type": "string",
            "format": "uuid"
          },
          "title": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["pending", "completed"]
          },
          "due_date": {
            "type": "string",
            "format": "date-time"
          },
          "created_at": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    },
    "total_count": {
      "type": "integer"
    },
    "message": {
      "type": "string"
    },
    "error": {
      "type": "string"
    }
  }
}
```

**Success Response Example**:
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "due_date": "2026-02-27T10:00:00Z",
      "created_at": "2026-02-26T10:00:00Z"
    }
  ],
  "total_count": 1,
  "message": "Found 1 task"
}
```

---

### Tool 3: update_task

Update an existing task's details. Can identify task by ID or by title (for natural language matching).

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The UUID of the authenticated user"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the task to update (optional if task_title provided)"
    },
    "task_title": {
      "type": "string",
      "description": "The current title of the task - use for natural language matching (e.g., 'groceries' will match 'Buy groceries')"
    },
    "new_title": {
      "type": "string",
      "description": "New title for the task",
      "minLength": 1,
      "maxLength": 500
    },
    "new_description": {
      "type": "string",
      "description": "New description for the task",
      "maxLength": 5000
    },
    "new_due_date": {
      "type": "string",
      "format": "date-time",
      "description": "New due date for the task"
    },
    "new_status": {
      "type": "string",
      "enum": ["pending", "completed"],
      "description": "New status for the task"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task_id": {
      "type": "string",
      "format": "uuid"
    },
    "title": {
      "type": "string"
    },
    "status": {
      "type": "string"
    },
    "due_date": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    },
    "message": {
      "type": "string"
    },
    "error": {
      "type": "string"
    }
  }
}
```

**Natural Language Matching**:
- If `task_title` is provided, the tool performs a case-insensitive partial match
- Example: `task_title="groceries"` matches `"Buy groceries"`, `"Grocery shopping"`, etc.
- If multiple matches found, returns the most recent one

---

### Tool 4: complete_task

Mark a task as completed. Can identify task by ID or by title (for natural language matching).

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The UUID of the authenticated user"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the task to complete (optional if task_title provided)"
    },
    "task_title": {
      "type": "string",
      "description": "The title of the task to complete - use for natural language matching (e.g., 'groceries' will match 'Buy groceries')"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "task_id": {
      "type": "string",
      "format": "uuid"
    },
    "title": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": ["completed"]
    },
    "completed_at": {
      "type": "string",
      "format": "date-time"
    },
    "message": {
      "type": "string"
    },
    "error": {
      "type": "string"
    }
  }
}
```

**Error Cases**:
- Task not found (by ID or title)
- Task already completed (returns error to prevent duplicate completion)

---

### Tool 5: delete_task

Delete a task permanently. Can identify task by ID or by title (for natural language matching), or delete all completed tasks.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["user_id"],
  "properties": {
    "user_id": {
      "type": "string",
      "description": "The UUID of the authenticated user"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "The ID of the task to delete (optional if task_title or delete_completed provided)"
    },
    "task_title": {
      "type": "string",
      "description": "The title of the task to delete - use for natural language matching"
    },
    "delete_completed": {
      "type": "boolean",
      "default": false,
      "description": "If true, delete all completed tasks (ignores task_id/task_title)"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean"
    },
    "deleted_count": {
      "type": "integer"
    },
    "deleted_tasks": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "message": {
      "type": "string"
    },
    "error": {
      "type": "string"
    }
  }
}
```

**Bulk Delete Example**:
```json
{
  "success": true,
  "deleted_count": 3,
  "deleted_tasks": ["Buy groceries", "Call mom", "Email John"],
  "message": "Deleted 3 task(s)"
}
```

---

## Implementation Requirements

### 1. User ID Injection

The `user_id` parameter MUST be automatically injected by the backend before calling MCP tools. The OpenAI Agent should NOT include `user_id` in tool call arguments - it's added server-side for security.

### 2. Natural Language Task Matching

When `task_title` is provided (instead of `task_id`):
1. Perform case-insensitive partial match on task titles
2. Search within user's tasks only (scoped by `user_id`)
3. Return the most recently created match if multiple found
4. Return error if no match found

### 3. Error Handling

All tools MUST return structured errors:
- Validation errors (missing required fields)
- Not found errors (task doesn't exist)
- Permission errors (user doesn't own task)
- State errors (task already completed, etc.)

### 4. Transaction Safety

All database operations MUST be wrapped in transactions:
- Rollback on error
- Commit only on success
- Handle concurrent modifications

### 5. Calling Existing Phase II Endpoints

MCP tools should NOT directly access the database. Instead:
- Call existing Phase II task CRUD endpoints
- Pass `user_id` from JWT token
- Handle endpoint responses and errors
- Transform response format for MCP tool output

**Example**:
```python
async def complete_task(user_id: str, task_id: str = None, task_title: str = None):
    # Call existing Phase II endpoint
    response = await httpx.patch(
        f"{PHASE_II_API_URL}/api/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {get_token()}"}
    )
    return transform_response(response)
```

## Agent Instructions

The OpenAI Agent must be configured with:

1. **Tool Descriptions**: Clear descriptions for when to use each tool
2. **Parameter Hints**: Guidance on `task_id` vs `task_title` usage
3. **Confirmation Pattern**: Ask user before destructive actions (delete)
4. **Clarification Pattern**: Ask which task if multiple matches found

**Example Agent Instructions**:
```
When completing, updating, or deleting tasks:
- If user mentions a task by name (e.g., "the groceries task"), use task_title parameter
- If you have the exact task ID from a previous list, use task_id parameter
- Always confirm before deleting tasks
- If multiple tasks match the title, ask the user to specify
```
