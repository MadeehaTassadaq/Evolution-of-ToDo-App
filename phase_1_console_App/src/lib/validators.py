"""
Input validation functions for the Phase I Console Todo Application.

This module provides validators for:
- Task titles (non-empty, max 200 characters)
- Task descriptions (max 1000 characters)
- Priority values (high, medium, low, or None)
- Date formats (ISO 8601)
- Recurrence intervals
"""

from typing import Optional
from src.lib.utils import parse_iso_date


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_title(title: str) -> str:
    """
    Validate task title.

    Requirements (FR-038):
    - Non-empty
    - Maximum 200 characters

    Args:
        title: Task title to validate

    Returns:
        str: Validated title (stripped of whitespace)

    Raises:
        ValidationError: If title is invalid

    Examples:
        >>> validate_title("Buy groceries")
        'Buy groceries'
        >>> validate_title("")
        Traceback (most recent call last):
        ...
        ValidationError: Title cannot be empty
    """
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")

    title = title.strip()

    if len(title) > 200:
        raise ValidationError(f"Title too long ({len(title)} characters, max 200)")

    return title


def validate_description(description: Optional[str]) -> Optional[str]:
    """
    Validate task description.

    Requirements (FR-003):
    - Optional field
    - Maximum 1000 characters if provided

    Args:
        description: Task description to validate (can be None)

    Returns:
        Optional[str]: Validated description or None

    Raises:
        ValidationError: If description exceeds max length
    """
    if description is None:
        return None

    description = description.strip()

    if len(description) > 1000:
        raise ValidationError(
            f"Description too long ({len(description)} characters, max 1000)"
        )

    return description if description else None


def validate_priority(priority: Optional[str]) -> Optional[str]:
    """
    Validate priority value.

    Requirements (FR-039):
    - Must be 'high', 'medium', 'low', or None

    Args:
        priority: Priority value to validate

    Returns:
        Optional[str]: Validated priority (lowercased) or None

    Raises:
        ValidationError: If priority value is invalid

    Examples:
        >>> validate_priority("high")
        'high'
        >>> validate_priority("High")
        'high'
        >>> validate_priority(None)
        None
        >>> validate_priority("urgent")
        Traceback (most recent call last):
        ...
        ValidationError: Priority must be 'high', 'medium', or 'low'
    """
    if priority is None:
        return None

    priority = priority.strip().lower()

    valid_priorities = ['high', 'medium', 'low']
    if priority not in valid_priorities:
        raise ValidationError(
            f"Priority must be 'high', 'medium', or 'low' (got '{priority}')"
        )

    return priority


def validate_due_date(date_string: Optional[str]) -> Optional[str]:
    """
    Validate due date format.

    Requirements (FR-040):
    - Must follow ISO 8601 format: YYYY-MM-DD or YYYY-MM-DD HH:MM

    Args:
        date_string: Date string to validate

    Returns:
        Optional[str]: Validated date string or None

    Raises:
        ValidationError: If date format is invalid

    Examples:
        >>> validate_due_date("2026-01-15")
        '2026-01-15'
        >>> validate_due_date("2026-01-15 09:00")
        '2026-01-15 09:00'
        >>> validate_due_date("15/01/2026")
        Traceback (most recent call last):
        ...
        ValidationError: Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM
    """
    if date_string is None:
        return None

    date_string = date_string.strip()

    # Validate by attempting to parse
    parsed = parse_iso_date(date_string)
    if parsed is None:
        raise ValidationError(
            "Invalid date format. Use YYYY-MM-DD or YYYY-MM-DD HH:MM"
        )

    return date_string


def validate_recurrence_interval(interval: Optional[str]) -> Optional[str]:
    """
    Validate recurrence interval.

    Requirements (FR-041):
    - Must be 'daily', 'weekly', 'monthly', 'yearly', or custom format

    Args:
        interval: Recurrence interval to validate

    Returns:
        Optional[str]: Validated interval or None

    Raises:
        ValidationError: If interval is invalid

    Examples:
        >>> validate_recurrence_interval("daily")
        'daily'
        >>> validate_recurrence_interval("weekly")
        'weekly'
        >>> validate_recurrence_interval("invalid")
        Traceback (most recent call last):
        ...
        ValidationError: Invalid recurrence interval
    """
    if interval is None:
        return None

    interval = interval.strip().lower()

    valid_intervals = ['daily', 'weekly', 'monthly', 'yearly']
    if interval not in valid_intervals:
        raise ValidationError(
            f"Invalid recurrence interval. Must be one of: {', '.join(valid_intervals)}"
        )

    return interval


def validate_tags(tags: Optional[list]) -> list:
    """
    Validate tags list.

    Args:
        tags: List of tag strings

    Returns:
        list: Validated tags (non-empty strings only)

    Examples:
        >>> validate_tags(["work", "urgent"])
        ['work', 'urgent']
        >>> validate_tags(None)
        []
        >>> validate_tags(["work", "", "home"])
        ['work', 'home']
    """
    if tags is None:
        return []

    # Filter out empty strings and strip whitespace
    return [tag.strip() for tag in tags if tag and tag.strip()]
