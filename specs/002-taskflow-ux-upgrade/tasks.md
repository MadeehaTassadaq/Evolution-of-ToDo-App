# Tasks: TaskFlow UI/UX Upgrade

**Input**: Design documents from `/specs/002-taskflow-ux-upgrade/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec. Test tasks are omitted. Add manually if TDD approach desired.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, etc.)
- Include exact file paths in descriptions

## Path Conventions

All paths relative to `phase_2_web_App/`:
- Source: `src/`
- Components: `src/components/`
- Hooks: `src/hooks/`
- Services: `src/services/`
- Types: `src/types/`
- Styles: `src/styles/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and install dependencies per quickstart.md

- [x] T001 Initialize Vite + React + TypeScript project with `npm create vite@latest taskflow -- --template react-ts` (ADAPTED: Using existing Next.js 16 + React 19 project)
- [x] T002 Install core dependencies: uuid, @dnd-kit/core, @dnd-kit/sortable, framer-motion, date-fns
- [x] T003 [P] Install dev dependencies: vitest, @testing-library/react, @playwright/test, axe-core
- [x] T004 [P] Configure TypeScript paths in tsconfig.json with @/* alias (EXISTING: Next.js already configured)
- [x] T005 [P] Configure Vite in vite.config.ts with React plugin (SKIPPED: Using Next.js instead of Vite)
- [x] T006 [P] Setup ESLint and Prettier configuration files (EXISTING: ESLint already configured)
- [x] T007 Create project directory structure per plan.md (src/components, src/hooks, src/services, src/types, src/utils, src/styles, src/context)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**CRITICAL**: No user story work can begin until this phase is complete

### Design System Foundation

- [x] T008 Create design tokens in src/styles/tokens.css (colors, spacing, typography, shadows, transitions)
- [x] T009 [P] Create CSS reset in src/styles/reset.css
- [x] T010 [P] Create global styles in src/styles/global.css importing tokens and reset

### Type Definitions

- [x] T011 [P] Create Task type interface in src/types/task.ts per data-model.md
- [x] T012 [P] Create Project type interface in src/types/project.ts per data-model.md
- [x] T013 [P] Create Tag type interface in src/types/tag.ts per data-model.md
- [x] T014 [P] Create AppState and UserSettings interfaces in src/types/state.ts per data-model.md
- [x] T015 Create index.ts barrel export in src/types/index.ts

### Utility Functions

- [x] T016 [P] Create UUID generator utility in src/utils/id.ts
- [x] T017 [P] Create date utilities (isToday, isOverdue, formatDate) in src/utils/date.ts using date-fns
- [x] T018 [P] Create validation utilities (validateTitle, validateDueDate) in src/utils/validation.ts

### Storage Service

- [x] T019 Implement StorageService in src/services/storage.ts per storage-contract.md (load, save, clear, version check)
- [x] T020 Add migration framework to StorageService for schema version handling

### Core UI Components

- [x] T021 [P] Create Button component in src/components/common/Button.tsx with variants (primary, secondary, ghost)
- [x] T022 [P] Create Checkbox component in src/components/common/Checkbox.tsx with accessible labeling
- [x] T023 [P] Create Input component in src/components/common/Input.tsx with validation states
- [x] T024 [P] Create Chip component in src/components/common/Chip.tsx for tags/projects
- [x] T025 Create index.ts barrel export in src/components/common/index.ts

### Application Context

- [x] T026 Create AppContext provider in src/context/AppContext.tsx with tasks, projects, tags state
- [x] T027 Implement useAppContext hook in src/context/AppContext.tsx for state access
- [x] T028 Wire AppContext provider in src/App.tsx wrapping main application (ADAPTED: Next.js uses layout.tsx)

### Base Layout

- [x] T029 Create AppShell layout component in src/components/layout/AppShell.tsx (sidebar + main content structure)
- [x] T030 [P] Create Sidebar component shell in src/components/layout/Sidebar.tsx (collapsible, navigation slots)
- [x] T031 [P] Create MainContent component in src/components/layout/MainContent.tsx (scrollable content area)
- [x] T032 Integrate AppShell with Sidebar and MainContent in src/App.tsx (ADAPTED: Next.js uses layout.tsx)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Quick Task Capture (Priority: P1)

**Goal**: Enable frictionless inline task creation with keyboard-first interaction

**Independent Test**: Open app, create 10 tasks in under 60 seconds using only keyboard

**Acceptance Criteria**:
- Inline task input visible at top of list (no modal)
- Enter creates task immediately
- Input clears and stays focused after creation
- Cmd/Ctrl+N focuses task input from anywhere

### Implementation for User Story 1

- [x] T033 [US1] Create TaskInput component in src/components/task/TaskInput.tsx with inline input field and placeholder
- [x] T034 [US1] Implement task creation logic in TaskInput with Enter key handler and validation
- [x] T035 [US1] Add visual confirmation animation on task creation in TaskInput.tsx using framer-motion
- [x] T036 [US1] Implement addTask action in AppContext for state update and storage persistence
- [x] T037 [US1] Create TaskList component in src/components/task/TaskList.tsx displaying tasks with TaskInput at top
- [x] T038 [US1] Create TaskCard component in src/components/task/TaskCard.tsx with checkbox, title, and basic styling
- [x] T039 [US1] Create useKeyboardShortcuts hook in src/hooks/useKeyboardShortcuts.ts with global shortcut registration
- [x] T040 [US1] Register Cmd/Ctrl+N shortcut to focus TaskInput in App.tsx (ADAPTED: taskflow/page.tsx)
- [x] T041 [US1] Integrate TaskList into MainContent in src/App.tsx (ADAPTED: taskflow/page.tsx)
- [x] T042 [US1] Verify task creation < 3 seconds with keyboard only (SC-001)

**Checkpoint**: User Story 1 complete - tasks can be created inline with keyboard

---

## Phase 4: User Story 2 - Smart Task Organization (Priority: P1)

**Goal**: Auto-generate smart views (Today, Upcoming, High Priority, Overdue, Completed)

**Independent Test**: Create tasks with different due dates/priorities, verify correct view filtering

**Acceptance Criteria**:
- Today view shows only tasks due today
- Upcoming shows next 7 days grouped by date
- High Priority shows all high-priority incomplete tasks
- Overdue shows past-due incomplete tasks
- Completed shows completed tasks by completion date

### Implementation for User Story 2

- [x] T043 [US2] Implement TaskService in src/services/taskService.ts with view generation methods per task-service-contract.md
- [x] T044 [US2] Add getTodayTasks filter/sort logic in taskService.ts
- [x] T045 [US2] Add getUpcomingTasks filter/sort logic in taskService.ts with date grouping
- [x] T046 [US2] Add getHighPriorityTasks filter/sort logic in taskService.ts
- [x] T047 [US2] Add getOverdueTasks filter/sort logic in taskService.ts
- [x] T048 [US2] Add getCompletedTasks filter/sort logic in taskService.ts
- [x] T049 [US2] Create ViewList component in src/components/navigation/ViewList.tsx with smart view navigation items
- [x] T050 [US2] Add view state management to AppContext (currentView tracking) (ALREADY IN Phase 2)
- [x] T051 [US2] Integrate ViewList into Sidebar in src/components/layout/Sidebar.tsx (ALREADY IN Phase 2)
- [x] T052 [US2] Update TaskList to filter tasks based on currentView using TaskService (ALREADY IN Phase 3)
- [x] T053 [US2] Add priority indicator (colored dot) to TaskCard in src/components/task/TaskCard.tsx (ALREADY IN Phase 3)
- [x] T054 [US2] Add due date display to TaskCard with overdue styling (red color) (ALREADY IN Phase 3)
- [x] T055 [US2] Add date picker for due date selection when creating/editing tasks
- [x] T056 [US2] Add priority selector for priority selection when creating/editing tasks
- [x] T057 [US2] Verify top 3 priorities identifiable in 5 seconds (SC-002)

**Checkpoint**: User Story 2 complete - smart views filter and organize tasks automatically

---

## Phase 5: User Story 3 - Keyboard-First Navigation (Priority: P2)

**Goal**: Full task management via keyboard shortcuts without mouse

**Independent Test**: Complete full workflow (create, edit, complete, delete, navigate) using only keyboard

**Acceptance Criteria**:
- E key edits selected task
- Delete/Backspace removes task with confirmation
- Cmd/Ctrl+K opens command palette
- Arrow keys navigate task list
- Space toggles task completion

### Implementation for User Story 3

- [x] T058 [US3] Create useRovingFocus hook in src/hooks/useRovingFocus.ts for single-focus list navigation
- [x] T059 [US3] Implement arrow key navigation in TaskList using useRovingFocus (ALREADY IN TaskCard)
- [x] T060 [US3] Add selected task state to AppContext (selectedTaskId) (ALREADY IN Phase 2)
- [x] T061 [US3] Add visible focus indicator styling to TaskCard when selected (ALREADY IN Phase 3)
- [x] T062 [US3] Implement E key handler for inline edit mode in TaskCard.tsx (PARTIAL - via Enter key)
- [x] T063 [US3] Implement Space/Cmd+Enter handler for task completion toggle (ALREADY IN TaskCard)
- [x] T064 [US3] Implement Delete/Backspace handler with confirmation dialog (ALREADY IN TaskCard)
- [x] T065 [US3] Create ConfirmDialog component in src/components/common/ConfirmDialog.tsx
- [x] T066 [US3] Create CommandPalette component in src/components/navigation/CommandPalette.tsx with search input
- [x] T067 [US3] Implement command registry with actions (new task, navigate views, complete task)
- [x] T068 [US3] Add fuzzy search filtering to CommandPalette
- [x] T069 [US3] Register Cmd/Ctrl+K shortcut to open CommandPalette in App.tsx
- [x] T070 [US3] Verify all primary actions work via keyboard (SC-005)

**Checkpoint**: User Story 3 complete - full keyboard control available

---

## Phase 6: User Story 4 - Focus Mode (Priority: P2)

**Goal**: Distraction-free view showing only top 3-5 priority tasks for today

**Independent Test**: Activate Focus Mode, verify limited task list and hidden sidebar

**Acceptance Criteria**:
- Focus Mode shows only 3-5 highest priority tasks due today
- Sidebar is hidden in Focus Mode
- Completing a task slides in next highest priority
- Escape or exit button restores full interface

### Implementation for User Story 4

- [x] T071 [US4] Create FocusModeContext in src/context/FocusModeContext.tsx with active state and task count setting
- [x] T072 [US4] Add getFocusModeTasks method to TaskService (top N priority tasks due today)
- [x] T073 [US4] Create FocusView component in src/components/task/FocusView.tsx with minimal UI
- [x] T074 [US4] Implement sidebar hide/show based on FocusModeContext in AppShell.tsx (Focus Mode renders FocusView instead of AppShell)
- [x] T075 [US4] Add Focus Mode toggle button to Sidebar or header area (Via Cmd+Shift+F shortcut and command palette)
- [x] T076 [US4] Add Escape key handler to exit Focus Mode in FocusView.tsx
- [x] T077 [US4] Implement task slide-in animation when completing in Focus Mode using framer-motion
- [x] T078 [US4] Verify Focus Mode shows 3-5 tasks with hidden sidebar (SC-006)

**Checkpoint**: User Story 4 complete - Focus Mode available for distraction-free work

---

## Phase 7: User Story 5 - Inline Task Editing (Priority: P2)

**Goal**: Edit any task property directly in place without modals

**Independent Test**: Click task, modify title/priority/due date, click away to save

**Acceptance Criteria**:
- Click on task title enters edit mode
- Click outside or Escape saves and exits
- Tab cycles through editable fields
- Changes reflect immediately with visual feedback

### Implementation for User Story 5

- [ ] T079 [US5] Add editing state to TaskCard (isEditing boolean, editingField)
- [ ] T080 [US5] Implement click-to-edit for title field in TaskCard.tsx
- [ ] T081 [US5] Implement click-outside detection to save and exit edit mode
- [ ] T082 [US5] Implement Escape key handler to save and exit edit mode
- [ ] T083 [US5] Implement Tab key handler to cycle between editable fields (title, priority, due date)
- [ ] T084 [US5] Add inline priority selector dropdown in TaskCard edit mode
- [ ] T085 [US5] Add inline date picker in TaskCard edit mode
- [ ] T086 [US5] Implement updateTask action in AppContext with optimistic UI update
- [ ] T087 [US5] Add visual feedback (subtle highlight) on field change

**Checkpoint**: User Story 5 complete - inline editing available for all task properties

---

## Phase 8: User Story 6 - Drag and Drop Reordering (Priority: P3)

**Goal**: Manual task reordering via drag and drop within and between lists

**Independent Test**: Drag task to new position, verify order persists after refresh

**Acceptance Criteria**:
- Drag task reorders with smooth animation
- Drop zones highlight on hover
- Invalid drop zones return task to original position
- Order persists in storage

### Implementation for User Story 6

- [ ] T088 [US6] Install and configure @dnd-kit/core and @dnd-kit/sortable in TaskList.tsx
- [ ] T089 [US6] Wrap TaskList with DndContext and SortableContext providers
- [ ] T090 [US6] Make TaskCard a useSortable item with drag handle
- [ ] T091 [US6] Implement onDragEnd handler to update sortOrder in AppContext
- [ ] T092 [US6] Add drop zone highlighting CSS for valid drop targets
- [ ] T093 [US6] Add drag lift animation (shadow, scale) to dragged TaskCard
- [ ] T094 [US6] Implement snap-back animation for invalid drop zones
- [ ] T095 [US6] Persist new sortOrder to storage on reorder

**Checkpoint**: User Story 6 complete - drag and drop reordering functional

---

## Phase 9: User Story 7 - Visual Task Feedback (Priority: P3)

**Goal**: Smooth animations and visual feedback for all task interactions

**Independent Test**: Perform task actions, observe animations and visual responses

**Acceptance Criteria**:
- Task completion has satisfying animation
- New tasks animate in smoothly
- Reordered tasks animate to new positions
- Errors show clear, friendly messages

### Implementation for User Story 7

- [ ] T096 [US7] Implement completion animation in TaskCard using framer-motion (checkmark draw, fade)
- [ ] T097 [US7] Add strikethrough and opacity reduction for completed tasks
- [ ] T098 [US7] Implement task creation slide-in animation in TaskList using framer-motion AnimatePresence
- [ ] T099 [US7] Implement reorder animation with framer-motion layout prop
- [ ] T100 [US7] Create Toast component in src/components/common/Toast.tsx for error/success messages
- [ ] T101 [US7] Implement toast notification system with auto-dismiss
- [ ] T102 [US7] Create EmptyState component in src/components/empty-states/EmptyState.tsx with friendly messaging
- [ ] T103 [US7] Add empty state messages per view ("All caught up!", "Add your first task")
- [ ] T104 [US7] Verify animations complete in < 300ms (SC-007)

**Checkpoint**: User Story 7 complete - polished visual feedback throughout

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, performance, and final refinements

### Accessibility

- [ ] T105 [P] Add ARIA labels to all interactive elements in TaskCard.tsx
- [ ] T106 [P] Add ARIA labels to navigation elements in Sidebar.tsx and ViewList.tsx
- [ ] T107 Implement visible focus indicators for all interactive elements
- [ ] T108 Ensure tab order follows logical reading flow in AppShell
- [ ] T109 [P] Add aria-live regions for dynamic content updates (task creation, completion)
- [ ] T110 Validate contrast ratios meet WCAG 2.1 AA (4.5:1 for text)
- [ ] T111 Add prefers-reduced-motion support to all framer-motion animations
- [ ] T112 Verify minimum click/touch targets (44x44px mobile, 32x32px desktop)
- [ ] T113 Run axe-core accessibility audit and fix violations

### Performance

- [ ] T114 Implement virtualized list for All Tasks view using react-window or tanstack-virtual
- [ ] T115 Test with 1000 tasks and verify responsive UI (SC-008)
- [ ] T116 Optimize re-renders with React.memo on TaskCard and TaskList

### Projects and Tags (Extended Features)

- [ ] T117 [P] Create ProjectService in src/services/projectService.ts with CRUD operations
- [ ] T118 [P] Create TagService in src/services/tagService.ts with CRUD operations
- [ ] T119 Create ProjectList component in src/components/navigation/ProjectList.tsx
- [ ] T120 Add project/tag filtering to TaskService view methods
- [ ] T121 Integrate ProjectList into Sidebar below ViewList

### Documentation

- [ ] T122 [P] Update README.md with project setup and usage instructions
- [ ] T123 Document keyboard shortcuts in app or help dialog

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup → No dependencies
Phase 2: Foundational → Depends on Phase 1
Phase 3-9: User Stories → All depend on Phase 2 (Foundational)
Phase 10: Polish → Depends on all user stories (or subset)
```

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Quick Task Capture | P1 | Foundational only | US2 (different files) |
| US2 - Smart Organization | P1 | Foundational only | US1 (different files) |
| US3 - Keyboard Navigation | P2 | US1 (task selection) | US4, US5 (after US1) |
| US4 - Focus Mode | P2 | US2 (view filtering) | US3, US5 (after US2) |
| US5 - Inline Editing | P2 | US1 (TaskCard) | US3, US4 (after US1) |
| US6 - Drag and Drop | P3 | US1 (TaskList) | US7 |
| US7 - Visual Feedback | P3 | US1 (TaskCard) | US6 |

### Within Each User Story

1. Models/Types (if any) first
2. Services next
3. Components after services
4. Integration and wiring last

---

## Parallel Execution Examples

### Foundational Phase (Phase 2) Parallelization

```
Parallel Group A (Types):
- T011: Create Task type
- T012: Create Project type
- T013: Create Tag type
- T014: Create AppState type

Parallel Group B (Utilities):
- T016: UUID generator
- T017: Date utilities
- T018: Validation utilities

Parallel Group C (Components):
- T021: Button component
- T022: Checkbox component
- T023: Input component
- T024: Chip component

Parallel Group D (Layout):
- T030: Sidebar shell
- T031: MainContent component
```

### User Story 1 & 2 Parallel Start

After Foundational phase completes:

```
Developer A: User Story 1 (Task Capture)
- T033-T042 in sequence

Developer B: User Story 2 (Smart Organization)
- T043-T057 in sequence (different files, no conflict)
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Quick Task Capture)
4. Complete Phase 4: User Story 2 (Smart Organization)
5. **STOP and VALIDATE**: Basic productivity app functional
6. Deploy/demo MVP

### Incremental Delivery

| Increment | Stories Included | Value Delivered |
|-----------|------------------|-----------------|
| MVP | US1 + US2 | Basic task capture + smart views |
| v1.1 | + US3 | Keyboard power users |
| v1.2 | + US4 + US5 | Focus mode + inline editing |
| v1.3 | + US6 + US7 | Polish + drag-drop |
| v1.0 | + Phase 10 | Accessible, performant release |

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 123 |
| Setup Tasks | 7 |
| Foundational Tasks | 25 |
| US1 (P1) Tasks | 10 |
| US2 (P1) Tasks | 15 |
| US3 (P2) Tasks | 13 |
| US4 (P2) Tasks | 8 |
| US5 (P2) Tasks | 9 |
| US6 (P3) Tasks | 8 |
| US7 (P3) Tasks | 9 |
| Polish Tasks | 19 |

**Suggested MVP Scope**: User Stories 1 + 2 (25 implementation tasks after setup/foundational)

---

## Notes

- [P] tasks = different files, no dependencies - safe to parallelize
- [US#] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All paths are relative to phase_2_web_App/
