# ADR 002: Dual Tool Architecture - Backend Tools and MCP Tools

## Status
Accepted

## Date
2026-01-13

## Context
The AI chatbot needs to interact with todo management functionality. The system is designed with OpenAI Agents that use function calling to perform todo operations. There's a decision to be made about how these operations connect to the actual data layer.

## Decision
We will implement both backend tools and MCP (Model Context Protocol) tools for todo operations:

1. Backend tools (`backend/services/todo_tools.py`) - Direct database access from the backend service
2. MCP tools (`mcp_server/tools/todo_tools.py`) - Standardized tools accessible via MCP protocol

The AI agent in the backend will call the backend tools directly rather than going through the MCP layer for this initial implementation.

## Alternatives Considered

### Alternative 1: MCP-Only Architecture
- **Pros**: More standardized, better separation, enables external AI agents to access tools
- **Cons**: More complex setup, additional network hop, potential latency
- **Rejected** for initial implementation due to complexity

### Alternative 2: Backend-Only Architecture
- **Pros**: Simpler, fewer moving parts, direct access
- **Cons**: Less flexible for future external AI integration
- **Considered** but decided to implement both for future extensibility

### Alternative 3: Hybrid Approach (Selected)
- **Pros**: Flexibility for current implementation, foundation for future MCP integration, allows for gradual migration
- **Cons**: More code to maintain initially, potential for inconsistency between implementations
- **Chosen** as it provides the best balance of immediate needs and future flexibility

## Consequences

### Positive
- Immediate functionality without complex MCP setup
- Foundation for future MCP integration
- Ability to evolve the architecture gradually
- Both internal and external AI agents can eventually use the same tools

### Negative
- Duplication of tool implementations
- Potential for inconsistency between the two sets of tools
- More maintenance overhead

## Rationale
The hybrid approach allows us to deliver the core functionality quickly while establishing the infrastructure for MCP tools. This positions us well for future requirements where external AI agents might need to access our tools via the MCP protocol.

## Links
- Feature Spec: `/specs/003-todo-ai-chatbot/spec.md`
- Implementation Plan: `/specs/003-todo-ai-chatbot/plan.md`
- Related Tasks: `/specs/003-todo-ai-chatbot/tasks.md`