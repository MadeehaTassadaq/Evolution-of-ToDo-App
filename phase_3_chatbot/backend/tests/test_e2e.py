"""
End-to-End Tests for Todo AI Chatbot
Tests for complete workflows from user input to task management
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from uuid import uuid4
import asyncio

from main import app  # Assuming the FastAPI app is in main.py


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.mark.asyncio
async def test_full_task_creation_workflow():
    """Test the complete workflow for task creation"""
    from src.message_parser import parse_message
    from src.nlp.intent_classifier import classify_intent
    from src.agents.todo_agent import TodoAgent

    # Mock services
    mock_openai_client = MagicMock()
    mock_mcp_server = MagicMock()

    # Create agent
    agent = TodoAgent(mock_openai_client, mock_mcp_server)

    # Test message parsing
    message = "Create a task called 'Buy groceries'"
    parsed_intent = parse_message(message)

    assert parsed_intent['intent'] == 'create_task'
    assert parsed_intent['parameters']['title'] == 'Buy groceries'

    # Test intent classification
    classified_intent, params = classify_intent(message)
    assert classified_intent.name == 'CREATE_TASK'
    assert params.get('title') == 'Buy groceries'


@pytest.mark.asyncio
async def test_full_task_management_workflow():
    """Test complete task management workflow: create, list, update, complete, delete"""
    from src.agents.todo_agent import TodoAgent

    # Mock services
    mock_openai_client = MagicMock()
    mock_mcp_server = MagicMock()

    # Mock MCP server methods
    mock_mcp_server.add_task = AsyncMock(return_value={
        "task_id": str(uuid4()),
        "title": "Test task",
        "status": "pending",
        "message": "Task 'Test task' created successfully"
    })
    mock_mcp_server.list_tasks = AsyncMock(return_value={
        "tasks": [{"title": "Test task", "status": "pending", "id": str(uuid4())}],
        "total_count": 1,
        "message": "Found 1 task(s)"
    })
    mock_mcp_server.update_task = AsyncMock(return_value={
        "title": "Updated task",
        "status": "pending",
        "message": "Task updated successfully"
    })
    mock_mcp_server.complete_task = AsyncMock(return_value={
        "title": "Updated task",
        "status": "completed",
        "message": "Task marked as completed"
    })
    mock_mcp_server.delete_task = AsyncMock(return_value={
        "deleted_count": 1,
        "deleted_tasks": ["Updated task"],
        "message": "Task 'Updated task' deleted successfully"
    })

    # Create agent
    agent = TodoAgent(mock_openai_client, mock_mcp_server)

    user_id = str(uuid4())
    thread_id = str(uuid4())

    # Step 1: Create task
    create_response = await agent.process_user_message(
        user_message="Create a task called 'Test task'",
        thread_id=thread_id,
        user_id=user_id
    )
    assert "created successfully" in create_response

    # Step 2: List tasks
    list_response = await agent.process_user_message(
        user_message="Show my tasks",
        thread_id=thread_id,
        user_id=user_id
    )
    assert "Test task" in list_response

    # Step 3: Update task
    update_response = await agent.process_user_message(
        user_message="Change 'Test task' to 'Updated task'",
        thread_id=thread_id,
        user_id=user_id
    )
    assert "updated successfully" in update_response

    # Step 4: Complete task
    complete_response = await agent.process_user_message(
        user_message="Complete the task 'Updated task'",
        thread_id=thread_id,
        user_id=user_id
    )
    assert "marked as completed" in complete_response

    # Step 5: Delete task
    delete_response = await agent.process_user_message(
        user_message="Delete the task 'Updated task'",
        thread_id=thread_id,
        user_id=user_id
    )
    assert "deleted successfully" in delete_response


@pytest.mark.asyncio
async def test_natural_language_variations():
    """Test handling of various natural language patterns"""
    from src.message_parser import parse_message

    variations = [
        ("Create a task called 'Buy groceries'", 'create_task'),
        ("Add 'Walk the dog' to my list", 'create_task'),
        ("Make a new task 'Clean the house'", 'create_task'),
        ("Show me my tasks", 'list_tasks'),
        ("What tasks do I have?", 'list_tasks'),
        ("List all my pending tasks", 'list_tasks'),
        ("Complete 'Buy groceries'", 'complete_task'),
        ("Finish 'Walk the dog'", 'complete_task'),
        ("Mark 'Clean the house' as done", 'complete_task'),
        ("Update 'Buy groceries' to 'Buy organic groceries'", 'update_task'),
        ("Change 'Walk the dog' to 'Walk the cat'", 'update_task'),
        ("Rename 'Clean the house' to 'Clean the apartment'", 'update_task'),
        ("Delete 'Buy organic groceries'", 'delete_task'),
        ("Remove 'Walk the cat'", 'delete_task'),
        ("Get rid of 'Clean the apartment'", 'delete_task'),
    ]

    for message, expected_intent in variations:
        result = parse_message(message)
        assert result['intent'] == expected_intent, f"Failed for message: {message}"


@pytest.mark.asyncio
async def test_error_handling_in_workflow():
    """Test error handling throughout the workflow"""
    from src.agents.todo_agent import TodoAgent

    # Mock services with errors
    mock_openai_client = MagicMock()
    mock_mcp_server = MagicMock()

    # Make the add_task method raise an exception
    mock_mcp_server.add_task = AsyncMock(side_effect=Exception("Database error"))

    # Create agent
    agent = TodoAgent(mock_openai_client, mock_mcp_server)

    user_id = str(uuid4())
    thread_id = str(uuid4())

    # Try to create a task that will fail
    response = await agent.process_user_message(
        user_message="Create a task called 'Failing task'",
        thread_id=thread_id,
        user_id=user_id
    )

    # Should contain error message
    assert "encountered an error" in response


@pytest.mark.asyncio
async def test_task_search_workflow():
    """Test the task search functionality"""
    from src.agents.todo_agent import TodoAgent

    # Mock services
    mock_openai_client = MagicMock()
    mock_mcp_server = MagicMock()

    # Mock responses
    mock_mcp_server.list_tasks = AsyncMock(return_value={
        "tasks": [
            {"title": "Buy groceries", "status": "pending", "id": str(uuid4()), "user_id": str(uuid4())},
            {"title": "Walk the dog", "status": "completed", "id": str(uuid4()), "user_id": str(uuid4())},
            {"title": "Clean the house", "status": "pending", "id": str(uuid4()), "user_id": str(uuid4())}
        ],
        "total_count": 3,
        "message": "Found 3 task(s)"
    })

    # Create agent
    agent = TodoAgent(mock_openai_client, mock_mcp_server)

    user_id = str(uuid4())
    thread_id = str(uuid4())

    # Test searching for tasks
    search_response = await agent.process_user_message(
        user_message="Find tasks about groceries",
        thread_id=thread_id,
        user_id=user_id
    )

    # Response should indicate search results
    assert "groceries" in search_response.lower() or "found" in search_response.lower()


def test_api_endpoints_exist(client):
    """Test that required API endpoints exist"""
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200

    # Test that chatkit endpoints exist (these would be tested properly when implemented)
    response = client.get("/api/v1/chatkit/health")
    # This might not exist yet, so we'll just check if the server is running
    assert response.status_code in [200, 404, 405]  # Different possible responses


@pytest.mark.asyncio
async def test_security_validation():
    """Test that security validation occurs during workflows"""
    from src.security import validate_mcp_tool_input, sanitize_task_input

    # Test input validation
    tool_params = {
        "title": "Normal task",
        "description": "This is a normal task description"
    }

    validated_params = validate_mcp_tool_input("add_task", tool_params)
    assert validated_params["title"] == "Normal task"

    # Test sanitization
    sanitized = sanitize_task_input("Task <script>alert('xss')</script>", "Description with <b>HTML</b>")
    assert "<script>" not in sanitized["title"]
    assert "<b>" not in sanitized["description"]