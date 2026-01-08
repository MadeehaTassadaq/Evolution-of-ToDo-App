"""
RecurrenceService - Business logic for handling recurring tasks.
"""

from datetime import datetime
from src.models.task import Task
from src.models.recurrence_rule import RecurrenceRule
from src.lib.utils import add_days, add_weeks, add_months, add_years, format_datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.task_service import TaskService


class RecurrenceService:
    """
    Service layer for recurring task operations.
    """

    def __init__(self):
        """
        Initialize RecurrenceService.
        """
        pass

    def calculate_next_due_date(self, current_due: datetime, rule: RecurrenceRule) -> datetime:
        """
        Calculate the next due date for a recurring task.

        Args:
            current_due: The current due date
            rule: The recurrence rule

        Returns:
            The next due date
        """
        if rule.interval_type == "daily":
            return add_days(current_due, rule.interval_count)
        elif rule.interval_type == "weekly":
            return add_weeks(current_due, rule.interval_count)
        elif rule.interval_type == "monthly":
            return add_months(current_due, rule.interval_count)
        elif rule.interval_type == "yearly":
            return add_years(current_due, rule.interval_count)
        else:
            raise ValueError(f"Invalid interval type: {rule.interval_type}")

    def generate_next_occurrence(self, task: Task, task_service: "TaskService") -> Task:
        """
        Generate the next occurrence of a recurring task.

        Args:
            task: The recurring task
            task_service: The TaskService instance to use for creating the new task

        Returns:
            The new task occurrence
        """
        if not task.recurrence:
            raise ValueError("Task is not a recurring task")

        next_due_date = self.calculate_next_due_date(task.due_date, task.recurrence)

        new_task = task_service.create_task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=format_datetime(next_due_date),
            recurrence=task.recurrence,
        )

        return new_task
