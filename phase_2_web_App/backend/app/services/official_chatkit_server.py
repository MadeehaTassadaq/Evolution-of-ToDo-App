"""
Official ChatKit Server using openai-chatkit Python SDK

This extends ChatKitServer and implements the respond() method properly
to work with the official @openai/chatkit-react frontend library.
"""

import json
import logging
from typing import Any, AsyncIterator
from datetime import datetime, timezone

from chatkit.server import ChatKitServer
from chatkit.agents import stream_agent_response, AgentContext
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    ThreadItemDoneEvent,
    AssistantMessageItem,
    AssistantMessageContent,
)
from openai import OpenAI
from sqlmodel import Session, select

from ..models.user import User
from ..models.task import Task

logger = logging.getLogger(__name__)


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class TodoChatKitServer(ChatKitServer[dict]):
    """
    Official ChatKit server for Todo AI Assistant.

    Extends ChatKitServer from openai-chatkit package.
    """

    def __init__(self):
        """Initialize the ChatKit server with minimal store."""
        # Create a simple in-memory store for thread management
        from chatkit.store import InMemoryStore
        from chatkit.attachment_store import InMemoryAttachmentStore

        super().__init__(
            data_store=InMemoryStore(),
            attachment_store=InMemoryAttachmentStore()
        )
        self.openai_client = OpenAI()
        logger.info("[ChatKitServer] Initialized with official ChatKit SDK")

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process user message and stream response events.

        This is the main method that ChatKitServer calls.
        It must yield ThreadStreamEvent objects.
        """
        # Get user info from context
        user_id = context.get("user_id")
        db = context.get("db")

        if not user_id or not db:
            logger.error("[ChatKitServer] Missing user_id or db in context")
            yield self._error_event("Authentication required")
            return

        user = db.get(User, user_id)
        if not user:
            yield self._error_event("User not found")
            return

        # Extract user message
        user_message = ""
        if item and item.content:
            for content in item.content:
                if hasattr(content, 'text'):
                    user_message = content.text
                    break

        logger.info(f"[ChatKitServer] Processing message from {user.email}: {user_message[:50]}")

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

            assistant_id = self.store.generate_item_id("msg", thread, context)
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=assistant_id,
                    thread_id=thread.id,
                    created_at=utc_now(),
                    content=[
                        AssistantMessageContent(
                            type="output_text",
                            text=greeting,
                            annotations=[]
                        )
                    ],
                )
            )
            return

        # Get user's tasks for context
        try:
            tasks = db.exec(select(Task).where(Task.user_id == user_id).limit(10)).all()
            task_context = ""
            if tasks:
                task_context = "\n\nRecent tasks:\n" + "\n".join([
                    f"- {t.title} (Status: {t.status}, ID: {t.id})"
                    for t in tasks
                ])
        except Exception as e:
            logger.exception(f"[ChatKitServer] Error loading tasks")
            task_context = ""

        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful todo management assistant. You help users manage their tasks through natural language.

The user's ID is: {user_id}{task_context}

Available tools you can use:
1. add_task(title: str, description: str = None) - Add a new task
2. list_tasks(status: str = None) - List all tasks or filter by status
3. update_task(task_id: str, title: str = None, description: str = None, status: str = None) - Update a task
4. complete_task(task_id: str) - Mark a task as completed
5. delete_task(task_id: str) - Delete a task

When you need to use a tool, respond with a tool call in this format:
TOOL:<tool_name>:<json_parameters>

After executing a tool, report the result to the user in a friendly way.

Always be concise and helpful."""
            }
        ]

        messages.append({"role": "user", "content": user_message})

        # Call OpenAI API
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Add a new task to the user's todo list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "The task title"},
                                "description": {"type": "string", "description": "Optional description"}
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List all tasks or filter by status",
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
                        "description": "Mark a task as completed",
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

        # Execute tool calls
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
                    logger.exception(f"[ChatKitServer] Error executing {function_name}")
                    result = f"❌ Error: {str(e)}"

                final_response = result

        else:
            final_response = assistant_message.content or "I understand. How can I help you with your tasks?"

        # Yield the assistant message
        assistant_id = self.store.generate_item_id("msg", thread, context)
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=assistant_id,
                thread_id=thread.id,
                created_at=utc_now(),
                content=[
                    AssistantMessageContent(
                        type="output_text",
                        text=final_response,
                        annotations=[]
                    )
                ],
            )
        )

        logger.info(f"[ChatKitServer] Completed response for thread {thread.id}")

    def _error_event(self, message: str) -> ThreadStreamEvent:
        """Create an error event."""
        from chatkit.types import ErrorEvent, ErrorCode
        return ErrorEvent(
            code=ErrorCode.STREAM_ERROR,
            message=message,
            allow_retry=False
        )

