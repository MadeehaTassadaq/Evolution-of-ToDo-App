from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

# Get DATABASE_URL from environment, with a fallback for Hugging Face Spaces
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to a default URL if not set (for development only)
    # In Hugging Face Spaces, this should be provided as a secret
    DATABASE_URL = os.getenv("HF_DATABASE_URL", "sqlite:///./todo_app.db")
    print(f"Using database URL: {DATABASE_URL}")

# Configure engine with connection pooling settings for Neon serverless Postgres
# For SQLite, use a simpler engine configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Check connection validity before using
        pool_recycle=300,    # Recycle connections after 5 minutes
        pool_size=5,         # Maximum pool size
        max_overflow=10,     # Allow up to 10 overflow connections
    )

def create_db_and_tables():
    """Create all database tables"""
    # Import models to register them with SQLModel
    from app.models.user import User
    from app.models.task import Task
    from app.models.conversation import Conversation
    from app.models.message import Message
    SQLModel.metadata.create_all(engine)

def get_session():
    from sqlmodel import Session
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_session_unmanaged():
    """
    Get a session without automatic closing.
    Use this for SSE streaming where the session needs to stay open.
    Caller is responsible for closing the session.
    """
    from sqlmodel import Session
    return Session(engine)
