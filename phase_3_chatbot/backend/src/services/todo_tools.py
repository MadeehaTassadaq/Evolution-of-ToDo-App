"""
Todo Tools for Backend Operations
Database-backed tools for todo management operations that can be used by the backend
without MCP server dependencies.
"""

import logging
from typing import List, Optional, Dict, Any

# Configure logging for debugging
logger = logging.getLogger(__name__)
from pydantic import BaseModel
from uuid import UUID
from database.models.todo import Todo, TodoCreate, TodoUpdate
from .todo_service import TodoService


class TodoItem(BaseModel):
    """Represents a todo item."""
    id: UUID
    title: str
    description: Optional[str] = None
    status: str = "pending"  # "pending", "completed"
    priority: Optional[str] = None
    due_date: Optional[str] = None
    user_id: UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AddTaskParams(BaseModel):
    """Parameters for add_task tool."""
    user_id: str  # Will be converted to UUID
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None


class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool."""
    user_id: str  # Will be converted to UUID
    status_filter: Optional[str] = None  # "all", "pending", "completed"


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool."""
    user_id: str  # Will be converted to UUID
    task_id: Optional[UUID] = None  # Optional - can use task_title instead
    task_title: Optional[str] = None  # Optional - natural language lookup
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task tool."""
    user_id: str  # Will be converted to UUID
    task_id: Optional[UUID] = None  # Optional - can use task_title instead
    task_title: Optional[str] = None  # Optional - natural language lookup


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""
    user_id: str  # Will be converted to UUID
    task_id: Optional[UUID] = None  # Optional - can use task_title instead
    task_title: Optional[str] = None  # Optional - natural language lookup


class TodoTools:
    """Class containing all todo management tools that use the database."""

    def __init__(self, session):
        """Initialize with a database session."""
        self.session = session
        self.todo_service = TodoService(session)

    def _convert_user_id(self, user_id: str) -> UUID:
        """
        Convert string user_id to UUID format.

        Args:
            user_id: User ID as string from auth system

        Returns:
            UUID object
        """
        try:
            # Try to parse as UUID directly
            return UUID(user_id)
        except ValueError:
            # If it's not a UUID, we need to look up the actual UUID from the user table
            # For this case, let's assume the auth system provides UUIDs as strings
            # In a real scenario, we'd query the user table by username/email
            raise ValueError(f"Invalid user_id format: {user_id}. Expected UUID.")

    def add_task(self, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new task to the user's todo list.

        Args:
            user_id: The ID of the user creating the todo (string from auth)
            title: The title of the todo
            description: Optional description
            due_date: Optional due date

        Returns:
            Dictionary with success status and task information
        """
        try:
            # Validate input
            if not title or not title.strip():
                return {
                    "success": False,
                    "error_code": "VALIDATION_ERROR",
                    "error_message": "Title is required for the task",
                    "recoverable": True
                }

            # Convert user_id to UUID format
            user_uuid = self._convert_user_id(user_id)

            # Create new task
            new_task = self.todo_service.create_todo(
                user_id=user_uuid,
                title=title.strip(),
                description=description,
                due_date=due_date
            )

            # Convert to TodoItem format
            task_item = TodoItem(
                id=str(new_task.id),
                title=new_task.title,
                description=new_task.description,
                status=new_task.status,
                priority=new_task.priority,
                due_date=new_task.due_date.isoformat() if new_task.due_date else None,
                user_id=str(new_task.user_id),
                created_at=new_task.created_at.isoformat() if new_task.created_at else None,
                updated_at=new_task.updated_at.isoformat() if new_task.updated_at else None
            )

            return {
                "success": True,
                "task": task_item.model_dump(),
                "message": f"Task '{title}' added successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "ADD_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def list_tasks(self, user_id: str, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        List tasks for a specific user.

        Args:
            user_id: The ID of the user
            status_filter: Optional status filter ("all", "pending", "completed")

        Returns:
            Dictionary with success status and list of tasks
        """
        try:
            # Convert user_id to UUID format
            user_uuid = self._convert_user_id(user_id)

            # Get tasks
            tasks = self.todo_service.get_todos_by_user(
                user_id=user_uuid,
                status_filter=status_filter
            )

            # Convert to TodoItem format
            task_items = [
                TodoItem(
                    id=str(task.id),
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    due_date=task.due_date.isoformat() if task.due_date else None,
                    user_id=str(task.user_id),
                    created_at=task.created_at.isoformat() if task.created_at else None,
                    updated_at=task.updated_at.isoformat() if task.updated_at else None
                ).model_dump() for task in tasks
            ]

            return {
                "success": True,
                "tasks": task_items,
                "total_count": len(task_items)
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "LIST_TASKS_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def update_task(self, user_id: str, task_id: UUID = None, task_title: str = None,
                   title: Optional[str] = None, description: Optional[str] = None,
                   status: Optional[str] = None, priority: Optional[str] = None,
                   due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task by ID or title.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to update (optional if task_title provided)
            task_title: The title of the task to update (for natural language lookup)
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            priority: New priority (optional)
            due_date: New due date (optional)

        Returns:
            Dictionary with success status and updated task
        """
        try:
            # Validate that at least one identifier is provided
            if not task_id and not task_title:
                return {
                    "success": False,
                    "error_code": "VALIDATION_ERROR",
                    "error_message": "Either task_id or task_title must be provided",
                    "recoverable": True
                }

            # Convert user_id to UUID format
            user_uuid = self._convert_user_id(user_id)

            task_uuid = None

            # If task_title provided, look up by title first
            if task_title and not task_id:
                todo = self.todo_service.get_todo_by_title(task_title, user_uuid)
                if not todo:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND",
                        "error_message": f"No task found matching '{task_title}'",
                        "recoverable": False
                    }
                task_uuid = todo.id
            elif task_id:
                # Convert task_id to UUID if it's a string
                if isinstance(task_id, str):
                    try:
                        task_uuid = UUID(task_id)
                    except ValueError:
                        return {
                            "success": False,
                            "error_code": "VALIDATION_ERROR",
                            "error_message": f"Invalid task_id format: {task_id}. Expected UUID.",
                            "recoverable": False
                        }
                else:
                    task_uuid = task_id

            # Prepare update data
            update_data = TodoUpdate(
                title=title,
                description=description,
                status=status,
                priority=priority,
                due_date=due_date
            )

            # Update the task
            updated_task = self.todo_service.update_todo(
                todo_id=task_uuid,
                user_id=user_uuid,
                update_data=update_data
            )

            if not updated_task:
                identifier = task_title if task_title else str(task_id)
                return {
                    "success": False,
                    "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                    "error_message": f"Task '{identifier}' not found or you don't have permission to update it",
                    "recoverable": False
                }

            # Convert to TodoItem format
            task_item = TodoItem(
                id=str(updated_task.id),
                title=updated_task.title,
                description=updated_task.description,
                status=updated_task.status,
                priority=updated_task.priority,
                due_date=updated_task.due_date.isoformat() if updated_task.due_date else None,
                user_id=str(updated_task.user_id),
                created_at=updated_task.created_at.isoformat() if updated_task.created_at else None,
                updated_at=updated_task.updated_at.isoformat() if updated_task.updated_at else None
            )

            return {
                "success": True,
                "task": task_item.model_dump(),
                "message": f"Task '{updated_task.title}' updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "UPDATE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def complete_task(self, user_id: str, task_id: UUID = None, task_title: str = None) -> Dict[str, Any]:
        """
        Mark a task as completed by ID or title.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to mark as completed (optional if task_title provided)
            task_title: The title of the task to complete (for natural language lookup)

        Returns:
            Dictionary with success status and updated task
        """
        try:
            # Validate that at least one identifier is provided
            if not task_id and not task_title:
                return {
                    "success": False,
                    "error_code": "VALIDATION_ERROR",
                    "error_message": "Either task_id or task_title must be provided",
                    "recoverable": True
                }

            # Convert user_id to UUID format
            user_uuid = self._convert_user_id(user_id)

            task_uuid = None

            # If task_title provided, look up by title first
            if task_title and not task_id:
                todo = self.todo_service.get_todo_by_title(task_title, user_uuid)
                if not todo:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND",
                        "error_message": f"No task found matching '{task_title}'",
                        "recoverable": False
                    }
                task_uuid = todo.id
            elif task_id:
                # Convert task_id to UUID if it's a string
                if isinstance(task_id, str):
                    try:
                        task_uuid = UUID(task_id)
                    except ValueError:
                        return {
                            "success": False,
                            "error_code": "VALIDATION_ERROR",
                            "error_message": f"Invalid task_id format: {task_id}. Expected UUID.",
                            "recoverable": False
                        }
                else:
                    task_uuid = task_id

            # Prepare update data to mark as completed
            update_data = TodoUpdate(status="completed")

            # Update the task
            updated_task = self.todo_service.update_todo(
                todo_id=task_uuid,
                user_id=user_uuid,
                update_data=update_data
            )

            if not updated_task:
                identifier = task_title if task_title else str(task_id)
                return {
                    "success": False,
                    "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                    "error_message": f"Task '{identifier}' not found or you don't have permission to update it",
                    "recoverable": False
                }

            # Convert to TodoItem format
            task_item = TodoItem(
                id=str(updated_task.id),
                title=updated_task.title,
                description=updated_task.description,
                status=updated_task.status,
                priority=updated_task.priority,
                due_date=updated_task.due_date.isoformat() if updated_task.due_date else None,
                user_id=str(updated_task.user_id),
                created_at=updated_task.created_at.isoformat() if updated_task.created_at else None,
                updated_at=updated_task.updated_at.isoformat() if updated_task.updated_at else None
            )

            return {
                "success": True,
                "task": task_item.model_dump(),
                "message": f"Task '{updated_task.title}' marked as completed"
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "COMPLETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def delete_task(self, user_id: str, task_id: UUID = None, task_title: str = None) -> Dict[str, Any]:
        """
        Delete a task by ID or title.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to delete (optional if task_title provided)
            task_title: The title of the task to delete (for natural language lookup)

        Returns:
            Dictionary with success status
        """
        try:
            # Validate that at least one identifier is provided
            if not task_id and not task_title:
                logger.warning(f"delete_task called without task_id or task_title for user {user_id}")
                return {
                    "success": False,
                    "error_code": "VALIDATION_ERROR",
                    "error_message": "Either task_id or task_title must be provided",
                    "recoverable": True
                }

            logger.info(f"delete_task called: user_id={user_id}, task_id={task_id}, task_title={task_title}")

            # Convert user_id to UUID format
            user_uuid = self._convert_user_id(user_id)

            task_uuid = None
            deleted_task_title = task_title  # Store for success message

            # If task_title provided, look up by title first
            if task_title and not task_id:
                logger.info(f"Looking up task by title: '{task_title}' for user {user_uuid}")
                todo = self.todo_service.get_todo_by_title(task_title, user_uuid)
                if not todo:
                    logger.warning(f"Task not found with title: '{task_title}' for user {user_uuid}")
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND",
                        "error_message": f"No task found matching '{task_title}'",
                        "recoverable": False
                    }
                task_uuid = todo.id
                deleted_task_title = todo.title
                logger.info(f"Found task by title: {task_uuid}")
            elif task_id:
                # Convert task_id to UUID if it's a string
                if isinstance(task_id, str):
                    try:
                        task_uuid = UUID(task_id)
                    except ValueError:
                        logger.error(f"Invalid task_id format: {task_id}")
                        return {
                            "success": False,
                            "error_code": "VALIDATION_ERROR",
                            "error_message": f"Invalid task_id format: {task_id}. Expected UUID.",
                            "recoverable": False
                        }
                else:
                    task_uuid = task_id
                logger.info(f"Using task_id: {task_uuid}")

            # Delete the task
            logger.info(f"Deleting task: todo_id={task_uuid}, user_id={user_uuid}")
            success = self.todo_service.delete_todo(
                todo_id=task_uuid,
                user_id=user_uuid
            )

            if not success:
                identifier = task_title if task_title else str(task_id)
                logger.error(f"Failed to delete task '{identifier}' - not found or permission denied")
                return {
                    "success": False,
                    "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                    "error_message": f"Task '{identifier}' not found or you don't have permission to delete it",
                    "recoverable": False
                }

            logger.info(f"Successfully deleted task: '{deleted_task_title}'")
            return {
                "success": True,
                "message": f"Task '{deleted_task_title}' deleted successfully"
            }

        except Exception as e:
            logger.exception(f"Exception in delete_task: {str(e)}")
            return {
                "success": False,
                "error_code": "DELETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }