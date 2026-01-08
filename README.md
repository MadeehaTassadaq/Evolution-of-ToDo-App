# Phase I Console Todo Application

A feature-rich, in-memory Python console todo application built with Spec-Driven Development principles. This application provides an **interactive menu-driven interface** for intuitive task management with full CRUD operations, organization features, and time-aware task handling.

## bonaude🎯 Interactive UI Highlights

✨ **No Commands to Memorize** - All options visible on screen
✨ **Numbered Task Selection** - Select tasks by number (1, 2, 3...), no IDs to remember
✨ **Guided Prompts** - Step-by-step instructions for every action
✨ **Self-Explanatory** - No help command needed, everything explained on screen
✨ **Safe Operations** - Confirmation prompts for destructive actions

## Features

### Basic Task Management (User Story 1)
- ✅ **Create tasks** with title and description
- ✅ **View all tasks** in a formatted table
- ✅ **Update tasks** (title, description, priority)
- ✅ **Delete tasks** by ID
- ✅ **Mark tasks as complete/incomplete** (toggle)

### Task Organization (User Story 2)
- ✅ **Priority levels**: high, medium, low
- ✅ **Tags**: Add multiple tags to tasks
- ✅ **Search**: Find tasks by keyword (title, description, tags)
- ✅ **Filter**: Filter by status, priority, or tag
- ✅ **Sort**: Sort by due date, priority, or title

### Time-Aware Management (User Story 3)
- ✅ **Due dates**: Set due dates with optional times
- ✅ **Recurring tasks**: Daily, weekly, monthly, yearly recurrence
- ✅ **Overdue detection**: Visual indicators for overdue tasks
- ✅ **Upcoming tasks**: View tasks due within specified hours

## Requirements

- Python 3.11 or higher
- `uv` package manager (recommended)

## Usage

### Running the Application

**With uv (recommended):**
```bash
uv run --no-project python3 main.py
```

**Or with standard Python:**
```bash
python3 main.py
```

**Demo with features showcase:**
```bash
python3 demo_interactive.py
```

### Interactive Interface

The application now uses an **interactive menu-driven interface**. When you launch the app, you'll see:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          📝  PHASE I CONSOLE TODO APPLICATION  📝                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  1️⃣  Add New Task          - Create a new todo item
  2️⃣  List All Tasks        - View all your tasks
  3️⃣  Update Task           - Modify an existing task
  4️⃣  Mark Complete/Pending - Toggle task status
  5️⃣  Delete Task           - Remove a task
  6️⃣  Search & Filter       - Find specific tasks
  7️⃣  Exit                  - Close the application

👉 Select an option (1-7):
```

Simply enter a number to select an action. All tasks are numbered (1, 2, 3...) so you never need to remember or copy IDs!

📖 **For detailed usage instructions**, see [INTERACTIVE_UI_GUIDE.md](./INTERACTIVE_UI_GUIDE.md)

### Legacy Command-Line Interface

The original command-line interface is still available for advanced users. Import and use the `CommandParser` and `CommandHandler` classes directly.

**add**
```
add <title> [options]
    Add a new task
    Options:
        --description, -d <text>     Task description
        --priority, -p <level>       Priority: high, medium, low
        --tags, -t <tag1> <tag2>     Tags (space-separated)
        --due-date <date>            Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)
        --recurrence <interval>      Recurrence interval (daily, weekly, monthly, yearly)
```

**list**
```
list
    List all tasks
```

**update**
```
update <task_id> [options]
    Update an existing task
    Options:
        --title <text>               New title
        --description, -d <text>     New description
        --priority, -p <level>       New priority (use "none" to clear)
```

**delete**
```
delete <task_id>
    Delete a task
```

**complete**
```
complete <task_id>
    Toggle task completion status
```

**search**
```
search <keyword>
    Search tasks
```

**filter**
```
filter <filter_by> <value>
    Filter by status, priority, or tag
```

**sort**
```
sort <sort_by>
    Sort by due_date, priority, or title
```

**tag**
```
tag <task_id> <action> <tags>
    Add or remove tags from a task
    Action: add, remove
```

**overdue**
```
overdue
    List overdue tasks
```

**upcoming**
```
upcoming [hours]
    List upcoming tasks (default: 24 hours)
```

**help**
```
help
    Show help message
```

**exit, quit, q**
```
exit, quit, q
    Exit the application
```

## Examples

### Example Session

```bash
$ uv run --no-project python3 main.py

todo> add Buy groceries --priority high --tags shopping home
✓ Task created successfully: 'Buy groceries' (ID: f274e560)

todo> add Write report --description "Q1 summary" --due-date "2026-01-10 14:00"
✓ Task created successfully: 'Write report' (ID: 200996c3)

todo> list
================================================================================
STATUS   ID         TITLE                          PRIORITY   DUE DATE
================================================================================
[ ]      f274e560   Buy groceries                  high
                       {shopping  home}
[ ]      200996c3   Write report                   -          2026-01-10 14:00
                      → Q1 summary
================================================================================

Total: 2 task(s)

todo> complete f274e560
✓ Task 'Buy groceries' (ID: f274e560) marked as completed

todo> filter priority high
================================================================================
STATUS   ID         TITLE                          PRIORITY   DUE DATE
================================================================================
[✓]      f274e560   Buy groceries                  high
                       {shopping  home}
================================================================================

Total: 1 task(s)

todo> exit
Goodbye!
```

### Creating Recurring Tasks

```bash
# Daily recurring task
todo> add Daily standup --due-date "2026-01-08 09:00" --recurrence daily
✓ Task created successfully: 'Daily standup' (ID: abc12345)

# When you complete a recurring task, a new occurrence is automatically created
todo> complete abc12345
✓ Task 'Daily standup' (ID: abc12345) marked as completed
# A new task with the next due date is automatically created
```

## Project Structure

```
.
├── main.py                          # Application entry point (Interactive UI)
├── demo_interactive.py              # Demo script with feature showcase
├── INTERACTIVE_UI_GUIDE.md          # Detailed user guide for interactive interface
├── src/
│   ├── models/
│   │   ├── task.py                  # Task entity
│   │   ├── task_list.py             # In-memory task repository
│   │   └── recurrence_rule.py       # Recurrence configuration
│   ├── services/
│   │   ├── task_service.py          # Task CRUD operations
│   │   ├── search_service.py        # Search, filter, sort logic
│   │   └── recurrence_service.py    # Recurring task logic
│   ├── cli/
│   │   ├── interactive.py           # Interactive menu-driven UI (NEW!)
│   │   ├── parser.py                # Command line parser (legacy)
│   │   ├── renderer.py              # Output formatting
│   │   └── commands.py              # Command handlers (legacy)
│   └── lib/
│       ├── utils.py                 # Utility functions
│       └── validators.py            # Input validation
├── specs/
│   └── 001-phase-1-console-todo/
│       ├── spec.md                  # Feature specification
│       ├── plan.md                  # Implementation plan
│       └── tasks.md                 # Task breakdown
├── pyproject.toml                   # Project configuration
└── README.md                        # This file
```

## Architecture

### Design Principles
- **Spec-Driven Development**: All features defined in specifications before implementation
- **No External Dependencies**: Uses only Python 3.11+ standard library
- **In-Memory Storage**: All data stored in memory (dict + list structures)
- **Service Layer Pattern**: Clean separation between CLI, services, and models
- **Value Objects**: Immutable RecurrenceRule for recurrence configuration

### Data Storage
- **Primary Storage**: Python dictionary for O(1) lookups by task ID
- **Order Preservation**: Python list maintains insertion order
- **No Persistence**: Data is lost when application exits (by design for Phase I)

### Validation
- Title: Non-empty, max 200 characters
- Description: Optional, max 1000 characters
- Priority: Must be 'high', 'medium', or 'low' (or None)
- Tags: Each tag max 50 characters, no duplicates
- Due Date: ISO 8601 format (YYYY-MM-DD or YYYY-MM-DD HH:MM)

## Development

### Code Quality
- All code follows Python 3.11+ best practices
- Type hints used throughout
- Comprehensive docstrings with examples
- Input validation at service layer
- Error handling with user-friendly messages

### Testing
Testing is done manually through the REPL interface. All features have been validated against the acceptance criteria defined in `specs/001-phase-1-console-todo/spec.md`.

## Constitution

This project follows strict Spec-Driven Development principles defined in `.specify/memory/constitution.md` (Version 1.1.0, ratified 2026-01-03).

### Core Principles
1. **Specification First**: No work begins without an approved spec and linked plan
2. **Agentic Implementation Only**: Claude Code + Spec-Kit Plus generate every change
3. **Phase Isolation & Sequencing**: Each phase works inside its own directory with explicit cross-phase approvals
4. **Traceable Tasks & Records**: "No Task = No Code" plus Prompt History Records for every user interaction
5. **Testable Acceptance Criteria**: Every spec/task defines measurable verification steps before completion
6. **Immutable Specifications & Controlled Change**: Once ratified, specs change only via new revisions that rerun the full "Specify → Plan → Tasks → Implement" loop

## Future Phases

Phase I focuses on console-based in-memory todo management. Future phases will add:

- **Phase II**: Persistent storage (file-based or database)
- **Phase III**: Advanced features (categories, subtasks, attachments)
- **Phase IV**: Web interface
- **Phase V**: Cloud deployment and multi-user support

## License

This project is part of the "Evolution of Todo" learning initiative.

---

**Built with**: Python 3.11+ | **Storage**: In-Memory | **Architecture**: Service Layer Pattern | **Development**: Spec-Driven Development
