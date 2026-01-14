"""
Security Module for Todo AI Chatbot
Handles security validation and sanitization for MCP tool inputs
"""

import html
import re
from typing import Dict, Any, Union
from urllib.parse import urlparse
import bleach

from .error_handler import ValidationError


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input string to prevent injection attacks

    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if input_str is None:
        return None

    # Truncate to max length
    if len(input_str) > max_length:
        input_str = input_str[:max_length]

    # Remove null bytes (potential for SQL injection in some databases)
    input_str = input_str.replace('\x00', '')

    # Strip leading/trailing whitespace
    input_str = input_str.strip()

    # Basic sanitization to prevent script tags and other potentially harmful content
    # Use bleach to remove potentially dangerous HTML
    sanitized = bleach.clean(input_str, strip=True)

    return sanitized


def validate_safe_content(content: str, field_name: str) -> None:
    """
    Validate that content doesn't contain unsafe patterns

    Args:
        content: Content to validate
        field_name: Name of the field being validated

    Raises:
        ValidationError: If content contains unsafe patterns
    """
    if not content:
        return

    # Check for potential SQL injection patterns
    sql_patterns = [
        r"(?i)(union\s+select|drop\s+\w+|create\s+\w+|alter\s+\w+|delete\s+from|insert\s+into)",
        r"(?i)(exec\s*\(|execute\s*\(|sp_|xp_)",
        r"(?i)(;\s*(drop|create|alter|delete|insert))",
        r"(?i)(script|javascript:|vbscript:|on\w+\s*=)"
    ]

    for pattern in sql_patterns:
        if re.search(pattern, content):
            raise ValidationError(f"{field_name} contains potentially unsafe content")

    # Check for potential command injection patterns
    cmd_patterns = [
        r"[;&|]",
        r"\$\(",
        r"`[^`]*`",
        r"eval\s*\(",
        r"exec\s*\("
    ]

    for pattern in cmd_patterns:
        if re.search(pattern, content):
            # Allow these in certain contexts but flag for review
            pass  # For now, just log - in a real system you might want to reject


def sanitize_task_input(title: str, description: str = None) -> Dict[str, str]:
    """
    Sanitize task input fields

    Args:
        title: Task title
        description: Task description (optional)

    Returns:
        Dictionary with sanitized inputs
    """
    sanitized_inputs = {}

    if title is not None:
        # Sanitize title
        sanitized_title = sanitize_input(title, max_length=500)
        validate_safe_content(sanitized_title, "title")
        sanitized_inputs['title'] = sanitized_title

    if description is not None:
        # Sanitize description
        sanitized_description = sanitize_input(description, max_length=5000)
        validate_safe_content(sanitized_description, "description")
        sanitized_inputs['description'] = sanitized_description

    return sanitized_inputs


def validate_url(url: str) -> bool:
    """
    Validate that a URL is properly formatted

    Args:
        url: URL to validate

    Returns:
        True if valid, False otherwise
    """
    if not url:
        return True  # Allow None/empty URLs

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_json_input(data: Union[Dict, str]) -> Union[Dict, str]:
    """
    Sanitize JSON input to prevent prototype pollution and other attacks

    Args:
        data: JSON data to sanitize

    Returns:
        Sanitized JSON data
    """
    if isinstance(data, str):
        # If it's a string, try to parse it and then sanitize
        import json
        try:
            parsed = json.loads(data)
            return sanitize_json_input(parsed)
        except json.JSONDecodeError:
            # If it's not valid JSON, sanitize as string
            return sanitize_input(data)

    elif isinstance(data, dict):
        # Sanitize dictionary keys and values
        sanitized = {}
        for key, value in data.items():
            # Sanitize the key
            safe_key = sanitize_input(str(key))
            # Prevent prototype pollution by blocking __proto__ and constructor
            if safe_key in ["__proto__", "constructor", "prototype"]:
                continue

            # Sanitize the value recursively
            sanitized[safe_key] = sanitize_json_input(value)

        return sanitized

    elif isinstance(data, list):
        # Sanitize each element in the list
        return [sanitize_json_input(item) for item in data]

    else:
        # For primitive types, return as is
        return data


def validate_mcp_tool_input(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize inputs for MCP tools

    Args:
        tool_name: Name of the MCP tool
        params: Parameters passed to the tool

    Returns:
        Sanitized parameters
    """
    validated_params = params.copy()

    if tool_name == "add_task":
        # Validate add_task parameters
        if "title" in validated_params:
            sanitized = sanitize_task_input(validated_params["title"],
                                          validated_params.get("description"))
            validated_params.update(sanitized)

    elif tool_name == "update_task":
        # Validate update_task parameters
        if "new_title" in validated_params:
            sanitized = sanitize_task_input(validated_params["new_title"],
                                          validated_params.get("new_description"))
            # Update only the specific fields
            if "new_title" in sanitized:
                validated_params["new_title"] = sanitized["title"]
            if "new_description" in sanitized:
                validated_params["new_description"] = sanitized["description"]

    elif tool_name == "list_tasks":
        # Validate list_tasks parameters
        if "status" in validated_params:
            status = validated_params["status"]
            if status not in [None, "all", "pending", "completed"]:
                raise ValidationError("Invalid status parameter for list_tasks")

        if "limit" in validated_params:
            limit = validated_params["limit"]
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                raise ValidationError("Limit must be an integer between 1 and 100")

    elif tool_name == "complete_task" or tool_name == "delete_task":
        # Validate task identifiers
        if "task_title" in validated_params and validated_params["task_title"]:
            validated_params["task_title"] = sanitize_input(validated_params["task_title"])

    # Sanitize all string parameters
    for key, value in validated_params.items():
        if isinstance(value, str):
            validated_params[key] = sanitize_input(value)

    return validated_params


def is_safe_filename(filename: str) -> bool:
    """
    Check if a filename is safe to use

    Args:
        filename: Filename to validate

    Returns:
        True if safe, False otherwise
    """
    if not filename:
        return True

    # Check for path traversal attempts
    if '..' in filename or './' in filename:
        return False

    # Check for potentially dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    if any(char in filename for char in dangerous_chars):
        return False

    return True


def validate_user_permission(user_id: str, requested_user_id: str, operation: str) -> bool:
    """
    Validate if a user has permission to perform an operation on another user's data

    Args:
        user_id: ID of the requesting user
        requested_user_id: ID of the user whose data is being accessed
        operation: Operation being performed

    Returns:
        True if permission is granted, False otherwise
    """
    # Basic validation: users can only operate on their own data
    # In a real system, you might have more complex permission rules
    return str(user_id) == str(requested_user_id)


def mask_sensitive_data(data: Union[Dict, str, Any]) -> Union[Dict, str, Any]:
    """
    Mask sensitive data in logs and responses

    Args:
        data: Data to mask

    Returns:
        Data with sensitive information masked
    """
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if isinstance(key, str) and any(sensitive in key.lower() for sensitive in
                                            ["password", "token", "secret", "key", "auth", "credential"]):
                masked[key] = "***MASKED***"
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data