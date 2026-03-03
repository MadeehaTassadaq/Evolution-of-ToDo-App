"""
Todo Tools for Backend Operations

Bridges Phase III chatbot to Phase II's REST API for todo management.
Uses HTTP calls to Phase II backend instead of direct database access.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID

# Configure logging for debugging
logger = logging.getLogger(__name__)

from .phase2_api_client import Phase2ApiClient


class TodoTools:
    """
    Class containing all todo management tools that bridge to Phase II API.

    This class provides the same interface as before but now calls Phase II's
    REST API instead of accessing the database directly.
    """

    def __init__(self, session=None, access_token: Optional[str] = None):
        """
        Initialize with the Phase II API client.

        Args:
            session: Database session (kept for compatibility, but not used)
            access_token: JWT Bearer token for Phase II API authentication
        """
        self.session = session  # Kept for compatibility
        self.api_client = Phase2ApiClient(access_token=access_token)
        logger.info("[TodoTools] Initialized with Phase2ApiClient")

    def add_task(self, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new task to the user's todo list via Phase II API.

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

            # Call Phase II API
            result = self.api_client.add_task(
                title=title.strip(),
                description=description,
                due_date=due_date
            )

            return result

        except Exception as e:
            logger.exception(f"[TodoTools] Error in add_task: {str(e)}")
            return {
                "success": False,
                "error_code": "ADD_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def list_tasks(self, user_id: str, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        List tasks for the authenticated user via Phase II API.

        Args:
            user_id: The ID of the user (Phase II API extracts from token)
            status_filter: Optional status filter ("all", "pending", "completed")

        Returns:
            Dictionary with success status and list of tasks
        """
        try:
            # Call Phase II API
            result = self.api_client.list_tasks(status_filter=status_filter)

            return result

        except Exception as e:
            logger.exception(f"[TodoTools] Error in list_tasks: {str(e)}")
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
        Update an existing task by ID or title via Phase II API.

        Args:
            user_id: The ID of the user (Phase II API extracts from token)
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

            target_task_id = task_id

            # If task_title provided, look up by title first
            if task_title and not task_id:
                task = self.api_client.find_task_by_title(task_title)
                if not task:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND",
                        "error_message": f"No task found matching '{task_title}'",
                        "recoverable": False
                    }
                target_task_id = UUID(task.get("id"))

            # Convert task_id to UUID if it's a string
            if isinstance(target_task_id, str):
                try:
                    target_task_id = UUID(target_task_id)
                except ValueError:
                    return {
                        "success": False,
                        "error_code": "VALIDATION_ERROR",
                        "error_message": f"Invalid task_id format: {task_id}. Expected UUID.",
                        "recoverable": False
                    }

            # Call Phase II API
            result = self.api_client.update_task(
                task_id=target_task_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                due_date=due_date
            )

            return result

        except Exception as e:
            logger.exception(f"[TodoTools] Error in update_task: {str(e)}")
            return {
                "success": False,
                "error_code": "UPDATE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def complete_task(self, user_id: str, task_id: UUID = None, task_title: str = None) -> Dict[str, Any]:
        """
        Mark a task as completed by ID or title via Phase II API.

        Args:
            user_id: The ID of the user (Phase II API extracts from token)
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

            target_task_id = task_id

            # If task_title provided, look up by title first
            if task_title and not task_id:
                task = self.api_client.find_task_by_title(task_title)
                if not task:
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND",
                        "error_message": f"No task found matching '{task_title}'",
                        "recoverable": False
                    }
                target_task_id = UUID(task.get("id"))

            # Convert task_id to UUID if it's a string
            if isinstance(target_task_id, str):
                try:
                    target_task_id = UUID(target_task_id)
                except ValueError:
                    return {
                        "success": False,
                        "error_code": "VALIDATION_ERROR",
                        "error_message": f"Invalid task_id format: {task_id}. Expected UUID.",
                        "recoverable": False
                    }

            # Call Phase II API
            result = self.api_client.complete_task(task_id=target_task_id)

            return result

        except Exception as e:
            logger.exception(f"[TodoTools] Error in complete_task: {str(e)}")
            return {
                "success": False,
                "error_code": "COMPLETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def delete_task(self, user_id: str, task_id: UUID = None, task_title: str = None) -> Dict[str, Any]:
        """
        Delete a task by ID or title via Phase II API.

        Args:
            user_id: The ID of the user (Phase II API extracts from token)
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

            target_task_id = task_id
            deleted_task_title = task_title  # Store for success message

            # If task_title provided, look up by title first
            if task_title and not task_id:
                logger.info(f"Looking up task by title: '{task_title}'")
                task = self.api_client.find_task_by_title(task_title)
                if not task:
                    logger.warning(f"Task not found with title: '{task_title}'")
                    return {
                        "success": False,
                        "error_code": "TASK_NOT_FOUND",
                        "error_message": f"No task found matching '{task_title}'",
                        "recoverable": False
                    }
                target_task_id = UUID(task.get("id"))
                deleted_task_title = task.get("title", task_title)
                logger.info(f"Found task by title: {target_task_id}")

            # Convert task_id to UUID if it's a string
            if isinstance(target_task_id, str):
                try:
                    target_task_id = UUID(target_task_id)
                except ValueError:
                    logger.error(f"Invalid task_id format: {target_task_id}")
                    return {
                        "success": False,
                        "error_code": "VALIDATION_ERROR",
                        "error_message": f"Invalid task_id format: {target_task_id}. Expected UUID.",
                        "recoverable": False
                    }

            logger.info(f"Deleting task: {target_task_id}")

            # Call Phase II API
            result = self.api_client.delete_task(task_id=target_task_id)

            # Update success message with task title
            if result.get("success") and deleted_task_title:
                result["message"] = f"Task '{deleted_task_title}' deleted successfully"

            return result

        except Exception as e:
            logger.exception(f"[TodoTools] Error in delete_task: {str(e)}")
            return {
                "success": False,
                "error_code": "DELETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }