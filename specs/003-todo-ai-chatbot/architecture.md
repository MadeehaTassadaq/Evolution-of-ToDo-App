# Architecture Documentation: Todo AI Chatbot (Phase III)

## Overview
This document describes the architecture of the Todo AI Chatbot system, an isolated implementation under /phase_3_chatbot that provides natural language task management capabilities.

## Folder Responsibilities

### `/backend`
- **Purpose**: FastAPI-based backend service with OpenAI Agents integration
- **Components**:
  - Core API endpoints for chat functionality
  - Chat orchestration service
  - OpenAI Agent integration
  - Authentication and authorization logic
  - Business logic services

### `/mcp_server`
- **Purpose**: Model Context Protocol (MCP) server for standardized tool access
- **Components**:
  - MCP tool definitions for todo operations
  - Stateless tool execution handlers
  - Structured input/output validation
  - Error handling and response formatting

### `/frontend`
- **Purpose**: User interface using OpenAI ChatKit for natural language interaction
- **Components**:
  - Chat interface with message history
  - Authentication integration
  - Real-time messaging capabilities
  - Tool action confirmation displays

### `/database`
- **Purpose**: Database models and migration management
- **Components**:
  - SQLModel entity definitions
  - Database session management
  - Alembic migration scripts
  - Index definitions for performance

### `/specs`
- **Purpose**: Specification and documentation files for the Todo AI Chatbot system
- **Components**:
  - Architecture documentation (this file)
  - MCP tool specifications
  - Agent behavior specifications
  - Stateless compliance documentation