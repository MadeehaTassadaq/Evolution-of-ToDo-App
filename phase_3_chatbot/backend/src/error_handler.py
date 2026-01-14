"""
Error Handler for Todo AI Chatbot
Centralized error handling for all application layers
"""

from typing import Dict, Any, Union
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

from .app_logging import log_error


class TodoError(Exception):
    """
    Base exception class for Todo AI Chatbot
    """
    def __init__(self, message: str, error_code: str = "TODO_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary representation
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code
        }


class ValidationError(TodoError):
    """
    Exception raised for validation errors
    """
    def __init__(self, message: str, field_errors: Dict[str, str] = None):
        super().__init__(message, "VALIDATION_ERROR", 400)
        self.field_errors = field_errors or {}

    def to_dict(self) -> Dict[str, Any]:
        error_dict = super().to_dict()
        error_dict["field_errors"] = self.field_errors
        return error_dict


class AuthenticationError(TodoError):
    """
    Exception raised for authentication errors
    """
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)


class AuthorizationError(TodoError):
    """
    Exception raised for authorization errors
    """
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHORIZATION_ERROR", 403)


class ResourceNotFoundError(TodoError):
    """
    Exception raised when a requested resource is not found
    """
    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"

        super().__init__(message, "RESOURCE_NOT_FOUND", 404)
        self.resource_type = resource_type
        self.resource_id = resource_id


class BusinessLogicError(TodoError):
    """
    Exception raised for business logic errors
    """
    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(message, error_code, 422)


class DatabaseError(TodoError):
    """
    Exception raised for database-related errors
    """
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, "DATABASE_ERROR", 500)


class ExternalServiceError(TodoError):
    """
    Exception raised for external service errors (e.g., OpenAI API)
    """
    def __init__(self, service_name: str, message: str = None):
        if message is None:
            message = f"Error communicating with {service_name}"
        else:
            message = f"Error with {service_name}: {message}"

        super().__init__(message, "EXTERNAL_SERVICE_ERROR", 502)
        self.service_name = service_name


def handle_error(error: Exception, context: str = "", user_id: str = None) -> Dict[str, Any]:
    """
    Centralized error handler that logs and formats errors appropriately

    Args:
        error: The exception to handle
        context: Context where the error occurred
        user_id: User ID if applicable

    Returns:
        Dictionary with error details
    """
    # Log the error with context
    log_error(error, context, user_id)

    # Handle specific error types
    if isinstance(error, TodoError):
        return error.to_dict()
    elif isinstance(error, HTTPException):
        return {
            "error_code": "HTTP_ERROR",
            "message": error.detail,
            "status_code": error.status_code
        }
    elif isinstance(error, ValueError):
        return ValidationError(str(error)).to_dict()
    else:
        # For unexpected errors, return a generic error
        return {
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred",
            "status_code": 500
        }


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for FastAPI

    Args:
        request: The request that caused the exception
        exc: The exception that occurred

    Returns:
        JSONResponse with error details
    """
    error_response = handle_error(exc, f"Request to {request.url}",
                                  getattr(request.state, 'user_id', None))

    return JSONResponse(
        status_code=error_response.get('status_code', 500),
        content=error_response
    )


def wrap_with_error_handling(func):
    """
    Decorator to wrap functions with error handling

    Args:
        func: The function to wrap

    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TodoError:
            # Re-raise TodoErrors as they're already properly formatted
            raise
        except Exception as e:
            # Convert other exceptions to TodoError
            raise TodoError(f"Unexpected error in {func.__name__}: {str(e)}")

    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that required fields are present in the data

    Args:
        data: Dictionary containing the data to validate
        required_fields: List of required field names

    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            {field: "This field is required" for field in missing_fields}
        )


def validate_field_length(value: str, field_name: str, min_length: int = 1, max_length: int = None) -> None:
    """
    Validate the length of a field

    Args:
        value: Value to validate
        field_name: Name of the field
        min_length: Minimum length allowed
        max_length: Maximum length allowed (None means no limit)

    Raises:
        ValidationError: If the field length is invalid
    """
    if value is None:
        raise ValidationError(f"{field_name} cannot be null")

    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long")

    if max_length and len(value) > max_length:
        raise ValidationError(f"{field_name} must be no more than {max_length} characters long")


def validate_enum_value(value: str, field_name: str, valid_values: list) -> None:
    """
    Validate that a value is one of the valid enum values

    Args:
        value: Value to validate
        field_name: Name of the field
        valid_values: List of valid values

    Raises:
        ValidationError: If the value is not in the valid values
    """
    if value not in valid_values:
        raise ValidationError(f"{field_name} must be one of: {', '.join(valid_values)}")


# Specific validation functions for task-related operations
def validate_task_title(title: str) -> None:
    """
    Validate task title according to business rules

    Args:
        title: Task title to validate

    Raises:
        ValidationError: If the title is invalid
    """
    validate_field_length(title, "title", min_length=1, max_length=500)


def validate_task_description(description: str) -> None:
    """
    Validate task description according to business rules

    Args:
        description: Task description to validate

    Raises:
        ValidationError: If the description is invalid
    """
    if description is not None:
        validate_field_length(description, "description", max_length=5000)


def validate_task_status(status: str) -> None:
    """
    Validate task status according to business rules

    Args:
        status: Task status to validate

    Raises:
        ValidationError: If the status is invalid
    """
    validate_enum_value(status, "status", ["pending", "completed"])