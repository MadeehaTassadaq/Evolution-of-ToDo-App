# Interactive Console Todo Application - User Guide

## 🎯 Overview

The Interactive Console Todo Application provides a **menu-driven interface** where everything you need is visible on screen. No commands to memorize, no IDs to remember!

## ✨ Key Features

### 1. **Visible Menu System**
- All available actions displayed on every screen
- Numbered options (1-7) for easy selection
- Clear descriptions of what each option does

### 2. **Numbered Task Selection**
- Tasks are numbered: 1, 2, 3, 4...
- Select tasks by their number instead of remembering long IDs
- No copy-pasting or typing complex identifiers

### 3. **Guided Prompts**
- Step-by-step instructions for every action
- Examples shown for date formats and inputs
- Optional fields clearly marked (press Enter to skip)

### 4. **Self-Explanatory Interface**
- No help command needed
- Everything explained on screen
- Visual indicators (✓, ✗, ⚠️, 📌, etc.)

### 5. **Safety Features**
- Confirmation prompts for destructive actions
- Clear warnings before deletion
- Easy cancellation (enter 0 or type 'no')

## 🚀 Getting Started

### Running the Application

```bash
# Method 1: Run main application
python3 main.py

# Method 2: Run demo script
python3 demo_interactive.py

# Method 3: Use uv (if configured)
uv run main.py
```

### First Launch

When you launch the app, you'll see:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║          📝  PHASE I CONSOLE TODO APPLICATION  📝                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

✨ Welcome! Manage your tasks efficiently with this interactive console app.

⏸️  Press Enter to continue...
```

## 📋 Main Menu

After the welcome screen, you'll see the main menu:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  MAIN MENU                                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

  1️⃣  Add New Task          - Create a new todo item
  2️⃣  List All Tasks        - View all your tasks
  3️⃣  Update Task           - Modify an existing task
  4️⃣  Mark Complete/Pending - Toggle task status
  5️⃣  Delete Task           - Remove a task
  6️⃣  Search & Filter       - Find specific tasks
  7️⃣  Exit                  - Close the application

────────────────────────────────────────────────────────────────────────────────

👉 Select an option (1-7):
```

Simply type a number (1-7) and press Enter!

## 📝 How to Use Each Feature

### 1. Adding a New Task

**Steps:**
1. Select option `1` from main menu
2. Enter task title (required)
3. Optionally add description (press Enter to skip)
4. Optionally select priority: 1=High, 2=Medium, 3=Low (or skip)
5. Optionally add tags (space-separated, e.g., "work urgent")
6. Optionally add due date (format: YYYY-MM-DD or YYYY-MM-DD HH:MM)

**Example Flow:**
```
📌 Task title (required): Buy groceries

💬 Description (optional, press Enter to skip):
   Get milk, eggs, and bread

⭐ Priority (optional):
   1. High
   2. Medium
   3. Low
   Press Enter to skip
   Select (1-3): 2

🏷️  Tags (optional, space-separated, e.g., work urgent):
   shopping essentials

📅 Due date (optional, format: YYYY-MM-DD or YYYY-MM-DD HH:MM):
   Examples: 2026-01-15  or  2026-01-15 14:30
   2026-01-05

────────────────────────────────────────────────────────────────────────────────
✅ Task created successfully!
   Title: Buy groceries
   Priority: MEDIUM
   Tags: shopping, essentials
────────────────────────────────────────────────────────────────────────────────
```

### 2. Listing All Tasks

**Steps:**
1. Select option `2` from main menu
2. View all tasks with numbers

**Example Output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  📋 ALL TASKS                                                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────────────────────────────────────────────────────────
#    Status   Title                              Priority   Due Date
────────────────────────────────────────────────────────────────────────────────
1    ⏳ Todo  Buy groceries                      MEDIUM     2026-01-05 00:00
     🏷️  shopping, essentials
     💬 Get milk, eggs, and bread

2    ✅ Done  Complete project report            HIGH       2026-01-04 17:00

3    ⏳ Todo  Team meeting preparation           -          2026-01-06 10:00 ⚠️
     🏷️  work, urgent

────────────────────────────────────────────────────────────────────────────────
Total: 3 task(s)

📝 Legend: ✅ = Completed, ⏳ = Pending, ⚠️ = Overdue
```

**Notice:**
- Tasks are numbered (1, 2, 3...)
- Status shown with clear symbols
- Tags and descriptions shown inline
- Overdue tasks marked with ⚠️

### 3. Updating a Task

**Steps:**
1. Select option `3` from main menu
2. View numbered list of all tasks
3. Enter the task number (e.g., `2` for the second task)
4. Update any fields (press Enter to keep current value)

**Example Flow:**
```
👉 Enter task number to update (or 0 to cancel): 1

────────────────────────────────────────────────────────────────────────────────
Current Task: Buy groceries
Description: Get milk, eggs, and bread
Priority: MEDIUM
────────────────────────────────────────────────────────────────────────────────

💡 Leave blank to keep current value

📌 New title (current: Buy groceries):
   Buy groceries and cleaning supplies

💬 New description (current: Get milk, eggs, and bread):
   Get milk, eggs, bread, and dish soap

⭐ New priority (current: medium):
   1. High
   2. Medium
   3. Low
   4. Remove priority
   Select (1-4): 1

────────────────────────────────────────────────────────────────────────────────
✅ Task updated successfully!
   Title: Buy groceries and cleaning supplies
────────────────────────────────────────────────────────────────────────────────
```

### 4. Marking Tasks Complete/Pending

**Steps:**
1. Select option `4` from main menu
2. View numbered list of all tasks
3. Enter the task number to toggle its status

**Example:**
```
👉 Enter task number to toggle status (or 0 to cancel): 1

✅ Task 'Buy groceries and cleaning supplies' marked as completed ✅
```

The task status toggles between:
- ⏳ Pending (Todo)
- ✅ Completed (Done)

### 5. Deleting a Task

**Steps:**
1. Select option `5` from main menu
2. View numbered list of all tasks
3. Enter the task number to delete
4. Confirm deletion by typing `yes`

**Example Flow:**
```
👉 Enter task number to delete (or 0 to cancel): 3

────────────────────────────────────────────────────────────────────────────────
⚠️  You are about to delete:
   Team meeting preparation
────────────────────────────────────────────────────────────────────────────────

❓ Are you sure? Type 'yes' to confirm: yes

✅ Task 'Team meeting preparation' deleted successfully!
```

**Safety Features:**
- Clear confirmation required
- Shows what will be deleted
- Easy cancellation (type anything other than 'yes')

### 6. Search & Filter

Select option `6` to access the search and filter submenu:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🔍 SEARCH & FILTER                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

  1️⃣  Search by keyword
  2️⃣  Filter by status (completed/pending)
  3️⃣  Filter by priority
  4️⃣  Filter by tag
  5️⃣  Show overdue tasks
  6️⃣  Show upcoming tasks
  7️⃣  Sort tasks
  0️⃣  Back to main menu
```

#### 6.1 Search by Keyword
- Searches in task titles and descriptions
- Case-insensitive matching
- Shows all matching tasks with numbers

#### 6.2 Filter by Status
- Option 1: Show only completed tasks
- Option 2: Show only pending tasks

#### 6.3 Filter by Priority
- Option 1: High priority tasks
- Option 2: Medium priority tasks
- Option 3: Low priority tasks

#### 6.4 Filter by Tag
- Enter a tag name
- Shows all tasks with that tag

#### 6.5 Show Overdue Tasks
- Automatically shows tasks past their due date
- Only includes incomplete tasks

#### 6.6 Show Upcoming Tasks
- Enter number of hours to look ahead (default: 24)
- Shows tasks due within that timeframe

#### 6.7 Sort Tasks
- Option 1: Sort by due date (earliest first)
- Option 2: Sort by priority (high → low)
- Option 3: Sort by title (A-Z)

### 7. Exit Application

**Steps:**
1. Select option `7` from main menu
2. See goodbye message and exit

```
════════════════════════════════════════════════════════════════════════════════
       Thank you for using Phase I Console Todo Application!
    Your tasks are stored in memory and will be lost on exit.
════════════════════════════════════════════════════════════════════════════════

👋 Goodbye!
```

## 💡 Tips & Best Practices

### Input Tips
- **Canceling Actions:** Enter `0` when prompted for task numbers to cancel
- **Skipping Optional Fields:** Just press Enter to skip
- **Date Format:** Use `YYYY-MM-DD` (e.g., 2026-01-15) or `YYYY-MM-DD HH:MM` (e.g., 2026-01-15 14:30)
- **Tags:** Separate multiple tags with spaces (e.g., "work urgent important")

### Navigation Tips
- **Always Read Prompts:** Each screen explains what to do
- **Use Numbers:** All selections use simple numbers (1, 2, 3...)
- **Visual Indicators:**
  - ✅ = Success
  - ❌ = Error
  - ⚠️ = Warning/Overdue
  - 📌 = Task title
  - 💬 = Description
  - 🏷️ = Tags
  - ⭐ = Priority

### Organization Tips
- Use **tags** to categorize tasks (work, personal, shopping, urgent)
- Set **priorities** for important tasks
- Add **descriptions** for complex tasks
- Set **due dates** to track deadlines

## 🎨 Visual Elements

The interface uses various Unicode symbols for clarity:

| Symbol | Meaning |
|--------|---------|
| ✅ | Completed task or successful action |
| ⏳ | Pending/Todo task |
| ❌ | Error or invalid input |
| ⚠️ | Warning or overdue task |
| 📝 | Note or legend |
| 📌 | Task title |
| 💬 | Description |
| 🏷️ | Tags |
| ⭐ | Priority |
| 📅 | Due date |
| 🔍 | Search |
| 👉 | Action prompt |
| ⏸️ | Pause (press Enter) |
| 👋 | Goodbye |

## ❓ Frequently Asked Questions

### Q: Do I need to type commands?
**A:** No! Just select numbers from the visible menu.

### Q: How do I remember task IDs?
**A:** You don't! Tasks are numbered 1, 2, 3... in the list.

### Q: What if I make a mistake?
**A:** You can cancel most operations by entering `0` or choosing not to confirm.

### Q: Can I see what each option does before selecting?
**A:** Yes! Each menu shows descriptions next to every option.

### Q: Are my tasks saved?
**A:** Tasks are stored in memory during the session. They will be lost when you exit (this is Phase 1 - persistence comes in future phases).

### Q: How do I delete a task?
**A:** Select option 5, choose the task number, and confirm by typing 'yes'.

### Q: Can I update multiple fields at once?
**A:** Yes! When updating, you can change title, description, and priority in one go.

### Q: How do I mark a task as complete?
**A:** Select option 4, then enter the task number. Status toggles automatically.

## 🆘 Troubleshooting

### "Invalid option" message
- Make sure you're entering a number within the valid range
- Example: For main menu, enter 1-7

### Task number not working
- Verify the task number from the list display
- Task numbers start at 1, not 0

### Date format error
- Use format: YYYY-MM-DD (e.g., 2026-01-15)
- Or with time: YYYY-MM-DD HH:MM (e.g., 2026-01-15 14:30)

### Accidentally closed the app
- Tasks are in memory only (Phase 1)
- You'll need to re-enter them after restart
- Future phases will add persistence

## 🚀 Quick Start Example

Here's a complete workflow to get you started:

```
1. Launch app: python3 main.py
2. Press Enter at welcome screen
3. Select 1 (Add Task)
4. Enter: "Buy groceries for dinner"
5. Skip description (press Enter)
6. Select priority: 2 (Medium)
7. Enter tags: shopping food
8. Enter due date: 2026-01-10
9. Press Enter to continue
10. Select 2 (List Tasks) - see your task numbered as #1
11. Select 4 (Mark Complete)
12. Enter: 1 (to mark task #1 complete)
13. Select 2 (List Tasks) - see task now shows ✅
14. Select 7 (Exit)
```

## 📊 Comparison: Old vs New Interface

### Old Command-Line Interface
```
todo> add Buy milk --priority high
✓ Task created successfully: 'Buy milk' (ID: abc123de)

todo> delete abc123de
✓ Task deleted
```
❌ Problems:
- Must remember commands
- Must copy/paste IDs
- No guidance visible

### New Interactive Interface
```
╔══════════════════════════════════════════════════════════════╗
║  MAIN MENU                                                   ║
╚══════════════════════════════════════════════════════════════╝

  1️⃣  Add New Task
  2️⃣  List All Tasks
  5️⃣  Delete Task
  ...

👉 Select: 5

#  Status   Title
1  ⏳ Todo  Buy milk
2  ⏳ Todo  Write report

👉 Enter task number: 1
❓ Confirm deletion? yes
✅ Deleted!
```
✅ Benefits:
- All options visible
- Simple number selection
- Clear confirmations
- Self-explanatory

---

**Enjoy your improved task management experience! 🎉**
