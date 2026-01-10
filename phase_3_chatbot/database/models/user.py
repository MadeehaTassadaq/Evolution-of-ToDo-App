from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from .base import BaseSQLModel
import uuid


class UserBase(SQLModel):
    """Base class containing common fields for User operations."""
    username: str = Field(max_length=100, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """User entity representing an authenticated user."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    hashed_password: str = Field(sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserRead(UserBase):
    """Schema for reading user data."""
    id: str
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    """Schema for updating user data."""
    username: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None
    password: Optional[str] = None