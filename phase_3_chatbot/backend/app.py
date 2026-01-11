"""
Hugging Face Spaces Entry Point for Todo AI Chatbot Backend

This file serves as the entry point for Hugging Face Spaces deployment.
It creates the FastAPI application instance that will be served by the platform.
"""

import sys
import os
# Add the current directory to the path to allow relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router
from dotenv import load_dotenv
from security_config import security_config

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Todo AI Chatbot Backend",
    description="Backend service for Todo AI Chatbot with OpenAI Agents integration",
    version="1.0.0"
)

# Configure CORS for Hugging Face Spaces
frontend_origin = os.getenv("FRONTEND_ORIGIN", "https://huggingface.co")
allow_origins = [frontend_origin]

# Always include Hugging Face domains for proper functioning
allow_origins.extend([
    "https://huggingface.co",
    "https://*.huggingface.co",
    "https://*.hf.space",
    "https://*.hf.run",
    "https://*.gradio.live",
    "https://*.gradio.app",
    "http://localhost:7860",  # Default Gradio port
    "http://localhost:8000",  # Default FastAPI port
])

# Add development origins if in development mode
if os.getenv("ENVIRONMENT", "production") == "development":
    allow_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Allow credentials for auth
    allow_origin_regex=r"https://.*\.hf\.space(?:\:[0-9]+)?",
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Todo AI Chatbot Backend is running on Hugging Face Spaces",
        "version": "1.0.0",
        "status": "operational",
        "platform": "huggingface-spaces"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "todo-ai-chatbot-backend",
        "version": "1.0.0",
        "platform": "huggingface-spaces",
        "checks": {
            "database": "configured",
            "authentication": "enabled",
            "stateless": True,
            "environment": os.getenv("ENVIRONMENT", "production")
        }
    }

@app.get("/info")
def info():
    return {
        "app": "Todo AI Chatbot Backend",
        "runtime": "FastAPI on Hugging Face Spaces",
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "jwt_secret_set": bool(os.getenv("JWT_SECRET_KEY")),
    }

# For Hugging Face Spaces, we typically don't run uvicorn here
# The platform handles serving the app object
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))  # Hugging Face Spaces uses PORT environment variable
    uvicorn.run(app, host="0.0.0.0", port=port)