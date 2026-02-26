from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str  # Changed from password_hash to match database schema
    username: str | None = Field(default=None)
    is_active: bool | None = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
