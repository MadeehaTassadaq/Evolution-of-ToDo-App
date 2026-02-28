"""
Todo Service for Database Operations
Service layer for todo management using SQLModel and database models.
"""

import logging
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from database.models.todo import Todo, TodoCreate, TodoUpdate


logger = logging.getLogger(__name__)


class TodoService:
    """Service class for todo CRUD operations."""

    def __init__(self, session: Session):
        """
        Initialize the service with a database session.

        Args:
            session: SQLModel Session for database operations
        """
        self.session = session

    def create_todo(
        self,
        user_id: UUID,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Todo:
        """
        Create a new todo for a user.

        Args:
            user_id: The ID of the user
            title: Title of the todo
            description: Optional description
            due_date: Optional due date

        Returns:
            The created Todo object
        """
        from datetime import datetime

        todo = Todo(
            user_id=user_id,
            title=title,
            description=description,
            due_date=datetime.fromisoformat(due_date) if due_date else None
        )
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def get_todo(self, todo_id: UUID, user_id: UUID) -> Optional[Todo]:
        """
        Get a specific todo by ID for a user.

        Args:
            todo_id: The ID of the todo
            user_id: The ID of the user

        Returns:
            The Todo object if found, None otherwise
        """
        statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return self.session.exec(statement).first()

    def get_todos_by_user(
        self,
        user_id: UUID,
        status_filter: Optional[str] = None
    ) -> List[Todo]:
        """
        Get all todos for a user, optionally filtered by status.

        Args:
            user_id: The ID of the user
            status_filter: Optional status filter ("pending", "completed", or None for all)

        Returns:
            List of Todo objects
        """
        statement = select(Todo).where(Todo.user_id == user_id)

        if status_filter and status_filter != "all":
            statement = statement.where(Todo.status == status_filter)

        statement = statement.order_by(Todo.created_at.desc())
        return self.session.exec(statement).all()

    def get_todo_by_title(self, title: str, user_id: UUID) -> Optional[Todo]:
        """
        Get a todo by title (partial match) for a user.

        Args:
            title: The title to search for (partial match)
            user_id: The ID of the user

        Returns:
            The Todo object if found, None otherwise
        """
        statement = select(Todo).where(
            Todo.user_id == user_id,
            Todo.title.icontains(title)
        )
        return self.session.exec(statement).first()

    def update_todo(
        self,
        todo_id: UUID,
        user_id: UUID,
        update_data: TodoUpdate
    ) -> Optional[Todo]:
        """
        Update an existing todo.

        Args:
            todo_id: The ID of the todo to update
            user_id: The ID of the user
            update_data: Data to update

        Returns:
            The updated Todo object, or None if not found
        """
        todo = self.get_todo(todo_id, user_id)
        if not todo:
            return None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(todo, key, value)

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo(self, todo_id: UUID, user_id: UUID) -> bool:
        """
        Delete a todo.

        Args:
            todo_id: The ID of the todo to delete
            user_id: The ID of the user

        Returns:
            True if deleted, False if not found
        """
        todo = self.get_todo(todo_id, user_id)
        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()
        return True
