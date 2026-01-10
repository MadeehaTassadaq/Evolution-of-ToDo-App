"""
Todo Tools for Backend Operations
Database-backed tools for todo management operations that can be used by the backend
without MCP server dependencies.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from database.models.todo import Todo, TodoCreate, TodoUpdate
from backend.services.todo_service import TodoService


class TodoItem(BaseModel):
    """Represents a todo item."""
    id: int
    title: str
    description: Optional[str] = None
    status: str = "pending"  # "pending", "completed"
    due_date: Optional[str] = None
    user_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AddTaskParams(BaseModel):
    """Parameters for add_task tool."""
    user_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None


class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool."""
    user_id: str
    status_filter: Optional[str] = None  # "all", "pending", "completed"


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool."""
    user_id: str
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task tool."""
    user_id: str
    task_id: int


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""
    user_id: str
    task_id: int


class TodoTools:
    """Class containing all todo management tools that use the database."""

    def __init__(self, session):
        """Initialize with a database session."""
        self.session = session
        self.todo_service = TodoService(session)

    def add_task(self, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new task to the user's todo list.

        Args:
            user_id: The ID of the user creating the todo
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

            # Create new task
            new_task = self.todo_service.create_todo(
                user_id=user_id,
                title=title.strip(),
                description=description,
                due_date=due_date
            )

            # Convert to TodoItem format
            task_item = TodoItem(
                id=new_task.id,
                title=new_task.title,
                description=new_task.description,
                status=new_task.status,
                due_date=new_task.due_date,
                user_id=new_task.user_id,
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
            # Get tasks
            tasks = self.todo_service.get_todos_by_user(
                user_id=user_id,
                status_filter=status_filter
            )

            # Convert to TodoItem format
            task_items = [
                TodoItem(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    due_date=task.due_date,
                    user_id=task.user_id,
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

    def update_task(self, user_id: str, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, status: Optional[str] = None,
                   due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            due_date: New due date (optional)

        Returns:
            Dictionary with success status and updated task
        """
        try:
            # Prepare update data
            update_data = TodoUpdate(
                title=title,
                description=description,
                status=status,
                due_date=due_date
            )

            # Update the task
            updated_task = self.todo_service.update_todo(
                todo_id=task_id,
                user_id=user_id,
                update_data=update_data
            )

            if not updated_task:
                return {
                    "success": False,
                    "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                    "error_message": f"Task with ID {task_id} not found or you don't have permission to update it",
                    "recoverable": False
                }

            # Convert to TodoItem format
            task_item = TodoItem(
                id=updated_task.id,
                title=updated_task.title,
                description=updated_task.description,
                status=updated_task.status,
                due_date=updated_task.due_date,
                user_id=updated_task.user_id,
                created_at=updated_task.created_at.isoformat() if updated_task.created_at else None,
                updated_at=updated_task.updated_at.isoformat() if updated_task.updated_at else None
            )

            return {
                "success": True,
                "task": task_item.model_dump(),
                "message": f"Task {task_id} updated successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "UPDATE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def complete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to mark as completed

        Returns:
            Dictionary with success status and updated task
        """
        try:
            # Prepare update data to mark as completed
            update_data = TodoUpdate(status="completed")

            # Update the task
            updated_task = self.todo_service.update_todo(
                todo_id=task_id,
                user_id=user_id,
                update_data=update_data
            )

            if not updated_task:
                return {
                    "success": False,
                    "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                    "error_message": f"Task with ID {task_id} not found or you don't have permission to update it",
                    "recoverable": False
                }

            # Convert to TodoItem format
            task_item = TodoItem(
                id=updated_task.id,
                title=updated_task.title,
                description=updated_task.description,
                status=updated_task.status,
                due_date=updated_task.due_date,
                user_id=updated_task.user_id,
                created_at=updated_task.created_at.isoformat() if updated_task.created_at else None,
                updated_at=updated_task.updated_at.isoformat() if updated_task.updated_at else None
            )

            return {
                "success": True,
                "task": task_item.model_dump(),
                "message": f"Task {task_id} marked as completed"
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "COMPLETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def delete_task(self, user_id: str, task_id: int) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            user_id: The ID of the user
            task_id: The ID of the task to delete

        Returns:
            Dictionary with success status
        """
        try:
            # Delete the task
            success = self.todo_service.delete_todo(
                todo_id=task_id,
                user_id=user_id
            )

            if not success:
                return {
                    "success": False,
                    "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                    "error_message": f"Task with ID {task_id} not found or you don't have permission to delete it",
                    "recoverable": False
                }

            return {
                "success": True,
                "message": f"Task {task_id} deleted successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error_code": "DELETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }