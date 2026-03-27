"""
Phase II API Client

Bridges Phase III chatbot to Phase II's REST API endpoints for todo operations.
This allows the chatbot to work with the actual todo data from Phase II.

Phase II API Base URL: http://localhost:8000 (local) or production URL
Authentication: JWT Bearer token
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import httpx

logger = logging.getLogger(__name__)


class Phase2ApiClient:
    """
    HTTP client for Phase II backend todo API endpoints.

    This client calls Phase II's REST API instead of accessing the database directly,
    ensuring the chatbot works with the same todo data as the Phase II web app.
    """

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            access_token: JWT Bearer token for authentication. If None, will try to get from env.
        """
        self.base_url = os.getenv(
            "PHASE2_API_URL",
            "http://localhost:8000"
        ).rstrip("/")

        # Use provided token or try to get from environment
        self.access_token = access_token or os.getenv("PHASE2_ACCESS_TOKEN")

        logger.info(f"[Phase2ApiClient] Initialized with base_url: {self.base_url}")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        headers = {
            "Content-Type": "application/json",
        }

        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return headers

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and parse JSON.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response

        Raises:
            HTTPError: If request failed
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"[Phase2ApiClient] HTTP error: {e.response.status_code} - {e.response.text}")
            # Return error info instead of raising
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "error_message": e.response.text
            }
        except Exception as e:
            logger.error(f"[Phase2ApiClient] Request error: {str(e)}")
            return {
                "success": False,
                "error": "request_error",
                "error_message": str(e)
            }

    def list_tasks(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        List all tasks for the authenticated user.

        Args:
            status_filter: Optional status filter ("pending", "completed")

        Returns:
            Dictionary with tasks list
        """
        try:
            url = f"{self.base_url}/api/tasks"

            logger.info(f"[Phase2ApiClient] Listing tasks from {url}")

            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    url,
                    headers=self._get_headers()
                )

            tasks = self._handle_response(response)

            # If we got a list, filter by status if needed
            if isinstance(tasks, list):
                if status_filter and status_filter in ["pending", "completed"]:
                    filtered_tasks = [t for t in tasks if t.get("status") == status_filter]
                    return {
                        "success": True,
                        "tasks": filtered_tasks,
                        "total_count": len(filtered_tasks)
                    }
                return {
                    "success": True,
                    "tasks": tasks,
                    "total_count": len(tasks)
                }

            # Handle error response
            if isinstance(tasks, dict) and not tasks.get("success"):
                return tasks

            return tasks

        except Exception as e:
            logger.exception(f"[Phase2ApiClient] Error listing tasks: {str(e)}")
            return {
                "success": False,
                "error_code": "LIST_TASKS_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def add_task(self, title: str, description: Optional[str] = None,
                 due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a new task.

        Args:
            title: Task title
            description: Optional description
            due_date: Optional due date (ISO format string)

        Returns:
            Dictionary with created task
        """
        try:
            url = f"{self.base_url}/api/tasks"

            # Prepare task data
            task_data = {
                "title": title,
                "description": description,
                "due_date": due_date
            }

            # Remove None values
            task_data = {k: v for k, v in task_data.items() if v is not None}

            logger.info(f"[Phase2ApiClient] Creating task: {task_data}")

            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=task_data
                )

            result = self._handle_response(response)

            if isinstance(result, dict) and "id" in result:
                # Successfully created
                return {
                    "success": True,
                    "task": result,
                    "message": f"Task '{title}' added successfully"
                }

            # Handle error response
            if isinstance(result, dict):
                if not result.get("success"):
                    return result
                # Might be an error dict without success key
                if "error" in result:
                    return {
                        "success": False,
                        "error_code": "ADD_TASK_ERROR",
                        "error_message": result.get("error", "Unknown error"),
                        "recoverable": True
                    }

            return result

        except Exception as e:
            logger.exception(f"[Phase2ApiClient] Error adding task: {str(e)}")
            return {
                "success": False,
                "error_code": "ADD_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def update_task(self, task_id: UUID, title: Optional[str] = None,
                    description: Optional[str] = None, status: Optional[str] = None,
                    priority: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            priority: New priority (optional)
            due_date: New due date (optional)

        Returns:
            Dictionary with updated task
        """
        try:
            url = f"{self.base_url}/api/tasks/{task_id}"

            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if status is not None:
                update_data["status"] = status
            if priority is not None:
                update_data["priority"] = priority
            if due_date is not None:
                update_data["due_date"] = due_date

            logger.info(f"[Phase2ApiClient] Updating task {task_id}: {update_data}")

            with httpx.Client(timeout=30.0) as client:
                response = client.put(
                    url,
                    headers=self._get_headers(),
                    json=update_data
                )

            result = self._handle_response(response)

            if isinstance(result, dict) and "id" in result:
                # Successfully updated
                return {
                    "success": True,
                    "task": result,
                    "message": f"Task '{result.get('title')}' updated successfully"
                }

            # Handle error response
            if isinstance(result, dict):
                if "detail" in result:
                    # FastAPI error response
                    return {
                        "success": False,
                        "error_code": "UPDATE_TASK_ERROR",
                        "error_message": result.get("detail", "Unknown error"),
                        "recoverable": True
                    }

            return result

        except Exception as e:
            logger.exception(f"[Phase2ApiClient] Error updating task: {str(e)}")
            return {
                "success": False,
                "error_code": "UPDATE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def complete_task(self, task_id: UUID) -> Dict[str, Any]:
        """
        Toggle task completion status.

        Args:
            task_id: ID of the task to toggle

        Returns:
            Dictionary with updated task
        """
        try:
            url = f"{self.base_url}/api/tasks/{task_id}/complete"

            logger.info(f"[Phase2ApiClient] Toggling completion for task {task_id}")

            with httpx.Client(timeout=30.0) as client:
                response = client.patch(
                    url,
                    headers=self._get_headers()
                )

            result = self._handle_response(response)

            if isinstance(result, dict) and "id" in result:
                # Successfully toggled
                return {
                    "success": True,
                    "task": result,
                    "message": f"Task '{result.get('title')}' marked as {result.get('status')}"
                }

            # Handle error response
            if isinstance(result, dict):
                if "detail" in result:
                    # FastAPI error response
                    return {
                        "success": False,
                        "error_code": "COMPLETE_TASK_ERROR",
                        "error_message": result.get("detail", "Unknown error"),
                        "recoverable": True
                    }

            return result

        except Exception as e:
            logger.exception(f"[Phase2ApiClient] Error completing task: {str(e)}")
            return {
                "success": False,
                "error_code": "COMPLETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def delete_task(self, task_id: UUID) -> Dict[str, Any]:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete

        Returns:
            Dictionary with deletion result
        """
        try:
            url = f"{self.base_url}/api/tasks/{task_id}"

            logger.info(f"[Phase2ApiClient] Deleting task {task_id}")

            with httpx.Client(timeout=30.0) as client:
                response = client.delete(
                    url,
                    headers=self._get_headers()
                )

            result = self._handle_response(response)

            # Phase II returns {"ok": true} on successful deletion
            if isinstance(result, dict) and result.get("ok"):
                return {
                    "success": True,
                    "message": "Task deleted successfully"
                }

            # Handle error response
            if isinstance(result, dict):
                if "detail" in result:
                    # FastAPI error response
                    return {
                        "success": False,
                        "error_code": "DELETE_TASK_ERROR",
                        "error_message": result.get("detail", "Unknown error"),
                        "recoverable": True
                    }

            return result

        except Exception as e:
            logger.exception(f"[Phase2ApiClient] Error deleting task: {str(e)}")
            return {
                "success": False,
                "error_code": "DELETE_TASK_ERROR",
                "error_message": str(e),
                "recoverable": True
            }

    def find_task_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Find a task by title (for natural language lookup).

        Args:
            title: Task title to search for (supports partial matching)

        Returns:
            Task dict if found, None otherwise
        """
        try:
            # List all tasks and find matching one
            result = self.list_tasks()

            if not result.get("success"):
                return None

            tasks = result.get("tasks", [])

            # Try exact match first
            for task in tasks:
                if task.get("title", "").lower() == title.lower():
                    return task

            # Try partial match
            for task in tasks:
                if title.lower() in task.get("title", "").lower():
                    return task

            return None

        except Exception as e:
            logger.error(f"[Phase2ApiClient] Error finding task by title: {str(e)}")
            return None
