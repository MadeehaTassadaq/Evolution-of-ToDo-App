from typing import Optional, List
from sqlmodel import Session, select
from datetime import datetime
import uuid
from models.todo import Todo, TodoCreate, TodoUpdate


class TodoService:
    """Service class for handling todo-related operations using the database."""

    def __init__(self, session: Session):
        self.session = session

    def create_todo(self, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Todo:
        """
        Create a new todo item in the database.

        Args:
            user_id: The ID of the user creating the todo
            title: The title of the todo
            description: Optional description
            due_date: Optional due date

        Returns:
            The created Todo object
        """
        todo = Todo(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            status="pending"
        )
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def get_todos_by_user(self, user_id: str, status_filter: Optional[str] = None) -> List[Todo]:
        """
        Get all todos for a specific user, optionally filtered by status.

        Args:
            user_id: The ID of the user
            status_filter: Optional status filter ("all", "pending", "completed")

        Returns:
            List of Todo objects
        """
        query = select(Todo).where(Todo.user_id == user_id)

        if status_filter and status_filter != "all":
            query = query.where(Todo.status == status_filter)

        query = query.order_by(Todo.created_at.desc())
        return self.session.exec(query).all()

    def get_todo_by_id(self, todo_id: int, user_id: str) -> Optional[Todo]:
        """
        Get a specific todo by ID and verify user ownership.

        Args:
            todo_id: The ID of the todo
            user_id: The ID of the user

        Returns:
            Todo object if found and owned by user, None otherwise
        """
        statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return self.session.exec(statement).first()

    def update_todo(self, todo_id: int, user_id: str, update_data: TodoUpdate) -> Optional[Todo]:
        """
        Update a todo item.

        Args:
            todo_id: The ID of the todo to update
            user_id: The ID of the user
            update_data: TodoUpdate object with fields to update

        Returns:
            Updated Todo object if successful, None if not found or not owned by user
        """
        todo = self.get_todo_by_id(todo_id, user_id)
        if not todo:
            return None

        # Update fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(todo, field, value)

        # Update the updated_at timestamp
        todo.updated_at = datetime.utcnow()

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo(self, todo_id: int, user_id: str) -> bool:
        """
        Delete a todo item.

        Args:
            todo_id: The ID of the todo to delete
            user_id: The ID of the user

        Returns:
            True if deleted successfully, False if not found or not owned by user
        """
        todo = self.get_todo_by_id(todo_id, user_id)
        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()
        return True