---
title: Todo AI Chatbot FastAPI Backend
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Todo AI Chatbot Backend

A FastAPI backend service for the Todo AI Chatbot application.

## Features

- RESTful API endpoints for todo management
- User authentication with JWT
- OpenAI integration for AI-powered chat
- PostgreSQL database support (Neon)
- Rate limiting and security features

## API Endpoints

- `GET /` - Root endpoint, returns service status
- `GET /health` - Health check endpoint
- `GET /docs` - OpenAPI documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/chat` - Chat endpoint

## Environment Variables

The following environment variables should be configured:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `OPENAI_API_KEY` - OpenAI API key
- `FRONTEND_ORIGIN` - Frontend URL for CORS

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 7860
```

## License

MIT License
