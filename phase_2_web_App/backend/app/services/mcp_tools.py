"""
MCP-compatible stateless tools for Todo ChatKit integration.

These tools follow MCP patterns:
- Stateless functions with explicit parameters
- Database-backed persistence
- User-scoped operations
- Pure function semantics (no hidden state)

NOTE: When using function_tool decorator, ToolContext must be the first parameter.

NATURAL LANGUAGE TASK REFERENCES:
All tools now support natural language references instead of requiring task IDs.
Users can reference tasks by:
- Exact title: "complete the buy groceries task"
- Partial title: "delete the groceries task"
- Position: "complete the first task", "mark the last task as done"
- Recent: "complete the task I just added"
- UUID (backward compatibility): "complete task abc-123"
"""

import logging
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select
from agents import function_tool
from agents.tool_context import ToolContext

from ..models.task import Task
from .task_resolver import resolve_task_reference

logger = logging.getLogger(__name__)


# ============================================================================
# MCP Tools - Stateless, Database-Backed Functions
# ============================================================================

@function_tool
async def add_task(
    context: ToolContext,
    title: str,
    description: Optional[str] = None,
) -> str:
    """
    Add a new task to the user's todo list.

    Args:
        context: ToolContext containing agent run context (must be first param)
        title: The task title (required)
        description: Optional task description

    Returns:
        Confirmation message with task details
    """
    # Get user_id and database session from context
    request_context = context.context
    user_id = request_context.get("user_id")
    db = request_context.get("db")

    if not user_id or not db:
        logger.error("[MCP:add_task] Missing user_id or db in context")
        return "❌ Error: Authentication required"

    # Create new task
    new_task = Task(
        title=title,
        description=description or "",
        user_id=user_id,
        status="pending"
    )

    try:
        from datetime import datetime, timezone

        # Set timestamps
        new_task.created_at = datetime.now(timezone.utc)
        new_task.updated_at = datetime.now(timezone.utc)

        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        logger.info(f"[MCP:add_task] Created task {new_task.id} for user {user_id}")
        return f"✅ Added task: {new_task.title}"
    except Exception as e:
        logger.exception(f"[MCP:add_task] Error creating task: {e}")
        db.rollback()
        return f"❌ Error adding task: {str(e)}"


@function_tool
async def list_tasks(
    context: ToolContext,
    status_filter: Optional[str] = None,
) -> str:
    """
    List all tasks or filter by status.

    Args:
        context: ToolContext containing agent run context (must be first param)
        status_filter: Optional filter by status ("pending", "completed", or "all")

    Returns:
        Formatted list of tasks with position numbers for easy natural language reference
    """
    request_context = context.context
    user_id = request_context.get("user_id")
    db = request_context.get("db")

    if not user_id or not db:
        logger.error("[MCP:list_tasks] Missing user_id or db in context")
        return "❌ Error: Authentication required"

    try:
        statement = select(Task).where(Task.user_id == user_id)

        # Apply status filter if provided
        if status_filter and status_filter.lower() != "all":
            statement = statement.where(Task.status == status_filter.lower())

        tasks = db.exec(statement.order_by(Task.created_at.desc())).all()

        if not tasks:
            status_desc = f" ({status_filter})" if status_filter else ""
            return f"📋 No tasks found{status_desc}"

        # Format task list with position numbers for natural language reference
        # Position 1 is the most recent (top of list)
        task_list = []
        for i, t in enumerate(tasks, 1):
            status_emoji = "✅" if t.status == "completed" else "📝"
            task_list.append(
                f"{i}. {status_emoji} {t.title}"
            )

        logger.info(f"[MCP:list_tasks] Listed {len(tasks)} tasks for user {user_id}")
        status_info = f" ({status_filter})" if status_filter else ""

        # Add helpful hint about referencing tasks
        hint = "\n\n💡 Tip: You can reference tasks by title (e.g., 'complete the groceries task'), position (e.g., 'complete the first task'), or say 'last' for the most recent task."

        return f"📋 Your tasks{status_info}:\n\n" + "\n".join(task_list) + hint

    except Exception as e:
        logger.exception(f"[MCP:list_tasks] Error listing tasks: {e}")
        return f"❌ Error listing tasks: {str(e)}"


@function_tool
async def update_task(
    context: ToolContext,
    task_reference: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    Update a task's title, description, or status.

    Args:
        context: ToolContext containing agent run context (must be first param)
        task_reference: The task to update - can be natural language (title, position like "first"/"last"/"recent") or task ID
        title: New title (optional)
        description: New description (optional)
        status: New status: "pending" or "completed" (optional)

    Returns:
        Confirmation message with updated task details

    Examples:
        - update_task(task_reference="groceries", title="Buy groceries for mom")
        - update_task(task_reference="first task", status="completed")
        - update_task(task_reference="last", description="Call mom about dinner")
    """
    request_context = context.context
    user_id = request_context.get("user_id")
    db = request_context.get("db")

    if not user_id or not db:
        logger.error("[MCP:update_task] Missing user_id or db in context")
        return "❌ Error: Authentication required"

    # Clean up task reference - remove any extra formatting
    task_reference = task_reference.strip().strip('\'"').strip('`')

    # Use task resolver to find the task
    resolution = await resolve_task_reference(
        db=db,
        user_id=user_id,
        reference=task_reference,
        intent="update"
    )

    # Handle disambiguation
    if resolution.disambiguation_message:
        return resolution.disambiguation_message

    # Handle errors
    if resolution.error:
        return resolution.error

    # Get the task
    task = resolution.task
    if not task or task.user_id != user_id:
        logger.warning(f"[MCP:update_task] Task {task_reference} not found for user {user_id}")
        return f"❌ Task not found"

    try:
        from datetime import datetime, timezone

        # Track what was changed
        changes = []

        # Update fields if provided
        if title is not None and title != task.title:
            old_title = task.title
            task.title = title
            changes.append(f"title to '{title}'")

        if description is not None and description != task.description:
            task.description = description
            changes.append(f"description")

        if status is not None:
            if status.lower() in ["pending", "completed"]:
                old_status = task.status
                if old_status != status.lower():
                    task.status = status.lower()
                    changes.append(f"status to '{status.lower()}'")
            else:
                return f"❌ Invalid status: {status}. Use 'pending' or 'completed'"

        if not changes:
            return f"ℹ️ No changes made to task: {task.title}"

        task.updated_at = datetime.now(timezone.utc)  # Update timestamp
        db.commit()
        db.refresh(task)

        # Build response with changes
        change_desc = ", ".join(changes)
        logger.info(f"[MCP:update_task] Updated task {task.id} for user {user_id} using {resolution.strategy_used}")
        return f"✅ Updated task: {task.title} ({change_desc})"

    except Exception as e:
        logger.exception(f"[MCP:update_task] Error updating task: {e}")
        db.rollback()
        return f"❌ Error updating task: {str(e)}"


@function_tool
async def complete_task(
    context: ToolContext,
    task_reference: str,
) -> str:
    """
    Mark a task as completed.

    Args:
        context: ToolContext containing agent run context (must be first param)
        task_reference: The task to complete - can be natural language (title, position like "first"/"last"/"recent") or task ID

    Returns:
        Confirmation message

    Examples:
        - complete_task(task_reference="buy groceries") - matches task by title
        - complete_task(task_reference="first task") - completes the first (top) task
        - complete_task(task_reference="last task") - completes the most recent task
        - complete_task(task_reference="abc-123") - backward compatible with task IDs
    """
    request_context = context.context
    user_id = request_context.get("user_id")
    db = request_context.get("db")

    if not user_id or not db:
        logger.error("[MCP:complete_task] Missing user_id or db in context")
        return "❌ Error: Authentication required"

    # Clean up task reference - remove any extra formatting
    task_reference = task_reference.strip().strip('\'"').strip('`')

    # Use task resolver to find the task
    resolution = await resolve_task_reference(
        db=db,
        user_id=user_id,
        reference=task_reference,
        intent="complete"
    )

    # Handle disambiguation
    if resolution.disambiguation_message:
        return resolution.disambiguation_message

    # Handle errors
    if resolution.error:
        return resolution.error

    # Get the task
    task = resolution.task
    if not task or task.user_id != user_id:
        logger.warning(f"[MCP:complete_task] Task {task_reference} not found for user {user_id}")
        return f"❌ Task not found"

    try:
        from datetime import datetime, timezone

        old_status = task.status
        if old_status == "completed":
            return f"ℹ️ Task '{task.title}' is already completed!"

        task.status = "completed"
        task.updated_at = datetime.now(timezone.utc)  # Update timestamp
        db.commit()
        db.refresh(task)
        logger.info(f"[MCP:complete_task] Completed task {task.id} for user {user_id} using {resolution.strategy_used}")
        return f"✅ Completed task: {task.title}"
    except Exception as e:
        logger.exception(f"[MCP:complete_task] Error completing task: {e}")
        db.rollback()
        return f"❌ Error completing task: {str(e)}"


@function_tool
async def delete_task(
    context: ToolContext,
    task_reference: str,
) -> str:
    """
    Delete a task from the user's todo list.

    Args:
        context: ToolContext containing agent run context (must be first param)
        task_reference: The task to delete - can be natural language (title, position like "first"/"last"/"recent") or task ID

    Returns:
        Confirmation message

    Examples:
        - delete_task(task_reference="groceries") - deletes task by title
        - delete_task(task_reference="first task") - deletes the first (top) task
        - delete_task(task_reference="last") - deletes the most recent task
        - delete_task(task_reference="abc-123") - backward compatible with task IDs
    """
    request_context = context.context
    user_id = request_context.get("user_id")
    db = request_context.get("db")

    if not user_id or not db:
        logger.error("[MCP:delete_task] Missing user_id or db in context")
        return "❌ Error: Authentication required"

    # Clean up task reference - remove any extra formatting
    task_reference = task_reference.strip().strip('\'"').strip('`')

    # Use task resolver to find the task
    resolution = await resolve_task_reference(
        db=db,
        user_id=user_id,
        reference=task_reference,
        intent="delete"
    )

    # Handle disambiguation
    if resolution.disambiguation_message:
        return resolution.disambiguation_message

    # Handle errors
    if resolution.error:
        return resolution.error

    # Get the task
    task = resolution.task
    if not task or task.user_id != user_id:
        logger.warning(f"[MCP:delete_task] Task {task_reference} not found for user {user_id}")
        return "❌ Task not found"

    try:
        title = task.title
        # Store the task info before deletion
        task_info = {"title": title, "id": str(task.id), "status": task.status}
        db.delete(task)
        db.commit()
        logger.info(f"[MCP:delete_task] Deleted task {task.id} for user {user_id} using {resolution.strategy_used}")
        return f"🗑️ Deleted task: {title}"
    except Exception as e:
        logger.exception(f"[MCP:delete_task] Error deleting task: {e}")
        db.rollback()
        return f"❌ Error deleting task: {str(e)}"


# ============================================================================
# Tools Export List
# ============================================================================

MCP_TOOLS = [
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
]
