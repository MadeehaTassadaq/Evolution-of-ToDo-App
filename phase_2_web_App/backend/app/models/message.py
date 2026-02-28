from sqlmodel import SQLModel, Field, Relationship, Column
from typing import TYPE_CHECKING, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import JSON

if TYPE_CHECKING:
    from .conversation import Conversation


def utc_now():
    return datetime.now(timezone.utc)


class MessageBase(SQLModel):
    """Base class containing common fields for Message operations."""
    role: str = Field(max_length=20)  # "user", "assistant", or "tool_call"
    content: str
    timestamp: datetime = Field(default_factory=utc_now)


class Message(MessageBase, table=True):
    """Message entity representing individual exchanges within a conversation."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversation.id",
        index=True,
        nullable=False
    )
    extra_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    conversation_id: UUID
    role: str  # Must be one of "user", "assistant", or "tool_call"
    extra_data: Optional[Dict[str, Any]] = None


class MessageRead(MessageBase):
    """Schema for reading message data."""
    id: UUID
    conversation_id: UUID
    timestamp: datetime
    extra_data: Optional[Dict[str, Any]] = None
