"""
CLI output renderer for the Phase I Console Todo Application.

Formats task lists and messages for console display.
"""

from typing import List
from src.models.task import Task


class Renderer:
    """
    Render tasks and messages for console output.

    Handles formatting for task lists, success messages, and errors.
    """

    def render_task_list(self, tasks: List[Task]) -> str:
        """
        Render a list of tasks as a formatted table.

        Args:
            tasks: List of Task objects to display

        Returns:
            str: Formatted table with task details

        Examples:
            >>> from src.models.task import Task
            >>> from src.lib.utils import generate_task_id
            >>> task = Task(id=generate_task_id(), title="Buy groceries")
            >>> renderer = Renderer()
            >>> output = renderer.render_task_list([task])
            >>> "Buy groceries" in output
            True
        """
        if not tasks:
            return "No tasks found."

        lines = []
        lines.append("\n" + "=" * 80)
        lines.append(f"{'STATUS':<8} {'ID':<10} {'TITLE':<30} {'PRIORITY':<10} {'DUE DATE':<15}")
        lines.append("=" * 80)

        for task in tasks:
            # Status indicator
            status = "✓" if task.completed else " "

            # Short ID (first 8 characters)
            short_id = task.id[:8]

            # Title (truncate if needed)
            title = task.title
            if len(title) > 28:
                title = title[:25] + "..."

            # Priority
            priority = task.priority if task.priority else "-"

            # Due date
            due_date = ""
            if task.due_date:
                due_date = task.due_date.strftime("%Y-%m-%d %H:%M")
                if task.is_overdue() and not task.completed:
                    due_date += " ⚠"

            # Tags (display below if present)
            tags_str = ""
            if task.tags:
                tags_str = f" {{{'  '.join(task.tags)}}}"

            line = f"[{status}]      {short_id}   {title:<30} {priority:<10} {due_date:<15}"
            lines.append(line)

            if tags_str:
                lines.append(f"         {' ' * 10}   {tags_str}")

            if task.description:
                desc = task.description
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                lines.append(f"         {' ' * 10}   → {desc}")

            if task.recurrence:
                lines.append(f"         {' ' * 10}   (recurrence: {task.recurrence})")

        lines.append("=" * 80)
        lines.append(f"\nTotal: {len(tasks)} task(s)")
        lines.append("")

        return "\n".join(lines)

    def render_task_detail(self, task: Task) -> str:
        """
        Render a single task with full details.

        Args:
            task: Task object to display

        Returns:
            str: Formatted task details

        Examples:
            >>> from src.models.task import Task
            >>> from src.lib.utils import generate_task_id
            >>> task = Task(id=generate_task_id(), title="Buy groceries",
            ...             description="Milk, eggs, bread", priority="high")
            >>> renderer = Renderer()
            >>> output = renderer.render_task_detail(task)
            >>> "Buy groceries" in output
            True
            >>> "high" in output
            True
        """
        lines = []
        lines.append("\n" + "=" * 80)

        # Status and title
        status = "✓ COMPLETED" if task.completed else "○ PENDING"
        lines.append(f"[{status}] {task.title}")
        lines.append("=" * 80)

        # ID
        lines.append(f"ID:          {task.id}")

        # Description
        if task.description:
            lines.append(f"Description: {task.description}")

        # Priority
        if task.priority:
            priority_display = task.priority.upper()
            lines.append(f"Priority:    {priority_display}")

        # Tags
        if task.tags:
            tags_display = ", ".join(task.tags)
            lines.append(f"Tags:        {tags_display}")

        # Due date
        if task.due_date:
            due_str = task.due_date.strftime("%Y-%m-%d %H:%M")
            if task.is_overdue() and not task.completed:
                due_str += " ⚠ OVERDUE"
            lines.append(f"Due:         {due_str}")

        # Recurrence
        if task.recurrence:
            lines.append(f"Recurrence:  {task.recurrence}")

        lines.append("=" * 80)
        lines.append("")

        return "\n".join(lines)

    def render_success(self, message: str) -> str:
        """
        Render a success message.

        Args:
            message: Success message text

        Returns:
            str: Formatted success message

        Examples:
            >>> renderer = Renderer()
            >>> renderer.render_success("Task created successfully")
            '✓ Task created successfully'
        """
        return f"✓ {message}"

    def render_error(self, message: str) -> str:
        """
        Render an error message.

        Args:
            message: Error message text

        Returns:
            str: Formatted error message

        Examples:
            >>> renderer = Renderer()
            >>> renderer.render_error("Task not found")
            '✗ Error: Task not found'
        """
        return f"✗ Error: {message}"

    def render_warning(self, message: str) -> str:
        """
        Render a warning message.

        Args:
            message: Warning message text

        Returns:
            str: Formatted warning message

        Examples:
            >>> renderer = Renderer()
            >>> renderer.render_warning("Task is overdue")
            '⚠ Warning: Task is overdue'
        """
        return f"⚠ Warning: {message}"
