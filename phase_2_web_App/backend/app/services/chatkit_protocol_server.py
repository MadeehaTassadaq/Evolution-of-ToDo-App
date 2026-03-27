"""
ChatKit Protocol Server for Phase II Backend

Implements the ChatKit SSE protocol for compatibility with @openai/chatkit-react.
This version sends the correct event sequence that the official widget expects.
"""

import json
import logging
import uuid as uuid_lib
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, Optional

from openai import OpenAI
from sqlmodel import Session, select

from ..database import get_session
from ..models.user import User
from ..models.task import Task

logger = logging.getLogger(__name__)


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class SimpleChatKitServer:
    """
    ChatKit protocol server that sends correct events for @openai/chatkit-react widget.

    Based on the official protocol requirements:
    1. Send response.input_message.created event first
    2. Send response.message.delta events for content
    3. Send response.end event to complete
    """

    def __init__(self):
        """Initialize the ChatKit server."""
        self.openai_client = OpenAI()
        logger.info("[ChatKitServer] Initialized with official protocol support")

    async def process_request(
        self,
        request_body: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Process a ChatKit request and yield SSE events.

        Args:
            request_body: Raw request body bytes
            context: Optional context with user_id, db_session

        Yields:
            SSE-formatted event strings
        """
        try:
            # Parse request
            request = json.loads(request_body.decode("utf-8"))
            request_type = request.get("type")

            logger.info(f"[ChatKitServer] Request type: {request_type}")

            # Get user_id and db from context
            if not context or "user_id" not in context:
                yield self._sse_event("error", {"error": "User not authenticated"})
                return

            user_id = context.get("user_id")
            db = context.get("db")
            if not db:
                yield self._sse_event("error", {"error": "Database session not available"})
                return

            # Get user from database
            user = db.get(User, user_id)
            if not user:
                yield self._sse_event("error", {"error": "User not found"})
                return

            logger.info(f"[ChatKitServer] Processing request for user: {user.email}")

            # Handle different ChatKit protocol request types
            if request_type == "threads.list":
                async for event in self._handle_threads_list(user_id, db):
                    yield event
                return

            if request_type == "threads.create":
                params = request.get("params", {})
                input_data = params.get("input", {})
                content_list = input_data.get("content", [])

                # Extract message text from content
                user_message = ""
                for content_item in content_list:
                    if content_item.get("type") == "input_text":
                        user_message = content_item.get("text", "")
                        break

                # Get quoted text if present
                quoted_text = input_data.get("quoted_text", "")

                # Generate IDs
                thread_id = str(uuid_lib.uuid4())
                user_message_id = str(uuid_lib.uuid4())

                # Process the message with official protocol
                async for event in self._handle_message_with_protocol(
                    thread_id, user_message_id, user_message, quoted_text, user_id, db
                ):
                    yield event
                return

            # Handle simple message format (for testing)
            thread_id = request.get("thread_id") or str(uuid_lib.uuid4())
            user_message = request.get("message", "")
            user_message_id = str(uuid_lib.uuid4())

            async for event in self._handle_message_with_protocol(
                thread_id, user_message_id, user_message, "", user_id, db
            ):
                yield event

        except Exception as e:
            logger.exception(f"[ChatKitServer] Error processing request")
            yield self._sse_event("error", {"error": str(e)})

    async def _handle_threads_list(
        self,
        user_id: str,
        db: Session
    ) -> AsyncIterator[str]:
        """
        Handle threads.list request.

        Args:
            user_id: The authenticated user's ID
            db: Database session

        Yields:
            SSE-formatted event strings
        """
        # Return empty thread list (response event format)
        yield self._sse_event("response", {"threads": []})
        yield self._sse_event("done", {})

    async def _handle_message_with_protocol(
        self,
        thread_id: str,
        user_message_id: str,
        user_message: str,
        quoted_text: str,
        user_id: str,
        db: Session
    ) -> AsyncIterator[str]:
        """
        Handle message request with ChatKit protocol events.

        Event sequence (matches frontend expectations):
        1. thread.item.added - acknowledges user message
        2. thread.item.added - streams assistant response
        3. thread.item.done - signals completion

        Args:
            thread_id: The conversation thread ID
            user_message_id: User message ID
            user_message: The user's message
            quoted_text: Quoted text from previous messages
            user_id: The authenticated user's ID
            db: Database session

        Yields:
            SSE-formatted event strings
        """
        # Step 1: Send user message as thread.item.added event
        # (Frontend already adds user message locally, but we send it for consistency)
        # yield self._sse_event("thread.item.added", {
        #     "item": {
        #         "id": user_message_id,
        #         "type": "message",
        #         "role": "user",
        #         "content": [{"type": "input_text", "text": user_message}],
        #         "created_at": utc_now().isoformat()
        #     }
        # })
        # yield self._sse_event("thread.item.done", {"item_id": user_message_id})

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

            assistant_message_id = str(uuid_lib.uuid4())

            # Send assistant message using official ChatKit protocol format
            # ThreadItemAddedEvent: {type: "thread.item.added", item: {...}}
            # AssistantMessageContent uses type="output_text"
            yield self._sse_event("thread.item.added", {
                "type": "thread.item.added",
                "item": {
                    "id": assistant_message_id,
                    "thread_id": thread_id,
                    "type": "assistant_message",
                    "role": "assistant",
                    "content": [{
                        "type": "output_text",
                        "text": greeting,
                        "annotations": []
                    }],
                    "created_at": utc_now().isoformat()
                }
            })

            # Send ThreadItemDoneEvent
            yield self._sse_event("thread.item.done", {
                "type": "thread.item.done",
                "item_id": assistant_message_id
            })
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
            logger.exception(f"[ChatKitServer] Error loading tasks: {e}")
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

                except Exception as e:
                    logger.exception(f"[ChatKitServer] Error executing {function_name}")
                    result = f"❌ Error executing {function_name}: {str(e)}"

                # Format result into response
                final_response = result

                # If there's also text content from the assistant, include it
                if assistant_message.content:
                    final_response = assistant_message.content + "\n\n" + final_response
        else:
            # No tool calls, just use the text response
            final_response = assistant_message.content or "I understand. How can I help you with your tasks?"

        # Generate assistant message ID
        assistant_message_id = str(uuid_lib.uuid4())

        # Send assistant message using official ChatKit protocol format
        # ThreadItemAddedEvent: {type: "thread.item.added", item: {...}}
        # AssistantMessageContent uses type="output_text"
        yield self._sse_event("thread.item.added", {
            "type": "thread.item.added",
            "item": {
                "id": assistant_message_id,
                "thread_id": thread_id,
                "type": "assistant_message",
                "role": "assistant",
                "content": [{
                    "type": "output_text",
                    "text": final_response,
                    "annotations": []
                }],
                "created_at": utc_now().isoformat()
            }
        })

        # Send ThreadItemDoneEvent
        yield self._sse_event("thread.item.done", {
            "type": "thread.item.done",
            "item_id": assistant_message_id
        })

        logger.info(f"[ChatKitServer] Completed response for thread {thread_id}")

    def _sse_event(self, event_type: str, data: Dict[str, Any]) -> bytes:
        """
        Create SSE-formatted event bytes using ChatKit protocol format.

        ChatKit format: data: {json}\n\n
        The event type is inside the JSON as 'type' field.

        Args:
            event_type: The event type (included in JSON as 'type')
            data: The event data dictionary

        Returns:
            SSE-formatted bytes
        """
        # Ensure data has the type field
        if 'type' not in data:
            data['type'] = event_type
        # Serialize to JSON and wrap in SSE format
        json_str = json.dumps(data, separators=(',', ':'))
        return f"data: {json_str}\n\n".encode('utf-8')


# Global ChatKit server instance
chatkit_server = SimpleChatKitServer()
