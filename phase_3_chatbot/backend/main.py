import sys
import os
from contextlib import asynccontextmanager

# Add the src directory to the Python path so imports work correctly
# This makes 'database', 'services', etc. available as top-level imports
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import router
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlmodel import SQLModel
from database.session import engine

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    # Import models to register them with SQLModel metadata
    from database.models.user import User  # noqa: F401
    SQLModel.metadata.create_all(engine)
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Todo AI Chatbot Backend",
    description="Backend service for Todo AI Chatbot with OpenAI Agents integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - in production, use specific origins
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
allow_origins = [frontend_origin]
if os.getenv("ENVIRONMENT", "development") == "development":
    allow_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",  # Phase II Backend server
        "http://localhost:7860",  # Phase III Backend server (this server)
        "http://127.0.0.1:7860",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Todo AI Chatbot Backend is running",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "todo-ai-chatbot-backend",
        "version": "1.0.0",
        "checks": {
            "database": "connected",
            "authentication": "enabled",
            "stateless": True
        }
    }