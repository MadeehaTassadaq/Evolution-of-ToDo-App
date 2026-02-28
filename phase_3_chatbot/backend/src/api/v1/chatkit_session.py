"""
ChatKit Session Endpoint for OpenAI-Hosted Backend

This endpoint creates ChatKit sessions using OpenAI's hosted backend.
The frontend uses the getClientSecret pattern to obtain session tokens.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os

router = APIRouter()

# OpenAI client for ChatKit sessions
# Note: ChatKit support requires openai>=1.0.0
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SessionResponse(BaseModel):
    """Response model for session creation."""
    client_secret: str


@router.post("/chatkit/session", response_model=SessionResponse)
async def create_chatkit_session(request: Request):
    """
    Create a ChatKit session using OpenAI's hosted backend.

    This endpoint is called by the frontend to obtain a client secret
    that can be used with the ChatKit widget.

    The client secret contains:
    - The session token
    - Expiration time
    - User identification

    Returns:
        SessionResponse with client_secret that the frontend can use
    """
    if not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="OpenAI package not available. Please install: pip install 'openai>=1.0.0'"
        )

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY not configured"
        )

    # Get authenticated user from request state (set by auth middleware)
    # For now, we'll use a simple user ID
    user_id = getattr(request.state, "user_id", None) or "default_user"

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Create a ChatKit session
        # Note: This uses the OpenAI ChatKit API which provides
        # hosted chat server with tool calling support
        session = client.chatkit.sessions.create(
            user={
                "id": user_id,
                "name": f"User {user_id}",
            },
            # Configure tools that the assistant can use
            tools=[
                {
                    "type": "function",
                    "name": "add_task",
                    "description": "Add a new task to the todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description"
                            }
                        },
                        "required": ["title"]
                    }
                },
                {
                    "type": "function",
                    "name": "list_tasks",
                    "description": "List all tasks or filter by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status_filter": {
                                "type": "string",
                                "enum": ["pending", "completed", "all"],
                                "description": "Filter tasks by status"
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The task ID to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description"
                            }
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "type": "function",
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The task ID to mark complete"
                            }
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "type": "function",
                    "name": "delete_task",
                    "description": "Delete a task from the list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The task ID to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            ]
        )

        return SessionResponse(client_secret=session.client_secret)

    except Exception as e:
        # If ChatKit API is not available, raise an error
        if "chatkit" in str(e).lower() or "sessions" in str(e).lower():
            raise HTTPException(
                status_code=501,
                detail=(
                    "ChatKit API not available. The OpenAI Python SDK may need to be updated. "
                    "Please ensure you have the latest version: pip install --upgrade openai"
                )
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create ChatKit session: {str(e)}"
        )


@router.get("/chatkit/session/health")
async def session_health_check():
    """Health check for the session endpoint."""
    return {
        "status": "available",
        "openai_available": OPENAI_AVAILABLE,
        "endpoint": "/api/chatkit/session"
    }
