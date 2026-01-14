"""
Database-backed Store for ChatKit
Implements a ChatKit-compatible store interface using SQLModel/PostgreSQL
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from dataclasses import dataclass

from database.models.conversation import Conversation
from database.models.message import Message


@dataclass
class ThreadMetadata:
    """Thread metadata for ChatKit compatibility."""
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    user_id: str


@dataclass
class ThreadItem:
    """Thread item for ChatKit compatibility."""
    id: str
    type: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
    user_id: str
    thread_id: str


class Store:
    """Base store interface for ChatKit compatibility."""
    pass


class DatabaseStore(Store):
    """
    Database-backed implementation of the ChatKit-compatible Store interface
    Uses SQLModel with PostgreSQL for persistence
    """

    def __init__(self, session: Session):
        """
        Initialize the store with a database session
        """
        self.session = session

    async def get_thread(self, thread_id: str) -> Optional[ThreadMetadata]:
        """Get a thread by ID"""
        try:
            conversation = self.session.query(Conversation).filter_by(id=thread_id).first()

            if not conversation:
                return None

            return ThreadMetadata(
                id=conversation.id,
                name=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                user_id=conversation.user_id
            )
        except Exception as e:
            raise e

    async def list_threads(self, user_id: str) -> List[ThreadMetadata]:
        """List all threads for a user"""
        try:
            conversations = self.session.query(Conversation).filter_by(user_id=user_id).all()

            thread_list = []
            for conv in conversations:
                thread_metadata = ThreadMetadata(
                    id=conv.id,
                    name=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    user_id=conv.user_id
                )
                thread_list.append(thread_metadata)

            return thread_list
        except Exception as e:
            raise e

    async def create_thread(self, user_id: str, title: str = "New Conversation") -> ThreadMetadata:
        """Create a new thread"""
        try:
            from ..database.models.conversation import Conversation as ConversationModel

            conversation = ConversationModel(
                user_id=user_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.session.add(conversation)
            self.session.commit()
            self.session.refresh(conversation)

            return ThreadMetadata(
                id=conversation.id,
                name=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                user_id=conversation.user_id
            )
        except Exception as e:
            self.session.rollback()
            raise e

    async def get_items(self, thread_id: str, limit: int = 20) -> List[ThreadItem]:
        """Get items (messages) from a thread"""
        try:
            messages = (self.session.query(Message)
                       .filter_by(conversation_id=thread_id)
                       .order_by(Message.created_at.asc())
                       .limit(limit)
                       .all())

            items = []
            for msg in messages:
                item = ThreadItem(
                    id=str(msg.id),
                    type=msg.role,  # 'user' or 'assistant'
                    content=msg.content,
                    created_at=msg.created_at,
                    user_id=msg.user_id if hasattr(msg, 'user_id') else "",
                    thread_id=thread_id
                )
                items.append(item)

            return items
        except Exception as e:
            raise e

    async def add_item(self, thread_id: str, role: str, content: str) -> ThreadItem:
        """Add an item (message) to a thread"""
        try:
            from ..database.models.message import Message as MessageModel

            message = MessageModel(
                conversation_id=thread_id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )

            self.session.add(message)
            self.session.commit()
            self.session.refresh(message)

            return ThreadItem(
                id=str(message.id),
                type=message.role,
                content=message.content,
                created_at=message.created_at,
                user_id=message.user_id if hasattr(message, 'user_id') else "",
                thread_id=thread_id
            )
        except Exception as e:
            self.session.rollback()
            raise e