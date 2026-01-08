# Task Service Contract: TaskFlow

**Feature**: 002-taskflow-ux-upgrade
**Date**: 2026-01-08

---

## Overview

This contract defines the task management service interface, including CRUD operations, filtering, and view generation.

---

## Task Service Interface

### ITaskService

```typescript
interface ITaskService {
  // CRUD Operations
  createTask(input: CreateTaskInput): Task;
  updateTask(id: string, input: UpdateTaskInput): Task;
  deleteTask(id: string): void;
  getTask(id: string): Task | null;
  getAllTasks(): Task[];

  // Completion
  toggleComplete(id: string): Task;
  completeTask(id: string): Task;
  uncompleteTask(id: string): Task;

  // Reordering
  reorderTask(id: string, newIndex: number): void;
  moveTaskToProject(id: string, projectId: string | null): Task;

  // Views
  getTodayTasks(): Task[];
  getUpcomingTasks(): Task[];
  getHighPriorityTasks(): Task[];
  getOverdueTasks(): Task[];
  getCompletedTasks(): Task[];
  getTasksByProject(projectId: string): Task[];
  getTasksByTag(tagId: string): Task[];
  getFocusModeTasks(count?: number): Task[];
}
```

---

## Input Types

### CreateTaskInput

```typescript
interface CreateTaskInput {
  title: string;                           // Required, 1-500 chars
  priority?: "low" | "medium" | "high";    // Default: "medium"
  dueDate?: string | null;                 // ISO 8601 date
  projectId?: string | null;
  tags?: string[];
}
```

### UpdateTaskInput

```typescript
interface UpdateTaskInput {
  title?: string;
  priority?: "low" | "medium" | "high";
  dueDate?: string | null;
  projectId?: string | null;
  tags?: string[];
}
```

---

## View Definitions

### Today View

**Filter**: `dueDate == today && !completed`
**Sort**: Priority (high → medium → low), then sortOrder

```typescript
function getTodayTasks(): Task[] {
  const today = startOfDay(new Date()).toISOString();
  return tasks
    .filter(t => !t.completed && t.dueDate === today)
    .sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      const pDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      return pDiff !== 0 ? pDiff : a.sortOrder - b.sortOrder;
    });
}
```

### Upcoming View

**Filter**: `dueDate > today && dueDate <= today+7 && !completed`
**Sort**: dueDate (ascending), then priority

```typescript
function getUpcomingTasks(): Task[] {
  const today = startOfDay(new Date());
  const nextWeek = addDays(today, 7);
  return tasks
    .filter(t => !t.completed && t.dueDate > today && t.dueDate <= nextWeek)
    .sort((a, b) => {
      const dateDiff = new Date(a.dueDate) - new Date(b.dueDate);
      if (dateDiff !== 0) return dateDiff;
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
}
```

### High Priority View

**Filter**: `priority == "high" && !completed`
**Sort**: dueDate (nulls last), then sortOrder

### Overdue View

**Filter**: `dueDate < today && !completed`
**Sort**: dueDate (oldest first), then priority

### Completed View

**Filter**: `completed == true`
**Sort**: completedAt (newest first)
**Limit**: Last 100 completed tasks

### Focus Mode View

**Filter**: `dueDate == today && !completed`
**Sort**: Priority (high first), then sortOrder
**Limit**: Configurable (default: 5, range: 3-10)

---

## Validation Rules

### Task Title

```typescript
function validateTitle(title: string): ValidationResult {
  if (!title || title.trim().length === 0) {
    return { valid: false, error: "Title is required" };
  }
  if (title.length > 500) {
    return { valid: false, error: "Title must be 500 characters or less" };
  }
  return { valid: true };
}
```

### Due Date

```typescript
function validateDueDate(dueDate: string | null): ValidationResult {
  if (dueDate === null) return { valid: true };
  if (!isValidISO8601Date(dueDate)) {
    return { valid: false, error: "Invalid date format" };
  }
  return { valid: true };
}
```

### Project Reference

```typescript
function validateProjectId(projectId: string | null): ValidationResult {
  if (projectId === null) return { valid: true };
  if (!projectExists(projectId)) {
    return { valid: false, error: "Project not found" };
  }
  return { valid: true };
}
```

---

## Error Responses

| Error Code | Message | Cause |
|------------|---------|-------|
| TASK_NOT_FOUND | "Task not found" | Invalid task ID |
| VALIDATION_ERROR | "{field}: {message}" | Input validation failed |
| PROJECT_NOT_FOUND | "Project not found" | Invalid project reference |
| TAG_NOT_FOUND | "Tag not found" | Invalid tag reference |

---

## Events

The service emits events for UI synchronization:

```typescript
type TaskEvent =
  | { type: 'TASK_CREATED'; task: Task }
  | { type: 'TASK_UPDATED'; task: Task }
  | { type: 'TASK_DELETED'; taskId: string }
  | { type: 'TASK_COMPLETED'; task: Task }
  | { type: 'TASK_UNCOMPLETED'; task: Task }
  | { type: 'TASKS_REORDERED'; tasks: Task[] };
```

---

## Performance Guarantees

1. **View Generation**: < 50ms for 1000 tasks
2. **Single Task Operation**: < 10ms
3. **Reorder Operation**: < 100ms for affected tasks
4. **State Persistence**: < 200ms for full state save
