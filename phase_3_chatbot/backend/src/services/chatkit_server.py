"""
Simple ChatKit Server Implementation for Todo AI Chatbot
Doesn't depend on external chatkit package
"""

from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from database.session import Session


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


class TodoChatKitServer:
    """Simple ChatKit-compatible server implementation"""

    def __init__(self, session: Session):
        self.session = session

    async def create_thread(
        self,
        user_id: str,
        metadata: Optional[dict] = None,
        initial_messages: Optional[list] = None
    ) -> ThreadMetadata:
        """Create a new conversation thread"""
        from database.models.conversation import Conversation

        conversation = Conversation(
            user_id=str(user_id),
            title=metadata.get("title", "New Conversation") if metadata else "New Conversation",
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

    async def list_threads(self, user_id: str) -> List[ThreadMetadata]:
        """List all conversation threads for a user"""
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

    async def get_thread(self, thread_id: str) -> Optional[ThreadMetadata]:
        """Get a specific conversation thread"""
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

    async def list_items(
        self,
        thread_id: str,
        before: Optional[str] = None,
        limit: Optional[int] = 20
    ) -> List[ThreadItem]:
        """List messages in a conversation thread"""
        from database.models.message import Message

        query = self.session.query(Message).filter_by(conversation_id=thread_id).order_by(Message.created_at.asc())

        if limit:
            query = query.limit(limit)

        messages = query.all()

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
