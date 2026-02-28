from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timezone
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .message import Message


def utc_now():
    return datetime.now(timezone.utc)


class ConversationBase(SQLModel):
    """Base class containing common fields for Conversation operations."""
    title: Optional[str] = Field(default="New Conversation", max_length=200)
    status: str = Field(default="active", max_length=20)


class Conversation(ConversationBase, table=True):
    """Conversation entity representing a user's ongoing dialogue with the chatbot."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    user_id: UUID


class ConversationRead(ConversationBase):
    """Schema for reading conversation data."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None


class ConversationUpdate(SQLModel):
    """Schema for updating a conversation."""
    title: Optional[str] = None
    status: Optional[str] = None
