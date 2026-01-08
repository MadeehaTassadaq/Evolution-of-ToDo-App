"""
Task model for the Phase I Console Todo Application.

Represents a single todo item with all attributes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from src.models.recurrence_rule import RecurrenceRule


@dataclass
class Task:
    """
    Mutable data class representing a todo task.

    Attributes:
        id: Unique task identifier (UUID)
        title: Task title (required, max 200 chars)
        description: Optional task description (max 1000 chars)
        completed: Completion status (default: False)
        priority: Optional priority (high, medium, low)
        tags: List of tag strings (default: empty list)
        due_date: Optional due date/time
        recurrence: Optional recurrence rule for recurring tasks

    Examples:
        >>> from src.lib.utils import generate_task_id
        >>> task = Task(
        ...     id=generate_task_id(),
        ...     title="Buy groceries",
        ...     description="Milk, eggs, bread"
        ... )
        >>> task.completed
        False
        >>> task.title
        'Buy groceries'
    """

    id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Optional[RecurrenceRule] = None

    def __post_init__(self):
        """Validate task attributes after initialization."""
        if not self.id:
            raise ValueError("Task ID cannot be empty")

        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        if self.title and len(self.title) > 200:
            raise ValueError(f"Title too long ({len(self.title)} chars, max 200)")

        if self.description and len(self.description) > 1000:
            raise ValueError(
                f"Description too long ({len(self.description)} chars, max 1000)"
            )

        if self.priority and self.priority not in ['high', 'medium', 'low']:
            raise ValueError(
                f"Invalid priority: {self.priority}. "
                "Must be 'high', 'medium', or 'low'"
            )

    def toggle_complete(self) -> None:
        """Toggle the completion status of this task."""
        self.completed = not self.completed

    def is_overdue(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if this task is overdue.

        Args:
            current_time: Time to compare against (default: now)

        Returns:
            bool: True if task has due_date and it's past current_time

        Examples:
            >>> from datetime import datetime, timedelta
            >>> task = Task(id="1", title="Test", due_date=datetime.now() - timedelta(days=1))
            >>> task.is_overdue()
            True
            >>> task_future = Task(id="2", title="Test", due_date=datetime.now() + timedelta(days=1))
            >>> task_future.is_overdue()
            False
        """
        if self.due_date is None:
            return False

        if current_time is None:
            current_time = datetime.now()

        return self.due_date < current_time

    def add_tag(self, tag: str) -> None:
        """
        Add a tag to this task.

        Args:
            tag: Tag string to add

        Examples:
            >>> task = Task(id="1", title="Test")
            >>> task.add_tag("work")
            >>> task.tags
            ['work']
            >>> task.add_tag("urgent")
            >>> task.tags
            ['work', 'urgent']
        """
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from this task.

        Args:
            tag: Tag string to remove

        Examples:
            >>> task = Task(id="1", title="Test", tags=["work", "urgent"])
            >>> task.remove_tag("work")
            >>> task.tags
            ['urgent']
        """
        if tag in self.tags:
            self.tags.remove(tag)

    def __str__(self) -> str:
        """Human-readable representation."""
        status = "✓" if self.completed else " "
        priority_str = f" [{self.priority}]" if self.priority else ""
        due_str = f" (due: {self.due_date.strftime('%Y-%m-%d')})" if self.due_date else ""
        tags_str = f" {{{', '.join(self.tags)}}}" if self.tags else ""

        return f"[{status}] {self.title}{priority_str}{due_str}{tags_str}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Task(id='{self.id[:8]}...', title='{self.title}', "
            f"completed={self.completed})"
        )
