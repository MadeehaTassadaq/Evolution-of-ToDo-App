"""
Unit Tests for MCP Tools
Tests for the MCP tools implementation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.mcp_tools.server import TodoMCPServer


@pytest.fixture
def mcp_server():
    """Create a mock MCP server for testing"""
    server = TodoMCPServer()

    # Mock the database session
    server.SessionLocal = MagicMock()
    mock_db = AsyncMock()
    server.SessionLocal.return_value = mock_db

    return server, mock_db


@pytest.mark.asyncio
async def test_add_task_success(mcp_server):
    """Test successful task addition"""
    server, mock_db = mcp_server

    # Mock task creation
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = "Test task"
    mock_task.status = "pending"
    mock_task.created_at = "2023-01-01T00:00:00"

    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    # Configure the mock to return our mock task when queried
    mock_db.query().filter().first.return_value = mock_task

    # Test the add_task method
    result = await server.add_task(
        title="Test task",
        description="Test description",
        user_id=str(uuid4())
    )

    assert result["message"] == "Task 'Test task' created successfully"
    assert result["title"] == "Test task"
    assert result["status"] == "pending"


@pytest.mark.asyncio
async def test_list_tasks_success(mcp_server):
    """Test successful task listing"""
    server, mock_db = mcp_server

    # Mock tasks
    mock_task1 = MagicMock()
    mock_task1.id = uuid4()
    mock_task1.title = "Task 1"
    mock_task1.status = "pending"
    mock_task1.created_at = "2023-01-01T00:00:00"

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [mock_task1]
    mock_query.count.return_value = 1

    mock_db.query.return_value = mock_query

    # Test the list_tasks method
    user_id = str(uuid4())
    result = await server.list_tasks(user_id=user_id)

    assert result["total_count"] == 1
    assert len(result["tasks"]) == 1
    assert result["tasks"][0]["title"] == "Task 1"


@pytest.mark.asyncio
async def test_complete_task_success(mcp_server):
    """Test successful task completion"""
    server, mock_db = mcp_server

    # Mock task
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = "Test task"
    mock_task.status = "pending"
    mock_task.updated_at = "2023-01-01T00:00:00"

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_task

    mock_db.query.return_value = mock_query

    # Test the complete_task method
    result = await server.complete_task(
        task_id=str(mock_task.id),
        user_id=str(uuid4())
    )

    assert result["status"] == "completed"
    assert result["message"] == "Task 'Test task' marked as completed"


@pytest.mark.asyncio
async def test_update_task_success(mcp_server):
    """Test successful task update"""
    server, mock_db = mcp_server

    # Mock task
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = "Old task"
    mock_task.status = "pending"
    mock_task.updated_at = "2023-01-01T00:00:00"

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_task

    mock_db.query.return_value = mock_query

    # Test the update_task method
    result = await server.update_task(
        task_id=str(mock_task.id),
        new_title="Updated task",
        user_id=str(uuid4())
    )

    assert result["title"] == "Updated task"
    assert result["message"] == "Task updated successfully"


@pytest.mark.asyncio
async def test_delete_task_success(mcp_server):
    """Test successful task deletion"""
    server, mock_db = mcp_server

    # Mock task
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = "Test task"

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = mock_task

    mock_db.query.return_value = mock_query

    # Test the delete_task method
    result = await server.delete_task(
        task_id=str(mock_task.id),
        user_id=str(uuid4())
    )

    assert result["deleted_count"] == 1
    assert result["deleted_tasks"] == ["Test task"]