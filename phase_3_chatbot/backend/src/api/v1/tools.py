"""
Tool Execution Endpoint for ChatKit Client Tools

This endpoint handles tool execution requests from the ChatKit widget's onClientTool handler.
When using OpenAI's hosted ChatKit service, client tools are executed by calling this endpoint.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from services.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution."""
    name: str
    arguments: Dict[str, Any] = {}


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    http_request: Request,
    current_user: str = Depends(get_current_user)
):
    """
    Execute a ChatKit client tool.

    This endpoint is called by the ChatKit widget's onClientTool handler
    when using OpenAI's hosted ChatKit service.

    Supported tools:
    - add_task: Add a new task to the todo list
    - list_tasks: List all tasks or filter by status
    - update_task: Update an existing task
    - complete_task: Mark a task as completed
    - delete_task: Delete a task from the list

    Args:
        request: Tool execution request with tool name and arguments
        http_request: The FastAPI request object
        current_user: Authenticated user ID (injected)

    Returns:
        ToolExecutionResponse with success status and result data
    """
    tool_name = request.name
    parameters = request.arguments

    logger.info(f"[Tools] Executing tool '{tool_name}' for user {current_user} with params: {parameters}")

    try:
        from database.session import get_session_context
        from services.todo_tools import TodoTools

        with get_session_context() as session:
            todo_tools = TodoTools(session)

            # Inject user_id into parameters for all tools
            parameters_with_user = {**parameters, "user_id": current_user}

            # Execute the appropriate tool
            if tool_name == "add_task":
                result = todo_tools.add_task(**parameters_with_user)

            elif tool_name == "list_tasks":
                result = todo_tools.list_tasks(**parameters_with_user)

            elif tool_name == "update_task":
                result = todo_tools.update_task(**parameters_with_user)

            elif tool_name == "complete_task":
                result = todo_tools.complete_task(**parameters_with_user)

            elif tool_name == "delete_task":
                result = todo_tools.delete_task(**parameters_with_user)

            else:
                logger.warning(f"[Tools] Unknown tool requested: {tool_name}")
                return ToolExecutionResponse(
                    success=False,
                    error=f"Unknown tool: {tool_name}"
                )

            logger.info(f"[Tools] Tool '{tool_name}' completed: {result.get('success')}")
            return ToolExecutionResponse(
                success=result.get("success", False),
                data=result.get("data"),
                error=result.get("error")
            )

    except Exception as e:
        logger.exception(f"[Tools] Error executing tool '{tool_name}'")
        return ToolExecutionResponse(
            success=False,
            error=str(e)
        )


@router.get("/tools/list")
async def list_tools():
    """
    List all available client tools.

    Returns information about all tools that can be executed by the ChatKit widget.
    """
    return {
        "tools": [
            {
                "name": "add_task",
                "description": "Add a new task to the todo list",
                "parameters": {
                    "title": {"type": "string", "description": "The task title"},
                    "description": {"type": "string", "description": "Optional task description", "optional": True}
                }
            },
            {
                "name": "list_tasks",
                "description": "List all tasks or filter by status",
                "parameters": {
                    "status_filter": {"type": "string", "description": "Filter by status (pending/completed/all)", "optional": True}
                }
            },
            {
                "name": "update_task",
                "description": "Update an existing task",
                "parameters": {
                    "task_id": {"type": "string", "description": "The task ID to update"},
                    "title": {"type": "string", "description": "New task title", "optional": True},
                    "description": {"type": "string", "description": "New task description", "optional": True}
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "task_id": {"type": "string", "description": "The task ID to mark complete"}
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task from the list",
                "parameters": {
                    "task_id": {"type": "string", "description": "The task ID to delete"}
                }
            }
        ]
    }
