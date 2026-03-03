"""
ChatKit Server for Phase II Backend

Implements the ChatKit server using OpenAI for AI logic and direct
database access for todo operations (stateless architecture).
"""

import logging
import os
from typing import Any, AsyncIterator, Dict, Optional
from datetime import datetime, timezone

from chatkit.server import ChatKitServer
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadCreatedEvent,
)
from chatkit.store import Store
from openai import OpenAI

from ..models.task import Task
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class TodoChatKitServer(ChatKitServer[Dict[str, Any]]):
    """
    ChatKit Server for Todo AI Chatbot.

    This server integrates OpenAI for natural language processing with
    direct database access for todo operations (stateless architecture).
    """

    def __init__(self, store: Store[Dict[str, Any]]):
        """Initialize the ChatKit server with store and OpenAI client."""
        super().__init__(store=store)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("[TodoChatKitServer] Initialized with OpenAI client")

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: Optional[UserMessageItem],
        context: Dict[str, Any]
    ) -> AsyncIterator:
        """
        Respond to a user message.

        Args:
            thread: The thread metadata
            input_user_message: The user's message (optional for greeting)
            context: Request context with user_id, email, and db session

        Yields:
            ChatKit events (ThreadItemDoneEvent, ThreadCreatedEvent)
        """
        user_id = context.get("user_id")
        db: Session = context.get("db")

        if not db:
            logger.error("[TodoChatKitServer] No database session in context")
            yield self._error_response("Database session not available")
            return

        logger.info(f"[TodoChatKitServer] Processing message for user {user_id}")

        # Extract user message text
        user_message_text = ""
        if input_user_message:
            for content_part in input_user_message.content:
                if hasattr(content_part, "text"):
                    user_message_text += content_part.text

        # If no message, send greeting
        if not user_message_text:
            greeting = (
                "Hi! I'm your Todo AI Assistant. I can help you:\n\n"
                "• Add a new task\n"
                "• Show your tasks\n"
                "• Update a task\n"
                "• Mark a task complete\n"
                "• Delete a task\n\n"
                "What would you like to do?"
            )
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id(thread, context),
                    thread_id=thread.id,
                    created_at=utc_now(),
                    content=[{"type": "text", "text": greeting}],
                )
            )
            return

        # Get user's recent tasks for context
        try:
            tasks = db.exec(select(Task).where(Task.user_id == user_id).limit(10)).all()
            task_context = ""
            if tasks:
                task_context = "\n\nRecent tasks:\n" + "\n".join([
                    f"- {t.title} (Status: {t.status}, ID: {t.id})"
                    for t in tasks
                ])
        except Exception as e:
            logger.exception(f"[TodoChatKitServer] Error loading tasks: {e}")
            task_context = ""

        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful todo management assistant. You help users manage their tasks through natural language.

The user's ID is: {user_id}{task_context}

Available tools you can use:
1. add_task(title: str, description: str = None) - Add a new task
2. list_tasks(status: str = None) - List all tasks or filter by status (pending/completed)
3. update_task(task_id: str, title: str = None, description: str = None, status: str = None) - Update a task
4. complete_task(task_id: str) - Mark a task as completed
5. delete_task(task_id: str) - Delete a task

When you need to use a tool, respond with a tool call in this format:
TOOL:<tool_name>:<json_parameters>

For example:
TOOL:add_task:{{"title": "Buy groceries", "description": "Go to the store"}}

After executing a tool, report the result to the user in a friendly way.

Always be concise and helpful. If the user asks to show tasks, use the list_tasks tool."""
            }
        ]

        # Add user message
        messages.append({"role": "user", "content": user_message_text})

        # Call OpenAI API
        try:
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
                                    "status": {"type": "string", "enum": ["pending", "completed", "all"], "description": "Filter by status"}
                                }
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "update_task",
                            "description": "Update an existing task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The task ID"},
                                    "title": {"type": "string", "description": "New title"},
                                    "description": {"type": "string", "description": "New description"},
                                    "status": {"type": "string", "enum": ["pending", "completed"], "description": "New status"}
                                },
                                "required": ["task_id"]
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
                                    "task_id": {"type": "string", "description": "The task ID"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "delete_task",
                            "description": "Delete a task",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string", "description": "The task ID"}
                                },
                                "required": ["task_id"]
                            }
                        }
                    }
                ],
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls

            final_response = ""

            # Execute tool calls if any
            if tool_calls:
                import json
                tool_results = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        # Execute the tool directly on database
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

                        elif function_name == "update_task":
                            task_id = function_args.get("task_id")
                            task = db.get(Task, task_id)
                            if task and task.user_id == user_id:
                                if "title" in function_args:
                                    task.title = function_args["title"]
                                if "description" in function_args:
                                    task.description = function_args["description"]
                                if "status" in function_args:
                                    task.status = function_args["status"]
                                db.commit()
                                result = f"✅ Updated task: {task.title}"
                            else:
                                result = "❌ Task not found"

                        elif function_name == "complete_task":
                            task_id = function_args.get("task_id")
                            task = db.get(Task, task_id)
                            if task and task.user_id == user_id:
                                task.status = "completed"
                                db.commit()
                                result = f"✅ Completed task: {task.title}"
                            else:
                                result = "❌ Task not found"

                        elif function_name == "delete_task":
                            task_id = function_args.get("task_id")
                            task = db.get(Task, task_id)
                            if task and task.user_id == user_id:
                                title = task.title
                                db.delete(task)
                                db.commit()
                                result = f"🗑️ Deleted task: {title}"
                            else:
                                result = "❌ Task not found"

                        else:
                            result = f"❓ Unknown tool: {function_name}"

                        tool_results.append(result)

                    except Exception as e:
                        logger.exception(f"[TodoChatKitServer] Error executing {function_name}")
                        tool_results.append(f"❌ Error executing {function_name}: {str(e)}")

                # Combine tool results for final response
                final_response = "\n\n".join(tool_results)

                # If there's also text content from the assistant, include it
                if assistant_message.content:
                    final_response = assistant_message.content + "\n\n" + final_response
            else:
                # No tool calls, just use the text response
                final_response = assistant_message.content or "I understand. How can I help you with your tasks?"

        except Exception as e:
            logger.exception(f"[TodoChatKitServer] Error calling OpenAI: {e}")
            final_response = "Sorry, I encountered an error processing your request. Please try again."

        # Yield the assistant response
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=self.store.generate_item_id(thread, context),
                thread_id=thread.id,
                created_at=utc_now(),
                content=[{"type": "text", "text": final_response}],
            )
        )

    def _error_response(self, message: str) -> ThreadItemDoneEvent:
        """Create an error response event."""
        return ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=self.store.generate_item_id(None, None),
                thread_id="",
                created_at=utc_now(),
                content=[{"type": "text", "text": f"❌ {message}"}],
            )
        )
