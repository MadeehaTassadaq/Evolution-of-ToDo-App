# Todo AI Chatbot - Phase III

This is a stateless, AI-powered todo management system that integrates with OpenAI Agents and MCP (Model Context Protocol) tools.

## Architecture

### Stateless Design
- All persistent data is stored in the database
- No server-side session state is maintained
- The application can be restarted without losing user data
- Horizontal scaling is supported

### Components

1. **Backend API** - FastAPI application handling business logic
2. **MCP Server** - Standardized tools for todo operations
3. **Frontend UI** - Next.js chat interface
4. **Database Layer** - SQLModel with PostgreSQL support

## Security Features

- JWT-based authentication
- Input validation and sanitization
- Rate limiting (configurable)
- CORS configured for frontend integration
- Password strength enforcement
- Secure token handling

## API Endpoints

- `POST /api/v1/chat` - Process natural language todo requests
- `POST /api/v1/login` - User authentication
- `POST /api/v1/register` - User registration
- `GET /api/v1/conversations/{id}/messages` - Retrieve conversation history

## Running the Application

### Backend
```bash
cd backend
pip install -r requirements.txt
python run_migrations.py
uvicorn main:app --reload --port 8000
```

### MCP Server
```bash
cd mcp_server
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost/todo_chatbot
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_ORIGIN=http://localhost:3000
ENVIRONMENT=development
```

## Validation

Run the statelessness and safety validation script:

```bash
python validate_statelessness.py
```

## Database Migrations

The application uses Alembic for database migrations:

```bash
# To run migrations
python run_migrations.py

# Migration files are in database/migrations/
```

## Safety Measures

1. **Input Validation**: All user inputs are validated and sanitized
2. **Authentication**: JWT tokens required for all user actions
3. **Authorization**: Users can only access their own data
4. **Rate Limiting**: Configurable rate limiting to prevent abuse
5. **Statelessness**: No server-side session state maintained
6. **Secure Defaults**: Secure configuration values by default