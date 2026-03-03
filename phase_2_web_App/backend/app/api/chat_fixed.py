"""
Chat API endpoints - Fixed version using working custom SSE format

This uses a simpler custom approach that matches what @openai/chatkit-react expects.
"""

import logging
import json
from typing import AsyncIterator
from datetime import datetime, timezone
import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from ..middleware.auth import get_current_user_from_request
from ..database import get_session
from ..models.user import User
from ..models.task import Task

from openai import OpenAI
import os

router = APIRouter(prefix="/v1", tags=["chat"])
logger = logging.getLogger(__name__)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def utc_now():
    return datetime.now(timezone.utc)


def _to_iso_format(dt: datetime) -> str:
    """Convert datetime to ISO format string."""
    return dt.isoformat().replace("+00:00", "Z")


@router.post("/chatkit")
async def chatkit_streaming_endpoint(
    request: Request,
    current_user: dict = Depends(get_current_user_from_request),
    db: Session = Depends(get_session)
):
    """
    ChatKit streaming endpoint.

    Compatible with @openai/chatkit-react widget.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    logger.info(f"[ChatKit] Request from user_id={user_id}, email={user.email}")

    request_body = await request.body()
    logger.info(f"[ChatKit] Request body: {request_body[:200]}...")

    try:
        request_data = json.loads(request_body.decode())
    except:
        request_data = {}

    request_type = request_data.get("type", "")
    logger.info(f"[ChatKit] Request type: {request_type}")

    # Extract user message
    user_message = ""
    if request_type == "threads.create":
        params = request_data.get("params", {})
        input_data = params.get("input", {})
        content_list = input_data.get("content", [])
        for content_item in content_list:
            if content_item.get("type") == "input_text":
                user_message = content_item.get("text", "")
                break

    thread_id = request_data.get("thread_id") or str(uuid_lib.uuid4())

    async def event_stream():
        """Yield SSE events in the format ChatKit React expects."""

        # Helper to yield SSE event
        def yield_event(data: dict):
            json_str = json.dumps(data, separators=(',', ':'))
            return f"data: {json_str}\n\n"

        # Send thread.created event first (required for new threads)
        yield yield_event({
            "type": "thread.created",
            "thread": {
                "id": thread_id,
                "created_at": _to_iso_format(utc_now()),
                "title": None,
                "metadata": {}
            }
        })

        # If no message, send greeting
        if not user_message:
            greeting = (
                "Hi! I'm your Todo AI Assistant. I can help you:\n\n"
                "• Add a new task\n"
                "• Show your tasks\n"
                "• Update a task\n"
                "• Mark a task complete\n"
                "• Delete a task\n\n"
                "What would you like to do?"
            )

            msg_id = str(uuid_lib.uuid4())

            # Yield greeting as thread.item.done event with item included
            yield yield_event({
                "type": "thread.item.done",
                "item": {
                    "id": msg_id,
                    "thread_id": thread_id,
                    "type": "assistant_message",
                    "role": "assistant",
                    "content": [{
                        "type": "output_text",
                        "text": greeting,
                        "annotations": []
                    }],
                    "created_at": _to_iso_format(utc_now())
                }
            })

            # Send response.end event
            yield yield_event({
                "type": "response.end",
                "response": {
                    "id": f"resp_{msg_id}",
                    "thread_id": thread_id,
                    "status": "completed"
                }
            })
            return

        # Get tasks context
        try:
            tasks = db.exec(select(Task).where(Task.user_id == user_id).limit(10)).all()
            task_context = ""
            if tasks:
                task_context = "\n\nRecent tasks:\n" + "\n".join([
                    f"- {t.title} (Status: {t.status}, ID: {t.id})"
                    for t in tasks
                ])
        except Exception as e:
            logger.exception(f"[ChatKit] Error loading tasks")
            task_context = ""

        # Build OpenAI messages
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful todo management assistant.

User ID: {user_id}{task_context}

Available tools:
1. add_task(title: str, description: str = None) - Add a new task
2. list_tasks(status: str = None) - List all tasks
3. complete_task(task_id: str) - Mark a task as completed
4. delete_task(task_id: str) - Delete a task

Use tools in format: TOOL:<tool_name>:<json_parameters>"""
            },
            {"role": "user", "content": user_message}
        ]

        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Add a new task",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List all tasks",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "enum": ["pending", "completed", "all"]}
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark task as completed",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {"type": "string"}
                            },
                            "required": ["task_id"]
                        }
                    }
                },
            ],
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        final_response = ""

        # Execute tools
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                try:
                    if function_name == "add_task":
                        new_task = Task(
                            title=function_args.get("title", "Untitled"),
                            description=function_args.get("description", ""),
                            user_id=user_id,
                            status="pending"
                        )
                        db.add(new_task)
                        db.commit()
                        db.refresh(new_task)
                        result = f"✅ Added task: {new_task.title}"

                    elif function_name == "list_tasks":
                        status_filter = function_args.get("status")
                        statement = select(Task).where(Task.user_id == user_id)
                        if status_filter and status_filter != "all":
                            statement = statement.where(Task.status == status_filter)
                        tasks = db.exec(statement).all()

                        if tasks:
                            task_list = "\n".join([f"• {t.title} ({t.status})" for t in tasks])
                            result = f"📋 Your tasks:\n{task_list}"
                        else:
                            result = "📋 No tasks found"

                    elif function_name == "complete_task":
                        task_id = function_args.get("task_id")
                        task = db.get(Task, task_id)
                        if task and task.user_id == user_id:
                            task.status = "completed"
                            db.commit()
                            result = f"✅ Completed task: {task.title}"
                        else:
                            result = "❌ Task not found"

                    else:
                        result = f"❓ Unknown tool: {function_name}"

                except Exception as e:
                    logger.exception(f"[ChatKit] Error executing {function_name}")
                    result = f"❌ Error: {str(e)}"

                final_response = result
        else:
            final_response = assistant_message.content or "How can I help you with your tasks?"

        # Yield assistant message as thread.item.done event (with item included)
        # This is what the official ChatKit SDK does
        msg_id = str(uuid_lib.uuid4())

        yield yield_event({
            "type": "thread.item.done",
            "item": {
                "id": msg_id,
                "thread_id": thread_id,
                "type": "assistant_message",
                "role": "assistant",
                "content": [{
                    "type": "output_text",
                    "text": final_response,
                    "annotations": []
                }],
                "created_at": _to_iso_format(utc_now())
            }
        })

        # Send response.end event to signal completion
        yield yield_event({
            "type": "response.end",
            "response": {
                "id": f"resp_{msg_id}",
                "thread_id": thread_id,
                "status": "completed"
            }
        })

        logger.info(f"[ChatKit] Completed response for thread {thread_id}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
