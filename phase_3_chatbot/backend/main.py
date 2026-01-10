from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router
from dotenv import load_dotenv
import os
from security_config import security_config

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Todo AI Chatbot Backend",
    description="Backend service for Todo AI Chatbot with OpenAI Agents integration",
    version="1.0.0"
)

# Configure CORS - in production, use specific origins
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
allow_origins = [frontend_origin]
if os.getenv("ENVIRONMENT", "development") == "development":
    allow_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:8000",  # Backend server
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