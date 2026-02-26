"""
SearchService - Business logic for searching, filtering, and sorting tasks.
"""

from typing import List
from datetime import datetime, timedelta
from src.models.task import Task


class SearchService:
    """
    Service layer for task search, filter, and sort operations.
    """

    def search_tasks(self, tasks: List[Task], keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title, description, and tags.

        Args:
            tasks: List of tasks to search
            keyword: Search keyword

        Returns:
            List of matching tasks
        """
        keyword = keyword.lower()
        return [
            task
            for task in tasks
            if keyword in task.title.lower()
            or (task.description and keyword in task.description.lower())
            or any(keyword in tag.lower() for tag in task.tags)
        ]

    def filter_by_status(self, tasks: List[Task], completed: bool) -> List[Task]:
        """
        Filter tasks by completion status.

        Args:
            tasks: List of tasks to filter
            completed: Completion status to filter by

        Returns:
            List of matching tasks
        """
        return [task for task in tasks if task.completed == completed]

    def filter_by_priority(self, tasks: List[Task], priority: str) -> List[Task]:
        """
        Filter tasks by priority.

        Args:
            tasks: List of tasks to filter
            priority: Priority to filter by

        Returns:
            List of matching tasks
        """
        return [task for task in tasks if task.priority == priority]

    def filter_by_tag(self, tasks: List[Task], tag: str) -> List[Task]:
        """
        Filter tasks by tag.

        Args:
            tasks: List of tasks to filter
            tag: Tag to filter by

        Returns:
            List of matching tasks
        """
        return [task for task in tasks if tag in task.tags]

    def filter_by_due_date_range(self, tasks: List[Task], start: datetime, end: datetime) -> List[Task]:
        """
        Filter tasks by due date range.

        Args:
            tasks: List of tasks to filter
            start: Start of date range
            end: End of date range

        Returns:
            List of matching tasks
        """
        return [
            task
            for task in tasks
            if task.due_date and start <= task.due_date <= end
        ]

    def get_overdue_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Get all overdue tasks.

        Args:
            tasks: List of tasks to check

        Returns:
            List of overdue tasks
        """
        return [task for task in tasks if task.is_overdue()]

    def get_upcoming_tasks(self, tasks: List[Task], hours: int) -> List[Task]:
        """
        Get tasks due within a specified number of hours.

        Args:
            tasks: List of tasks to check
            hours: Number of hours to check within

        Returns:
            List of upcoming tasks
        """
        now = datetime.now()
        upcoming_time = now + timedelta(hours=hours)
        return [
            task
            for task in tasks
            if task.due_date and now <= task.due_date <= upcoming_time
        ]

    def sort_by_due_date(self, tasks: List[Task], ascending: bool = True) -> List[Task]:
        """
        Sort tasks by due date.

        Args:
            tasks: List of tasks to sort
            ascending: Sort ascending if True, descending if False

        Returns:
            Sorted list of tasks
        """
        return sorted(
            tasks,
            key=lambda task: task.due_date if task.due_date else datetime.max,
            reverse=not ascending,
        )

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority (high -> medium -> low).

        Args:
            tasks: List of tasks to sort

        Returns:
            Sorted list of tasks
        """
        priority_map = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: priority_map.get(task.priority, 3),
        )

    def sort_by_title(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks alphabetically by title.

        Args:
            tasks: List of tasks to sort

        Returns:
            Sorted list of tasks
        """
        return sorted(tasks, key=lambda task: task.title.lower())
