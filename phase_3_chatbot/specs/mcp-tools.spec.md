# MCP Tool Specifications: Todo AI Chatbot

## Overview
This document specifies the Model Context Protocol (MCP) tools for todo operations in the Todo AI Chatbot system.

## Tool Versioning Strategy
- Version Format: Major.Minor.Patch (e.g., 1.0.0)
- Breaking Changes: Increment major version
- New Features: Increment minor version
- Bug Fixes: Increment patch version
- Current Version: 1.0.0

## Available Tools

### 1. add_task
**Purpose**: Add a new task to the user's todo list.

**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user adding the task",
    "required": true
  },
  "title": {
    "type": "string",
    "description": "The title of the task",
    "required": true,
    "minLength": 1
  },
  "description": {
    "type": "string",
    "description": "Optional description of the task",
    "required": false
  },
  "due_date": {
    "type": "string",
    "format": "date-time",
    "description": "Optional due date for the task",
    "required": false
  }
}
```

**Output Schema**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation succeeded",
    "required": true
  },
  "task": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "status": {"type": "string"},
      "due_date": {"type": "string", "format": "date-time"},
      "user_id": {"type": "string"}
    },
    "required": ["id", "title", "status", "user_id"]
  },
  "message": {
    "type": "string",
    "description": "Success message",
    "required": false
  },
  "error_code": {
    "type": "string",
    "description": "Error code if success is false",
    "required": false
  },
  "error_message": {
    "type": "string",
    "description": "Error message if success is false",
    "required": false
  },
  "recoverable": {
    "type": "boolean",
    "description": "Whether the error is recoverable",
    "required": false
  }
}
```

### 2. list_tasks
**Purpose**: List tasks for a specific user.

**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user whose tasks to list",
    "required": true
  },
  "status_filter": {
    "type": "string",
    "enum": ["all", "pending", "completed"],
    "description": "Filter tasks by status",
    "required": false,
    "default": "all"
  }
}
```

**Output Schema**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation succeeded",
    "required": true
  },
  "tasks": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string"},
        "due_date": {"type": "string", "format": "date-time"},
        "user_id": {"type": "string"}
      },
      "required": ["id", "title", "status", "user_id"]
    }
  },
  "total_count": {
    "type": "integer",
    "description": "Total number of tasks matching the filter",
    "required": true
  },
  "error_code": {
    "type": "string",
    "description": "Error code if success is false",
    "required": false
  },
  "error_message": {
    "type": "string",
    "description": "Error message if success is false",
    "required": false
  },
  "recoverable": {
    "type": "boolean",
    "description": "Whether the error is recoverable",
    "required": false
  }
}
```

### 3. update_task
**Purpose**: Update an existing task.

**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user updating the task",
    "required": true
  },
  "task_id": {
    "type": "integer",
    "description": "The ID of the task to update",
    "required": true
  },
  "title": {
    "type": "string",
    "description": "New title for the task",
    "required": false
  },
  "description": {
    "type": "string",
    "description": "New description for the task",
    "required": false
  },
  "status": {
    "type": "string",
    "enum": ["pending", "completed"],
    "description": "New status for the task",
    "required": false
  },
  "due_date": {
    "type": "string",
    "format": "date-time",
    "description": "New due date for the task",
    "required": false
  }
}
```

**Output Schema**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation succeeded",
    "required": true
  },
  "task": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "status": {"type": "string"},
      "due_date": {"type": "string", "format": "date-time"},
      "user_id": {"type": "string"}
    },
    "required": ["id", "title", "status", "user_id"]
  },
  "message": {
    "type": "string",
    "description": "Success message",
    "required": false
  },
  "error_code": {
    "type": "string",
    "description": "Error code if success is false",
    "required": false
  },
  "error_message": {
    "type": "string",
    "description": "Error message if success is false",
    "required": false
  },
  "recoverable": {
    "type": "boolean",
    "description": "Whether the error is recoverable",
    "required": false
  }
}
```

### 4. complete_task
**Purpose**: Mark a task as completed.

**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user completing the task",
    "required": true
  },
  "task_id": {
    "type": "integer",
    "description": "The ID of the task to complete",
    "required": true
  }
}
```

**Output Schema**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation succeeded",
    "required": true
  },
  "task": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "status": {"type": "string"},
      "due_date": {"type": "string", "format": "date-time"},
      "user_id": {"type": "string"}
    },
    "required": ["id", "title", "status", "user_id"]
  },
  "message": {
    "type": "string",
    "description": "Success message",
    "required": false
  },
  "error_code": {
    "type": "string",
    "description": "Error code if success is false",
    "required": false
  },
  "error_message": {
    "type": "string",
    "description": "Error message if success is false",
    "required": false
  },
  "recoverable": {
    "type": "boolean",
    "description": "Whether the error is recoverable",
    "required": false
  }
}
```

### 5. delete_task
**Purpose**: Delete a task.

**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user deleting the task",
    "required": true
  },
  "task_id": {
    "type": "integer",
    "description": "The ID of the task to delete",
    "required": true
  }
}
```

**Output Schema**:
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation succeeded",
    "required": true
  },
  "message": {
    "type": "string",
    "description": "Success message",
    "required": false
  },
  "error_code": {
    "type": "string",
    "description": "Error code if success is false",
    "required": false
  },
  "error_message": {
    "type": "string",
    "description": "Error message if success is false",
    "required": false
  },
  "recoverable": {
    "type": "boolean",
    "description": "Whether the error is recoverable",
    "required": false
  }
}
```

## Error Handling

### Standard Error Codes
- `TASK_NOT_FOUND`: Task with specified ID does not exist
- `PERMISSION_DENIED`: User does not have permission to perform the operation
- `INVALID_STATUS`: Invalid status value provided
- `ADD_TASK_ERROR`: Error occurred while adding task
- `LIST_TASKS_ERROR`: Error occurred while listing tasks
- `UPDATE_TASK_ERROR`: Error occurred while updating task
- `COMPLETE_TASK_ERROR`: Error occurred while completing task
- `DELETE_TASK_ERROR`: Error occurred while deleting task

### Error Response Format
All error responses follow the standard format with:
- `success: false`
- `error_code`: Machine-readable error code
- `error_message`: Human-readable error description
- `recoverable`: Boolean indicating if error is recoverable