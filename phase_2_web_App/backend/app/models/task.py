from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)


class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str
    description: str | None = None
    status: str = "pending"
    priority: str | None = None
    due_date: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
