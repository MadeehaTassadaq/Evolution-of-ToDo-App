from sqlmodel import create_engine, Session
from typing import Generator
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env file in the backend directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Fallback to default location
    load_dotenv()


# Get database URL from environment, with a default for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/todo_chatbot_dev")

# Create engine with proper settings based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't need special connection args
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # For PostgreSQL, we need to remove problematic parameters from the connection string
    # Remove channel_binding if present as it might not be supported by psycopg2
    processed_database_url = DATABASE_URL
    if 'channel_binding=' in processed_database_url:
        # Remove the channel_binding parameter from the URL
        import urllib.parse
        parsed = urllib.parse.urlparse(processed_database_url)
        query_params = urllib.parse.parse_qs(parsed.query)

        # Remove channel_binding parameter
        if 'channel_binding' in query_params:
            del query_params['channel_binding']

        # Reconstruct the query string without channel_binding
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        processed_database_url = parsed._replace(query=new_query).geturl()

    engine = create_engine(
        processed_database_url,
        echo=False
    )


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
    from .models.todo import Todo
    from .models.user import User

    # Create all tables
    SQLModel.metadata.create_all(engine)


def drop_tables():
    """Drop all database tables (for testing purposes)."""
    from sqlmodel import SQLModel
    from .models.conversation import Conversation
    from .models.message import Message
    from .models.todo import Todo
    from .models.user import User

    # Drop all tables
    SQLModel.metadata.drop_all(engine)