from sqlmodel import create_engine, Session
from typing import Generator
import os
from contextlib import contextmanager


# Get database URL from environment, with a default for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_chatbot_dev")

# Create engine
engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    """Get a database session for dependency injection."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context():
    """Get a database session with context manager for use in services."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """Create all database tables based on SQLModel models."""
    from sqlmodel import SQLModel
    from .models.conversation import Conversation
    from .models.message import Message

    # Create all tables
    SQLModel.metadata.create_all(engine)


def drop_tables():
    """Drop all database tables (for testing purposes)."""
    from sqlmodel import SQLModel
    from .models.conversation import Conversation
    from .models.message import Message

    # Drop all tables
    SQLModel.metadata.drop_all(engine)