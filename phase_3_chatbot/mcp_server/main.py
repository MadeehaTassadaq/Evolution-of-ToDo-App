"""
MCP Server for Todo AI Chatbot
Provides standardized tools for todo operations via Model Context Protocol
"""

import asyncio
import os
from mcp.server import Server
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP server
server = Server("todo-mcp-server")

# Simple in-memory storage for demonstration
# In a real implementation, this would connect to a database
todos = {}
next_id = 1

# Import and register the tools from the tools module with the server
from .tools import todo_tools
todo_tools.register_tools(server)

async def serve():
    """Start the MCP server."""
    async with server.serve():
        print("MCP Server running...")
        await asyncio.Event().wait()  # Keep the server running


if __name__ == "__main__":
    asyncio.run(serve())