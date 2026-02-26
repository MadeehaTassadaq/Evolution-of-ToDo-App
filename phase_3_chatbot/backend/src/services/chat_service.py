from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from database.models.conversation import Conversation, ConversationCreate
from database.models.message import Message, MessageCreate
from database.session import get_session_context
import uuid


class ChatService:
    """Service class for handling chat-related operations including conversation and message management."""

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: The ID of the user creating the conversation
            title: Optional title for the conversation

        Returns:
            The created Conversation object
        """
        conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation"
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            The Conversation object if found, None otherwise
        """
        statement = select(Conversation).where(Conversation.id == conversation_id)
        return self.session.exec(statement).first()

    def get_or_create_conversation(self, user_id: str, conversation_id: Optional[str] = None) -> Conversation:
        """
        Get an existing conversation or create a new one if conversation_id is not provided.

        Args:
            user_id: The ID of the user
            conversation_id: Optional existing conversation ID (treats "default" as None)

        Returns:
            The Conversation object
        """
        # Treat "default" as a sentinel value meaning "create new conversation"
        if conversation_id and conversation_id != "default":
            conversation = self.get_conversation_by_id(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation with ID {conversation_id} not found")
            if conversation.user_id != user_id:
                raise ValueError("User does not have permission to access this conversation")
            return conversation
        else:
            return self.create_conversation(user_id)

    def add_message_to_conversation(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender ('user', 'assistant', 'tool')
            content: The content of the message
            metadata: Optional metadata for the message

        Returns:
            The created Message object
        """
        # Validate role
        valid_roles = ['user', 'assistant', 'tool']
        if role not in valid_roles:
            raise ValueError(f"Role must be one of {valid_roles}")

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_=metadata
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages_for_conversation(self, conversation_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        """
        Retrieve messages for a conversation with pagination.

        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of Message objects
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_full_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get the full conversation history formatted for AI agent consumption.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            List of message dictionaries formatted for the AI agent
        """
        messages = self.get_messages_for_conversation(conversation_id)
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "id": msg.id
            }
            for msg in messages
        ]

    def update_conversation_title(self, conversation_id: str, title: str) -> Conversation:
        """
        Update the title of a conversation.

        Args:
            conversation_id: The ID of the conversation
            title: The new title

        Returns:
            The updated Conversation object
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation with ID {conversation_id} not found")

        conversation.title = title
        conversation.updated_at = datetime.utcnow()
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation