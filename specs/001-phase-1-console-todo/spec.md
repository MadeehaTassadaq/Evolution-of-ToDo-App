# Feature Specification: Phase I Console Todo Application

**Feature Branch**: `001-phase-1-console-todo`
**Created**: 2026-01-03
**Status**: Draft
**Input**: User description: "Phase I: In-Memory Python Console Todo App with Basic, Intermediate, and Advanced features"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Task Management (Priority: P1)

As a user, I want to create, view, update, delete, and mark tasks as complete using a console interface so that I can manage my daily todos without any external dependencies.

**Why this priority**: Core CRUD operations are the foundation of any todo system. Without these, the application provides no value. This represents the absolute minimum viable product.

**Independent Test**: Can be fully tested by launching the console app, adding a task titled "Buy groceries", viewing the task list to confirm it appears, updating the title to "Buy organic groceries", marking it as complete, and finally deleting it. Each operation should succeed and reflect in the task list.

**Acceptance Scenarios**:

1. **Given** an empty task list, **When** I add a task with title "Write report", **Then** the task appears in my task list with a unique identifier and is marked as incomplete
2. **Given** a task exists with ID "task-001", **When** I delete task "task-001", **Then** the task is removed from the list and no longer appears in view operations
3. **Given** a task exists with title "Review code", **When** I update the task title to "Review pull request", **Then** the task list reflects the new title
4. **Given** a task exists and is marked incomplete, **When** I mark the task as complete, **Then** the task's completion status changes to complete
5. **Given** a task exists and is marked complete, **When** I mark the task as incomplete, **Then** the task's completion status changes to incomplete
6. **Given** three tasks exist in the system, **When** I view the task list, **Then** all three tasks are displayed with their current state

---

### User Story 2 - Task Organization (Priority: P2)

As a user, I want to assign priorities, add tags, search, filter, and sort my tasks so that I can organize and find tasks efficiently in a growing list.

**Why this priority**: Once users have many tasks, they need organizational tools. This enables users to manage 10+ tasks effectively, which is where a todo app becomes genuinely useful.

**Independent Test**: Can be fully tested by creating 5 tasks with different priorities (high, medium, low), adding tags like "work" and "home" to different tasks, then searching for "meeting", filtering by priority "high", and sorting by priority to see high-priority tasks first.

**Acceptance Scenarios**:

1. **Given** a task exists, **When** I assign priority "high" to the task, **Then** the task displays with priority "high"
2. **Given** a task exists, **When** I add tags "work" and "urgent" to the task, **Then** the task is associated with both tags
3. **Given** five tasks exist with titles containing different words, **When** I search for keyword "report", **Then** only tasks with "report" in title, description, or tags are returned
4. **Given** ten tasks exist with mixed priorities, **When** I filter by priority "high", **Then** only tasks with priority "high" are displayed
5. **Given** tasks exist with various completion statuses, **When** I filter by completion status "incomplete", **Then** only incomplete tasks are shown
6. **Given** tasks exist with different priorities, **When** I sort by priority descending, **Then** tasks appear in order: high, medium, low

---

### User Story 3 - Time-Aware Task Management (Priority: P3)

As a user, I want to set due dates with times and create recurring tasks so that I can manage deadlines and repetitive responsibilities.

**Why this priority**: Time-awareness elevates the todo app from a simple list to a scheduling tool. This is essential for users managing deadlines and recurring commitments like "Daily standup" or "Monthly report".

**Independent Test**: Can be fully tested by creating a task with due date "2026-01-10 14:00", creating a recurring task "Team meeting" set to repeat weekly, marking the recurring task complete to verify the next occurrence is generated with the correct due date, and listing tasks to see due dates displayed.

**Acceptance Scenarios**:

1. **Given** I am creating a task, **When** I set due date "2026-01-15" and time "09:00", **Then** the task stores and displays the due date as "2026-01-15 09:00"
2. **Given** I am creating a task, **When** I set recurrence to "daily", **Then** the task is marked as recurring with interval "daily"
3. **Given** a recurring task exists with due date "2026-01-05" and recurrence "weekly", **When** I mark the task complete, **Then** a new incomplete occurrence is created with due date "2026-01-12" (7 days later)
4. **Given** tasks exist with various due dates, **When** I sort by due date ascending, **Then** tasks with earliest due dates appear first, followed by tasks with no due date
5. **Given** tasks exist with due dates in past, present, and future, **When** I filter by due date range "2026-01-01 to 2026-01-07", **Then** only tasks with due dates within that range are shown
6. **Given** a task with due date "2026-01-05 10:00" exists, **When** current time passes "2026-01-05 10:00", **Then** the system can identify the task as overdue

---

### Edge Cases

- What happens when a user tries to delete a task that doesn't exist? System returns an error message "Task not found" without crashing
- What happens when a user provides an invalid priority value (not "high", "medium", or "low")? System rejects the input and prompts for valid priority
- What happens when a user tries to create a task with an empty title? System rejects the task and requires a non-empty title
- What happens when a recurring task is marked complete but the recurrence interval is invalid or missing? System treats it as a one-time task and marks complete without creating a new occurrence
- What happens when a user searches with a keyword that matches no tasks? System returns an empty result set with message "No tasks match your search"
- What happens when due date is set to a past date? System accepts the date and can identify the task as overdue
- What happens when a task has multiple tags and the user removes one tag? Only the specified tag is removed, others remain
- What happens when a user attempts to update a non-existent task? System returns error "Task not found"
- What happens when sorting by priority and some tasks have no priority assigned? Tasks without priority appear last in the sorted list

## Requirements *(mandatory)*

### Functional Requirements

#### Basic Level (Phase I Core)

- **FR-001**: System MUST generate a unique identifier for each task automatically upon creation
- **FR-002**: System MUST allow users to create a task with a required title (non-empty string, max 200 characters)
- **FR-003**: System MUST allow users to optionally provide a description for a task (max 1000 characters)
- **FR-004**: System MUST store tasks in memory during the session (no persistence required)
- **FR-005**: System MUST allow users to view all tasks in a readable list format showing ID, title, completion status
- **FR-006**: System MUST allow users to delete a task by its unique identifier
- **FR-007**: System MUST allow users to update a task's title, description, priority, tags, due date, and recurrence settings
- **FR-008**: System MUST allow users to mark a task as complete without deleting it
- **FR-009**: System MUST allow users to toggle a task back to incomplete status
- **FR-010**: System MUST maintain task completion status as a boolean (complete/incomplete)

#### Intermediate Level (Organization & Usability)

- **FR-011**: System MUST support three priority levels: "high", "medium", "low"
- **FR-012**: System MUST allow tasks to exist without an assigned priority (default: no priority)
- **FR-013**: System MUST allow users to add multiple tags to a task (e.g., "work", "home", "urgent")
- **FR-014**: System MUST allow users to remove tags from a task
- **FR-015**: System MUST support keyword search across task title, description, and tags
- **FR-016**: System MUST support filtering tasks by completion status (complete/incomplete/all)
- **FR-017**: System MUST support filtering tasks by priority level
- **FR-018**: System MUST support filtering tasks by due date range
- **FR-019**: System MUST support filtering tasks by tags (show tasks with specific tag)
- **FR-020**: System MUST support sorting tasks by due date (ascending/descending)
- **FR-021**: System MUST support sorting tasks by priority (high → medium → low)
- **FR-022**: System MUST support sorting tasks alphabetically by title
- **FR-023**: Search and filter operations MUST be composable (e.g., search + filter by priority)

#### Advanced Level (Time-Aware Features)

- **FR-024**: System MUST allow users to set a due date for a task in format "YYYY-MM-DD"
- **FR-025**: System MUST allow users to optionally include time with due date in format "YYYY-MM-DD HH:MM"
- **FR-026**: System MUST validate due dates to ensure they follow ISO 8601 format
- **FR-027**: System MUST support recurring tasks with intervals: "daily", "weekly", "monthly", "yearly"
- **FR-028**: System MUST support custom recurring intervals (e.g., "every 3 days", "every 2 weeks")
- **FR-029**: System MUST automatically generate next occurrence when a recurring task is marked complete
- **FR-030**: System MUST calculate next due date based on recurrence interval (e.g., weekly adds 7 days)
- **FR-031**: System MUST identify tasks as overdue when current date/time exceeds due date/time
- **FR-032**: System MUST allow users to view tasks that have reminders approaching (e.g., due within 24 hours)
- **FR-033**: Recurring task completion MUST create new occurrence with status "incomplete" and updated due date

### Data Integrity Requirements

- **FR-034**: Task identifiers MUST be unique across all tasks in the session
- **FR-035**: Task state MUST be deterministic (same inputs produce same outputs)
- **FR-036**: Task data MUST be serializable for potential future export
- **FR-037**: All task operations MUST maintain referential integrity (cannot reference non-existent tasks)

### Validation Requirements

- **FR-038**: System MUST reject task creation if title is empty or exceeds 200 characters
- **FR-039**: System MUST reject priority values other than "high", "medium", "low", or null
- **FR-040**: System MUST reject invalid date formats for due dates
- **FR-041**: System MUST reject invalid recurrence interval values

### Key Entities *(include if feature involves data)*

- **Task**: Represents a single todo item with unique identifier, title, optional description, completion status, optional priority, optional tags (list), optional due date/time, optional recurrence configuration
- **RecurrenceRule**: Represents repetition pattern with interval type (daily/weekly/monthly/yearly/custom) and interval count (e.g., 1, 3, 7)
- **TaskList**: In-memory collection of all tasks, supports CRUD operations, search, filter, and sort

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create, view, update, delete, and complete tasks without system errors or crashes
- **SC-002**: Users can organize up to 100 tasks using priorities, tags, search, filter, and sort without performance degradation (operations complete in under 1 second)
- **SC-003**: Users can set up recurring tasks that automatically generate new occurrences upon completion with correct next due date calculation
- **SC-004**: 100% of search queries return results within 500ms for task lists up to 100 items
- **SC-005**: System correctly identifies overdue tasks by comparing current date/time with task due dates
- **SC-006**: Users can manage a realistic daily workload (20-30 tasks) efficiently using organizational features
- **SC-007**: All task state changes (create, update, delete, complete) are immediately reflected in subsequent view operations
- **SC-008**: Task data remains consistent and serializable throughout the session (no data corruption)

## Assumptions

- Users run the console application in a terminal environment that supports standard input/output
- Each user session is independent (no multi-user concurrency required)
- Date/time references use the system clock of the machine running the application
- Default recurrence intervals follow standard calendar rules (week = 7 days, month = 30 days, year = 365 days)
- Tasks without due dates are treated as "someday/maybe" tasks and appear last when sorting by due date
- Tag names are case-sensitive (e.g., "Work" and "work" are different tags)
- Maximum task list size is 1000 tasks per session (reasonable limit for in-memory storage)
- Console application uses UTF-8 encoding for text input/output
- Error messages are displayed in English
- Task IDs are generated using sequential numbering or UUID format (implementation choice)

## Out of Scope

- User authentication or multi-user support
- Data persistence across sessions (file storage, databases)
- Graphical user interface or web interface
- Real-time notifications or background reminders
- Task sharing or collaboration features
- Import/export functionality
- Undo/redo capabilities
- Task attachments or file uploads
- Integration with external calendars or services
- Natural language processing or AI-powered features
- Task dependencies or subtasks
- Time tracking or task duration estimates
- Custom task fields or metadata beyond specified attributes
