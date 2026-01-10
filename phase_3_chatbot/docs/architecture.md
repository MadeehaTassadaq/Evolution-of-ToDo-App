# Todo AI Chatbot Architecture

## Overview
The Todo AI Chatbot is a stateless, scalable application that allows users to manage their todo tasks through natural language interactions. The system integrates with OpenAI Agents and MCP (Model Context Protocol) tools to provide intelligent task management capabilities.

## System Architecture

### High-Level Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend UI   │────│   Backend API    │────│   MCP Server    │
│   (Next.js)     │    │   (FastAPI)      │    │   (MCP Tools)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │  (PostgreSQL)   │
                       └─────────────────┘
```

### Component Details

#### Frontend UI (Next.js)
- **Location**: `frontend/`
- **Technology**: Next.js with App Router
- **Features**:
  - Chat interface for natural language interactions
  - Authentication flow (login/register)
  - Real-time message display
  - Tool call visualization
  - Responsive design

#### Backend API (FastAPI)
- **Location**: `backend/`
- **Technology**: FastAPI framework
- **Features**:
  - RESTful API endpoints
  - JWT-based authentication
  - Conversation management
  - Integration with AI agent
  - MCP tool orchestration
  - Database operations

#### MCP Server (MCP Tools)
- **Location**: `mcp_server/`
- **Technology**: Model Context Protocol
- **Features**:
  - Standardized todo management tools
  - Database-backed operations
  - Type-safe tool interfaces
  - Error handling and validation

#### Database Layer
- **Technology**: SQLModel with PostgreSQL
- **Features**:
  - Conversation persistence
  - Message history storage
  - Todo item management
  - User authentication data
  - Alembic-based migrations

## Data Flow

### Natural Language Request Processing
1. User sends natural language message via frontend
2. Frontend sends request to backend API with auth token
3. Backend retrieves conversation history from database
4. AI Agent processes message and determines required tools
5. Backend executes MCP tools via direct database calls
6. Results are returned to AI Agent
7. AI Agent generates natural language response
8. Backend stores user and assistant messages in database
9. Response is sent back to frontend
10. Frontend displays the conversation

### Authentication Flow
1. User provides credentials on login page
2. Credentials are sent to `/api/v1/login`
3. Backend validates credentials against database
4. JWT token is generated and returned
5. Frontend stores token in localStorage
6. All subsequent requests include token in Authorization header
7. Backend validates token on each protected endpoint

## API Endpoints

### Chat Endpoints
- `POST /api/v1/chat` - Process natural language todo requests
- `GET /api/v1/conversations/{id}/messages` - Retrieve conversation history

### Authentication Endpoints
- `POST /api/v1/login` - User authentication
- `POST /api/v1/register` - User registration

## Security Considerations

### Authentication
- JWT tokens with configurable expiration
- Secure token storage in frontend
- Token validation on all protected endpoints
- Proper logout functionality

### Input Validation
- Server-side validation of all inputs
- Sanitization of user-provided content
- SQL injection prevention via SQLModel
- XSS prevention through proper output encoding

### Authorization
- Users can only access their own data
- Conversation ownership verification
- Role-based access controls (future extension)

## Statelessness Design

### Principles
- No server-side session state
- All persistent data in database
- Horizontal scaling support
- Restart-safe operations

### Implementation
- JWT tokens for authentication state
- Database as the single source of truth
- No in-memory caches for critical data
- Configuration-based settings

## Deployment Considerations

### Backend
- Environment variables for configuration
- Database connection pooling
- Proper CORS configuration
- Health check endpoints

### Frontend
- Environment-based API endpoints
- Static asset optimization
- Client-side routing
- Service worker support (optional)

### Database
- Production-grade PostgreSQL setup
- Regular backups
- Connection monitoring
- Performance optimization