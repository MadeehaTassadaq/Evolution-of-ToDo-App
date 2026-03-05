---
name: chatkit-actions
description: Implements interactive widget actions and bidirectional communication patterns for ChatKit. This skill should be used when building AI-driven interactive UIs with buttons, forms, entity tagging (@mentions), composer tools, and server-handled widget actions. Covers the full widget lifecycle from creation to replacement.
---

# ChatKit Actions Skill

> **NOTE:** Interactive widgets and actions are NOT currently implemented in the ToDo ChatKit project. This skill is kept as a reference for future enhancements. The current implementation uses simple text chat only.

## Overview

This skill documents the full power of ChatKit's agentic UI capabilities - where AI can render interactive widgets, users can click buttons that trigger both client and server actions, and the conversation becomes a two-way interactive experience.

**Current Implementation Status:**
- The ToDo ChatKit project currently uses simple text-based chat (`output_text` messages)
- No interactive widgets, buttons, or server actions are implemented
- All task operations are handled through direct OpenAI function calling in the backend
- See `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/official_chatkit_server.py`

**Future Use:**
This skill provides patterns and templates for adding interactive UI elements to enhance the user experience with clickable task cards, inline completion buttons, priority selectors, and more.

## Core Concepts

### Action Handler Types

Widgets can specify where actions are handled:

| Handler | Defined In | Processed By | Use Case |
|---------|------------|--------------|----------|
| `"client"` | Widget template | Frontend `onAction` | Navigation, local state, send follow-up |
| `"server"` | Widget template | Backend `action()` method | Data mutation, widget replacement |

### Widget Lifecycle

1. Agent tool generates widget → yield WidgetItem
2. Widget renders in chat with action buttons
3. User clicks action → action dispatched
4. Handler processes action (client or server)
5. Optional: Widget replaced with updated state

## Key Patterns

1. **Widget Templates** (.widget files) - Reusable UI components
2. **Client Actions** - Frontend-only (navigation, follow-up messages)
3. **Server Actions** - Backend (data mutation, widget updates)
4. **Entity Tagging** - @mentions for users, tasks, articles
5. **Composer Tools** - Mode selection buttons

## Common Pitfalls

1. **action.arguments vs action.payload** - Use `action.payload` (arguments doesn't exist)
2. **RequestContext wrapping** - Don't wrap context, it's already RequestContext
3. **UserMessageItem required fields** - Include id, thread_id, created_at, inference_options
4. **Wrong content type** - Use `type="input_text"` for user messages

## Potential Enhancements for ToDo App

Interactive widgets could significantly enhance the ToDo ChatKit experience. Here are specific examples:

### 1. **Clickable Task Cards Widget**
Display tasks as interactive cards with inline action buttons:
```widget
type: task-list
title: "Your Tasks"
items: [
  {
    id: "task-123",
    title: "Buy groceries",
    status: "pending",
    actions: [
      { label: "✓ Complete", action: "server.complete", payload: { taskId: "123" } },
      { label: "Edit", action: "client.edit", payload: { taskId: "123" } },
      { label: "Delete", action: "server.delete", payload: { taskId: "123" } }
    ]
  }
]
```

### 2. **Task Priority Selector Widget**
Allow users to set task priority through visual buttons:
```widget
type: priority-selector
task_id: "123"
current_priority: "medium"
options: [
  { label: "Low", value: "low", color: "gray" },
  { label: "Medium", value: "medium", color: "yellow" },
  { label: "High", value: "high", color: "red" }
]
action: "server.set_priority"
```

### 3. **Entity Tagging for Task Assignment**
Use @mentions to assign tasks to team members:
```
User: "Create a task for code review @jane"
AI: Renders task card with @jane tagged
Action: Click @jane to view her assigned tasks
```

### 4. **Inline Task Creation Form**
Rich form widget for creating tasks with all fields:
```widget
type: task-form
fields: [
  { name: "title", type: "text", required: true },
  { name: "description", type: "textarea" },
  { name: "priority", type: "select", options: ["low", "medium", "high"] },
  { name: "assignee", type: "mention", entity_type: "user" }
]
actions: [
  { label: "Create Task", action: "server.create" },
  { label: "Cancel", action: "client.close" }
]
```

### 5. **Bulk Task Operations Widget**
Select multiple tasks and perform batch actions:
```widget
type: bulk-actions
selected_tasks: ["123", "456", "789"]
actions: [
  { label: "Complete All", action: "server.bulk_complete" },
  { label: "Delete All", action: "server.bulk_delete", confirm: true }
]
```

## Quick Start for ToDo App

To enable interactive widgets in the ToDo ChatKit project, make these changes:

### Backend Changes (`official_chatkit_server.py`)

**1. Import widget types:**
```python
from chatkit.types import WidgetItem, WidgetTemplate
```

**2. Add action handler method:**
```python
async def action(self, thread: ThreadMetadata, action: Action, context: dict) -> AsyncIterator[ThreadStreamEvent]:
    """Handle server-side widget actions."""
    user_id = context.get("user_id")
    db = context.get("db")

    if action.name == "complete":
        task_id = action.payload.get("taskId")
        task = db.get(Task, task_id)
        task.status = "completed"
        db.commit()

        # Replace widget with updated state
        yield self._task_list_widget(user_id, db)
```

**3. Yield widgets from tools:**
```python
# In list_tasks tool
yield WidgetItem(
    id=widget_id,
    thread_id=thread.id,
    created_at=utc_now(),
    template=self._task_list_template(),
    data={"tasks": tasks}
)
```

### Frontend Changes (`ChatKitOfficialWidget.tsx`)

**1. Add client action handler:**
```typescript
const chatKit = useChatKit({
  // ... existing config
  onAction: async (action) => {
    if (action.handler === 'client') {
      // Handle client-side actions
      if (action.name === 'edit') {
        // Open edit modal with task data
        openEditModal(action.payload.taskId);
      }
    }
    // Server actions are sent to backend automatically
  }
});
```

**2. Widget component registration (if needed):**
The ChatKit SDK handles most widgets automatically, but custom widgets may need registration.

### Example: Complete Task Action Flow

```
1. User sees task list widget with "✓ Complete" buttons
2. User clicks button → action dispatched
3. Frontend onAction intercepts if handler="client"
4. Backend action() method called if handler="server"
5. Backend updates database
6. Backend yields updated widget replacement
7. UI updates with new task state
```

## References

- `references/widget-templates.md` - Widget template syntax
- `references/client-vs-server-actions.md` - Action routing guide
- `references/entity-tagging.md` - @mention implementation
- `references/composer-tools.md` - Tool choice patterns
- `references/server-action-handler.py` - Complete backend action handler pattern

## Widget Template Assets

- `assets/line-select.widget` - Server action selection list
- `assets/name-suggestions.widget` - Client action with "more" button
- `assets/article-list.widget` - Rich card layout with images

## Evidence Sources

**Current Implementation:**
The ToDo ChatKit project does NOT currently use these interactive widget patterns. The current implementation at:
- Backend: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/backend/app/services/official_chatkit_server.py` - Uses simple `AssistantMessageItem` with `type="output_text"` only
- Frontend: `/home/madeeha/Documents/ToDoApp/Evolution-of-ToDo-App/phase_2_web_App/frontend/src/components/ChatKitOfficialWidget.tsx` - Standard ChatKit widget without action handlers

**Reference Patterns:**
All patterns in this skill are derived from OpenAI ChatKit advanced samples:
- `blueprints/openai-chatkit-advanced-samples-main/examples/cat-lounge/`
- `blueprints/openai-chatkit-advanced-samples-main/examples/metro-map/`
- `blueprints/openai-chatkit-advanced-samples-main/examples/news-guide/`

These patterns can be adapted for the ToDo app when adding interactive features.
