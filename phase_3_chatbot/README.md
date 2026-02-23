# Todo AI Chatbot - Phase III

A stateless, AI-powered todo management system that integrates with OpenAI Agents, MCP (Model Context Protocol) tools, and OpenAI ChatKit for a modern chat interface.

## Architecture

### Stateless Design
- All persistent data is stored in the database (Neon PostgreSQL)
- No server-side session state is maintained
- The application can be restarted without losing user data
- Horizontal scaling is supported

### Components

1. **Backend API** - FastAPI application handling business logic
2. **MCP Server** - Standardized tools for todo operations
3. **Frontend UI** - Next.js 14 chat interface with OpenAI ChatKit
4. **Database Layer** - SQLModel with Neon PostgreSQL

## Prerequisites

- **Node.js**: v18+ (tested with v24.13.0)
- **Python**: 3.11+ (tested with 3.13)
- **uv**: Latest package manager for Python (`pip install uv`)
- **Neon PostgreSQL**: Database service (get free account at https://neon.tech)

## Quick Start

### 1. Clone and Navigate

```bash
cd phase_3_chatbot
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies using uv
uv sync

# Create .env file with your Neon database URL and OpenAI API key
cp .env.example .env
# Edit .env with your credentials:
# DATABASE_URL=postgresql://user:pass@host/db
# OPENAI_API_KEY=sk-your-key-here
```

Example `.env` file:
```env
# Database connection string (Neon PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:npg_xxx@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

# JWT Secret Key (change this in production!)
JWT_SECRET_KEY=local-development-secret-key-change-in-production-min-32-chars-please

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Frontend Origin for CORS
FRONTEND_ORIGIN=http://localhost:3000

# Environment (development/production)
ENVIRONMENT=development

# Token expiry (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Backend Port (for local development)
BACKEND_PORT=8000
```

### 3. Start the Backend

```bash
# Activate the virtual environment
source .venv/bin/activate

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at:
- API: http://localhost:8000
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs

### 4. Frontend Setup (in a new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start the Next.js development server
npm run dev
```

Frontend will be available at:
- http://localhost:3000

### 5. Access the Application

1. Open http://localhost:3000 in your browser
2. Click "Create Demo Account" to register a test user
3. Or use the demo credentials:
   - Username: `demo`
   - Password: `password123`

## Project Structure

```
phase_3_chatbot/
├── backend/
│   ├── src/
│   │   ├── agents/          # OpenAI Agents integration
│   │   ├── api/             # FastAPI routes
│   │   ├── database/        # Database models and session
│   │   ├── mcp_tools/       # MCP server implementation
│   │   ├── services/        # Business logic services
│   │   └── middleware/      # Auth middleware
│   ├── main.py              # Application entry point
│   ├── pyproject.toml       # Python dependencies (uv)
│   └── .env                 # Environment variables
├── frontend/
│   ├── app/                 # Next.js 14 App Router
│   │   ├── api/             # API proxy routes
│   │   ├── chatkit/         # ChatKit interface
│   │   └── login/           # Login page
│   ├── components/          # React components
│   ├── package.json         # Node dependencies
│   └── next.config.js       # Next.js configuration
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/login` - User authentication
- `POST /api/v1/register` - User registration

### Chat
- `POST /api/v1/chat` - Process natural language todo requests
- `GET /api/v1/conversations/{id}/messages` - Retrieve conversation history

### ChatKit
- `WS /api/chatkit/ws` - WebSocket endpoint for ChatKit protocol
- `GET /api/chatkit/health` - ChatKit health check
- `POST /api/chatkit/threads` - Create a new thread
- `GET /api/chatkit/threads` - List user's threads
- `GET /api/chatkit/threads/{id}` - Get a specific thread
- `GET /api/chatkit/threads/{id}/messages` - List messages in a thread

## Security Features

- JWT-based authentication
- Input validation and sanitization
- Rate limiting (configurable)
- CORS configured for frontend integration
- Password strength enforcement
- Secure token handling

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
uv run uvicorn main:app --reload --port 8000

# Run tests
uv run pytest

# Format code
uv run black .
```

### Frontend Development

```bash
cd frontend

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | - |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | - |
| `OPENAI_API_KEY` | OpenAI API key for AI features | - |
| `FRONTEND_ORIGIN` | Frontend URL for CORS | `http://localhost:3000` |
| `ENVIRONMENT` | Development or production | `development` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry time | `60` |

## Database Migrations

The application uses SQLModel with auto-creation of tables on startup. For production, consider using Alembic for migrations:

```bash
# Tables are auto-created on startup
# See main.py lifespan function
```

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'xxx'`
```bash
# Solution: Reinstall dependencies
cd backend
uv sync
```

**Problem**: Database connection error
```bash
# Solution: Check your DATABASE_URL in .env
# Make sure the Neon database is accessible
```

### Frontend Issues

**Problem**: `Cannot connect to backend`
```bash
# Solution: Make sure backend is running on port 8000
curl http://localhost:8000/health
```

**Problem**: `UNMET DEPENDENCY`
```bash
# Solution: Reinstall node modules
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Deployment

### Hugging Face Spaces

The backend includes a `Dockerfile` for Hugging Face Spaces deployment. See `space.yaml` for configuration.

### Production Considerations

1. Change `JWT_SECRET_KEY` to a secure random string
2. Set `ENVIRONMENT=production`
3. Use a production-grade database
4. Configure proper CORS origins
5. Enable HTTPS
6. Set up monitoring and logging

## License

MIT License

## Contributing

This project follows Spec-Driven Development principles. See the main project README for details.
