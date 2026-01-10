from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional, Dict, Any
from datetime import datetime
import uuid
from .base import BaseSQLModel

if TYPE_CHECKING:
    from .conversation import Conversation  # For type checking to avoid circular imports


class MessageBase(SQLModel):
    """Base class containing common fields for Message operations."""
    role: str = Field(max_length=20)  # "user", "assistant", or "tool"
    content: str = Field(sa_column_kwargs={"nullable": False})
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Message(MessageBase, table=True):
    """Message entity representing individual exchanges within a conversation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(
        foreign_key="conversation.id",
        index=True,
        nullable=False
    )
    metadata_: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs={"name": "metadata"})  # Using metadata_ to avoid Python keyword

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    conversation_id: str
    role: str  # Must be one of "user", "assistant", or "tool"


class MessageRead(MessageBase):
    """Schema for reading message data."""
    id: str
    conversation_id: str
    timestamp: datetime
    metadata_: Optional[Dict[str, Any]] = None