# Todo AI Chatbot Deployment Guide

## Overview
This document provides instructions for deploying the Todo AI Chatbot application in various environments, from development to production.

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Docker (optional, recommended for containerized deployment)

### Environment Setup
Before deployment, ensure the following are available:
- PostgreSQL database instance
- Domain name (for production)
- SSL certificate (for production)
- SMTP server for email notifications (optional)

## Architecture Components

### Backend Services
1. **Main API Server** - Handles application logic and API endpoints
2. **MCP Server** - Provides standardized tools for AI agent integration
3. **Database** - Stores all application data persistently

### Frontend Services
1. **Next.js Application** - Chat interface and user authentication

## Development Deployment

### Local Development Setup

#### 1. Clone the repository
```bash
git clone <repository-url>
cd phase_3_chatbot
```

#### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

#### 3. Database Setup
Create a PostgreSQL database and configure the connection:
```bash
# Create database
createdb todo_chatbot_dev

# Update environment
echo "DATABASE_URL=postgresql://username:password@localhost/todo_chatbot_dev" > .env
```

#### 4. Run Database Migrations
```bash
python run_migrations.py
```

#### 5. Start Backend Server
```bash
uvicorn main:app --reload --port 8000
```

#### 6. Start MCP Server
```bash
cd mcp_server
python main.py
```

#### 7. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables (Development)
Create `.env` files in respective directories:

**Backend (.env):**
```
DATABASE_URL=postgresql://localhost:5432/todo_chatbot_dev
JWT_SECRET_KEY=dev-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_ORIGIN=http://localhost:3000
ENVIRONMENT=development
```

## Production Deployment

### Containerized Deployment (Recommended)

#### Docker Compose Setup
Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: todo_chatbot_db
    environment:
      POSTGRES_DB: todo_chatbot
      POSTGRES_USER: todo_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: todo_chatbot_backend
    environment:
      DATABASE_URL: postgresql://todo_user:secure_password@postgres:5432/todo_chatbot
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      FRONTEND_ORIGIN: ${FRONTEND_ORIGIN}
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: unless-stopped

  mcp-server:
    build:
      context: ./mcp_server
      dockerfile: Dockerfile
    container_name: todo_chatbot_mcp
    environment:
      DATABASE_URL: postgresql://todo_user:secure_password@postgres:5432/todo_chatbot
    ports:
      - "8001:8001"
    depends_on:
      - postgres
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: todo_chatbot_frontend
    environment:
      NEXT_PUBLIC_API_BASE_URL: ${API_BASE_URL}
    ports:
      - "3000:3000"
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Dockerfile for Backend
Create `backend/Dockerfile`:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile for Frontend
Create `frontend/Dockerfile`:

```Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### Manual Production Deployment

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install python3.11 python3.11-venv python3.11-dev nginx postgresql postgresql-contrib supervisor

# Create application user
sudo adduser --system --group --disabled-password --home /opt/todo-chatbot todo-user
```

#### 2. Database Setup
```bash
# Create database user
sudo -u postgres createuser --interactive todo_user
sudo -u postgres createdb todo_chatbot
sudo -u postgres psql -c "ALTER USER todo_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE todo_chatbot TO todo_user;"
```

#### 3. Application Setup
```bash
# Copy application files
sudo mkdir -p /opt/todo-chatbot
sudo chown todo-user:todo-user /opt/todo-chatbot
sudo -u todo-user rsync -av /path/to/source/ /opt/todo-chatbot/

# Setup Python environment
sudo -u todo-user python3.11 -m venv /opt/todo-chatbot/venv
sudo -u todo-user /opt/todo-chatbot/venv/bin/pip install -r /opt/todo-chatbot/backend/requirements.txt
```

#### 4. Database Migration
```bash
# Activate virtual environment and run migrations
sudo -u todo-user /opt/todo-chatbot/venv/bin/python /opt/todo-chatbot/run_migrations.py
```

#### 5. Process Management with Supervisor
Create `/etc/supervisor/conf.d/todo-chatbot.conf`:

```ini
[program:todo-chatbot-backend]
command=/opt/todo-chatbot/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
directory=/opt/todo-chatbot/backend
user=todo-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/todo-chatbot-backend.log
environment=DATABASE_URL="postgresql://todo_user:secure_password@localhost/todo_chatbot",JWT_SECRET_KEY="prod-secret-key",ENVIRONMENT="production"

[program:todo-chatbot-mcp]
command=/opt/todo-chatbot/venv/bin/python main.py
directory=/opt/todo-chatbot/mcp_server
user=todo-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/todo-chatbot-mcp.log
environment=DATABASE_URL="postgresql://todo_user:secure_password@localhost/todo_chatbot"
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start todo-chatbot-backend todo-chatbot-mcp
```

#### 6. Nginx Configuration
Create `/etc/nginx/sites-available/todo-chatbot`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # API requests to backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/todo-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Environment Variables (Production)

**Backend (.env):**
```
DATABASE_URL=postgresql://todo_user:secure_password@localhost/todo_chatbot
JWT_SECRET_KEY=super-long-random-string-at-least-32-characters-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
FRONTEND_ORIGIN=https://yourdomain.com
ENVIRONMENT=production
```

## Scaling Strategies

### Horizontal Scaling
- Deploy multiple backend instances behind a load balancer
- Use external session store if needed (not required for this stateless app)
- Scale MCP server independently based on AI processing load
- Database connection pooling configuration

### Database Scaling
- Connection pooling settings
- Read replicas for heavy read operations
- Connection limits and timeouts

### CDN Configuration
- Serve static assets through CDN
- Cache frontend builds for faster loading
- Asset versioning for cache busting

## Monitoring & Maintenance

### Health Checks
- Backend: `GET /health` endpoint (returns 200 when healthy)
- Database connectivity monitoring
- MCP server availability
- Disk space and memory usage

### Logging
- Application logs in structured format
- Error logs with stack traces
- Access logs for security monitoring
- Performance metrics collection

### Backups
- Database backups with pg_dump
- Configuration file backups
- Automated backup scheduling
- Backup verification procedures

### Security Updates
- Regular dependency updates
- OS security patches
- Certificate renewal (if using SSL)
- Vulnerability scanning

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Verify database credentials
- Check network connectivity
- Confirm database service is running
- Validate connection string format

#### Authentication Problems
- Check JWT secret configuration
- Verify token expiration settings
- Confirm token inclusion in requests
- Validate user data in database

#### Frontend-Backend Communication
- Check CORS configuration
- Verify API endpoint URLs
- Confirm authentication token transmission
- Review network request logs

### Diagnostic Commands

```bash
# Check service status
sudo supervisorctl status

# View application logs
sudo tail -f /var/log/todo-chatbot-backend.log

# Test database connectivity
psql postgresql://todo_user:secure_password@localhost/todo_chatbot -c "SELECT version();"

# Check API health
curl -X GET https://yourdomain.com/health
```

## Rollback Procedures

### Database Rollback
```bash
# Restore from backup
pg_restore -d todo_chatbot /path/to/backup.dump
```

### Application Rollback
- Deploy previous version using the same process
- Monitor for service restoration
- Verify functionality with smoke tests

## Performance Tuning

### Backend Optimization
- Database connection pool size
- HTTP timeout configurations
- Memory usage limits
- Request/response compression

### Frontend Optimization
- Build optimization
- Asset compression
- Caching strategies
- Bundle size reduction