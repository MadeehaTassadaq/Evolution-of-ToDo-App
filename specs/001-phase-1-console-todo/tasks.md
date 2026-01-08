
---
description: "Task list for Phase I Console Todo Application implementation"
---

# Tasks: Phase I Console Todo Application

**Input**: Design documents from `/specs/001-phase-1-console-todo/`
**Prerequisites**: plan.md (complete), spec.md (complete)

**Tests**: 
- Tests are mandatory and must be generated from acceptance criteria defined in the spec.
- No test code may be written manually.
- All tests must be produced by Claude Code during implementation.
- Failing tests must be resolved by refining the spec, not modifying code.


**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, at repository root
- Paths assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project root directory structure (src/, src/models/, src/services/, src/cli/, src/lib/)
- [X] T002 [P] Create __init__.py files in src/ and all subdirectories
- [X] T003 [P] Create main.py entry point in repository root

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Implement ID generation utility in src/lib/utils.py (UUID4)
- [X] T005 [P] Implement date/time utilities in src/lib/utils.py (ISO 8601 parsing and formatting)
- [X] T006 [P] Implement input validators in src/lib/validators.py (title length, priority values, date format)
- [X] T007 Implement Task model class in src/models/task.py (id, title, description, completed, priority, tags, due_date, recurrence)
- [X] T008 Implement RecurrenceRule model class in src/models/recurrence_rule.py (interval_type, interval_count)
- [X] T009 Implement TaskList repository class in src/models/task_list.py (in-memory dict + list storage with CRUD operations)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to create, view, update, delete, and mark tasks as complete via console CRUD operations

**Independent Test**: Launch console app, add task "Buy groceries", view list to confirm, update title to "Buy organic groceries", mark complete, delete task. All operations succeed.

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement TaskService.create_task() in src/services/task_service.py (validate title, generate ID, store task)
- [X] T011 [P] [US1] Implement TaskService.get_task(task_id) in src/services/task_service.py (lookup by ID, handle not found)
- [X] T012 [P] [US1] Implement TaskService.get_all_tasks() in src/services/task_service.py (return ordered list)
- [X] T013 [P] [US1] Implement TaskService.update_task(task_id, **updates) in src/services/task_service.py (validate updates, apply changes)
- [X] T014 [P] [US1] Implement TaskService.delete_task(task_id) in src/services/task_service.py (remove from storage)
- [X] T015 [P] [US1] Implement TaskService.toggle_complete(task_id) in src/services/task_service.py (toggle completion status)
- [X] T016 [US1] Implement command parser for 'add' command in src/cli/parser.py (parse title and description)
- [X] T017 [US1] Implement command parser for 'list' command in src/cli/parser.py (no arguments)
- [X] T018 [US1] Implement command parser for 'update' command in src/cli/parser.py (parse task ID and fields to update)
- [X] T019 [US1] Implement command parser for 'delete' command in src/cli/parser.py (parse task ID)
- [X] T020 [US1] Implement command parser for 'complete' command in src/cli/parser.py (parse task ID)
- [X] T021 [P] [US1] Implement renderer for task list display in src/cli/renderer.py (format table with ID, title, status)
- [X] T022 [P] [US1] Implement renderer for success/error messages in src/cli/renderer.py (user-friendly output)
- [X] T023 [US1] Implement 'add' command handler in src/cli/commands.py (call TaskService.create_task, render result)
- [X] T024 [US1] Implement 'list' command handler in src/cli/commands.py (call TaskService.get_all_tasks, render list)
- [X] T025 [US1] Implement 'update' command handler in src/cli/commands.py (call TaskService.update_task, render result)
- [X] T026 [US1] Implement 'delete' command handler in src/cli/commands.py (call TaskService.delete_task, render result)
- [X] T027 [US1] Implement 'complete' command handler in src/cli/commands.py (call TaskService.toggle_complete, render result)
- [X] T028 [US1] Implement REPL loop in main.py (read command, dispatch to parser, handle errors, repeat)

**Checkpoint**: At this point, User Story 1 (Basic CRUD) should be fully functional and testable independently. MVP is complete!

---

## Phase 4: User Story 2 - Task Organization (Priority: P2)

**Goal**: Enable users to assign priorities, add tags, search, filter, and sort tasks for efficient organization

**Independent Test**: Create 5 tasks with different priorities (high, medium, low), add tags like "work" and "home", search for "meeting", filter by priority "high", sort by priority

### Implementation for User Story 2

- [X] T029 [P] [US2] Extend TaskService.create_task() to support priority parameter in src/services/task_service.py
- [X] T030 [P] [US2] Extend TaskService.create_task() to support tags parameter in src/services/task_service.py
- [X] T031 [P] [US2] Implement TaskService.add_tag(task_id, tag) in src/services/task_service.py (add tag to task)
- [X] T032 [P] [US2] Implement TaskService.remove_tag(task_id, tag) in src/services/task_service.py (remove specific tag)
- [X] T033 [US2] Implement SearchService.search_tasks(keyword) in src/services/search_service.py (search title, description, tags)
- [X] T034 [US2] Implement SearchService.filter_by_status(completed) in src/services/search_service.py (filter complete/incomplete)
- [X] T035 [US2] Implement SearchService.filter_by_priority(priority) in src/services/search_service.py (filter by high/medium/low)
- [X] T036 [US2] Implement SearchService.filter_by_tag(tag) in src/services/search_service.py (tasks with specific tag)
- [X] T037 [US2] Implement SearchService.sort_by_due_date(ascending) in src/services/search_service.py (sort by due date)
- [X] T038 [US2] Implement SearchService.sort_by_priority() in src/services/search_service.py (sort high → medium → low)
- [X] T039 [US2] Implement SearchService.sort_by_title() in src/services/search_service.py (alphabetical sort)
- [X] T040 [US2] Implement command parser for 'search' command in src/cli/parser.py (parse keyword)
- [X] T041 [US2] Implement command parser for 'filter' command in src/cli/parser.py (parse filter type and value)
- [X] T042 [US2] Implement command parser for 'sort' command in src/cli/parser.py (parse sort criterion)
- [X] T043 [US2] Extend command parser for 'add' to accept --priority and --tags flags in src/cli/parser.py
- [X] T044 [US2] Implement command parser for 'tag' command in src/cli/parser.py (add/remove tags from task)
- [X] T045 [P] [US2] Extend renderer to display priority and tags in src/cli/renderer.py (update table format)
- [X] T046 [US2] Implement 'search' command handler in src/cli/commands.py (call SearchService.search_tasks, render results)
- [X] T047 [US2] Implement 'filter' command handler in src/cli/commands.py (call appropriate SearchService filter, render results)
- [X] T048 [US2] Implement 'sort' command handler in src/cli/commands.py (call appropriate SearchService sort, render results)
- [X] T049 [US2] Implement 'tag' command handler in src/cli/commands.py (call TaskService add/remove_tag, render result)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can now organize tasks effectively.

---

## Phase 5: User Story 3 - Time-Aware Task Management (Priority: P3)

**Goal**: Enable users to set due dates with times and create recurring tasks for deadline and repetition management

**Independent Test**: Create task with due date "2026-01-10 14:00", create recurring task "Team meeting" (weekly), mark recurring task complete to verify next occurrence generated with correct due date

### Implementation for User Story 3

- [X] T050 [P] [US3] Implement date calculation utilities in src/lib/utils.py (add_days, add_weeks, add_months, add_years for recurrence)
- [X] T051 [P] [US3] Extend TaskService.create_task() to support due_date parameter in src/services/task_service.py
- [X] T052 [P] [US3] Extend TaskService.create_task() to support recurrence parameter in src/services/task_service.py
- [X] T053 [US3] Implement RecurrenceService.calculate_next_due_date(current_due, rule) in src/services/recurrence_service.py (compute next occurrence based on interval)
- [X] T054 [US3] Implement RecurrenceService.generate_next_occurrence(task) in src/services/recurrence_service.py (create new incomplete task with updated due date)
- [X] T055 [US3] Extend TaskService.toggle_complete() to handle recurring tasks in src/services/task_service.py (generate next occurrence if recurring)
- [X] T056 [US3] Implement TaskService.is_overdue(task_id) in src/services/task_service.py (compare due_date with current time)
- [X] T057 [US3] Implement SearchService.filter_by_due_date_range(start, end) in src/services/search_service.py (filter by date range)
- [X] T058 [US3] Implement SearchService.get_overdue_tasks() in src/services/search_service.py (tasks past due date)
- [X] T059 [US3] Implement SearchService.get_upcoming_tasks(hours) in src/services/search_service.py (tasks due within N hours)
- [X] T060 [US3] Implement command parser for 'add' with --due-date flag in src/cli/parser.py (parse ISO 8601 format)
- [X] T061 [US3] Implement command parser for 'add' with --recurrence flag in src/cli/parser.py (parse daily/weekly/monthly/yearly/custom)
- [X] T062 [US3] Implement command parser for 'overdue' command in src/cli/parser.py (no arguments)
- [X] T063 [US3] Implement command parser for 'upcoming' command in src/cli/parser.py (optional hours parameter)
- [X] T064 [P] [US3] Extend renderer to display due dates and recurrence info in src/cli/renderer.py (update table format)
- [X] T065 [P] [US3] Implement renderer for overdue indicator in src/cli/renderer.py (highlight overdue tasks)
- [X] T066 [US3] Implement 'overdue' command handler in src/cli/commands.py (call SearchService.get_overdue_tasks, render results)
- [X] T067 [US3] Implement 'upcoming' command handler in src/cli/commands.py (call SearchService.get_upcoming_tasks, render results)

**Checkpoint**: All three user stories should now be independently functional. Complete time-aware todo management system!

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final refinements

- [X] T068 [P] Add input validation error messages across all commands in src/lib/validators.py
- [X] T069 [P] Add graceful error handling for edge cases (empty list, not found, invalid input) in src/cli/commands.py
- [X] T070 [P] Add help command and usage instructions in src/cli/commands.py
- [X] T071 [P] Add exit/quit command in src/cli/commands.py
- [X] T072 [P] Improve table rendering with proper column widths and alignment in src/cli/renderer.py
- [X] T073 [P] Add color coding for priorities and status (optional enhancement) in src/cli/renderer.py
- [X] T074 Code review and refactoring for consistency and readability across all modules
- [X] T075 Create README.md with usage examples and feature list

**Checkpoint**: Production-ready Phase I Console Todo Application

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all three user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable

### Within Each User Story

- Models before services (foundational phase handles this)
- Services before CLI (parser and commands depend on services)
- Parser before command handlers (handlers use parser)
- Command handlers before REPL integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: T002 and T003 can run in parallel
- **Foundational (Phase 2)**: T004, T005, T006 can run in parallel; then T007, T008 parallel; then T009
- **User Story 1**: Service methods (T010-T015) parallel; Parser commands (T016-T020) parallel; Renderers (T021-T022) parallel; Command handlers must be sequential after parser
- **User Story 2**: Service methods (T029-T032) parallel; SearchService methods (T033-T039) parallel; Parser extensions (T040-T044) parallel
- **User Story 3**: Utilities (T050) first; Service extensions (T051-T052) parallel; RecurrenceService methods (T053-T054) sequential; SearchService methods (T057-T059) parallel
- **Polish (Phase 6)**: T068-T073 can all run in parallel

---

## Parallel Example: User Story 1 (MVP)

```bash
# After Foundational phase complete, launch service methods in parallel:
T010: TaskService.create_task()
T011: TaskService.get_task()
T012: TaskService.get_all_tasks()
T013: TaskService.update_task()
T014: TaskService.delete_task()
T015: TaskService.toggle_complete()

# Then launch parser commands in parallel:
T016: Parser for 'add'
T017: Parser for 'list'
T018: Parser for 'update'
T019: Parser for 'delete'
T020: Parser for 'complete'

# Then launch renderers in parallel:
T021: Task list renderer
T022: Message renderer

# Then implement command handlers sequentially:
T023 → T024 → T025 → T026 → T027 → T028 (REPL loop last)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only - Recommended)

1. **Phase 1: Setup** (T001-T003) - ~15 minutes
2. **Phase 2: Foundational** (T004-T009) - ~2 hours
3. **Phase 3: User Story 1** (T010-T028) - ~4 hours
4. **STOP and VALIDATE**: Test all CRUD operations independently
5. **Result**: Working console todo app with basic features (MVP)

**Total MVP Time**: ~6-7 hours of focused implementation

### Incremental Delivery (All User Stories)

1. Complete Setup + Foundational → Foundation ready (~2.5 hours)
2. Add User Story 1 → Test independently → **MVP Complete** (~4 hours)
3. Add User Story 2 → Test independently → **Organization features ready** (~3 hours)
4. Add User Story 3 → Test independently → **Full feature set** (~3 hours)
5. Polish → **Production ready** (~1 hour)

**Total Full Implementation**: ~13-14 hours

### Parallel Team Strategy

With 3 developers after Foundational phase complete:

1. Team completes Setup + Foundational together (~2.5 hours)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (MVP) - T010-T028
   - **Developer B**: User Story 2 (Organization) - T029-T049
   - **Developer C**: User Story 3 (Time-aware) - T050-T067
3. Stories complete and integrate independently (~4 hours parallel work)
4. Team reviews and applies Polish together (~1 hour)

**Total Parallel Time**: ~7-8 hours with 3 developers

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** maps task to specific user story for traceability
- **Each user story is independently completable and testable**
- **MVP = User Story 1 only** (Tasks T001-T028)
- **No tests required** per spec - focus on functional implementation
- Commit after completing each user story phase
- Stop at any checkpoint to validate story independently
- **Python stdlib only** - no external dependencies
- All paths relative to repository root

---

## Task Summary

- **Total Tasks**: 75
- **Setup**: 3 tasks
- **Foundational**: 6 tasks (blocks all user stories)
- **User Story 1 (MVP)**: 19 tasks
- **User Story 2**: 21 tasks
- **User Story 3**: 18 tasks
- **Polish**: 8 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- **US1**: Add, view, update, delete, complete tasks via console
- **US2**: Assign priorities, add tags, search, filter, sort tasks
- **US3**: Set due dates, create recurring tasks, view overdue/upcoming

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (Tasks T001-T028) = ~6-7 hours
