"""
TaskList repository for the Phase I Console Todo Application.

In-memory storage and CRUD operations for tasks.
"""

from typing import Dict, List, Optional
from src.models.task import Task


class TaskList:
    """
    In-memory repository for managing tasks.

    Uses a dict for O(1) ID lookups and a list for maintaining insertion order.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task objects
        _order: List of task IDs in insertion order

    Examples:
        >>> from src.lib.utils import generate_task_id
        >>> from src.models.task import Task
        >>> task_list = TaskList()
        >>> task = Task(id=generate_task_id(), title="Test task")
        >>> task_list.add(task)
        >>> len(task_list.all())
        1
    """

    def __init__(self):
        """Initialize empty task list."""
        self._tasks: Dict[str, Task] = {}
        self._order: List[str] = []

    def add(self, task: Task) -> None:
        """
        Add a task to the list.

        Args:
            task: Task object to add

        Raises:
            ValueError: If task with same ID already exists

        Examples:
            >>> task_list = TaskList()
            >>> task = Task(id="test-id", title="Test")
            >>> task_list.add(task)
            >>> task_list.get("test-id").title
            'Test'
        """
        if task.id in self._tasks:
            raise ValueError(f"Task with ID {task.id} already exists")

        self._tasks[task.id] = task
        self._order.append(task.id)

    def get(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object if found, None otherwise

        Examples:
            >>> task_list = TaskList()
            >>> task = Task(id="test-id", title="Test")
            >>> task_list.add(task)
            >>> task_list.get("test-id").title
            'Test'
            >>> task_list.get("nonexistent")
            None
        """
        return self._tasks.get(task_id)

    def all(self) -> List[Task]:
        """
        Get all tasks in insertion order.

        Returns:
            List of Task objects

        Examples:
            >>> task_list = TaskList()
            >>> task1 = Task(id="1", title="First")
            >>> task2 = Task(id="2", title="Second")
            >>> task_list.add(task1)
            >>> task_list.add(task2)
            >>> [t.title for t in task_list.all()]
            ['First', 'Second']
        """
        return [self._tasks[task_id] for task_id in self._order if task_id in self._tasks]

    def update(self, task: Task) -> None:
        """
        Update an existing task.

        Args:
            task: Task object with updated values

        Raises:
            KeyError: If task does not exist

        Examples:
            >>> task_list = TaskList()
            >>> task = Task(id="1", title="Original")
            >>> task_list.add(task)
            >>> task.title = "Updated"
            >>> task_list.update(task)
            >>> task_list.get("1").title
            'Updated'
        """
        if task.id not in self._tasks:
            raise KeyError(f"Task with ID {task.id} not found")

        self._tasks[task.id] = task

    def delete(self, task_id: str) -> None:
        """
        Delete a task by ID.

        Args:
            task_id: Task identifier

        Raises:
            KeyError: If task does not exist

        Examples:
            >>> task_list = TaskList()
            >>> task = Task(id="1", title="Test")
            >>> task_list.add(task)
            >>> task_list.delete("1")
            >>> task_list.get("1")
            None
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task with ID {task_id} not found")

        del self._tasks[task_id]
        self._order.remove(task_id)

    def exists(self, task_id: str) -> bool:
        """
        Check if a task exists.

        Args:
            task_id: Task identifier

        Returns:
            bool: True if task exists, False otherwise

        Examples:
            >>> task_list = TaskList()
            >>> task = Task(id="1", title="Test")
            >>> task_list.add(task)
            >>> task_list.exists("1")
            True
            >>> task_list.exists("nonexistent")
            False
        """
        return task_id in self._tasks

    def count(self) -> int:
        """
        Get the total number of tasks.

        Returns:
            int: Number of tasks in the list

        Examples:
            >>> task_list = TaskList()
            >>> task_list.count()
            0
            >>> task_list.add(Task(id="1", title="Test"))
            >>> task_list.count()
            1
        """
        return len(self._tasks)

    def clear(self) -> None:
        """
        Remove all tasks.

        Examples:
            >>> task_list = TaskList()
            >>> task_list.add(Task(id="1", title="Test"))
            >>> task_list.clear()
            >>> task_list.count()
            0
        """
        self._tasks.clear()
        self._order.clear()

    def __len__(self) -> int:
        """Support len() function."""
        return self.count()

    def __contains__(self, task_id: str) -> bool:
        """Support 'in' operator."""
        return self.exists(task_id)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"TaskList(tasks={self.count()})"
