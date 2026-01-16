# Research: Todo AI Chatbot with ChatKit + MCP

**Feature**: 004-chatkit-mcp-chatbot
**Date**: 2026-01-14
**Status**: Complete

## Executive Summary

This research consolidates findings on integrating OpenAI ChatKit for the frontend UI, ChatKit Python SDK for the backend, and MCP (Model Context Protocol) for exposing task operations as tools. The existing backend structure provides a solid foundation with FastAPI, SQLModel, and PostgreSQL already in place.

---

## Decision 1: Frontend Chat UI Framework

### Decision
Use **OpenAI ChatKit React** (`@openai/chatkit-react`) for the frontend chat interface.

### Rationale
- Drop-in chat solution that handles UI, streaming, and state management
- Framework-agnostic and integrates well with Next.js
- Supports tool call visualization
- Already installed in the frontend (`@openai/chatkit-react`, `@openai/chatkit`)

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Custom React chat UI | Already exists but requires maintenance; ChatKit provides better UX out-of-box |
| Vercel AI SDK Chat | More generic; ChatKit specifically designed for agentic interactions |

### Implementation Notes
```javascript
import { ChatKit, useChatKit } from "@openai/chatkit-react";

const chatkit = useChatKit({
  api: {
    url: "http://localhost:8000/api/v1/chatkit",
    domainKey: "todo-app",
  },
});
```

---

## Decision 2: Backend Chat Protocol

### Decision
Use **ChatKit Python SDK** (`openai-chatkit`) with a self-hosted backend approach.

### Rationale
- Full control over authentication, data storage, and agent logic
- Integrates with existing FastAPI infrastructure
- Supports streaming responses via SSE
- Works with OpenAI Agents SDK for tool execution

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| OpenAI-hosted backend | Limited control over auth, data residency, and custom logic |
| Raw OpenAI Chat Completions | Would require building chat protocol from scratch |

### Implementation Pattern
```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, UserMessageItem

class TodoChatKitServer(ChatKitServer[dict]):
    async def respond(self, thread, input_user_message, context):
        # Use OpenAI Agents SDK to process user input
        # Yield ThreadStreamEvent items
        pass

server = TodoChatKitServer(store=DatabaseStore())

@app.post("/api/v1/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})
    return StreamingResponse(result, media_type="text/event-stream")
```

---

## Decision 3: MCP Tool Architecture

### Decision
Use **MCP Python SDK** (`mcp`) with FastMCP for exposing task operations as tools to the AI agent.

### Rationale
- Standard protocol for exposing tools to LLMs
- Clean separation between tool definition and agent logic
- OpenAI Agents SDK has native MCP support via `MCPServerStdio` or direct tool registration
- Enables future extensibility (add more MCP servers without agent changes)

### Alternatives Considered
| Alternative | Rejected Because |
|-------------|------------------|
| Direct function tools in Agent | Less modular; harder to reuse tools across agents |
| OpenAI function calling only | Non-standard; MCP provides better interoperability |

### Implementation Pattern
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TodoTools")

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task for the user"""
    # Database operation
    return {"task_id": "...", "title": title}

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """List tasks for the user"""
    # Database query
    return [...]

@mcp.tool()
async def complete_task(user_id: str, task_id: str) -> dict:
    """Mark a task as complete"""
    # Database update
    return {"task_id": task_id, "status": "completed"}
```

---

## Decision 4: Agent Framework

### Decision
Use **OpenAI Agents SDK** (`openai-agents-python`) for agent orchestration with MCP tool integration.

### Rationale
- Native support for ChatKit integration via helpers (`simple_to_agent_input`, `stream_agent_response`)
- Built-in MCP server support (stdio, SSE, HTTP transports)
- Streaming-first design matches ChatKit requirements
- Tracing and debugging built-in

### Implementation Pattern
```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from chatkit.agents import AgentContext, stream_agent_response

todo_agent = Agent(
    name="TodoAssistant",
    instructions="""You are a helpful task management assistant...""",
    model="gpt-4o-mini",
)

async with MCPServerStdio(
    name="TodoTools",
    params={"command": "python", "args": ["-m", "mcp_tools.server"]},
) as mcp_server:
    agent = Agent(mcp_servers=[mcp_server])
```

---

## Decision 5: Data Persistence Strategy

### Decision
Use **SQLModel with PostgreSQL** (existing infrastructure) for all persistence, implementing ChatKit's `Store` interface.

### Rationale
- Existing database infrastructure in place (Neon PostgreSQL)
- SQLModel already configured with User, Task, Conversation, Message models
- ChatKit Store interface maps cleanly to existing patterns
- Stateless backend requirement satisfied by database persistence

### Store Implementation
```python
from chatkit.store import Store, NotFoundError
from sqlmodel import Session, select

class DatabaseChatKitStore(Store[dict]):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def load_thread(self, thread_id: str, context: dict):
        with self.session_factory() as session:
            conv = session.exec(
                select(Conversation).where(Conversation.id == thread_id)
            ).first()
            if not conv:
                raise NotFoundError(f"Thread {thread_id} not found")
            return ThreadMetadata(id=conv.id, created_at=conv.created_at)

    # ... implement other Store methods
```

---

## Decision 6: Authentication Integration

### Decision
Integrate ChatKit with existing JWT authentication via context injection.

### Rationale
- Existing auth system works (login/register tested successfully)
- ChatKit context parameter allows passing user identity
- Bearer token extracted in middleware, user_id passed to ChatKit server

### Implementation Pattern
```python
from fastapi import Depends
from services.auth_service import get_current_user

@app.post("/api/v1/chatkit")
async def chatkit_endpoint(
    request: Request,
    user_id: str = Depends(get_current_user)
):
    context = {"user_id": user_id}
    result = await server.process(await request.body(), context=context)
    return StreamingResponse(result, media_type="text/event-stream")
```

---

## Technical Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Language | Python | 3.11 |
| Web Framework | FastAPI | >=0.104.1 |
| Database ORM | SQLModel | >=0.0.16 |
| Database | PostgreSQL (Neon) | - |
| Chat UI | @openai/chatkit-react | latest |
| Chat Backend | openai-chatkit | latest |
| Agent Framework | openai-agents-python | latest |
| MCP SDK | mcp | >=1.25 |
| Testing | pytest, pytest-asyncio | >=7.4.3 |

---

## Dependencies to Add

```toml
# pyproject.toml additions
dependencies = [
    # Existing...
    "openai-chatkit>=0.1.0",
    "openai-agents>=0.1.0",
    "mcp>=1.25.0",
]
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| ChatKit Python SDK is new (2025) | Use official samples as reference; maintain fallback to raw streaming |
| MCP integration complexity | Start with direct tool registration, migrate to MCP server later |
| Streaming response handling | Test with simple responses first, add complexity incrementally |
| Auth token expiry during chat | Implement 401 handler in frontend to redirect to login |

---

## References

- [ChatKit Python SDK Quickstart](https://openai.github.io/chatkit-python/quickstart/)
- [OpenAI Agents SDK - MCP Integration](https://openai.github.io/openai-agents-python/mcp/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [ChatKit Advanced Samples](https://github.com/openai/openai-chatkit-advanced-samples)
