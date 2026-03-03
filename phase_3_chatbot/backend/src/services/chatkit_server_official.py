"""
Official ChatKit Server Implementation using the ChatKit Python SDK

This implementation uses the official OpenAI ChatKit Python SDK
for proper protocol handling with @openai/chatkit-react.
"""

import logging
from typing import Any, AsyncIterator, Dict, Optional
from datetime import datetime

from chatkit.server import ChatKitServer
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    ThreadItemDoneEvent,
    ThreadCreatedEvent,
    ClientEffectEvent,
)
from chatkit.store import Store

from database.session import get_session_context
from services.chat_service import ChatService
from agents.todo_agent import TodoAgent

logger = logging.getLogger(__name__)


class ChatKitPostgresStore(Store[Dict[str, Any]]):
    """
    PostgreSQL-backed Store for ChatKit server.

    Implements the Store interface from the ChatKit SDK.
    """

    def generate_thread_id(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique thread ID."""
        import uuid
        return str(uuid.uuid4())

    def generate_item_id(self, thread: Optional[ThreadMetadata] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique item ID."""
        import uuid
        return str(uuid.uuid4())

    def load_thread(self, thread_id: str, context: Optional[Dict[str, Any]] = None) -> Optional[ThreadMetadata]:
        """Load thread metadata from database."""
        with get_session_context() as session:
            from database.models.conversation import Conversation
            from sqlmodel import select

            statement = select(Conversation).where(Conversation.id == thread_id)
            conversation = session.exec(statement).first()

            if not conversation:
                return None

            # Check user access
            if context and "user_id" in context:
                user_id = context["user_id"]
                if str(conversation.user_id) != user_id:
                    return None

            return ThreadMetadata(
                id=str(conversation.id),
                title=conversation.title or "Todo Chat",
                created_at=conversation.created_at or datetime.utcnow(),
                updated_at=conversation.updated_at or datetime.utcnow(),
                status="active",
                metadata={"user_id": str(conversation.user_id)},
            )

    def load_threads(
        self,
        limit: int = 100,
        offset: int = 0,
        order: str = "desc",
        context: Optional[Dict[str, Any]] = None
    ) -> list[ThreadMetadata]:
        """Load threads for the user."""
        with get_session_context() as session:
            from database.models.conversation import Conversation
            from sqlmodel import select

            if context and "user_id" in context:
                user_id = context["user_id"]
                statement = select(Conversation).where(Conversation.user_id == user_id)
            else:
                statement = select(Conversation)

            if order == "desc":
                statement = statement.order_by(Conversation.updated_at.desc())
            else:
                statement = statement.order_by(Conversation.updated_at)

            statement = statement.offset(offset).limit(limit)
            conversations = session.exec(statement).all()

            return [
                ThreadMetadata(
                    id=str(conv.id),
                    title=conv.title or "Todo Chat",
                    created_at=conv.created_at or datetime.utcnow(),
                    updated_at=conv.updated_at or datetime.utcnow(),
                    status="active",
                    metadata={"user_id": str(conv.user_id)},
                )
                for conv in conversations
            ]

    def save_thread(self, thread: ThreadMetadata, context: Optional[Dict[str, Any]] = None) -> ThreadMetadata:
        """Save or update thread metadata."""
        with get_session_context() as session:
            from database.models.conversation import Conversation

            # Check if thread exists
            existing = session.get(Conversation, thread.id)

            if existing:
                existing.title = thread.title
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
            else:
                # Create new conversation
                if context and "user_id" in context:
                    user_id = context["user_id"]
                else:
                    raise ValueError("user_id required in context to create thread")

                # Convert user_id from string to UUID if needed
                from uuid import UUID
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        pass  # Keep as is if not a UUID

                new_conv = Conversation(
                    id=thread.id,
                    user_id=user_id,
                    title=thread.title or "Todo Chat",
                )
                session.add(new_conv)
                session.commit()
                session.refresh(new_conv)

            return thread

    def load_thread_items(
        self,
        thread_id: str,
        limit: int = 100,
        order: str = "asc",
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """Load items for a thread."""
        # This is handled by ChatService for now
        return []

    def add_thread_item(self, item, context: Optional[Dict[str, Any]] = None):
        """Add an item to a thread."""
        # Store messages via ChatService
        with get_session_context() as session:
            from services.chat_service import ChatService
            chat_service = ChatService(session)

            if isinstance(item, AssistantMessageItem):
                # Save assistant message
                content_text = ""
                for content_part in item.content:
                    if hasattr(content_part, "text"):
                        content_text += content_part.text

                chat_service.add_message_to_conversation(
                    conversation_id=item.thread_id,
                    role="assistant",
                    content=content_text
                )
            elif isinstance(item, UserMessageItem):
                # Save user message
                content_text = ""
                for content_part in item.content:
                    if hasattr(content_part, "text"):
                        content_text += content_part.text

                chat_service.add_message_to_conversation(
                    conversation_id=item.thread_id,
                    role="user",
                    content=content_text
                )

        return item

    # Other required methods with minimal implementation
    def load_item(self, item_id: str, context: Optional[Dict[str, Any]] = None) -> Optional:
        return None

    def save_item(self, item, context: Optional[Dict[str, Any]] = None):
        return item

    def delete_thread_item(self, thread_id: str, item_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return False

    def delete_thread(self, thread_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return False

    def load_attachment(self, attachment_id: str, context: Optional[Dict[str, Any]] = None) -> Optional:
        return None

    def save_attachment(self, attachment, context: Optional[Dict[str, Any]] = None):
        return attachment

    def delete_attachment(self, attachment_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return False


class TodoChatKitServer(ChatKitServer[Dict[str, Any]]):
    """
    ChatKit Server for Todo AI Chatbot using the official SDK.

    This server integrates with the TodoAgent to process natural language
    requests and perform todo operations via Phase II API.
    """

    def __init__(self):
        """Initialize the ChatKit server with PostgreSQL store."""
        store = ChatKitPostgresStore()
        super().__init__(store=store)
        self.agent = TodoAgent()

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
            context: Request context with user_id and access_token

        Yields:
            ChatKit events (ThreadItemDoneEvent, etc.)
        """
        user_id = context.get("user_id")
        access_token = context.get("access_token")

        logger.info(f"[TodoChatKitServer] Processing message for thread {thread.id}")

        # Get conversation history
        with get_session_context() as session:
            from services.chat_service import ChatService
            chat_service = ChatService(session)

            conversation = chat_service.get_conversation_by_id(thread.id)
            if not conversation:
                # Create conversation if it doesn't exist
                from uuid import UUID
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        pass

                conversation = chat_service.create_conversation(user_id)

            history = chat_service.get_full_conversation_history(conversation.id)

        # Extract user message text
        user_message_text = ""
        if input_user_message:
            for content_part in input_user_message.content:
                if hasattr(content_part, "text"):
                    user_message_text += content_part.text

        # If no message, send greeting
        if not user_message_text:
            greeting = "Hi! I can help you manage your todos. What would you like to do?"
            yield ThreadItemDoneEvent(
                item=AssistantMessageItem(
                    id=self.store.generate_item_id(thread, context),
                    thread_id=thread.id,
                    created_at=datetime.now(),
                    content=[{"type": "text", "text": greeting}],
                )
            )
            return

        # Process with agent
        agent_response = self.agent.process_message(
            user_message=user_message_text,
            conversation_history=history,
            user_id=user_id
        )

        response_text = agent_response.get("response", "")
        tool_calls = agent_response.get("tool_calls", [])

        logger.info(f"[TodoChatKitServer] Agent response: '{response_text[:100]}', tools: {len(tool_calls)}")

        # Execute tool calls if any
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            parameters = tool_call.get("arguments", {})

            try:
                from services.todo_tools import TodoTools

                # Create TodoTools with access_token for Phase II API authentication
                todo_tools = TodoTools(session=None, access_token=access_token)

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
                    if "tasks" in result:
                        # List of tasks returned
                        tasks = result.get("tasks", [])
                        if not tasks:
                            response_text = "You don't have any tasks yet."
                        else:
                            items_text = "\n".join([
                                f"- {item.get('title', 'Untitled')}: {item.get('status', 'pending')}"
                                for item in tasks
                            ])
                            response_text = f"Here are your tasks:\n{items_text}"
                    elif "task" in result:
                        # Single task returned
                        task = result["task"]
                        response_text = f"Task: {task.get('title', 'Untitled')} - {task.get('status', 'pending')}"
                    else:
                        response_text = result.get("message", "Action completed successfully!")
                else:
                    response_text = f"Error: {result.get('error_message', result.get('error', 'Unknown error'))}"

            except Exception as e:
                logger.exception(f"[TodoChatKitServer] Error executing tool {tool_name}")
                response_text = f"Sorry, I encountered an error: {str(e)}"

        # If there's response text, return it
        if not response_text and tool_calls:
            tool_names = [tc.get("name", "unknown") for tc in tool_calls]
            response_text = f"I've executed the following actions: {', '.join(tool_names)}"

        if not response_text:
            response_text = "I've processed your request. Is there anything else you'd like me to help you with?"

        # Yield the assistant response
        yield ThreadItemDoneEvent(
            item=AssistantMessageItem(
                id=self.store.generate_item_id(thread, context),
                thread_id=thread.id,
                created_at=datetime.now(),
                content=[{"type": "text", "text": response_text}],
            )
        )


# Global server instance
todo_chatkit_server = TodoChatKitServer()
