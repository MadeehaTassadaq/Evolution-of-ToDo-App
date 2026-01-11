from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .api import auth, tasks
from .database import create_db_and_tables

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create database tables
    try:
        logger.info("Initializing database...")
        create_db_and_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Don't prevent the app from starting if database fails
        # (for cases where DB might not be immediately available)
        logger.info("Continuing app startup despite database initialization error")
    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down...")

app = FastAPI(title="Evolution of ToDo API", version="1.0.0", lifespan=lifespan)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://huggingface.co/spaces/madeeha123/chatbot", "https://evolution-of-to-do-app-bafm.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix to match frontend expectations
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Evolution of ToDo API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
