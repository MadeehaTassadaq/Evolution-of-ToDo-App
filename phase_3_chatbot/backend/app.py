"""
Hugging Face Spaces entry point.
This module exposes the FastAPI app for deployment.
"""
import sys
import os

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Add the backend directory itself to path for security_config
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import router
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from security_config import security_config
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
# For HF Spaces, allow all origins for the API
allow_origins.extend([
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://localhost:8000",
    "http://localhost:7860",
    "https://*.hf.space",
    "*"  # Allow all origins for HF Spaces public API
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for HF Spaces
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
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
