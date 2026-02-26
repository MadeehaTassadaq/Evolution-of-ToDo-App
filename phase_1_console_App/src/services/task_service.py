"""
TaskService - Business logic for task CRUD operations.

Implements validation and state management for tasks.
"""

from typing import Optional, Dict, Any
from src.models.task import Task
from src.models.task_list import TaskList
from src.services.recurrence_service import RecurrenceService
from src.lib.utils import generate_task_id, parse_iso_date
from src.lib.validators import (
    validate_title,
    validate_description,
    validate_priority,
    validate_due_date,
    validate_tags,
    ValidationError
)


class TaskService:
    """
    Service layer for task operations.

    Handles business logic, validation, and task state management.
    """

    def __init__(self, task_list: TaskList, recurrence_service: RecurrenceService):
        """
        Initialize TaskService with a task repository.

        Args:
            task_list: TaskList repository instance
        """
        self.task_list = task_list
        self.recurrence_service = recurrence_service

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list] = None,
        due_date: Optional[str] = None,
        recurrence: Optional[str] = None
    ) -> Task:
        """
        Create a new task with validation.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Priority level (optional: high, medium, low)
            tags: List of tags (optional)
            due_date: Due date string in ISO 8601 format (optional)
            recurrence: Recurrence interval (optional)

        Returns:
            Task: Created task object

        Raises:
            ValidationError: If any input is invalid

        Examples:
            >>> from src.models.task_list import TaskList
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> task = service.create_task("Buy groceries")
            >>> task.title
            'Buy groceries'
            >>> task.completed
            False
        """
        # Validate inputs
        validated_title = validate_title(title)
        validated_description = validate_description(description)
        validated_priority = validate_priority(priority)
        validated_tags = validate_tags(tags)

        # Parse due date if provided
        due_date_obj = None
        if due_date:
            validated_due_date = validate_due_date(due_date)
            due_date_obj = parse_iso_date(validated_due_date)

        # Create task
        task = Task(
            id=generate_task_id(),
            title=validated_title,
            description=validated_description,
            priority=validated_priority,
            tags=validated_tags,
            due_date=due_date_obj
        )

        # Add to repository
        self.task_list.add(task)

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object if found, None otherwise

        Examples:
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> task = service.create_task("Test task")
            >>> retrieved = service.get_task(task.id)
            >>> retrieved.title
            'Test task'
        """
        return self.task_list.get(task_id)

    def get_all_tasks(self) -> list:
        """
        Get all tasks in insertion order.

        Returns:
            List of all Task objects

        Examples:
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> service.create_task("Task 1")
            >>> service.create_task("Task 2")
            >>> len(service.get_all_tasks())
            2
        """
        return self.task_list.all()

    def update_task(self, task_id: str, **updates: Dict[str, Any]) -> Task:
        """
        Update an existing task.

        Args:
            task_id: Task identifier
            **updates: Field updates (title, description, priority, tags, due_date)

        Returns:
            Updated Task object

        Raises:
            KeyError: If task not found
            ValidationError: If update values are invalid

        Examples:
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> task = service.create_task("Original title")
            >>> updated = service.update_task(task.id, title="New title")
            >>> updated.title
            'New title'
        """
        task = self.task_list.get(task_id)
        if task is None:
            raise KeyError(f"Task with ID {task_id} not found")

        # Validate and apply updates
        if 'title' in updates:
            task.title = validate_title(updates['title'])

        if 'description' in updates:
            task.description = validate_description(updates['description'])

        if 'priority' in updates:
            task.priority = validate_priority(updates['priority'])

        if 'tags' in updates:
            task.tags = validate_tags(updates['tags'])

        if 'due_date' in updates:
            due_date_str = updates['due_date']
            if due_date_str:
                validated_due_date = validate_due_date(due_date_str)
                task.due_date = parse_iso_date(validated_due_date)
            else:
                task.due_date = None

        # Update in repository
        self.task_list.update(task)

        return task

    def delete_task(self, task_id: str) -> None:
        """
        Delete a task by ID.

        Args:
            task_id: Task identifier

        Raises:
            KeyError: If task not found

        Examples:
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> task = service.create_task("To be deleted")
            >>> service.delete_task(task.id)
            >>> service.get_task(task.id)
            None
        """
        if not self.task_list.exists(task_id):
            raise KeyError(f"Task with ID {task_id} not found")

        self.task_list.delete(task_id)

    def toggle_complete(self, task_id: str) -> Task:
        """
        Toggle task completion status.

        Args:
            task_id: Task identifier

        Returns:
            Updated Task object

        Raises:
            KeyError: If task not found
        """
        task = self.task_list.get(task_id)
        if task is None:
            raise KeyError(f"Task with ID {task_id} not found")

        if task.recurrence and not task.completed:
            self.recurrence_service.generate_next_occurrence(task, self)

        task.toggle_complete()
        self.task_list.update(task)

        return task

    def task_count(self) -> int:
        """
        Get total number of tasks.

        Returns:
            int: Task count

        Examples:
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> service.task_count()
            0
            >>> service.create_task("Task 1")
            >>> service.task_count()
            1
        """
        return self.task_list.count()

    def add_tag(self, task_id: str, tag: str) -> Task:
        """
        Add a tag to a task.

        Args:
            task_id: Task identifier
            tag: Tag to add

        Returns:
            Updated Task object

        Raises:
            KeyError: If task not found
        """
        task = self.task_list.get(task_id)
        if task is None:
            raise KeyError(f"Task with ID {task_id} not found")

        task.add_tag(tag)
        self.task_list.update(task)

        return task

    def remove_tag(self, task_id: str, tag: str) -> Task:
        """
        Remove a tag from a task.

        Args:
            task_id: Task identifier
            tag: Tag to remove

        Returns:
            Updated Task object

        Raises:
            KeyError: If task not found
        """
        task = self.task_list.get(task_id)
        if task is None:
            raise KeyError(f"Task with ID {task_id} not found")

        task.remove_tag(tag)
        self.task_list.update(task)

        return task

    def is_overdue(self, task_id: str) -> bool:
        """
        Check if a task is overdue.

        Args:
            task_id: Task identifier

        Returns:
            bool: True if task is overdue, False otherwise

        Raises:
            KeyError: If task not found
        """
        task = self.task_list.get(task_id)
        if task is None:
            raise KeyError(f"Task with ID {task_id} not found")

        return task.is_overdue()
