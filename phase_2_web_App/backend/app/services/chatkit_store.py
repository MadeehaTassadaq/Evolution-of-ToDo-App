"""
ChatKit Store for Phase II Backend

Implements the ChatKit SDK Store interface using existing Phase II database models.
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
    Page
)

from ..models.conversation import Conversation
from ..models.message import Message
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class Phase2ChatKitStore(Store[Dict[str, Any]]):
    """
    PostgreSQL-backed Store for ChatKit server using Phase II database models.

    This implements the Store interface from the ChatKit SDK using the existing
    Conversation and Message models in the Phase II backend.
    """

    def generate_thread_id(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique thread ID."""
        return str(uuid4())

    def generate_item_id(self, thread: Optional[ThreadMetadata] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique item ID."""
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
            conversation = db.get(Conversation, thread_id)
            if not conversation:
                return None

            # Check user access
            if context and "user_id" in context:
                user_id = context["user_id"]
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        pass
                if str(conversation.user_id) != str(user_id):
                    return None

            return ThreadMetadata(
                id=str(conversation.id),
                title=conversation.title or "Todo Chat",
                created_at=conversation.created_at or utc_now(),
                updated_at=conversation.updated_at or utc_now(),
                status=conversation.status or "active",
                metadata={"user_id": str(conversation.user_id)},
            )
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error loading thread: {e}")
            return None

    async def load_threads(
        self,
        limit: int = 100,
        offset: int = 0,
        order: str = "desc",
        after: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ThreadMetadata]:
        """
        Load threads for the user.

        Args:
            limit: Maximum number of threads to return
            offset: Number of threads to skip
            order: Sort order ("desc" or "asc")
            after: Thread ID to start after (for cursor-based pagination)
            context: Request context containing user_id and db session

        Returns:
            List of ThreadMetadata objects
        """
        db = context.get("db") if context else None
        if not db:
            logger.warning("[Phase2ChatKitStore] No database session in context")
            return []

        try:
            if context and "user_id" in context:
                user_id = context["user_id"]
                if isinstance(user_id, str):
                    try:
                        user_id = UUID(user_id)
                    except ValueError:
                        pass
                statement = select(Conversation).where(Conversation.user_id == user_id)
            else:
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

            statement = statement.offset(offset).limit(limit)
            conversations = db.exec(statement).all()

            return [
                ThreadMetadata(
                    id=str(conv.id),
                    title=conv.title or "Todo Chat",
                    created_at=conv.created_at or utc_now(),
                    updated_at=conv.updated_at or utc_now(),
                    status=conv.status or "active",
                    metadata={"user_id": str(conv.user_id)},
                )
                for conv in conversations
            ]
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error loading threads: {e}")
            return []

    async def save_thread(self, thread: ThreadMetadata, context: Optional[Dict[str, Any]] = None) -> ThreadMetadata:
        """
        Save or update thread metadata.

        Args:
            thread: The thread metadata to save
            context: Request context containing user_id and db session

        Returns:
            The saved ThreadMetadata
        """
        db = context.get("db") if context else None
        if not db:
            logger.warning("[Phase2ChatKitStore] No database session in context")
            return thread

        try:
            # Check if thread exists
            existing = db.get(Conversation, thread.id)

            if existing:
                existing.title = thread.title
                existing.updated_at = utc_now()
                if thread.status:
                    existing.status = thread.status
                db.commit()
                db.refresh(existing)
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
                    raise ValueError("user_id required in context to create thread")

                new_conv = Conversation(
                    id=UUID(thread.id) if isinstance(thread.id, str) else thread.id,
                    user_id=user_id,
                    title=thread.title or "Todo Chat",
                    status=thread.status or "active",
                )
                db.add(new_conv)
                db.commit()
                db.refresh(new_conv)

            return thread
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error saving thread: {e}")
            return thread

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
            Page object with 'items' list and 'has_more' boolean for pagination
        """
        from chatkit.types import UserMessageItem, AssistantMessageItem, UserMessageContent, AssistantMessageContent

        db = context.get("db") if context else None
        if not db:
            return Page(items=[], has_more=False)

        try:
            statement = select(Message).where(Message.conversation_id == UUID(thread_id))

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

            # Return a Page object with items and has_more
            return Page(items=items, has_more=has_more)
        except Exception as e:
            logger.exception(f"[Phase2ChatKitStore] Error loading thread items: {e}")
            return Page(items=[], has_more=False)

    async def add_thread_item(self, item: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Add an item to a thread.

        Args:
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
            if content_text and item.thread_id:
                message = Message(
                    conversation_id=UUID(item.thread_id),
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
