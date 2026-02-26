"""
RecurrenceRule model for the Phase I Console Todo Application.

Represents a repetition pattern for recurring tasks.
"""

from dataclasses import dataclass
from typing import Literal


RecurrenceInterval = Literal['daily', 'weekly', 'monthly', 'yearly']


@dataclass(frozen=True)
class RecurrenceRule:
    """
    Immutable value object representing a task recurrence pattern.

    Attributes:
        interval_type: Type of recurrence (daily, weekly, monthly, yearly)
        interval_count: Number of intervals (e.g., 1 for daily, 2 for bi-weekly)

    Examples:
        >>> rule = RecurrenceRule(interval_type='daily', interval_count=1)
        >>> rule.interval_type
        'daily'
        >>> rule.interval_count
        1
        >>> rule_weekly = RecurrenceRule(interval_type='weekly', interval_count=2)
        >>> rule_weekly.interval_type
        'weekly'
    """

    interval_type: RecurrenceInterval
    interval_count: int = 1

    def __post_init__(self):
        """Validate recurrence rule parameters."""
        if self.interval_count < 1:
            raise ValueError("interval_count must be at least 1")

        valid_types = ['daily', 'weekly', 'monthly', 'yearly']
        if self.interval_type not in valid_types:
            raise ValueError(
                f"interval_type must be one of: {', '.join(valid_types)}"
            )

    def __str__(self) -> str:
        """Human-readable representation."""
        if self.interval_count == 1:
            return self.interval_type
        else:
            return f"every {self.interval_count} {self.interval_type[:-2]}s"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"RecurrenceRule(interval_type='{self.interval_type}', "
            f"interval_count={self.interval_count})"
        )
