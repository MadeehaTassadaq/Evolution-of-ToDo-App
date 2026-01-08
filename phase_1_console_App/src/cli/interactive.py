"""
Interactive menu-driven interface for the Console Todo Application.

Provides a user-friendly, self-explanatory interface with visible options
and numbered task selection (no memorizing IDs required).
"""

from typing import List, Optional, Tuple
from src.models.task import Task
from src.services.task_service import TaskService
from src.services.search_service import SearchService
from src.cli.renderer import Renderer


class InteractiveUI:
    """
    Interactive menu-driven user interface.

    Features:
    - Visible menu of all actions
    - Numbered task selection (1, 2, 3...)
    - Guided prompts for all inputs
    - No help command needed
    """

    def __init__(self, task_service: TaskService, search_service: SearchService, renderer: Renderer):
        """Initialize interactive UI."""
        self.task_service = task_service
        self.search_service = search_service
        self.renderer = renderer
        self.current_tasks = []  # Track displayed tasks for numbered selection

    def run(self):
        """Main interactive loop."""
        self.show_welcome()

        while True:
            try:
                self.show_main_menu()
                choice = input("\n👉 Select an option (1-7): ").strip()

                if choice == '1':
                    self.add_task_interactive()
                elif choice == '2':
                    self.list_tasks_interactive()
                elif choice == '3':
                    self.update_task_interactive()
                elif choice == '4':
                    self.mark_complete_interactive()
                elif choice == '5':
                    self.delete_task_interactive()
                elif choice == '6':
                    self.search_filter_menu()
                elif choice == '7':
                    self.exit_app()
                    break
                else:
                    print("\n❌ Invalid option. Please select 1-7.")
                    self.pause()

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                self.pause()

    def show_welcome(self):
        """Display welcome screen."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "          📝  PHASE I CONSOLE TODO APPLICATION  📝".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print("\n✨ Welcome! Manage your tasks efficiently with this interactive console app.\n")
        self.pause()

    def show_main_menu(self):
        """Display main menu with all available options."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  MAIN MENU".ljust(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("  1️⃣  Add New Task          - Create a new todo item")
        print("  2️⃣  List All Tasks        - View all your tasks")
        print("  3️⃣  Update Task           - Modify an existing task")
        print("  4️⃣  Mark Complete/Pending - Toggle task status")
        print("  5️⃣  Delete Task           - Remove a task")
        print("  6️⃣  Search & Filter       - Find specific tasks")
        print("  7️⃣  Exit                  - Close the application")
        print()
        print("─" * 80)

    def add_task_interactive(self):
        """Interactive task creation with guided prompts."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  ➕ ADD NEW TASK".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        # Title (required)
        title = input("📌 Task title (required): ").strip()
        if not title:
            print("\n❌ Task title cannot be empty!")
            self.pause()
            return

        # Description (optional)
        print("\n💬 Description (optional, press Enter to skip):")
        description = input("   ").strip() or None

        # Priority (optional)
        print("\n⭐ Priority (optional):")
        print("   1. High")
        print("   2. Medium")
        print("   3. Low")
        print("   Press Enter to skip")
        priority_choice = input("   Select (1-3): ").strip()
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}
        priority = priority_map.get(priority_choice)

        # Tags (optional)
        print("\n🏷️  Tags (optional, space-separated, e.g., work urgent):")
        tags_input = input("   ").strip()
        tags = tags_input.split() if tags_input else None

        # Due date (optional)
        print("\n📅 Due date (optional, format: YYYY-MM-DD or YYYY-MM-DD HH:MM):")
        print("   Examples: 2026-01-15  or  2026-01-15 14:30")
        due_date = input("   ").strip() or None

        try:
            task = self.task_service.create_task(
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date
            )

            print("\n" + "─" * 80)
            print(f"✅ Task created successfully!")
            print(f"   Title: {task.title}")
            if priority:
                print(f"   Priority: {priority.upper()}")
            if tags:
                print(f"   Tags: {', '.join(tags)}")
            print("─" * 80)

        except Exception as e:
            print(f"\n❌ Error creating task: {str(e)}")

        self.pause()

    def list_tasks_interactive(self):
        """Display all tasks with numbers for easy selection."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  📋 ALL TASKS".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        tasks = self.task_service.get_all_tasks()
        self.current_tasks = tasks

        if not tasks:
            print("📭 No tasks yet! Use option 1 to add your first task.\n")
        else:
            self.display_numbered_tasks(tasks)

        self.pause()

    def display_numbered_tasks(self, tasks: List[Task], show_legend: bool = True):
        """Display tasks with numbers for selection."""
        if not tasks:
            print("📭 No tasks found.\n")
            return

        print("─" * 80)
        print(f"{'#':<4} {'Status':<8} {'Title':<35} {'Priority':<10} {'Due Date':<15}")
        print("─" * 80)

        for idx, task in enumerate(tasks, 1):
            status = "✅ Done" if task.completed else "⏳ Todo"
            title = task.title[:33] + "..." if len(task.title) > 33 else task.title
            priority = (task.priority or "-").upper()

            due_date = ""
            if task.due_date:
                due_date = task.due_date.strftime("%Y-%m-%d %H:%M")
                if task.is_overdue() and not task.completed:
                    due_date += " ⚠️"

            print(f"{idx:<4} {status:<8} {title:<35} {priority:<10} {due_date:<15}")

            # Show tags if present
            if task.tags:
                tags_str = "🏷️  " + ", ".join(task.tags)
                print(f"     {tags_str}")

            # Show description if present
            if task.description:
                desc = task.description[:60] + "..." if len(task.description) > 60 else task.description
                print(f"     💬 {desc}")

        print("─" * 80)
        print(f"Total: {len(tasks)} task(s)")

        if show_legend:
            print("\n📝 Legend: ✅ = Completed, ⏳ = Pending, ⚠️ = Overdue")
        print()

    def update_task_interactive(self):
        """Interactive task update with numbered selection."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  ✏️  UPDATE TASK".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        tasks = self.task_service.get_all_tasks()
        self.current_tasks = tasks

        if not tasks:
            print("📭 No tasks to update!\n")
            self.pause()
            return

        self.display_numbered_tasks(tasks, show_legend=False)

        # Select task by number
        task_num = input("👉 Enter task number to update (or 0 to cancel): ").strip()

        if task_num == '0':
            return

        try:
            task_idx = int(task_num) - 1
            if task_idx < 0 or task_idx >= len(tasks):
                print("\n❌ Invalid task number!")
                self.pause()
                return

            task = tasks[task_idx]

        except ValueError:
            print("\n❌ Please enter a valid number!")
            self.pause()
            return

        # Show current task details
        print("\n" + "─" * 80)
        print(f"Current Task: {task.title}")
        if task.description:
            print(f"Description: {task.description}")
        if task.priority:
            print(f"Priority: {task.priority.upper()}")
        print("─" * 80)

        # Update fields
        print("\n💡 Leave blank to keep current value\n")

        updates = {}

        # New title
        new_title = input(f"📌 New title (current: {task.title}): ").strip()
        if new_title:
            updates['title'] = new_title

        # New description
        print(f"\n💬 New description (current: {task.description or 'none'}):")
        new_desc = input("   ").strip()
        if new_desc:
            updates['description'] = new_desc

        # New priority
        print(f"\n⭐ New priority (current: {task.priority or 'none'}):")
        print("   1. High")
        print("   2. Medium")
        print("   3. Low")
        print("   4. Remove priority")
        priority_choice = input("   Select (1-4): ").strip()
        priority_map = {'1': 'high', '2': 'medium', '3': 'low', '4': None}
        if priority_choice in priority_map:
            updates['priority'] = priority_map[priority_choice]

        if not updates:
            print("\n⚠️  No changes made.")
            self.pause()
            return

        try:
            updated_task = self.task_service.update_task(task.id, **updates)
            print("\n" + "─" * 80)
            print(f"✅ Task updated successfully!")
            print(f"   Title: {updated_task.title}")
            print("─" * 80)
        except Exception as e:
            print(f"\n❌ Error updating task: {str(e)}")

        self.pause()

    def mark_complete_interactive(self):
        """Interactive task completion toggle with numbered selection."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  ✓ MARK COMPLETE/PENDING".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        tasks = self.task_service.get_all_tasks()
        self.current_tasks = tasks

        if not tasks:
            print("📭 No tasks available!\n")
            self.pause()
            return

        self.display_numbered_tasks(tasks, show_legend=False)

        task_num = input("👉 Enter task number to toggle status (or 0 to cancel): ").strip()

        if task_num == '0':
            return

        try:
            task_idx = int(task_num) - 1
            if task_idx < 0 or task_idx >= len(tasks):
                print("\n❌ Invalid task number!")
                self.pause()
                return

            task = tasks[task_idx]
            updated_task = self.task_service.toggle_complete(task.id)

            status = "completed ✅" if updated_task.completed else "pending ⏳"
            print(f"\n✅ Task '{updated_task.title}' marked as {status}")

        except (ValueError, KeyError) as e:
            print(f"\n❌ Error: {str(e)}")

        self.pause()

    def delete_task_interactive(self):
        """Interactive task deletion with numbered selection and confirmation."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  🗑️  DELETE TASK".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        tasks = self.task_service.get_all_tasks()
        self.current_tasks = tasks

        if not tasks:
            print("📭 No tasks to delete!\n")
            self.pause()
            return

        self.display_numbered_tasks(tasks, show_legend=False)

        task_num = input("👉 Enter task number to delete (or 0 to cancel): ").strip()

        if task_num == '0':
            return

        try:
            task_idx = int(task_num) - 1
            if task_idx < 0 or task_idx >= len(tasks):
                print("\n❌ Invalid task number!")
                self.pause()
                return

            task = tasks[task_idx]

            # Confirmation prompt
            print("\n" + "─" * 80)
            print(f"⚠️  You are about to delete:")
            print(f"   {task.title}")
            print("─" * 80)
            confirm = input("\n❓ Are you sure? Type 'yes' to confirm: ").strip().lower()

            if confirm != 'yes':
                print("\n✅ Deletion cancelled.")
                self.pause()
                return

            self.task_service.delete_task(task.id)
            print(f"\n✅ Task '{task.title}' deleted successfully!")

        except (ValueError, KeyError) as e:
            print(f"\n❌ Error: {str(e)}")

        self.pause()

    def search_filter_menu(self):
        """Search and filter submenu."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  🔍 SEARCH & FILTER".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("  1️⃣  Search by keyword")
        print("  2️⃣  Filter by status (completed/pending)")
        print("  3️⃣  Filter by priority")
        print("  4️⃣  Filter by tag")
        print("  5️⃣  Show overdue tasks")
        print("  6️⃣  Show upcoming tasks")
        print("  7️⃣  Sort tasks")
        print("  0️⃣  Back to main menu")
        print()
        print("─" * 80)

        choice = input("\n👉 Select an option (0-7): ").strip()

        if choice == '1':
            self.search_by_keyword()
        elif choice == '2':
            self.filter_by_status()
        elif choice == '3':
            self.filter_by_priority()
        elif choice == '4':
            self.filter_by_tag()
        elif choice == '5':
            self.show_overdue_tasks()
        elif choice == '6':
            self.show_upcoming_tasks()
        elif choice == '7':
            self.sort_tasks()
        elif choice == '0':
            return
        else:
            print("\n❌ Invalid option!")
            self.pause()

    def search_by_keyword(self):
        """Search tasks by keyword."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  🔍 SEARCH BY KEYWORD".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        keyword = input("🔎 Enter search keyword: ").strip()

        if not keyword:
            print("\n❌ Please enter a keyword!")
            self.pause()
            return

        tasks = self.task_service.get_all_tasks()
        results = self.search_service.search_tasks(tasks, keyword)

        print(f"\n📊 Found {len(results)} task(s) matching '{keyword}':\n")
        self.display_numbered_tasks(results)
        self.pause()

    def filter_by_status(self):
        """Filter tasks by completion status."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  📊 FILTER BY STATUS".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("  1️⃣  Show completed tasks")
        print("  2️⃣  Show pending tasks")
        print()

        choice = input("👉 Select (1-2): ").strip()

        tasks = self.task_service.get_all_tasks()

        if choice == '1':
            results = self.search_service.filter_by_status(tasks, completed=True)
            status_name = "completed"
        elif choice == '2':
            results = self.search_service.filter_by_status(tasks, completed=False)
            status_name = "pending"
        else:
            print("\n❌ Invalid option!")
            self.pause()
            return

        print(f"\n📊 {status_name.upper()} tasks:\n")
        self.display_numbered_tasks(results)
        self.pause()

    def filter_by_priority(self):
        """Filter tasks by priority."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  ⭐ FILTER BY PRIORITY".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("  1️⃣  High priority")
        print("  2️⃣  Medium priority")
        print("  3️⃣  Low priority")
        print()

        choice = input("👉 Select (1-3): ").strip()
        priority_map = {'1': 'high', '2': 'medium', '3': 'low'}

        if choice not in priority_map:
            print("\n❌ Invalid option!")
            self.pause()
            return

        priority = priority_map[choice]
        tasks = self.task_service.get_all_tasks()
        results = self.search_service.filter_by_priority(tasks, priority)

        print(f"\n📊 {priority.upper()} priority tasks:\n")
        self.display_numbered_tasks(results)
        self.pause()

    def filter_by_tag(self):
        """Filter tasks by tag."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  🏷️  FILTER BY TAG".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        tag = input("🏷️  Enter tag name: ").strip()

        if not tag:
            print("\n❌ Please enter a tag!")
            self.pause()
            return

        tasks = self.task_service.get_all_tasks()
        results = self.search_service.filter_by_tag(tasks, tag)

        print(f"\n📊 Tasks with tag '{tag}':\n")
        self.display_numbered_tasks(results)
        self.pause()

    def show_overdue_tasks(self):
        """Show overdue tasks."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  ⚠️  OVERDUE TASKS".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        tasks = self.task_service.get_all_tasks()
        results = self.search_service.get_overdue_tasks(tasks)

        if results:
            print("📊 Overdue tasks:\n")
            self.display_numbered_tasks(results)
        else:
            print("✅ No overdue tasks!\n")

        self.pause()

    def show_upcoming_tasks(self):
        """Show upcoming tasks."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  📅 UPCOMING TASKS".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()

        hours = input("⏰ Show tasks due within how many hours? (default: 24): ").strip()

        try:
            hours = int(hours) if hours else 24
        except ValueError:
            hours = 24

        tasks = self.task_service.get_all_tasks()
        results = self.search_service.get_upcoming_tasks(tasks, hours)

        print(f"\n📊 Tasks due within {hours} hours:\n")
        self.display_numbered_tasks(results)
        self.pause()

    def sort_tasks(self):
        """Sort tasks."""
        self.clear_screen()
        print("╔" + "═" * 78 + "╗")
        print("║  🔀 SORT TASKS".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
        print("  1️⃣  Sort by due date")
        print("  2️⃣  Sort by priority")
        print("  3️⃣  Sort by title (A-Z)")
        print()

        choice = input("👉 Select (1-3): ").strip()

        tasks = self.task_service.get_all_tasks()

        if choice == '1':
            results = self.search_service.sort_by_due_date(tasks)
            sort_name = "due date"
        elif choice == '2':
            results = self.search_service.sort_by_priority(tasks)
            sort_name = "priority"
        elif choice == '3':
            results = self.search_service.sort_by_title(tasks)
            sort_name = "title"
        else:
            print("\n❌ Invalid option!")
            self.pause()
            return

        print(f"\n📊 Tasks sorted by {sort_name}:\n")
        self.display_numbered_tasks(results)
        self.pause()

    def exit_app(self):
        """Exit application with goodbye message."""
        self.clear_screen()
        print("\n" + "═" * 80)
        print("Thank you for using Phase I Console Todo Application!".center(80))
        print("Your tasks are stored in memory and will be lost on exit.".center(80))
        print("═" * 80)
        print("\n👋 Goodbye!\n")

    def clear_screen(self):
        """Clear console screen."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')

    def pause(self):
        """Pause for user to read output."""
        input("\n⏸️  Press Enter to continue...")
