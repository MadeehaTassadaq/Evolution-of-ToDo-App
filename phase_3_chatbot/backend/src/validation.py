"""
Validation Module for Todo AI Chatbot
Provides validation functions for task input parameters
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


def validate_task_input(title: str, description: Optional[str] = None,
                       due_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate task input parameters

    Args:
        title: Task title (required)
        description: Task description (optional)
        due_date: Task due date in ISO 8601 format (optional)

    Returns:
        Dictionary with validation result and error messages
    """
    errors = []

    # Validate title
    if not title or not title.strip():
        errors.append("Title is required")
    elif len(title.strip()) < 1:
        errors.append("Title must be at least 1 character long")
    elif len(title.strip()) > 500:
        errors.append("Title must be no more than 500 characters long")

    # Validate description
    if description and len(description) > 5000:
        errors.append("Description must be no more than 5000 characters long")

    # Validate due date
    if due_date:
        try:
            # Try to parse the date
            parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            # Check if it's in the past (optional validation)
            if parsed_date < datetime.now(parsed_date.tzinfo if parsed_date.tzinfo else None):
                # For tasks, we might allow past dates for overdue tasks
                pass
        except ValueError:
            errors.append("Due date must be in ISO 8601 format (e.g., '2023-12-31T23:59:59')")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate that a string is a valid UUID

    Args:
        uuid_string: String to validate

    Returns:
        True if valid UUID, False otherwise
    """
    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_update_params(new_title: Optional[str] = None,
                          new_description: Optional[str] = None,
                          new_due_date: Optional[str] = None,
                          new_status: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate parameters for task updates

    Args:
        new_title: New task title (optional)
        new_description: New task description (optional)
        new_due_date: New task due date (optional)
        new_status: New task status (optional)

    Returns:
        Dictionary with validation result and error messages
    """
    errors = []

    # Check if at least one parameter is provided
    if all(param is None for param in [new_title, new_description, new_due_date, new_status]):
        errors.append("At least one parameter must be provided for update")

    # Validate new title if provided
    if new_title is not None:
        if len(new_title.strip()) < 1:
            errors.append("New title must be at least 1 character long")
        elif len(new_title.strip()) > 500:
            errors.append("New title must be no more than 500 characters long")

    # Validate new description if provided
    if new_description is not None and len(new_description) > 5000:
        errors.append("New description must be no more than 5000 characters long")

    # Validate new due date if provided
    if new_due_date:
        try:
            datetime.fromisoformat(new_due_date.replace('Z', '+00:00'))
        except ValueError:
            errors.append("New due date must be in ISO 8601 format (e.g., '2023-12-31T23:59:59')")

    # Validate new status if provided
    if new_status and new_status not in ['pending', 'completed']:
        errors.append("New status must be either 'pending' or 'completed'")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def validate_status_filter(status: str) -> Dict[str, Any]:
    """
    Validate status filter parameter

    Args:
        status: Status filter ('all', 'pending', 'completed')

    Returns:
        Dictionary with validation result and error messages
    """
    errors = []

    if status not in ['all', 'pending', 'completed']:
        errors.append("Status filter must be 'all', 'pending', or 'completed'")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }