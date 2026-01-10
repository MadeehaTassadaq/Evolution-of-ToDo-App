from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime
from .base import BaseSQLModel


class TodoBase(SQLModel):
    """Base class containing common fields for Todo operations."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending", max_length=20)  # "pending", "completed"
    due_date: Optional[str] = Field(default=None, max_length=20)  # ISO format date string
    user_id: str = Field(max_length=255, index=True)  # References user from authentication system


class Todo(TodoBase, table=True):
    """Todo entity representing a user's task item."""

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TodoCreate(TodoBase):
    """Schema for creating a new todo."""
    pass


class TodoUpdate(SQLModel):
    """Schema for updating an existing todo."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = Field(default=None, max_length=20)  # "pending", "completed"
    due_date: Optional[str] = Field(default=None, max_length=20)  # ISO format date string


class TodoRead(TodoBase):
    """Schema for reading todo data."""
    id: int
    created_at: datetime
    updated_at: datetime