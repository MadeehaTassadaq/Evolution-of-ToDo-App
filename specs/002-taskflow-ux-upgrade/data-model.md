# Data Model: TaskFlow UI/UX Upgrade

**Feature**: 002-taskflow-ux-upgrade
**Date**: 2026-01-08
**Status**: Complete

---

## Entity Overview

Based on the feature specification, TaskFlow requires four core entities:

| Entity | Purpose | Persistence |
|--------|---------|-------------|
| Task | Individual action item | localStorage/IndexedDB |
| Project | Grouping of related tasks | localStorage/IndexedDB |
| Tag | Flexible task categorization | localStorage/IndexedDB |
| View | Dynamic filtered presentation | Computed (not persisted) |

---

## Entity Definitions

### Task

The primary entity representing a single action item.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | string (UUID) | Yes | Generated | Unique identifier |
| title | string | Yes | - | Task title (1-500 chars) |
| completed | boolean | Yes | false | Completion status |
| priority | enum | Yes | "medium" | "low" \| "medium" \| "high" |
| dueDate | string (ISO) \| null | No | null | Due date in ISO 8601 format |
| projectId | string \| null | No | null | Reference to parent project |
| tags | string[] | No | [] | Array of tag IDs |
| createdAt | string (ISO) | Yes | Generated | Creation timestamp |
| completedAt | string (ISO) \| null | No | null | Completion timestamp |
| sortOrder | number | Yes | Generated | Manual sort position |

**Validation Rules**:

- `title` cannot be empty or whitespace-only
- `title` maximum length: 500 characters
- `priority` must be one of: "low", "medium", "high"
- `dueDate` must be valid ISO 8601 date string if provided
- `projectId` must reference existing project if provided
- `tags` must reference existing tags if provided
- `sortOrder` must be non-negative integer

**State Transitions**:

```
[Created] ──(toggle)──> [Completed]
     ↑                       │
     └───────(toggle)────────┘
```

---

### Project

A grouping container for related tasks.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | string (UUID) | Yes | Generated | Unique identifier |
| name | string | Yes | - | Project name (1-100 chars) |
| description | string \| null | No | null | Optional description |
| color | string | Yes | "#6B7280" | Hex color for visual indicator |
| createdAt | string (ISO) | Yes | Generated | Creation timestamp |
| sortOrder | number | Yes | Generated | Display order in sidebar |

**Validation Rules**:

- `name` cannot be empty or whitespace-only
- `name` maximum length: 100 characters
- `color` must be valid hex color (#RRGGBB or #RGB)
- `sortOrder` must be non-negative integer

**Relationships**:

- One Project → Many Tasks (via `task.projectId`)
- Deleting a project sets associated tasks' `projectId` to null (orphan, not delete)

---

### Tag

A lightweight label for flexible task categorization.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | string (UUID) | Yes | Generated | Unique identifier |
| name | string | Yes | - | Tag name (1-50 chars) |
| createdAt | string (ISO) | Yes | Generated | Creation timestamp |

**Validation Rules**:

- `name` cannot be empty or whitespace-only
- `name` maximum length: 50 characters
- `name` must be unique (case-insensitive)

**Relationships**:

- Many Tags ↔ Many Tasks (via `task.tags` array)
- Deleting a tag removes it from all tasks' `tags` arrays

---

### View (Computed)

Dynamic filtered/sorted presentation of tasks. Not persisted; computed on demand.

**Smart Views** (system-generated):

| View | Filter Criteria | Sort Order |
|------|-----------------|------------|
| Today | `dueDate == today && !completed` | Priority (desc), sortOrder |
| Upcoming | `dueDate > today && dueDate <= today+7 && !completed` | dueDate (asc), priority (desc) |
| High Priority | `priority == "high" && !completed` | dueDate (asc), sortOrder |
| Overdue | `dueDate < today && !completed` | dueDate (asc), priority (desc) |
| Completed | `completed == true` | completedAt (desc) |
| All Tasks | No filter | sortOrder (asc) |

**Project Views** (per project):

| View | Filter Criteria | Sort Order |
|------|-----------------|------------|
| Project: {name} | `projectId == project.id` | sortOrder (asc) |

---

## Storage Schema

### localStorage Structure

```typescript
interface AppState {
  version: number;        // Schema version for migrations
  tasks: Task[];
  projects: Project[];
  tags: Tag[];
  settings: UserSettings;
}

interface UserSettings {
  focusModeTaskCount: number;  // Default: 5
  theme: "light" | "dark";     // Default: "light"
}
```

### Storage Keys

| Key | Content | Max Size |
|-----|---------|----------|
| `taskflow_state` | Serialized AppState | ~5MB (localStorage limit) |
| `taskflow_version` | Schema version number | Tiny |

---

## Data Operations

### Task Operations

| Operation | Description | Validation |
|-----------|-------------|------------|
| Create | Add new task | Title required; priority defaults to medium |
| Update | Modify task fields | Title cannot become empty |
| Delete | Remove task | Confirm if task has content |
| Complete | Toggle completion | Set completedAt on complete; clear on uncomplete |
| Reorder | Change sortOrder | Recalculate affected tasks' sortOrder |

### Project Operations

| Operation | Description | Side Effects |
|-----------|-------------|--------------|
| Create | Add new project | None |
| Update | Modify project fields | None |
| Delete | Remove project | Orphan associated tasks (set projectId to null) |
| Reorder | Change sortOrder | Recalculate affected projects' sortOrder |

### Tag Operations

| Operation | Description | Side Effects |
|-----------|-------------|--------------|
| Create | Add new tag | None |
| Update | Rename tag | None |
| Delete | Remove tag | Remove from all tasks' tags arrays |

---

## Indexing Strategy

For performance with 1000+ tasks, maintain computed indexes:

| Index | Purpose | Structure |
|-------|---------|-----------|
| tasksByDueDate | Today/Upcoming/Overdue views | Map<dateString, Task[]> |
| tasksByPriority | High Priority view | Map<priority, Task[]> |
| tasksByProject | Project views | Map<projectId, Task[]> |
| tasksByTag | Tag filtering | Map<tagId, Task[]> |

Indexes are recomputed on task create/update/delete operations.

---

## Migration Strategy

When schema changes are needed:

1. Increment `version` in stored state
2. On app load, check `taskflow_version` against current
3. If mismatch, run migration functions sequentially
4. Update `taskflow_version` after successful migration

**Migration Example**:

```
v1 → v2: Add `sortOrder` field to all tasks (default: index position)
v2 → v3: Convert `dueDate` from legacy format to ISO 8601
```

---

## Type Definitions (TypeScript)

```typescript
type Priority = "low" | "medium" | "high";
type Theme = "light" | "dark";

interface Task {
  id: string;
  title: string;
  completed: boolean;
  priority: Priority;
  dueDate: string | null;
  projectId: string | null;
  tags: string[];
  createdAt: string;
  completedAt: string | null;
  sortOrder: number;
}

interface Project {
  id: string;
  name: string;
  description: string | null;
  color: string;
  createdAt: string;
  sortOrder: number;
}

interface Tag {
  id: string;
  name: string;
  createdAt: string;
}

interface UserSettings {
  focusModeTaskCount: number;
  theme: Theme;
}

interface AppState {
  version: number;
  tasks: Task[];
  projects: Project[];
  tags: Tag[];
  settings: UserSettings;
}
```
