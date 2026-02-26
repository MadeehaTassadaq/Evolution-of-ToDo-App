"""
Database Store for ChatKit
Simple implementation without external dependencies
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from dataclasses import dataclass, asdict


@dataclass
class ThreadMetadata:
    """Thread metadata for ChatKit compatibility."""
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    user_id: str

    def dict(self):
        return {k: str(v) if isinstance(v, datetime) else v for k, v in asdict(self).items()}


@dataclass
class ThreadItem:
    """Thread item for ChatKit compatibility."""
    id: str
    type: str
    content: str
    created_at: datetime
    user_id: str
    thread_id: str

    def dict(self):
        return {k: str(v) if isinstance(v, datetime) else v for k, v in asdict(self).items()}


class Store:
    """Base store interface"""
    pass


class DatabaseStore(Store):
    """Database-backed implementation of the Store interface"""

    def __init__(self, session: Session):
        self.session = session

    async def get_thread(self, thread_id: str) -> Optional[ThreadMetadata]:
        """Get a thread by ID"""
        from database.models.conversation import Conversation

        conversation = self.session.query(Conversation).filter_by(id=thread_id).first()

        if not conversation:
            return None

        return ThreadMetadata(
            id=str(conversation.id),
            name=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            user_id=str(conversation.user_id)
        )

    async def list_threads(self, user_id: str) -> List[ThreadMetadata]:
        """List all threads for a user"""
        from database.models.conversation import Conversation

        conversations = self.session.query(Conversation).filter_by(user_id=str(user_id)).all()

        return [
            ThreadMetadata(
                id=str(c.id),
                name=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                user_id=str(c.user_id)
            ) for c in conversations
        ]

    async def create_thread(self, user_id: str, title: str = "New Conversation") -> ThreadMetadata:
        """Create a new thread"""
        from database.models.conversation import Conversation as ConversationModel

        conversation = ConversationModel(
            user_id=str(user_id),
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return ThreadMetadata(
            id=str(conversation.id),
            name=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            user_id=str(conversation.user_id)
        )

    async def get_items(self, thread_id: str, limit: int = 20) -> List[ThreadItem]:
        """Get items (messages) from a thread"""
        from database.models.message import Message

        messages = (self.session.query(Message)
                   .filter_by(conversation_id=thread_id)
                   .order_by(Message.created_at.asc())
                   .limit(limit)
                   .all())

        return [
            ThreadItem(
                id=str(m.id),
                type=m.role,
                content=m.content,
                created_at=m.created_at,
                user_id=str(getattr(m, 'user_id', '')),
                thread_id=thread_id
            ) for m in messages
        ]

    async def add_item(self, thread_id: str, role: str, content: str) -> ThreadItem:
        """Add an item (message) to a thread"""
        from database.models.message import Message as MessageModel

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
            user_id=str(getattr(message, 'user_id', '')),
            thread_id=thread_id
        )
