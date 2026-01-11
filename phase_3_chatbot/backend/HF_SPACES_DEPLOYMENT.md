# Hugging Face Spaces Deployment Instructions for Todo AI Chatbot Backend

## Overview
This document provides step-by-step instructions for deploying the Todo AI Chatbot Backend on Hugging Face Spaces using the FastAPI framework.

## Prerequisites
- Hugging Face account
- Git repository with the backend code
- Neon PostgreSQL database credentials
- OpenAI API key (if using OpenAI features)

## Repository Structure
Your repository should have the following structure:
```
backend/
├── app.py              # Main application entrypoint (created for HF Spaces)
├── requirements.txt    # Dependencies for HF Spaces
├── main.py            # Original main file (optional)
├── .env               # Environment variables (not committed)
├── api/
│   ├── router.py
│   └── v1/
│       ├── chat.py
│       └── auth.py
├── agents/
│   └── todo_agent.py
├── services/
│   ├── chat_service.py
│   ├── auth_service.py
│   └── todo_tools.py
├── models/
├── database/
│   ├── session.py
│   └── models/
└── security_config.py
```

## Step-by-Step Deployment

### 1. Prepare Your Repository
1. Create a new repository on Hugging Face Hub or use an existing one
2. Clone the repository to your local machine
3. Copy the backend code to the root of your repository
4. Ensure the following files are present:
   - `app.py` (entrypoint for Hugging Face Spaces)
   - `requirements.txt` (dependencies)
   - All other backend source files

### 2. Create the App Entry Point
Create `app.py` with the following content (already provided in this repository):

```python
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
```

### 3. Define Dependencies
Create `requirements.txt` with the following content:

```
fastapi==0.104.1
uvicorn==0.24.0
sqlmodel==0.0.16
alembic==1.13.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
openai==1.3.5
pyjwt==2.8.0
python-dotenv==1.0.0
asyncpg==0.29.0
neon-python>=0.3.0
pydantic>=2.5.0
better-exceptions>=0.3.3
```

### 4. Configure Environment Variables
1. Go to your Hugging Face Space settings
2. Navigate to the "Secrets" section
3. Add the following environment variables:

Required:
- `DATABASE_URL`: PostgreSQL connection string for Neon DB
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI features)

Optional:
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `FRONTEND_ORIGIN`: Allowed frontend origin (default: https://huggingface.co)
- `ENVIRONMENT`: Environment mode (production/development, default: production)

### 5. Set Runtime Configuration
1. In your Hugging Face Space settings:
2. Set the Runtime to "Python"
3. Ensure the Space hardware is sufficient (CPU is usually adequate for this application)

### 6. Deploy the Application
1. Push your code to the Hugging Face repository:
```bash
git add .
git commit -m "Add Todo AI Chatbot Backend for Hugging Face Spaces"
git push origin main
```

2. The Space will automatically start building and deploying your application

### 7. Verify the Deployment
1. Once the build completes, navigate to your Space URL
2. Test the endpoints:
   - Root endpoint: `https://YOUR_USERNAME.hf.space/`
   - Health check: `https://YOUR_USERNAME.hf.space/health`
   - Info endpoint: `https://YOUR_USERNAME.hf.space/info`

## Running Locally vs on Hugging Face Spaces

### Local Development
To run the application locally for development:
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Hugging Face Spaces
The platform automatically:
- Installs dependencies from `requirements.txt`
- Runs the application using the `app` object in `app.py`
- Sets the port using the `PORT` environment variable
- Handles SSL termination
- Manages traffic routing

## Health Check Endpoint
The application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "service": "todo-ai-chatbot-backend",
  "version": "1.0.0",
  "platform": "huggingface-spaces",
  "checks": {
    "database": "configured",
    "authentication": "enabled",
    "stateless": true,
    "environment": "production"
  }
}
```

## Troubleshooting

### Common Issues:
1. **Import Errors**: Ensure all dependencies are in requirements.txt
2. **Database Connection**: Verify DATABASE_URL is properly configured in Secrets
3. **CORS Issues**: Check that frontend domains are properly configured
4. **Environment Variables**: Confirm all required variables are set in Secrets

### Logs:
Check the Space logs in the Hugging Face UI for detailed error information.

## Scaling Considerations
- The application is designed to be stateless for horizontal scaling
- Database connection pooling is handled by SQLModel/SQLAlchemy
- For high-traffic applications, consider upgrading to a GPU space or using a more powerful CPU instance

## Security Best Practices
- Never commit sensitive information to the repository
- Use strong, randomly generated JWT secret keys
- Regularly rotate API keys
- Monitor access logs for unusual activity
- Keep dependencies up to date