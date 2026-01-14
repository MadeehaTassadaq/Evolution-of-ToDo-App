"""
ChatKit Server Implementation for Todo AI Chatbot
Implements the ChatKit-compatible protocol to handle chat requests
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass
from fastapi import WebSocket, WebSocketDisconnect

from database.models.user import User
from database.models.conversation import Conversation
from database.models.message import Message
from database.models.todo import Todo as Task  # Changed to use Todo model
from database.session import Session, engine
from .auth_service import auth_service


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
    type: str
    content: str
    created_at: datetime
    user_id: str
    thread_id: str


class TodoChatKitServer:
    """
    ChatKit-compatible server implementation for Todo AI Chatbot
    Handles the ChatKit protocol for threads and messages
    """


    def __init__(self, session: Session):
        """
        Initialize the ChatKit-compatible server with a database session
        """
        self.session = session

    async def create_thread(
        self,
        user_id: str,
        metadata: Optional[dict] = None
    ) -> ThreadMetadata:
        """Create a new conversation thread"""
        try:
            from ..database.models.conversation import Conversation

            # Create conversation in database
            conversation = Conversation(
                user_id=user_id,  # Using string user_id directly
                title=metadata.get("title", "New Conversation") if metadata else "New Conversation",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.session.add(conversation)
            self.session.commit()
            self.session.refresh(conversation)

            # Return thread metadata
            thread_metadata = ThreadMetadata(
                id=str(conversation.id),
                name=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                user_id=conversation.user_id
            )

            return thread_metadata

        except Exception as e:
            self.session.rollback()
            raise e

    async def list_threads(self, user_id: str) -> List[ThreadMetadata]:
        """List all conversation threads for a user"""
        try:
            conversations = self.session.query(Conversation).filter_by(user_id=user_id).all()

            thread_list = []
            for conv in conversations:
                thread_metadata = ThreadMetadata(
                    id=str(conv.id),
                    name=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    user_id=conv.user_id
                )
                thread_list.append(thread_metadata)

            return thread_list

        except Exception as e:
            raise e

    async def get_thread(self, thread_id: str) -> Optional[ThreadMetadata]:
        """Get a specific conversation thread"""
        try:
            conversation = self.session.query(Conversation).filter_by(id=thread_id).first()

            if not conversation:
                return None

            thread_metadata = ThreadMetadata(
                id=str(conversation.id),
                name=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                user_id=conversation.user_id
            )

            return thread_metadata

        except Exception as e:
            raise e

    async def list_items(
        self,
        thread_id: str,
        before: Optional[str] = None,
        limit: Optional[int] = 20
    ) -> List[ThreadItem]:
        """List messages in a conversation thread"""
        try:
            query = self.session.query(Message).filter_by(conversation_id=thread_id).order_by(Message.created_at.asc())

            if limit:
                query = query.limit(limit)

            messages = query.all()

            thread_items = []
            for msg in messages:
                thread_item = ThreadItem(
                    id=str(msg.id),
                    type=msg.role,  # user or assistant
                    content=msg.content,
                    created_at=msg.created_at,
                    user_id=msg.user_id if hasattr(msg, 'user_id') else "",
                    thread_id=thread_id
                )
                thread_items.append(thread_item)

            return thread_items

        except Exception as e:
            raise e