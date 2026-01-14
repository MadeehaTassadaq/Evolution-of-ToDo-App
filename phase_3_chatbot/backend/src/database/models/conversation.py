from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime
import uuid
from .base import BaseSQLModel

if TYPE_CHECKING:
    from .message import Message  # For type checking to avoid circular imports


class ConversationBase(SQLModel):
    """Base class containing common fields for Conversation operations."""
    title: Optional[str] = Field(default="New Conversation", max_length=200)
    status: str = Field(default="active", max_length=20)


class Conversation(ConversationBase, table=True):
    """Conversation entity representing a user's ongoing dialogue with the chatbot."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(max_length=255, index=True)  # References user from authentication system
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    user_id: str


class ConversationRead(ConversationBase):
    """Schema for reading conversation data."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None