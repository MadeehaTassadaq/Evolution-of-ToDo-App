# Storage Contract: TaskFlow

**Feature**: 002-taskflow-ux-upgrade
**Date**: 2026-01-08

---

## Overview

This contract defines the storage interface for TaskFlow. The implementation uses localStorage for MVP with an upgrade path to IndexedDB.

---

## Storage Interface

### IStorageService

```typescript
interface IStorageService {
  // State Operations
  loadState(): Promise<AppState | null>;
  saveState(state: AppState): Promise<void>;
  clearState(): Promise<void>;

  // Migration
  getVersion(): Promise<number>;
  setVersion(version: number): Promise<void>;

  // Health Check
  isAvailable(): boolean;
  getQuotaUsed(): Promise<number>; // bytes
}
```

---

## State Schema

### AppState (v1)

```typescript
interface AppState {
  version: 1;
  tasks: Task[];
  projects: Project[];
  tags: Tag[];
  settings: UserSettings;
}
```

### Task

```typescript
interface Task {
  id: string;           // UUID v4
  title: string;        // 1-500 chars
  completed: boolean;
  priority: "low" | "medium" | "high";
  dueDate: string | null;  // ISO 8601
  projectId: string | null;
  tags: string[];       // Tag IDs
  createdAt: string;    // ISO 8601
  completedAt: string | null;
  sortOrder: number;
}
```

### Project

```typescript
interface Project {
  id: string;           // UUID v4
  name: string;         // 1-100 chars
  description: string | null;
  color: string;        // Hex color
  createdAt: string;    // ISO 8601
  sortOrder: number;
}
```

### Tag

```typescript
interface Tag {
  id: string;           // UUID v4
  name: string;         // 1-50 chars, unique
  createdAt: string;    // ISO 8601
}
```

### UserSettings

```typescript
interface UserSettings {
  focusModeTaskCount: number;  // 3-10, default: 5
  theme: "light" | "dark";     // default: "light"
}
```

---

## Storage Keys

| Key | Type | Description |
|-----|------|-------------|
| `taskflow_state` | JSON string | Serialized AppState |
| `taskflow_version` | number | Schema version for migrations |

---

## Error Handling

### StorageError

```typescript
class StorageError extends Error {
  constructor(
    message: string,
    public readonly code: StorageErrorCode,
    public readonly cause?: unknown
  ) {
    super(message);
    this.name = 'StorageError';
  }
}

enum StorageErrorCode {
  QUOTA_EXCEEDED = 'QUOTA_EXCEEDED',
  PARSE_ERROR = 'PARSE_ERROR',
  WRITE_ERROR = 'WRITE_ERROR',
  NOT_AVAILABLE = 'NOT_AVAILABLE',
  MIGRATION_FAILED = 'MIGRATION_FAILED',
}
```

---

## Migration Contract

### IMigrationService

```typescript
interface IMigrationService {
  getCurrentVersion(): number;
  getTargetVersion(): number;
  needsMigration(storedVersion: number): boolean;
  migrate(state: unknown, fromVersion: number): AppState;
}
```

### Migration Registry

```typescript
type MigrationFn = (state: unknown) => unknown;

const migrations: Record<number, MigrationFn> = {
  1: (state) => state, // Initial version, no migration
  // 2: (state) => migrateV1ToV2(state),
};
```

---

## Guarantees

1. **Atomicity**: State is saved as a single JSON blob; partial writes are not possible
2. **Durability**: Data persists across browser sessions until explicitly cleared
3. **Consistency**: Schema version checked on every load; migrations run automatically
4. **Isolation**: Storage is per-origin; no cross-site data access

---

## Limitations

1. **Storage Quota**: ~5MB for localStorage (browser-dependent)
2. **No Sync**: Data is local to the browser; no cross-device sync
3. **No Encryption**: Data is stored in plaintext
4. **Single Tab**: No multi-tab synchronization (out of scope for MVP)
