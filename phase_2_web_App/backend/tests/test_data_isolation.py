import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import MagicMock
from uuid import UUID, uuid4
from src.main import app
from src.models.task import Task
from src.database import get_session
from src.middleware.auth import get_current_user


class MockSession:
    """Mock database session for testing."""
    def __init__(self, tasks=None):
        self.tasks = tasks or []
        self.added = []
        self.deleted = []

    def exec(self, statement):
        """Return mock result that supports .all()"""
        mock_result = MagicMock()
        # Filter tasks based on user_id if possible
        mock_result.all = MagicMock(return_value=self.tasks)
        return mock_result

    def get(self, model, task_id):
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass

    def delete(self, obj):
        self.deleted.append(obj)


def test_data_isolation_between_users():
    """
    Test that users can only access their own tasks and not tasks belonging to other users.
    """
    # Create two different users
    user1_id = uuid4()
    user2_id = uuid4()

    # Create tasks for user1
    user1_task = Task(
        id=uuid4(),
        user_id=user1_id,
        title="User 1 task",
        description="Task belonging to user 1"
    )

    # Create tasks for user2
    user2_task = Task(
        id=uuid4(),
        user_id=user2_id,
        title="User 2 task",
        description="Task belonging to user 2"
    )

    all_tasks = [user1_task, user2_task]

    # Create mock session with all tasks
    mock_session = MockSession(all_tasks)

    # Override dependencies
    def get_mock_session():
        return mock_session

    def get_user1():
        return {"id": user1_id}

    def get_user2():
        return {"id": user2_id}

    # Test user1 accessing their own task
    app.dependency_overrides[get_session] = get_mock_session
    app.dependency_overrides[get_current_user] = get_user1

    client = TestClient(app)

    try:
        # User1 accessing their own task should succeed
        response = client.get(f"/api/tasks/{user1_task.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(user1_task.id)

        # User1 accessing user2's task should be forbidden
        response = client.get(f"/api/tasks/{user2_task.id}")
        assert response.status_code == 403

        # Switch to user2
        app.dependency_overrides[get_current_user] = get_user2

        # User2 accessing their own task should succeed
        response = client.get(f"/api/tasks/{user2_task.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(user2_task.id)

        # User2 accessing user1's task should be forbidden
        response = client.get(f"/api/tasks/{user1_task.id}")
        assert response.status_code == 403
    finally:
        # Clean up overrides
        app.dependency_overrides.clear()


def test_user_cannot_modify_other_users_task():
    """
    Test that a user cannot update or delete another user's task.
    """
    user1_id = uuid4()
    user2_id = uuid4()

    # Task belonging to user2
    other_users_task = Task(
        id=uuid4(),
        user_id=user2_id,
        title="Other user's task",
        description="This task belongs to user 2"
    )

    mock_session = MockSession([other_users_task])

    def get_mock_session():
        return mock_session

    def get_user1():
        return {"id": user1_id}

    app.dependency_overrides[get_session] = get_mock_session
    app.dependency_overrides[get_current_user] = get_user1

    client = TestClient(app)

    try:
        # Try to update other user's task (should fail with 403)
        response = client.put(f"/api/tasks/{other_users_task.id}", json={
            "title": "Modified by other user",
            "description": "Should not be allowed"
        })
        assert response.status_code == 403

        # Try to delete other user's task (should fail with 403)
        response = client.delete(f"/api/tasks/{other_users_task.id}")
        assert response.status_code == 403

        # Try to complete other user's task (should fail with 403)
        response = client.patch(f"/api/tasks/{other_users_task.id}/complete")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_user_can_access_only_their_tasks():
    """
    Test that when a user requests all tasks, they only receive their own tasks.
    This test validates the API returns filtered results based on user ownership.
    """
    user1_id = uuid4()
    user2_id = uuid4()

    # Create tasks for user1
    user1_task1 = Task(
        id=uuid4(),
        user_id=user1_id,
        title="User 1 task 1",
        description="First task for user 1"
    )

    user1_task2 = Task(
        id=uuid4(),
        user_id=user1_id,
        title="User 1 task 2",
        description="Second task for user 1"
    )

    # Create tasks for user2
    user2_task1 = Task(
        id=uuid4(),
        user_id=user2_id,
        title="User 2 task 1",
        description="First task for user 2"
    )

    user1_tasks = [user1_task1, user1_task2]
    user2_tasks = [user2_task1]

    def get_mock_session_user1():
        return MockSession(user1_tasks)

    def get_mock_session_user2():
        return MockSession(user2_tasks)

    def get_user1():
        return {"id": user1_id}

    def get_user2():
        return {"id": user2_id}

    client = TestClient(app)

    try:
        # User1 requests their tasks
        app.dependency_overrides[get_session] = get_mock_session_user1
        app.dependency_overrides[get_current_user] = get_user1

        response = client.get("/api/tasks")
        assert response.status_code == 200
        user1_response_tasks = response.json()
        assert len(user1_response_tasks) == 2
        for task in user1_response_tasks:
            assert task["user_id"] == str(user1_id)

        # User2 requests their tasks
        app.dependency_overrides[get_session] = get_mock_session_user2
        app.dependency_overrides[get_current_user] = get_user2

        response = client.get("/api/tasks")
        assert response.status_code == 200
        user2_response_tasks = response.json()
        assert len(user2_response_tasks) == 1
        assert user2_response_tasks[0]["user_id"] == str(user2_id)
    finally:
        app.dependency_overrides.clear()
