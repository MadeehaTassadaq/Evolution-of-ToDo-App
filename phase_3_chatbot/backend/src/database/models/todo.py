from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from .base import BaseSQLModel


class TodoBase(SQLModel):
    """Base class containing common fields for Todo operations."""
    title: str
    description: Optional[str] = None
    status: str = "pending"  # "pending", "completed"
    priority: Optional[str] = None
    due_date: Optional[datetime] = None  # Use datetime instead of string
    user_id: UUID  # Use UUID to match the existing task table


class Todo(TodoBase, table=True):
    """Todo entity representing a user's task item."""

    __tablename__ = "task"  # Match the existing table name in the database
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""
    pass


class TodoUpdate(SQLModel):
    """Schema for updating an existing todo."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # "pending", "completed"
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TodoRead(TodoBase):
    """Schema for reading todo data."""
    id: UUID
    created_at: datetime
    updated_at: datetime