"""
Utility functions for the Phase I Console Todo Application.

This module provides core utilities including:
- UUID-based ID generation
- ISO 8601 date/time parsing and formatting
- Date calculation for recurring tasks
"""

import uuid
from datetime import datetime, timedelta
import calendar
from typing import Optional


def generate_task_id() -> str:
    """
    Generate a unique task identifier using UUID4.

    Returns:
        str: A unique task ID (UUID4 string format)

    Example:
        >>> task_id = generate_task_id()
        >>> len(task_id)
        36
    """
    return str(uuid.uuid4())


def parse_iso_date(date_string: str) -> Optional[datetime]:
    """
    Parse an ISO 8601 formatted date string.

    Supports formats:
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM

    Args:
        date_string: Date string in ISO 8601 format

    Returns:
        datetime object if parsing successful, None otherwise

    Examples:
        >>> parse_iso_date("2026-01-15")
        datetime.datetime(2026, 1, 15, 0, 0)
        >>> parse_iso_date("2026-01-15 09:00")
        datetime.datetime(2026, 1, 15, 9, 0)
    """
    if not date_string:
        return None

    try:
        # Try full datetime format first
        if ' ' in date_string:
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M")
        else:
            return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return None


def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """
    Format a datetime object to ISO 8601 string.

    Args:
        dt: datetime object to format
        include_time: If True, include time component

    Returns:
        str: Formatted date string

    Examples:
        >>> dt = datetime(2026, 1, 15, 9, 0)
        >>> format_datetime(dt, include_time=True)
        '2026-01-15 09:00'
        >>> format_datetime(dt, include_time=False)
        '2026-01-15'
    """
    if include_time:
        return dt.strftime("%Y-%m-%d %H:%M")
    else:
        return dt.strftime("%Y-%m-%d")


def add_days(dt: datetime, days: int) -> datetime:
    """Add specified number of days to a datetime."""
    return dt + timedelta(days=days)


def add_weeks(dt: datetime, weeks: int) -> datetime:
    """Add specified number of weeks to a datetime."""
    return dt + timedelta(weeks=weeks)


def add_months(dt: datetime, months: int) -> datetime:
    """
    Add specified number of months to a datetime.

    Handles month-end edge cases (e.g., Jan 31 + 1 month = Feb 28/29).

    Args:
        dt: Source datetime
        months: Number of months to add

    Returns:
        datetime: Result with added months
    """
    month = dt.month + months
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1

    # Handle day overflow (e.g., Jan 31 -> Feb 28)
    day = min(dt.day, calendar.monthrange(year, month)[1])

    return dt.replace(year=year, month=month, day=day)


def add_years(dt: datetime, years: int) -> datetime:
    """
    Add specified number of years to a datetime.

    Handles leap year edge cases.

    Args:
        dt: Source datetime
        years: Number of years to add

    Returns:
        datetime: Result with added years
    """
    try:
        return dt.replace(year=dt.year + years)
    except ValueError:
        # Handle Feb 29 on non-leap year
        return dt.replace(year=dt.year + years, day=28)
