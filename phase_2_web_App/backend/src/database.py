from sqlmodel import create_engine, SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Configure engine with connection pooling settings for Neon serverless Postgres
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
    from src.models.user import User
    from src.models.task import Task
    SQLModel.metadata.create_all(engine)

def get_session():
    from sqlmodel import Session
    with Session(engine) as session:
        yield session
