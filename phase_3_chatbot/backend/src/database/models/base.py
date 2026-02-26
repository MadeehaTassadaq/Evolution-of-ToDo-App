from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime
import uuid


class BaseSQLModel(SQLModel):
    """
    Base class for all SQLModel entities in the Todo AI Chatbot system.
    Provides common fields and functionality.
    """

    @classmethod
    def generate_uuid(cls) -> str:
        """Generate a UUID4 string for entity IDs."""
        return str(uuid.uuid4())


def get_current_time() -> datetime:
    """Get current UTC time for timestamp fields."""
    return datetime.utcnow()