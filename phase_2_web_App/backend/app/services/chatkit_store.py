"""
ChatKit Store for Phase II Backend

Implements the ChatKit SDK Store interface using existing Phase II database models.

Database now uses proper UUID types (after migration).
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata,
    ThreadItem,
    UserMessageItem,
    AssistantMessageItem,
    UserMessageContent,
    AssistantMessageContent,
    Page,
    ActiveStatus,
)

from ..models.conversation import Conversation
from ..models.message import Message
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def generate_thread_title_from_message(content: str) -> str:
    """
    Generate a meaningful thread title from the first user message.

    Args:
        content: The user's message content

    Returns:
        A concise title (max 50 characters)
    """
    if not content:
        return "New Chat"

    # Clean up the content
    title = content.strip()

    # Remove common prefixes
    prefixes_to_remove = [
        "i want to", "i'd like to", "i need to", "can you", "please", "help me",
        "hey", "hello", "hi there", "could you", "would you"
    ]
    for prefix in prefixes_to_remove:
        if title.lower().startswith(prefix):
            title = title[len(prefix):].strip()
            break

    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()

    # Truncate to 50 characters
    if len(title) > 50:
        title = title[:47] + "..."

    return title if title else "New Chat"


class Phase2ChatKitStore(Store[Dict[str, Any]]):
    """
    PostgreSQL-backed Store for ChatKit server using Phase II database models.

    This implements the Store interface from the ChatKit SDK using the existing
    Conversation and Message models in the Phase II backend.

    Database uses UUID types (migrated from VARCHAR).
    """

    def generate_thread_id(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique thread ID."""
        return str(uuid4())

    def generate_item_id(
        self,
        item_type: str,
        thread: ThreadMetadata,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a unique item ID.

        Args:
            item_type: Type of item ('thread', 'message', 'tool_call', etc.)
            thread: Thread metadata
            context: Optional request context

        Returns:
            A unique UUID as a string
        """
        return str(uuid4())

    async def load_thread(self, thread_id: str, context: Optional[Dict[str, Any]] = None) -> Optional[ThreadMetadata]:
        """
        Load thread metadata from database.

        Args:
            thread_id: The thread ID to load
            context: Request context containing user_id and db session

        Returns:
            ThreadMetadata if found, None otherwise
        """
        db = context.get("db") if context else None
        if not db:
            logger.warning("[Phase2ChatKitStore] No database session in context")
            return None

        try:
            # Validate thread_id is a valid UUID
            try:
                thread_uuid = UUID(thread_id)
            except ValueError:
                logger.warning(f"[Phase2ChatKitStore] Invalid thread_id format: {thread_id}")
                return None

            conversation = db.get(Conversation, thread_uuid)
            if not conversation:
                logger.info(f"[Phase2ChatKitStore] Thread not found: {thread_id}")
                return None

            # Check user access
            if context and "user_id" in context:
                user_id = context["user_id"]
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        logger.warning(f"[Phase2ChatKitStore] Invalid user_id in context")
                        return None
                if str(conversation.user_id) != str(user_id):
                    logger.warning(f"[Phase2ChatKitStore] User access denied to thread {thread_id}")
                    return None

            title = conversation.title or "New Chat"
            logger.info(f"[Phase2ChatKitStore] Loaded thread {thread_id} with title='{title}' for user={conversation.user_id}")
            return ThreadMetadata(
                id=str(conversation.id),
                title=title,
                created_at=conversation.created_at or utc_now(),
                updated_at=conversation.updated_at or utc_now(),
                status=ActiveStatus(),
                metadata={"user_id": str(conversation.user_id)},
            )
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error loading thread {thread_id}: {e}")
            return None

    async def load_threads(
        self,
        limit: int = 100,
        after: str = None,
        order: str = "desc",
        context: Optional[Dict[str, Any]] = None
    ) -> Page[ThreadMetadata]:
        """
        Load threads for the user.

        Args:
            limit: Maximum number of threads to return
            after: Thread ID to start after (for cursor-based pagination)
            order: Sort order ("desc" or "asc")
            context: Request context containing user_id and db session

        Returns:
            Page of ThreadMetadata objects with pagination info
        """
        db = context.get("db") if context else None
        if not db:
            logger.warning("[Phase2ChatKitStore] No database session in context")
            return Page(data=[], has_more=False)

        try:
            if context and "user_id" in context:
                user_id = context["user_id"]
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        pass
                statement = select(Conversation).where(Conversation.user_id == user_id)
                logger.info(f"[Phase2ChatKitStore] Loading threads for user_id={user_id}, limit={limit}, order={order}")
            else:
                logger.warning("[Phase2ChatKitStore] No user_id in context, loading all threads")
                statement = select(Conversation)

            # Handle cursor-based pagination with 'after' parameter
            if after:
                try:
                    after_uuid = UUID(after)
                    # Get the reference conversation to compare timestamps
                    ref_conv = db.get(Conversation, after_uuid)
                    if ref_conv:
                        if order == "desc":
                            # For desc order, get threads updated before the reference
                            statement = statement.where(Conversation.updated_at < ref_conv.updated_at)
                        else:
                            # For asc order, get threads updated after the reference
                            statement = statement.where(Conversation.updated_at > ref_conv.updated_at)
                except ValueError:
                    logger.warning(f"[Phase2ChatKitStore] Invalid 'after' thread ID: {after}")

            if order == "desc":
                statement = statement.order_by(Conversation.updated_at.desc())
            else:
                statement = statement.order_by(Conversation.updated_at)

            statement = statement.limit(limit + 1)  # Fetch one extra to determine has_more
            conversations = db.exec(statement).all()

            # Convert to ThreadMetadata objects
            threads = []
            for conv in conversations[:limit]:  # Only return up to limit
                title = conv.title or "New Chat"
                threads.append(ThreadMetadata(
                    id=str(conv.id),
                    title=title,
                    created_at=conv.created_at or utc_now(),
                    updated_at=conv.updated_at or utc_now(),
                    status=ActiveStatus(),
                    metadata={"user_id": str(conv.user_id)},
                ))
                logger.debug(f"[Phase2ChatKitStore] Thread {str(conv.id)[:8]}... title='{title}'")

            # Check if there are more threads
            has_more = len(conversations) > limit

            # Return Page object with pagination info
            result = Page(data=threads, has_more=has_more)
            logger.info(f"[Phase2ChatKitStore] Loaded {len(threads)} threads for user={user_id}, has_more={has_more}")
            return result
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error loading threads: {e}")
            return Page(data=[], has_more=False)

    async def save_thread(self, thread: ThreadMetadata, context: Optional[Dict[str, Any]] = None) -> ThreadMetadata:
        """
        Save or update thread metadata.

        Args:
            thread: The thread metadata to save
            context: Request context containing user_id and db session

        Returns:
            The saved ThreadMetadata (or original if save fails)
        """
        db = context.get("db") if context else None
        if not db:
            logger.warning("[Phase2ChatKitStore] No database session in context")
            return thread  # Return original thread

        try:
            # Check if thread exists
            try:
                thread_uuid = UUID(thread.id)
                existing = db.get(Conversation, thread_uuid)
            except ValueError:
                existing = None

            if existing:
                existing.title = thread.title
                existing.updated_at = utc_now()
                # Don't update status from thread metadata - keep DB status
                db.commit()
                db.refresh(existing)
                logger.info(f"[Phase2ChatKitStore] Updated thread {thread.id} with title='{thread.title}'")
            else:
                # Create new conversation
                if context and "user_id" in context:
                    user_id = context["user_id"]
                    if isinstance(user_id, str):
                        try:
                            user_id = UUID(user_id)
                        except ValueError:
                            pass
                else:
                    logger.warning("[Phase2ChatKitStore] user_id required in context to create thread")
                    return thread  # Return original thread

                # Generate meaningful title if not provided or generic
                title = thread.title
                if not title or title in ["Todo Chat", "New Conversation"]:
                    title = "New Chat"

                new_conv = Conversation(
                    id=UUID(thread.id) if isinstance(thread.id, str) else thread.id,
                    user_id=user_id,
                    title=title,
                    status="active",  # Database stores as string
                )
                db.add(new_conv)
                db.commit()
                db.refresh(new_conv)
                logger.info(f"[Phase2ChatKitStore] Created thread {thread.id} with title='{title}'")

            return thread
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error saving thread: {e}")
            return thread  # Always return thread, never None

    async def load_thread_items(
        self,
        thread_id: str,
        limit: int = 100,
        order: str = "asc",
        after: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> "Page[ThreadItem]":
        """
        Load items for a thread.

        Args:
            thread_id: The thread ID
            limit: Maximum number of items to return
            order: Sort order ("asc" or "desc")
            after: Message ID to start after (for cursor-based pagination)
            context: Request context containing db session

        Returns:
            Page object with 'data' list and 'has_more' boolean for pagination
        """
        db = context.get("db") if context else None
        if not db:
            logger.warning("[Phase2ChatKitStore] No database session in context")
            return Page(data=[], has_more=False)

        try:
            try:
                thread_uuid = UUID(thread_id)
            except ValueError:
                return Page(data=[], has_more=False)

            statement = select(Message).where(Message.conversation_id == thread_uuid)

            # Handle cursor-based pagination with 'after' parameter
            if after:
                try:
                    after_uuid = UUID(after)
                    # Get the reference message to compare timestamps
                    ref_msg = db.get(Message, after_uuid)
                    if ref_msg:
                        if order == "desc":
                            # For desc order, get messages before the reference
                            statement = statement.where(Message.timestamp < ref_msg.timestamp)
                        else:
                            # For asc order, get messages after the reference
                            statement = statement.where(Message.timestamp > ref_msg.timestamp)
                except ValueError:
                    logger.warning(f"[Phase2ChatKitStore] Invalid 'after' message ID: {after}")

            if order == "desc":
                statement = statement.order_by(Message.timestamp.desc())
            else:
                statement = statement.order_by(Message.timestamp.asc())
            statement = statement.limit(limit + 1)  # Fetch one extra to determine has_more
            messages = db.exec(statement).all()

            # Convert to ChatKit format
            items = []
            for msg in messages[:limit]:  # Only return up to limit items
                if msg.role == "user":
                    items.append(UserMessageItem(
                        id=str(msg.id),
                        thread_id=thread_id,
                        created_at=msg.timestamp or utc_now(),
                        content=[
                            UserMessageContent(
                                type="input_text",
                                text=msg.content
                            )
                        ]
                    ))
                else:  # assistant
                    items.append(AssistantMessageItem(
                        id=str(msg.id),
                        thread_id=thread_id,
                        created_at=msg.timestamp or utc_now(),
                        content=[
                            AssistantMessageContent(
                                type="output_text",
                                text=msg.content,
                                annotations=[]
                            )
                        ]
                    ))

            # Check if there are more items
            has_more = len(messages) > limit

            # Create and return Page object
            result = Page(data=items, has_more=has_more)
            logger.info(f"[Phase2ChatKitStore] Loaded {len(items)} items for thread {thread_id}, has_more={has_more}")
            return result
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error loading thread items: {e}")
            return Page(data=[], has_more=False)

    async def add_thread_item(
        self,
        thread_id: str,
        item: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Add an item to a thread.

        Args:
            thread_id: The thread ID
            item: The item to add (UserMessageItem or AssistantMessageItem)
            context: Request context containing db session

        Returns:
            The added item
        """
        db = context.get("db") if context else None
        if not db:
            return item

        try:
            from chatkit.types import UserMessageItem, AssistantMessageItem

            # Extract content text
            content_text = ""
            role = "user"

            if isinstance(item, AssistantMessageItem):
                role = "assistant"
                for content_part in item.content:
                    if hasattr(content_part, "text"):
                        content_text += content_part.text
            elif isinstance(item, UserMessageItem):
                role = "user"
                for content_part in item.content:
                    if hasattr(content_part, "text"):
                        content_text += content_part.text

            # Save message to database
            if content_text and thread_id:
                message = Message(
                    conversation_id=UUID(thread_id),
                    role=role,
                    content=content_text,
                    timestamp=item.created_at if hasattr(item, "created_at") else utc_now(),
                )
                db.add(message)
                db.commit()

            return item
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error adding thread item: {e}")
            return item

    # Minimal implementations for other required methods
    async def load_item(self, item_id: str, context: Optional[Dict[str, Any]] = None) -> Optional[ThreadItem]:
        return None

    async def save_item(self, item: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return item

    async def delete_thread_item(self, thread_id: str, item_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return False

    async def delete_thread(self, thread_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return False

    async def load_attachment(self, attachment_id: str, context: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        return None

    async def save_attachment(self, attachment: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        return attachment

    async def delete_attachment(self, attachment_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        return False
