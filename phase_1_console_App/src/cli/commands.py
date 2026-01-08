"""
Command handlers for the Phase I Console Todo Application.

Maps parsed commands to service operations and renders output.
"""

from typing import Dict, Any
from src.services.task_service import TaskService
from src.services.search_service import SearchService
from src.cli.renderer import Renderer
from src.lib.validators import ValidationError


class CommandHandler:
    """
    Handle CLI commands by coordinating service and renderer.

    Attributes:
        service: TaskService instance for business logic
        search_service: SearchService instance for search, filter, and sort
        renderer: Renderer instance for output formatting
    """

    def __init__(self, service: TaskService, search_service: SearchService, renderer: Renderer):
        """
        Initialize command handler.

        Args:
            service: TaskService instance
            search_service: SearchService instance
            renderer: Renderer instance
        """
        self.service = service
        self.search_service = search_service
        self.renderer = renderer

    def handle_add(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'add' command to create a new task.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - title: str (required)
                - description: str (optional)
                - priority: str (optional)
                - tags: list (optional)
                - due_date: str (optional)

        Returns:
            str: Formatted success or error message

        Examples:
            >>> from src.models.task_list import TaskList
            >>> from src.services.task_service import TaskService
            >>> from src.cli.renderer import Renderer
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> renderer = Renderer()
            >>> handler = CommandHandler(service, renderer)
            >>> cmd = {'command': 'add', 'title': 'Buy groceries', 'priority': 'high'}
            >>> result = handler.handle_add(cmd)
            >>> "Task created successfully" in result
            True
        """
        try:
            title = parsed_command.get('title')
            description = parsed_command.get('description')
            priority = parsed_command.get('priority')
            tags = parsed_command.get('tags')
            due_date = parsed_command.get('due_date')

            task = self.service.create_task(
                title=title,
                description=description,
                priority=priority,
                tags=tags,
                due_date=due_date
            )

            message = f"Task created successfully: '{task.title}' (ID: {task.id[:8]})"
            return self.renderer.render_success(message)

        except ValidationError as e:
            return self.renderer.render_error(str(e))
        except Exception as e:
            return self.renderer.render_error(f"Failed to create task: {str(e)}")

    def handle_list(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'list' command to display all tasks.

        Args:
            parsed_command: Parsed command dictionary (no arguments needed)

        Returns:
            str: Formatted task list or empty message

        Examples:
            >>> from src.models.task_list import TaskList
            >>> from src.services.task_service import TaskService
            >>> from src.cli.renderer import Renderer
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> renderer = Renderer()
            >>> handler = CommandHandler(service, renderer)
            >>> service.create_task("Task 1")
            >>> service.create_task("Task 2")
            >>> result = handler.handle_list({})
            >>> "Task 1" in result
            True
            >>> "Task 2" in result
            True
        """
        try:
            tasks = self.service.get_all_tasks()
            return self.renderer.render_task_list(tasks)

        except Exception as e:
            return self.renderer.render_error(f"Failed to list tasks: {str(e)}")

    def handle_update(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'update' command to modify an existing task.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - task_id: str (required)
                - title: str (optional)
                - description: str (optional)
                - priority: str (optional)

        Returns:
            str: Formatted success or error message

        Examples:
            >>> from src.models.task_list import TaskList
            >>> from src.services.task_service import TaskService
            >>> from src.cli.renderer import Renderer
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> renderer = Renderer()
            >>> handler = CommandHandler(service, renderer)
            >>> task = service.create_task("Original title")
            >>> cmd = {'command': 'update', 'task_id': task.id[:8],
            ...        'title': 'New title'}
            >>> result = handler.handle_update(cmd)
            >>> "Task updated successfully" in result
            True
        """
        try:
            task_id = parsed_command.get('task_id')
            if not task_id:
                return self.renderer.render_error("Task ID is required")

            # Find task by short ID (first 8 characters)
            task = self._find_task_by_short_id(task_id)
            if task is None:
                return self.renderer.render_error(f"Task with ID '{task_id}' not found")

            # Prepare updates
            updates = {}
            if 'title' in parsed_command and parsed_command['title']:
                updates['title'] = parsed_command['title']
            if 'description' in parsed_command:
                updates['description'] = parsed_command['description']
            if 'priority' in parsed_command:
                updates['priority'] = parsed_command['priority']

            if not updates:
                return self.renderer.render_warning("No updates provided")

            # Apply updates
            updated_task = self.service.update_task(task.id, **updates)

            message = f"Task updated successfully: '{updated_task.title}' (ID: {updated_task.id[:8]})"
            return self.renderer.render_success(message)

        except ValidationError as e:
            return self.renderer.render_error(str(e))
        except KeyError as e:
            return self.renderer.render_error(str(e))
        except Exception as e:
            return self.renderer.render_error(f"Failed to update task: {str(e)}")

    def handle_delete(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'delete' command to remove a task.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - task_id: str (required)

        Returns:
            str: Formatted success or error message

        Examples:
            >>> from src.models.task_list import TaskList
            >>> from src.services.task_service import TaskService
            >>> from src.cli.renderer import Renderer
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> renderer = Renderer()
            >>> handler = CommandHandler(service, renderer)
            >>> task = service.create_task("To be deleted")
            >>> cmd = {'command': 'delete', 'task_id': task.id[:8]}
            >>> result = handler.handle_delete(cmd)
            >>> "Task deleted successfully" in result
            True
        """
        try:
            task_id = parsed_command.get('task_id')
            if not task_id:
                return self.renderer.render_error("Task ID is required")

            # Find task by short ID
            task = self._find_task_by_short_id(task_id)
            if task is None:
                return self.renderer.render_error(f"Task with ID '{task_id}' not found")

            task_title = task.title
            task_short_id = task.id[:8]

            # Delete task
            self.service.delete_task(task.id)

            message = f"Task deleted successfully: '{task_title}' (ID: {task_short_id})"
            return self.renderer.render_success(message)

        except KeyError as e:
            return self.renderer.render_error(str(e))
        except Exception as e:
            return self.renderer.render_error(f"Failed to delete task: {str(e)}")

    def handle_complete(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'complete' command to toggle task completion status.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - task_id: str (required)

        Returns:
            str: Formatted success or error message

        Examples:
            >>> from src.models.task_list import TaskList
            >>> from src.services.task_service import TaskService
            >>> from src.cli.renderer import Renderer
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> renderer = Renderer()
            >>> handler = CommandHandler(service, renderer)
            >>> task = service.create_task("Test task")
            >>> cmd = {'command': 'complete', 'task_id': task.id[:8]}
            >>> result = handler.handle_complete(cmd)
            >>> "marked as completed" in result
            True
        """
        try:
            task_id = parsed_command.get('task_id')
            if not task_id:
                return self.renderer.render_error("Task ID is required")

            # Find task by short ID
            task = self._find_task_by_short_id(task_id)
            if task is None:
                return self.renderer.render_error(f"Task with ID '{task_id}' not found")

            # Toggle completion
            updated_task = self.service.toggle_complete(task.id)

            status = "completed" if updated_task.completed else "pending"
            message = f"Task '{updated_task.title}' (ID: {updated_task.id[:8]}) marked as {status}"
            return self.renderer.render_success(message)

        except KeyError as e:
            return self.renderer.render_error(str(e))
        except Exception as e:
            return self.renderer.render_error(f"Failed to complete task: {str(e)}")

    def handle_help(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'help' command to display usage information.

        Args:
            parsed_command: Parsed command dictionary (no arguments needed)

        Returns:
            str: Formatted help text
        """
        from src.cli.parser import CommandParser
        parser = CommandParser()
        return parser.get_help()

    def handle_exit(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'exit' command to quit the application.

        Args:
            parsed_command: Parsed command dictionary (no arguments needed)

        Returns:
            str: Exit message
        """
        return "Goodbye!"

    def _find_task_by_short_id(self, short_id: str):
        """
        Find a task by short ID (first 8 characters).

        Args:
            short_id: Short task ID (at least 8 characters)

        Returns:
            Task object if found, None otherwise

        Examples:
            >>> from src.models.task_list import TaskList
            >>> from src.services.task_service import TaskService
            >>> from src.cli.renderer import Renderer
            >>> task_list = TaskList()
            >>> service = TaskService(task_list)
            >>> renderer = Renderer()
            >>> handler = CommandHandler(service, renderer)
            >>> task = service.create_task("Test task")
            >>> found = handler._find_task_by_short_id(task.id[:8])
            >>> found.title
            'Test task'
        """
        all_tasks = self.service.get_all_tasks()
        for task in all_tasks:
            if task.id.startswith(short_id):
                return task
        return None

    def handle_search(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'search' command to find tasks by keyword.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - keyword: str (required)

        Returns:
            str: Formatted list of matching tasks
        """
        try:
            keyword = parsed_command.get('keyword')
            if not keyword:
                return self.renderer.render_error("Search keyword is required")

            tasks = self.service.get_all_tasks()
            results = self.search_service.search_tasks(tasks, ' '.join(keyword))
            return self.renderer.render_task_list(results)

        except Exception as e:
            return self.renderer.render_error(f"Failed to search tasks: {str(e)}")

    def handle_filter(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'filter' command to filter tasks.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - filter_by: str (required)
                - value: str (required)

        Returns:
            str: Formatted list of matching tasks
        """
        try:
            filter_by = parsed_command.get('filter_by')
            value = parsed_command.get('value')
            if not filter_by or not value:
                return self.renderer.render_error("Filter type and value are required")

            tasks = self.service.get_all_tasks()
            if filter_by == 'status':
                results = self.search_service.filter_by_status(tasks, value.lower() == 'completed')
            elif filter_by == 'priority':
                results = self.search_service.filter_by_priority(tasks, value)
            elif filter_by == 'tag':
                results = self.search_service.filter_by_tag(tasks, value)
            else:
                return self.renderer.render_error(f"Invalid filter type: {filter_by}")

            return self.renderer.render_task_list(results)

        except Exception as e:
            return self.renderer.render_error(f"Failed to filter tasks: {str(e)}")

    def handle_sort(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'sort' command to sort tasks.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - sort_by: str (required)

        Returns:
            str: Formatted list of sorted tasks
        """
        try:
            sort_by = parsed_command.get('sort_by')
            if not sort_by:
                return self.renderer.render_error("Sort criterion is required")

            tasks = self.service.get_all_tasks()
            if sort_by == 'due_date':
                results = self.search_service.sort_by_due_date(tasks)
            elif sort_by == 'priority':
                results = self.search_service.sort_by_priority(tasks)
            elif sort_by == 'title':
                results = self.search_service.sort_by_title(tasks)
            else:
                return self.renderer.render_error(f"Invalid sort criterion: {sort_by}")

            return self.renderer.render_task_list(results)

        except Exception as e:
            return self.renderer.render_error(f"Failed to sort tasks: {str(e)}")

    def handle_tag(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'tag' command to add or remove tags from a task.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - task_id: str (required)
                - action: str (required: 'add' or 'remove')
                - tags: list (required)

        Returns:
            str: Formatted success or error message
        """
        try:
            task_id = parsed_command.get('task_id')
            action = parsed_command.get('action')
            tags = parsed_command.get('tags')

            if not task_id or not action or not tags:
                return self.renderer.render_error("Task ID, action, and tags are required")

            task = self._find_task_by_short_id(task_id)
            if task is None:
                return self.renderer.render_error(f"Task with ID '{task_id}' not found")

            if action == 'add':
                for tag in tags:
                    self.service.add_tag(task.id, tag)
                message = f"Tags added to task '{task.title}'"
            elif action == 'remove':
                for tag in tags:
                    self.service.remove_tag(task.id, tag)
                message = f"Tags removed from task '{task.title}'"
            else:
                return self.renderer.render_error(f"Invalid tag action: {action}")

            return self.renderer.render_success(message)

        except KeyError as e:
            return self.renderer.render_error(str(e))
        except Exception as e:
            return self.renderer.render_error(f"Failed to modify tags: {str(e)}")

    def handle_overdue(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'overdue' command to list overdue tasks.

        Args:
            parsed_command: Parsed command dictionary

        Returns:
            str: Formatted list of overdue tasks
        """
        try:
            tasks = self.service.get_all_tasks()
            results = self.search_service.get_overdue_tasks(tasks)
            return self.renderer.render_task_list(results)

        except Exception as e:
            return self.renderer.render_error(f"Failed to get overdue tasks: {str(e)}")

    def handle_upcoming(self, parsed_command: Dict[str, Any]) -> str:
        """
        Handle 'upcoming' command to list upcoming tasks.

        Args:
            parsed_command: Parsed command dictionary with keys:
                - hours: int (optional)

        Returns:
            str: Formatted list of upcoming tasks
        """
        try:
            hours = parsed_command.get('hours', 24)
            tasks = self.service.get_all_tasks()
            results = self.search_service.get_upcoming_tasks(tasks, hours)
            return self.renderer.render_task_list(results)

        except Exception as e:
            return self.renderer.render_error(f"Failed to get upcoming tasks: {str(e)}")
