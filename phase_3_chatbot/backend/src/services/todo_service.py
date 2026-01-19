from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime
from uuid import UUID
from database.models.todo import Todo, TodoCreate, TodoUpdate


class TodoService:
    """Service class for handling todo-related operations using the database."""

    def __init__(self, session: Session):
        self.session = session

    def create_todo(self, user_id: UUID, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Todo:
        """
        Create a new todo item in the database.

        Args:
            user_id: The ID of the user creating the todo (UUID)
            title: The title of the todo
            description: Optional description
            due_date: Optional due date

        Returns:
            The created Todo object
        """
        # Convert due_date string to datetime if provided
        from datetime import datetime
        due_date_obj = None
        if due_date:
            try:
                from datetime import datetime
                # Parse ISO format date string
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                # If parsing fails, keep as None
                due_date_obj = None

        todo = Todo(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date_obj,
            status="pending"
        )
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def get_todos_by_user(self, user_id: UUID, status_filter: Optional[str] = None) -> List[Todo]:
        """
        Get all todos for a specific user, optionally filtered by status.

        Args:
            user_id: The ID of the user (UUID)
            status_filter: Optional status filter ("all", "pending", "completed")

        Returns:
            List of Todo objects
        """
        query = select(Todo).where(Todo.user_id == user_id)

        if status_filter and status_filter != "all":
            query = query.where(Todo.status == status_filter)

        query = query.order_by(Todo.created_at.desc())
        return self.session.exec(query).all()

    def get_todo_by_id(self, todo_id: UUID, user_id: UUID) -> Optional[Todo]:
        """
        Get a specific todo by ID and verify user ownership.

        Args:
            todo_id: The ID of the todo (UUID)
            user_id: The ID of the user (UUID)

        Returns:
            Todo object if found and owned by user, None otherwise
        """
        statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
        return self.session.exec(statement).first()

    def get_todo_by_title(self, title: str, user_id: UUID) -> Optional[Todo]:
        """
        Get a specific todo by title and verify user ownership.
        Uses case-insensitive partial matching for natural language support.

        Args:
            title: The title of the todo (partial match supported)
            user_id: The ID of the user (UUID)

        Returns:
            Todo object if found and owned by user, None otherwise
        """
        # First try exact match
        statement = select(Todo).where(
            Todo.title == title,
            Todo.user_id == user_id
        )
        result = self.session.exec(statement).first()
        if result:
            return result

        # If no exact match, try case-insensitive contains match
        statement = select(Todo).where(
            func.lower(Todo.title).contains(title.lower()),
            Todo.user_id == user_id
        )
        return self.session.exec(statement).first()

    def update_todo(self, todo_id: UUID, user_id: UUID, update_data: TodoUpdate) -> Optional[Todo]:
        """
        Update a todo item.

        Args:
            todo_id: The ID of the todo to update (UUID)
            user_id: The ID of the user (UUID)
            update_data: TodoUpdate object with fields to update

        Returns:
            Updated Todo object if successful, None if not found or not owned by user
        """
        todo = self.get_todo_by_id(todo_id, user_id)
        if not todo:
            return None

        # Update fields that are provided
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if field == "due_date" and value:
                # Convert due_date string to datetime if provided
                try:
                    from datetime import datetime
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # If parsing fails, keep the original value
                    pass
            setattr(todo, field, value)

        # Update the updated_at timestamp
        todo.updated_at = datetime.utcnow()

        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo(self, todo_id: UUID, user_id: UUID) -> bool:
        """
        Delete a todo item.

        Args:
            todo_id: The ID of the todo to delete (UUID)
            user_id: The ID of the user (UUID)

        Returns:
            True if deleted successfully, False if not found or not owned by user
        """
        todo = self.get_todo_by_id(todo_id, user_id)
        if not todo:
            return False

        self.session.delete(todo)
        self.session.commit()
        return True