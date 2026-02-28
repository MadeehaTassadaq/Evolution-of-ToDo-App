"""
Official OpenAI ChatKit Protocol Server Implementation

This module implements the ChatKit protocol directly for streaming responses.
It integrates with the OpenAI Agents SDK for AI responses and uses PostgreSQL for persistence.

ChatKit SSE Protocol Reference:
- Events are sent as: "event: <type>\ndata: <json>\n\n"
- Main event types: thread.message.item.created, thread.item.done
"""

import json
import logging
from typing import Any, AsyncIterator, Dict, Optional
from datetime import datetime
from uuid import uuid4

from sqlmodel import Session, select

from database.session import get_session_context
from database.models.conversation import Conversation
from database.models.message import Message
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class ChatKitStore:
    """
    PostgreSQL-backed Store for ChatKit server.
    Handles persistence of conversations and messages.
    """

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str] = None,
        limit: int = 100,
        order: str = "asc",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Load conversation history from the database.

        Args:
            thread_id: The conversation/thread ID
            after: Optional cursor for pagination
            limit: Maximum number of items to return
            order: Sort order ("asc" or "desc")
            context: Optional context including user_id

        Returns:
            Dict with items list and has_more flag
        """
        with get_session_context() as session:
            # Get conversation to verify access
            statement = select(Conversation).where(Conversation.id == thread_id)
            conversation = session.exec(statement).first()

            if not conversation:
                return {"items": [], "has_more": False}

            # Check user access if context provided
            if context and "user_id" in context:
                user_id = context["user_id"]
                if conversation.user_id != user_id:
                    logger.warning(f"Access denied for user {user_id} to thread {thread_id}")
                    return {"items": [], "has_more": False}

            # Get messages
            statement = select(Message).where(
                Message.conversation_id == thread_id
            ).order_by(Message.timestamp)

            if order == "desc":
                statement = statement.order_by(Message.timestamp.desc())

            if limit:
                statement = statement.limit(limit)

            messages = session.exec(statement).all()

            # Convert to ChatKit thread items format
            items = []
            for msg in messages:
                item = {
                    "id": msg.id,
                    "type": "message",
                    "role": msg.role,
                    "content": [{"type": "text", "text": msg.content}],
                    "created_at": (msg.timestamp or datetime.utcnow()).isoformat()
                }
                items.append(item)

            return {"items": items, "has_more": False}

    async def save_thread_item(
        self,
        thread_id: str,
        role: str,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a message to the database.

        Args:
            thread_id: The conversation/thread ID
            role: Message role ("user" or "assistant")
            content: Message content
            context: Optional context

        Returns:
            The message ID
        """
        with get_session_context() as session:
            # Create new message
            message = Message(
                conversation_id=thread_id,
                role=role,
                content=content
            )
            session.add(message)
            session.commit()
            session.refresh(message)

            logger.info(f"Saved message {message.id} to thread {thread_id}")

            return message.id

    def generate_item_id(self) -> str:
        """Generate a unique ID for a thread item."""
        return str(uuid4())


class TodoChatKitServer:
    """
    ChatKit protocol server implementation for Todo AI Chatbot.

    This implements the ChatKit SSE protocol for streaming chat responses
    with tool calling support for todo management.
    """

    def __init__(self):
        """Initialize the ChatKit server with store."""
        self.store = ChatKitStore()

    async def process_request(
        self,
        request_body: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Process a ChatKit request and yield SSE events.

        Args:
            request_body: Raw request body bytes
            context: Optional context with user_id

        Yields:
            SSE-formatted event strings
        """
        try:
            # Parse request
            request = json.loads(request_body.decode("utf-8"))
            thread_id = request.get("thread_id")
            user_message_content = request.get("message", "")

            # Get user_id from context
            if not context or "user_id" not in context:
                yield self._sse_event("error", {"error": "User not authenticated"})
                return

            user_id = context["user_id"]

            # Get or create conversation
            with get_session_context() as session:
                from services.chat_service import ChatService
                chat_service = ChatService(session)

                if thread_id:
                    conversation = chat_service.get_conversation_by_id(thread_id)
                    if not conversation:
                        # Create new conversation if thread_id doesn't exist
                        conversation = chat_service.create_conversation(user_id)
                        thread_id = str(conversation.id)
                    elif conversation.user_id != user_id:
                        yield self._sse_event("error", {"error": "Access denied"})
                        return
                else:
                    conversation = chat_service.create_conversation(user_id)
                    thread_id = str(conversation.id)

                # Save user message
                if user_message_content:
                    chat_service.add_message_to_conversation(
                        conversation_id=thread_id,
                        role="user",
                        content=user_message_content
                    )

                # Get conversation history
                history = chat_service.get_full_conversation_history(conversation.id)

            # If no message, send greeting
            if not user_message_content:
                greeting = "Hi! I can help you manage your todos. What would you like to do?"
                msg_id = self.store.generate_item_id()
                yield self._sse_event("thread.message.item.created", {
                    "id": msg_id,
                    "thread_id": thread_id,
                    "role": "assistant",
                    "content": [{"type": "text", "text": greeting}],
                    "created_at": datetime.utcnow().isoformat()
                })
                yield self._sse_event("thread.item.done", {"item_id": msg_id})
                return

            # Process with agent and stream response
            async for event in self._stream_agent_response(
                user_message=user_message_content,
                thread_id=thread_id,
                history=history,
                user_id=user_id
            ):
                yield event

        except Exception as e:
            logger.exception("Error processing ChatKit request")
            yield self._sse_event("error", {"error": str(e)})

    async def _stream_agent_response(
        self,
        user_message: str,
        thread_id: str,
        history: list,
        user_id: str
    ) -> AsyncIterator[str]:
        """
        Stream agent response using OpenAI Agents SDK.

        Args:
            user_message: The user's message
            thread_id: Current conversation thread ID
            history: Conversation history
            user_id: The authenticated user's ID

        Yields:
            SSE-formatted event strings
        """
        from agents.todo_agent import TodoAgent

        agent = TodoAgent()

        # Process message with agent
        agent_response = agent.process_message(
            user_message=user_message,
            conversation_history=history,
            user_id=user_id
        )

        response_text = agent_response.get("response", "")
        tool_calls = agent_response.get("tool_calls", [])

        # Execute tool calls if any
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            parameters = tool_call.get("arguments", {})

            try:
                from services.todo_tools import TodoTools

                with get_session_context() as session:
                    todo_tools = TodoTools(session)

                    # Call the appropriate tool
                    if tool_name == "add_task":
                        result = todo_tools.add_task(**parameters)
                    elif tool_name == "list_tasks":
                        result = todo_tools.list_tasks(**parameters)
                    elif tool_name == "update_task":
                        result = todo_tools.update_task(**parameters)
                    elif tool_name == "complete_task":
                        result = todo_tools.complete_task(**parameters)
                    elif tool_name == "delete_task":
                        result = todo_tools.delete_task(**parameters)
                    else:
                        result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                    # Format result into response
                    if result.get("success"):
                        if "data" in result:
                            if isinstance(result["data"], list):
                                if not result["data"]:
                                    response_text = "You don't have any tasks yet."
                                else:
                                    items_text = "\n".join([
                                        f"- {item.get('title', 'Untitled')}: {item.get('status', 'pending')}"
                                        for item in result["data"]
                                    ])
                                    response_text = f"Here are your tasks:\n{items_text}"
                            else:
                                response_text = f"Task: {result['data'].get('title', 'Untitled')} - {result['data'].get('status', 'pending')}"
                        else:
                            response_text = "Action completed successfully!"
                    else:
                        response_text = f"Error: {result.get('error', 'Unknown error')}"

            except Exception as e:
                logger.exception(f"Error executing tool {tool_name}")
                response_text = f"Sorry, I encountered an error: {str(e)}"

        # If there's response text, yield it
        if not response_text and tool_calls:
            tool_names = [tc.get("name", "unknown") for tc in tool_calls]
            response_text = f"I've executed the following actions: {', '.join(tool_names)}"

        if not response_text:
            response_text = "I've processed your request. Is there anything else you'd like me to help you with?"

        # Save assistant response to database
        await self.store.save_thread_item(
            thread_id=thread_id,
            role="assistant",
            content=response_text
        )

        # Generate message ID
        msg_id = self.store.generate_item_id()

        # Yield the assistant message event
        yield self._sse_event("thread.message.item.created", {
            "id": msg_id,
            "thread_id": thread_id,
            "role": "assistant",
            "content": [{"type": "text", "text": response_text}],
            "created_at": datetime.utcnow().isoformat()
        })

        # Yield the item done event
        yield self._sse_event("thread.item.done", {"item_id": msg_id})

    def _sse_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Create an SSE-formatted event string.

        Args:
            event_type: The event type
            data: The event data

        Returns:
            SSE-formatted string
        """
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


# Global ChatKit server instance
chatkit_server = TodoChatKitServer()
