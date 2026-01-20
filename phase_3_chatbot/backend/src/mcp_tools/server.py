"""
MCP Tools Server Implementation
Defines the Model Context Protocol tools for task management operations
"""

from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
import json

from database.session import Session, engine
from database.models.user import User
from database.models.todo import Todo


class ToolDefinition:
    """Simple class to hold tool definition"""
    def __init__(self, name, description, handler, input_schema=None, output_schema=None):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}


class TodoMCPServer:
    """
    MCP server implementation exposing task management operations as tools
    """

    def __init__(self):
        self.tools = {}  # Store tools by name
        self._setup_tools()

    def _setup_tools(self):
        """Setup all MCP tools for task management"""
        self.add_tool(
            name="add_task",
            description="Create a new task for the current user",
            handler=self.add_task,
            input_schema={
                "type": "object",
                "required": ["title"],
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the task (1-500 characters)",
                        "minLength": 1,
                        "maxLength": 500
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task",
                        "maxLength": 5000
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Optional due date for the task (ISO 8601 format)"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                    },
                    "title": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending"]
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        )

        self.add_tool(
            name="list_tasks",
            description="List all tasks for the current user, optionally filtered by status",
            handler=self.list_tasks,
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "default": "all",
                        "description": "Filter tasks by status"
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                        "description": "Maximum number of tasks to return"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "format": "uuid"
                                },
                                "title": {
                                    "type": "string"
                                },
                                "status": {
                                    "type": "string"
                                },
                                "due_date": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "created_at": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            }
                        }
                    },
                    "total_count": {
                        "type": "integer"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        )

        self.add_tool(
            name="complete_task",
            description="Mark a task as completed. Can identify task by ID or by title (for natural language matching)",
            handler=self.complete_task,
            input_schema={
                "type": "object",
                "required": [],
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The ID of the task to complete (optional if task_title provided)"
                    },
                    "task_title": {
                        "type": "string",
                        "description": "The title of the task to complete - use for natural language matching (e.g., 'groceries' will match 'Buy groceries')"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "title": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["completed"]
                    },
                    "completed_at": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        )

        self.add_tool(
            name="update_task",
            description="Update an existing task's details. Can identify task by ID or by title (for natural language matching)",
            handler=self.update_task,
            input_schema={
                "type": "object",
                "required": [],
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The ID of the task to update (optional if task_title provided)"
                    },
                    "task_title": {
                        "type": "string",
                        "description": "The current title of the task - use for natural language matching (e.g., 'groceries' will match 'Buy groceries')"
                    },
                    "new_title": {
                        "type": "string",
                        "description": "New title for the task",
                        "minLength": 1,
                        "maxLength": 500
                    },
                    "new_description": {
                        "type": "string",
                        "description": "New description for the task",
                        "maxLength": 5000
                    },
                    "new_due_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "New due date for the task"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "New status for the task"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid"
                    },
                    "title": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string"
                    },
                    "due_date": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        )

        self.add_tool(
            name="delete_task",
            description="Delete a task permanently. Can identify task by ID or by title (for natural language matching)",
            handler=self.delete_task,
            input_schema={
                "type": "object",
                "required": [],
                "properties": {
                    "task_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The ID of the task to delete (optional if task_title provided)"
                    },
                    "task_title": {
                        "type": "string",
                        "description": "The title of the task to delete - use for natural language matching (e.g., 'groceries' will match 'Buy groceries')"
                    },
                    "delete_completed": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, delete all completed tasks (ignores task_id/task_title)"
                    }
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "deleted_count": {
                        "type": "integer"
                    },
                    "deleted_tasks": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        )

    def add_tool(self, name: str, description: str, handler, input_schema=None, output_schema=None):
        """Add a tool to the server"""
        tool_def = ToolDefinition(name, description, handler, input_schema, output_schema)
        self.tools[name] = tool_def

    async def add_task(self, title: str, description: Optional[str] = None,
                      due_date: Optional[str] = None, user_id: str = None) -> Dict[str, Any]:
        """Add a new task to the database"""
        if not user_id:
            raise ValueError("user_id is required for add_task")

        from database.session import Session, engine
        db = Session(engine)
        try:
            # Create new task
            task = Todo(
                id=uuid4(),
                user_id=UUID(user_id),
                title=title,
                description=description,
                status="pending",
                due_date=datetime.fromisoformat(due_date.replace('Z', '+00:00')) if due_date else None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return {
                "task_id": str(task.id),
                "title": task.title,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "message": f"Todo '{task.title}' created successfully"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    async def list_tasks(self, status: str = "all", limit: int = 20,
                        user_id: str = None) -> Dict[str, Any]:
        """List tasks for a user with optional filtering"""
        if not user_id:
            raise ValueError("user_id is required for list_tasks")

        from database.session import Session, engine
        db = Session(engine)
        try:
            query = db.query(Todo).filter(Todo.user_id == UUID(user_id))

            if status != "all":
                query = query.filter(Todo.status == status)

            tasks = query.order_by(Todo.created_at.desc()).limit(limit).all()
            total_count = query.count()

            task_list = []
            for task in tasks:
                task_dict = {
                    "task_id": str(task.id),
                    "title": task.title,
                    "status": task.status,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat()
                }
                task_list.append(task_dict)

            return {
                "tasks": task_list,
                "total_count": total_count,
                "message": f"Found {len(task_list)} {'matching' if status != 'all' else ''} task(s)"
            }
        finally:
            db.close()

    async def complete_task(self, task_id: str = None, task_title: str = None,
                          user_id: str = None) -> Dict[str, Any]:
        """Complete a task by ID or title"""
        if not user_id:
            raise ValueError("user_id is required for complete_task")

        from database.session import Session, engine
        db = Session(engine)
        try:
            # Find task by ID or title
            task = None
            if task_id:
                task = db.query(Todo).filter(
                    Todo.id == UUID(task_id),
                    Todo.user_id == UUID(user_id)
                ).first()
            elif task_title:
                task = db.query(Todo).filter(
                    Todo.title == task_title,
                    Todo.user_id == UUID(user_id)
                ).first()

            if not task:
                raise ValueError(f"No task found with the specified ID or title")

            if task.status == "completed":
                raise ValueError("Todo is already marked as completed")

            # Update task status
            task.status = "completed"
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)

            return {
                "task_id": str(task.id),
                "title": task.title,
                "status": task.status,
                "completed_at": task.updated_at.isoformat(),
                "message": f"Todo '{task.title}' marked as completed"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    async def update_task(self, task_id: str = None, task_title: str = None,
                         new_title: str = None, new_description: str = None,
                         new_due_date: str = None, new_status: str = None,
                         user_id: str = None) -> Dict[str, Any]:
        """Update a task's details"""
        if not user_id:
            raise ValueError("user_id is required for update_task")

        # Check if any update parameters are provided
        updates_provided = any([
            new_title is not None,
            new_description is not None,
            new_due_date is not None,
            new_status is not None
        ])

        if not updates_provided:
            raise ValueError("No changes specified for update")

        from database.session import Session, engine
        db = Session(engine)
        try:
            # Find task by ID or title
            task = None
            if task_id:
                task = db.query(Todo).filter(
                    Todo.id == UUID(task_id),
                    Todo.user_id == UUID(user_id)
                ).first()
            elif task_title:
                task = db.query(Todo).filter(
                    Todo.title == task_title,
                    Todo.user_id == UUID(user_id)
                ).first()

            if not task:
                raise ValueError(f"No task found with the specified ID or title")

            # Apply updates
            if new_title is not None:
                task.title = new_title
            if new_description is not None:
                task.description = new_description
            if new_due_date is not None:
                task.due_date = datetime.fromisoformat(new_due_date.replace('Z', '+00:00'))
            if new_status is not None:
                task.status = new_status
            task.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(task)

            return {
                "task_id": str(task.id),
                "title": task.title,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "updated_at": task.updated_at.isoformat(),
                "message": "Todo updated successfully"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    async def delete_task(self, task_id: str = None, task_title: str = None,
                         delete_completed: bool = False, user_id: str = None) -> Dict[str, Any]:
        """Delete a task by ID or title, or delete all completed tasks"""
        if not user_id:
            raise ValueError("user_id is required for delete_task")

        from database.session import Session, engine
        db = Session(engine)
        try:
            deleted_tasks = []

            if delete_completed:
                # Delete all completed tasks for the user
                completed_tasks = db.query(Todo).filter(
                    Todo.user_id == UUID(user_id),
                    Todo.status == "completed"
                ).all()

                for task in completed_tasks:
                    deleted_tasks.append(task.title)

                delete_count = len(completed_tasks)

                # Actually delete the tasks
                for task in completed_tasks:
                    db.delete(task)

            else:
                # Delete specific task by ID or title
                task = None
                if task_id:
                    task = db.query(Todo).filter(
                        Todo.id == UUID(task_id),
                        Todo.user_id == UUID(user_id)
                    ).first()
                elif task_title:
                    task = db.query(Todo).filter(
                        Todo.title == task_title,
                        Todo.user_id == UUID(user_id)
                    ).first()

                if not task:
                    raise ValueError(f"No task found with the specified ID or title")

                deleted_tasks = [task.title]
                delete_count = 1

                # Delete the task
                db.delete(task)

            db.commit()

            return {
                "deleted_count": delete_count,
                "deleted_tasks": deleted_tasks,
                "message": f"Deleted {delete_count} task(s)" if delete_completed else f"Todo '{deleted_tasks[0]}' deleted successfully"
            }
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_app(self):
        """Get the MCP server instance"""
        return self

    def get_tool_names(self):
        """Get list of available tool names"""
        return list(self.tools.keys())

    def get_tool(self, name: str):
        """Get a specific tool by name"""
        return self.tools.get(name)