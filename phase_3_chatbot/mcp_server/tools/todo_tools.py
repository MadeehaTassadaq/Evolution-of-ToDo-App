"""
MCP Tools for Todo Operations
Standardized tools for todo management operations via Model Context Protocol
"""

from mcp.server.exceptions import McpError
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import database models and services
from database.models.todo import Todo, TodoCreate, TodoUpdate
from database.session import get_session_context
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


def register_tools(server):
    """Register all tools with the server."""

    @server.tool("add_task")
    async def add_task(params: AddTaskParams) -> Dict[str, Any]:
        """
        Add a new task to the user's todo list.

        Args:
            params: Parameters including user_id, title, and optional description/due_date

        Returns:
            Dictionary with success status and task information
        """
        try:
            # Validate input
            if not params.title or not params.title.strip():
                raise McpError("Title is required for the task")

            # Get a database session
            async with get_session_context() as session:
                # Create todo service
                todo_service = TodoService(session)

                # Create new task
                new_task = todo_service.create_todo(
                    user_id=params.user_id,
                    title=params.title.strip(),
                    description=params.description,
                    due_date=params.due_date
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
                    "message": f"Task '{params.title}' added successfully"
                }

        except Exception as e:
            return {
                "success": False,
                "error_code": "ADD_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }


    @server.tool("list_tasks")
    async def list_tasks(params: ListTasksParams) -> Dict[str, Any]:
        """
        List tasks for a specific user.

        Args:
            params: Parameters including user_id and optional status filter

        Returns:
            Dictionary with success status and list of tasks
        """
        try:
            # Get a database session
            async with get_session_context() as session:
                # Create todo service
                todo_service = TodoService(session)

                # Get tasks
                tasks = todo_service.get_todos_by_user(
                    user_id=params.user_id,
                    status_filter=params.status_filter
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


    @server.tool("update_task")
    async def update_task(params: UpdateTaskParams) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            params: Parameters including user_id, task_id, and optional fields to update

        Returns:
            Dictionary with success status and updated task
        """
        try:
            # Get a database session
            async with get_session_context() as session:
                # Create todo service
                todo_service = TodoService(session)

                # Prepare update data
                update_data = TodoUpdate(
                    title=params.title,
                    description=params.description,
                    status=params.status,
                    due_date=params.due_date
                )

                # Update the task
                updated_task = todo_service.update_todo(
                    todo_id=params.task_id,
                    user_id=params.user_id,
                    update_data=update_data
                )

                if not updated_task:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                        "error_message": f"Task with ID {params.task_id} not found or you don't have permission to update it",
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
                    "message": f"Task {params.task_id} updated successfully"
                }

        except Exception as e:
            return {
                "success": False,
                "error_code": "UPDATE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }


    @server.tool("complete_task")
    async def complete_task(params: CompleteTaskParams) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            params: Parameters including user_id and task_id

        Returns:
            Dictionary with success status and updated task
        """
        try:
            # Get a database session
            async with get_session_context() as session:
                # Create todo service
                todo_service = TodoService(session)

                # Prepare update data to mark as completed
                update_data = TodoUpdate(status="completed")

                # Update the task
                updated_task = todo_service.update_todo(
                    todo_id=params.task_id,
                    user_id=params.user_id,
                    update_data=update_data
                )

                if not updated_task:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                        "error_message": f"Task with ID {params.task_id} not found or you don't have permission to update it",
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
                    "message": f"Task {params.task_id} marked as completed"
                }

        except Exception as e:
            return {
                "success": False,
                "error_code": "COMPLETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }


    @server.tool("delete_task")
    async def delete_task(params: DeleteTaskParams) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            params: Parameters including user_id and task_id

        Returns:
            Dictionary with success status
        """
        try:
            # Get a database session
            async with get_session_context() as session:
                # Create todo service
                todo_service = TodoService(session)

                # Delete the task
                success = todo_service.delete_todo(
                    todo_id=params.task_id,
                    user_id=params.user_id
                )

                if not success:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND_OR_PERMISSION_DENIED",
                        "error_message": f"Task with ID {params.task_id} not found or you don't have permission to delete it",
                        "recoverable": False
                    }

                return {
                    "success": True,
                    "message": f"Task {params.task_id} deleted successfully"
                }

        except Exception as e:
            return {
                "success": False,
                "error_code": "DELETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }