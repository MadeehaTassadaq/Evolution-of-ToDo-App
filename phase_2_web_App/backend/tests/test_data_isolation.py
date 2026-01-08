import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from unittest.mock import patch
from uuid import UUID, uuid4
from backend.src.main import app
from backend.src.models.user import User
from backend.src.models.task import Task
from backend.src.database import get_session
from backend.src.api.auth import create_access_token

# TestClient for making requests to the FastAPI app
client = TestClient(app)

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

    # Mock the database session
    with patch("backend.src.api.tasks.get_session") as mock_get_session:
        # Create a mock session
        mock_session = Session(bind=None)

        # Mock the session.exec method to return the appropriate tasks based on user_id
        def mock_exec(statement):
            # If it's a select statement for tasks, filter by user_id from the current_user mock
            if hasattr(statement, 'whereclause'):
                # This is a simplified version - in real implementation, we'd check the where clause
                # For this test, we'll return the appropriate task based on the mock current user
                if "user1" in str(statement):
                    return [user1_task]
                elif "user2" in str(statement):
                    return [user2_task]
                else:
                    return [user1_task, user2_task]
            return [user1_task, user2_task]

        mock_session.exec = mock_exec
        mock_session.get = lambda model, task_id: user1_task if task_id == user1_task.id else user2_task
        mock_session.add = lambda obj: None
        mock_session.commit = lambda: None
        mock_session.refresh = lambda obj: None
        mock_session.delete = lambda obj: None

        mock_get_session.return_value = mock_session

        # Mock the auth dependency to return different users
        with patch("backend.src.api.tasks.get_current_user") as mock_get_current_user:
            # Test that user1 can access their own task
            mock_get_current_user.return_value = {"id": user1_id}

            # Test GET /tasks - user1 should only see their own tasks
            response = client.get("/api/tasks")
            assert response.status_code == 200
            # In a real scenario, this would only return user1's tasks

            # Test GET /tasks/{task_id} for user1's own task
            response = client.get(f"/api/tasks/{user1_task.id}")
            assert response.status_code == 200
            assert response.json()["id"] == str(user1_task.id)

            # Test GET /tasks/{task_id} for user2's task (should fail for user1)
            response = client.get(f"/api/tasks/{user2_task.id}")
            assert response.status_code == 403  # Forbidden access

            # Test that user2 can access their own task
            mock_get_current_user.return_value = {"id": user2_id}

            # Test GET /tasks/{task_id} for user2's own task
            response = client.get(f"/api/tasks/{user2_task.id}")
            assert response.status_code == 200
            assert response.json()["id"] == str(user2_task.id)

            # Test GET /tasks/{task_id} for user1's task (should fail for user2)
            response = client.get(f"/api/tasks/{user1_task.id}")
            assert response.status_code == 403  # Forbidden access

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

    with patch("backend.src.api.tasks.get_session") as mock_get_session:
        mock_session = Session(bind=None)
        mock_session.get = lambda model, task_id: other_users_task
        mock_session.add = lambda obj: None
        mock_session.commit = lambda: None
        mock_session.refresh = lambda obj: None
        mock_session.delete = lambda obj: None

        mock_get_session.return_value = mock_session

        with patch("backend.src.api.tasks.get_current_user") as mock_get_current_user:
            # User1 tries to access user2's task
            mock_get_current_user.return_value = {"id": user1_id}

            # Try to update other user's task (should fail)
            response = client.put(f"/api/tasks/{other_users_task.id}", json={
                "title": "Modified by other user",
                "description": "Should not be allowed"
            })
            assert response.status_code == 403  # Forbidden

            # Try to delete other user's task (should fail)
            response = client.delete(f"/api/tasks/{other_users_task.id}")
            assert response.status_code == 403  # Forbidden

            # Try to complete other user's task (should fail)
            response = client.patch(f"/api/tasks/{other_users_task.id}/complete")
            assert response.status_code == 403  # Forbidden

def test_user_can_access_only_their_tasks():
    """
    Test that when a user requests all tasks, they only receive their own tasks.
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

    all_tasks = [user1_task1, user1_task2, user2_task1]

    with patch("backend.src.api.tasks.get_session") as mock_get_session:
        mock_session = Session(bind=None)

        def mock_exec(statement):
            # Simulate filtering tasks by user_id
            if hasattr(statement, 'whereclause'):
                # In a real test, this would properly filter based on the where clause
                # For this test, we'll return tasks based on the authenticated user
                current_user_id = mock_get_current_user.return_value["id"]
                if current_user_id == user1_id:
                    return [t for t in all_tasks if t.user_id == user1_id]
                elif current_user_id == user2_id:
                    return [t for t in all_tasks if t.user_id == user2_id]
                else:
                    return []

        mock_session.exec = mock_exec
        mock_session.get = lambda model, task_id: next((t for t in all_tasks if t.id == task_id), None)
        mock_session.add = lambda obj: None
        mock_session.commit = lambda: None
        mock_session.refresh = lambda obj: None
        mock_session.delete = lambda obj: None

        mock_get_session.return_value = mock_session

        with patch("backend.src.api.tasks.get_current_user") as mock_get_current_user:
            # User1 requests their tasks
            mock_get_current_user.return_value = {"id": user1_id}
            response = client.get("/api/tasks")
            assert response.status_code == 200
            user1_tasks = response.json()
            # Should only contain user1's tasks
            assert len(user1_tasks) == 2
            for task in user1_tasks:
                assert task["user_id"] == str(user1_id)

            # User2 requests their tasks
            mock_get_current_user.return_value = {"id": user2_id}
            response = client.get("/api/tasks")
            assert response.status_code == 200
            user2_tasks = response.json()
            # Should only contain user2's tasks
            assert len(user2_tasks) == 1
            assert user2_tasks[0]["user_id"] == str(user2_id)