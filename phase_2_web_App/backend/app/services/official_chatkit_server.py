"""
Official ChatKit Server using OpenAI ChatKit Python SDK + OpenAI Agents SDK

This implementation:
1. Extends ChatKitServer for ChatKit protocol compliance
2. Uses OpenAI Agents SDK for agent execution (Agent + Runner)
3. Uses stream_agent_response() for ChatKit event streaming
4. Integrates MCP-compatible stateless tools
5. Maintains PostgreSQL store for thread persistence
"""

import logging
import os
from typing import AsyncIterator
from datetime import datetime, timezone

from chatkit.server import ChatKitServer
from chatkit.agents import AgentContext, stream_agent_response
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
)
from agents import Agent, Runner, set_default_openai_client
from openai import AsyncOpenAI
import json

from ..models.user import User
from ..models.task import Task
from sqlmodel import Session, select

logger = logging.getLogger(__name__)

# Import MCP tools
from .mcp_tools import MCP_TOOLS
from .chatkit_store import Phase2ChatKitStore, generate_thread_title_from_message


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class TodoChatKitServer(ChatKitServer[dict]):
    """
    Official ChatKit server for Todo AI Assistant.

    Architecture:
    - ChatKitServer: SSE streaming protocol for @openai/chatkit-react widget
    - OpenAI Agents SDK: Agent execution with tool calling
    - MCP Tools: Stateless, database-backed task operations
    - PostgreSQL Store: Thread persistence across server restarts

    Port: 8000 (FastAPI backend)
    Endpoint: /api/v1/chatkit
    """

    def __init__(self):
        """Initialize the ChatKit server with OpenAI Agents SDK integration."""
        # Initialize PostgreSQL store for thread persistence
        super().__init__(
            store=Phase2ChatKitStore()
        )

        # Lazy initialization - will be done on first use
        self.openai_client = None
        self.agent = None
        self._initialized = False

        logger.info("[ChatKitServer] Created (lazy initialization enabled)")

    def _ensure_initialized(self):
        """Ensure the OpenAI client and agent are initialized."""
        if self._initialized:
            return

        # Try to load from environment if not already set
        # This handles the case where .env is loaded after module import
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            # Try loading .env explicitly
            from dotenv import load_dotenv
            load_dotenv()
            openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            logger.error("[ChatKitServer] OPENAI_API_KEY not set in environment!")
            self.openai_client = None
            self.agent = None
            self._initialized = True  # Don't retry
        else:
            # Create async OpenAI client for Agents SDK
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            set_default_openai_client(self.openai_client)

            # Create the Agent with MCP tools
            self.agent = self._create_agent()
            self._initialized = True

            logger.info(
                "[ChatKitServer] Initialized with "
                "ChatKit SDK + OpenAI Agents SDK + "
                f"{len(MCP_TOOLS)} MCP tools + PostgreSQL store"
            )

    def _create_agent(self) -> Agent:
        """
        Create an OpenAI Agents SDK Agent with MCP tools.

        Returns:
            Agent instance configured for todo management
        """
        agent_instructions = """You are a helpful Todo Management Assistant. You help users manage their tasks through natural language.

Available Tools:
- add_task(title, description): Add a new task
- list_tasks(status_filter): List tasks (filter by "pending", "completed", or "all")
- update_task(task_reference, title, description, status): Update a task by reference
- complete_task(task_reference): Mark a task as completed by reference
- delete_task(task_reference): Delete a task by reference

NATURAL LANGUAGE TASK REFERENCES:
Users can reference tasks naturally without IDs:

1. Title References (Exact or Partial):
   - "complete the buy groceries task" → matches exact title
   - "mark the groceries task as done" → matches partial title
   - "delete the task about making meal" → matches title with keywords

2. Positional References:
   - "complete the first task" → completes task at position #1 (top of list)
   - "mark the last task as done" → completes most recent task
   - "delete the second task" → deletes task at position #2

3. Recent Task References:
   - "complete the task I just added" → completes most recently created task
   - "mark my recent task as done" → completes recent task

4. Task IDs (Backward Compatibility):
   - "complete task abc-123" → still works for users who provide IDs

HANDLING AMBIGUITY:
- When multiple tasks match, present options to the user clearly
- Guide users to be more specific if needed
- The system will automatically ask for clarification when 2+ tasks match

Guidelines:
1. Always confirm actions with the user after executing tools
2. Be concise and friendly in your responses
3. When a user asks to add a task, extract the title from their message
4. When listing tasks, the system shows position numbers (#1, #2, #3) for easy reference
5. Use emojis to make responses more engaging (✅ for success, 📋 for lists, ❌ for errors)
6. PREFER NATURAL LANGUAGE REFERENCES over task IDs
7. Only mention task IDs if the user specifically provides one

Example interactions:
- User: "Add a task to buy groceries"
  → Call add_task(title="Buy groceries")
  → Respond: "✅ Added task: Buy groceries"

- User: "Show my pending tasks"
  → Call list_tasks(status_filter="pending")
  → Respond: "📋 Your pending tasks:
    1. 📝 Buy Groceries
    2. 📝 Call Mom"

- User: "Mark the groceries task as complete"
  → Call complete_task(task_reference="groceries")
  → System finds "Buy Groceries" task
  → Respond: "✅ Completed task: Buy Groceries"

- User: "Delete the task about making meal"
  → Call delete_task(task_reference="making meal")
  → System finds task with title "Make meal prep"
  → Respond: "🗑️ Deleted task: Make meal prep"

- User: "Complete the first task"
  → Call complete_task(task_reference="first task")
  → System finds task at position #1
  → Respond: "✅ Completed task: Buy Groceries"

- User: "Update the food task to buy vegetables"
  → Call update_task(task_reference="food", title="Buy vegetables")
  → System finds "Buy Food" task
  → Respond: "✅ Updated task: Buy Vegetables"

- User: "Show all completed tasks"
  → Call list_tasks(status_filter="completed")
  → Respond with formatted list

Remember: Users speak naturally. Extract task references from their sentences and use them with the tools. The task resolver will handle matching by title, position, or recent references automatically.
"""

        agent = Agent(
            name="TodoAssistant",
            instructions=agent_instructions,
            tools=MCP_TOOLS,
            model="gpt-4o-mini"  # Better for function calling
        )

        logger.info(f"[ChatKitServer] Created agent with {len(MCP_TOOLS)} tools")
        return agent

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Process user message using OpenAI Agents SDK and stream ChatKit events.

        This is the main entry point called by ChatKitServer.process().

        Flow:
        1. Extract user message from UserMessageItem
        2. Create AgentContext with thread, store, and request context
        3. Run the Agent using Runner.run()
        4. Stream ChatKit events using stream_agent_response()

        Args:
            thread: ChatKit thread metadata
            item: User message item (None for initial greeting)
            context: Request context with user_id and db session

        Yields:
            ThreadStreamEvent objects for SSE streaming to frontend
        """
        logger.info(f"[ChatKitServer] respond() called - thread.id={thread.id}, item={item is not None}, user_id={context.get('user_id')}")

        # Ensure initialization (lazy loading with .env support)
        self._ensure_initialized()

        # Validate agent is initialized
        if not self.agent:
            logger.error("[ChatKitServer] Agent not initialized")
            from chatkit.types import ErrorEvent, ErrorCode
            yield ErrorEvent(
                code=ErrorCode.STREAM_ERROR,
                message="OpenAI API key not configured",
                allow_retry=False
            )
            return

        # Get user info from context
        user_id = context.get("user_id")
        db = context.get("db")

        if not user_id or not db:
            logger.error("[ChatKitServer] Missing user_id or db in context")
            from chatkit.types import ErrorEvent, ErrorCode
            yield ErrorEvent(
                code=ErrorCode.STREAM_ERROR,
                message="Authentication required",
                allow_retry=False
            )
            return

        user = db.get(User, user_id)
        if not user:
            logger.error(f"[ChatKitServer] User not found for user_id={user_id}")
            from chatkit.types import ErrorEvent, ErrorCode
            yield ErrorEvent(
                code=ErrorCode.STREAM_ERROR,
                message="User not found",
                allow_retry=False
            )
            return

        # Handle empty message (initial greeting)
        if not item or not item.content:
            logger.info(f"[ChatKitServer] Sending greeting to user {user.email}")
            greeting = self._get_greeting_message()
            from chatkit.types import AssistantMessageItem, AssistantMessageContent
            from chatkit.store import Store

            assistant_id = self.store.generate_item_id("msg", thread, context)
            greeting_item = AssistantMessageItem(
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

            yield greeting_item
            from chatkit.types import ThreadItemDoneEvent
            yield ThreadItemDoneEvent(item=greeting_item)
            return

        # Extract user message text
        user_message = ""
        if item and item.content:
            for content in item.content:
                if hasattr(content, 'text'):
                    user_message = content.text
                    break

        logger.info(f"[ChatKitServer] Processing message from {user.email}: {user_message[:50]}...")

        # Update thread title if it's generic (first message in conversation)
        if user_message and thread.title in ["New Chat", "Todo Chat", "New Conversation"]:
            new_title = generate_thread_title_from_message(user_message)
            thread.title = new_title
            # Save updated thread title
            try:
                await self.store.save_thread(thread, context)
                logger.info(f"[ChatKitServer] Updated thread {thread.id} title to '{new_title}'")
            except Exception as e:
                logger.warning(f"[ChatKitServer] Could not update thread title: {e}")

        # Get user's tasks for context (included in system prompt)
        try:
            tasks = db.exec(
                select(Task).where(Task.user_id == user_id).limit(10)
            ).all()
            task_context = ""
            if tasks:
                task_context = "\n\nRecent tasks:\n" + "\n".join([
                    f"- {t.title} (Status: {t.status}, ID: {t.id})"
                    for t in tasks
                ])
        except Exception as e:
            logger.exception(f"[ChatKitServer] Error loading tasks")
            task_context = ""

        # Update agent instructions with user-specific context
        enhanced_instructions = f"""User: {user.email} (ID: {user_id})
{task_context}

Original instructions remain unchanged."""

        # Create request context dict for MCP tools (contains user_id and db)
        # This will be passed to Runner.run_streamed() and wrapped in ToolContext
        request_context_for_runner = {
            "user_id": user_id,
            "email": user.email,
            "db": db
        }

        # Create AgentContext for stream_agent_response()
        # This connects the ChatKit thread with the ChatKit event streaming
        agent_context_for_streaming = AgentContext(
            thread=thread,
            store=self.store,
            request_context=request_context_for_runner,
        )

        try:
            # Run the agent using OpenAI Agents SDK with streaming
            # Runner.run_streamed() returns RunResultStreaming for real-time streaming
            # Note: run_streamed() is NOT async - it's a synchronous function
            logger.info(f"[ChatKitServer] Running agent for user {user.email}")

            try:
                result = Runner.run_streamed(
                    self.agent,
                    input=user_message,
                    context=request_context_for_runner  # Pass dict, not AgentContext
                )
                logger.info(f"[ChatKitServer] Agent run completed successfully, got result type: {type(result)}")
            except Exception as agent_error:
                logger.exception(f"[ChatKitServer] Agent execution failed: {agent_error}")
                raise

            # Stream ChatKit events from the agent result
            # stream_agent_response() converts RunResultStreaming to ThreadStreamEvent
            logger.info(f"[ChatKitServer] Starting to stream events from stream_agent_response()")
            event_count = 0
            try:
                async for event in stream_agent_response(
                    context=agent_context_for_streaming,  # Pass AgentContext here
                    result=result
                ):
                    event_count += 1
                    logger.debug(f"[ChatKitServer] Yielding event {event_count}: {type(event)}")
                    yield event

                logger.info(f"[ChatKitServer] Completed streaming {event_count} events for thread {thread.id}")
            except Exception as stream_error:
                logger.exception(f"[ChatKitServer] Error streaming events: {stream_error}")
                raise

        except Exception as e:
            logger.exception(f"[ChatKitServer] Error in agent execution: {e}")
            from chatkit.types import ErrorEvent, ErrorCode
            yield ErrorEvent(
                code=ErrorCode.STREAM_ERROR,
                message=f"Error processing your request: {str(e)}",
                allow_retry=True
            )

    def _get_greeting_message(self) -> str:
        """Get the greeting message for new conversations."""
        return (
            "Hi! 👋 I'm your Todo AI Assistant. I can help you:\n\n"
            "• ✅ Add a new task\n"
            "• 📋 Show your tasks\n"
            "• ✏️ Update a task\n"
            "• ✅ Mark a task complete\n"
            "• 🗑️ Delete a task\n\n"
            "What would you like to do?"
        )
