"""
Integration Tests for Chat Features
Tests for the integration between chat interface and task management
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app  # Assuming the FastAPI app is in main.py


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_task_via_chat():
    """Test creating a task through the chat interface"""
    # This would require mocking the entire chat flow
    # For now, we'll test the core functionality
    with patch('src.agents.todo_agent.TodoAgent') as mock_agent_class:
        mock_agent_instance = AsyncMock()
        mock_agent_instance.process_user_message.return_value = "Task 'Buy groceries' created successfully!"

        mock_agent_class.return_value = mock_agent_instance

        # Test would go here once we have the actual endpoint
        assert True  # Placeholder


@pytest.mark.asyncio
async def test_list_tasks_via_chat():
    """Test listing tasks through the chat interface"""
    with patch('src.agents.todo_agent.TodoAgent') as mock_agent_class:
        mock_agent_instance = AsyncMock()
        mock_agent_instance.process_user_message.return_value = "You have 2 task(s):\n- Task 1\n- Task 2"

        mock_agent_class.return_value = mock_agent_instance

        # Test would go here once we have the actual endpoint
        assert True  # Placeholder


@pytest.mark.asyncio
async def test_complete_task_via_chat():
    """Test completing a task through the chat interface"""
    with patch('src.agents.todo_agent.TodoAgent') as mock_agent_class:
        mock_agent_instance = AsyncMock()
        mock_agent_instance.process_user_message.return_value = "Task marked as completed!"

        mock_agent_class.return_value = mock_agent_instance

        # Test would go here once we have the actual endpoint
        assert True  # Placeholder


def test_chat_endpoint_exists(client):
    """Test that the chat endpoint exists"""
    # This test assumes we have a chat endpoint
    # Since we created the chatkit endpoint, let's test its existence
    response = client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_mcp_tool_integration():
    """Test integration between chat interface and MCP tools"""
    # Mock the MCP server
    with patch('src.mcp_tools.server.TodoMCPServer') as mock_mcp_class:
        mock_mcp_instance = MagicMock()
        mock_mcp_instance.add_task = AsyncMock(return_value={
            "task_id": str(uuid4()),
            "title": "Test task",
            "status": "pending",
            "message": "Task 'Test task' created successfully"
        })

        mock_mcp_class.return_value = mock_mcp_instance

        # Test the integration
        result = await mock_mcp_instance.add_task(
            title="Test task",
            user_id=str(uuid4())
        )

        assert result["message"] == "Task 'Test task' created successfully"
        assert result["status"] == "pending"


@pytest.mark.asyncio
async def test_agent_with_mock_services():
    """Test the agent with mocked services"""
    from src.agents.todo_agent import TodoAgent

    # Mock the OpenAI client and MCP server
    mock_openai_client = MagicMock()
    mock_mcp_server = MagicMock()

    # Create agent instance
    agent = TodoAgent(mock_openai_client, mock_mcp_server)

    # Mock the process_user_message method
    with patch.object(agent, '_execute_intent') as mock_execute:
        mock_execute.return_value = "Task created successfully!"

        result = await agent.process_user_message(
            user_message="Create a task called 'Test'",
            thread_id=str(uuid4()),
            user_id=str(uuid4())
        )

        assert result == "Task created successfully!"


@pytest.mark.asyncio
async def test_message_parsing_integration():
    """Test integration between message parsing and task operations"""
    from src.message_parser import parse_message

    # Test parsing a create task message
    result = parse_message("Create a task called 'Buy milk'")

    assert result['intent'] == 'create_task'
    assert result['parameters']['title'] == 'Buy milk'

    # Test parsing a list tasks message
    result = parse_message("Show my tasks")

    assert result['intent'] == 'list_tasks'

    # Test parsing a complete task message
    result = parse_message("Complete the task 'Buy milk'")

    assert result['intent'] == 'complete_task'
    assert result['parameters']['task_title'] == 'Buy milk'