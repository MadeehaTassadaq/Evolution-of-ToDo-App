"""
Command parser for the Phase I Console Todo Application.

Parses user input into structured command objects.
"""

import argparse
import shlex
from typing import Optional, Dict, Any


class CommandParser:
    """
    Parse console commands into structured data.

    Supports commands: add, list, update, delete, complete, help, exit
    """

    def __init__(self):
        """Initialize command parser with argparse subparsers."""
        self.parser = argparse.ArgumentParser(
            prog='todo',
            description='Phase I Console Todo Application',
            add_help=False
        )

        self.subparsers = self.parser.add_subparsers(
            dest='command',
            help='Available commands'
        )

        # Add command
        self.add_parser = self.subparsers.add_parser(
            'add',
            help='Add a new task'
        )
        self.add_parser.add_argument(
            'title',
            nargs='+',
            help='Task title'
        )
        self.add_parser.add_argument(
            '--description', '-d',
            help='Task description'
        )
        self.add_parser.add_argument(
            '--priority', '-p',
            choices=['high', 'medium', 'low'],
            help='Task priority'
        )
        self.add_parser.add_argument(
            '--tags', '-t',
            nargs='+',
            help='Task tags (space-separated)'
        )
        self.add_parser.add_argument(
            '--due-date',
            help='Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)'
        )
        self.add_parser.add_argument(
            '--recurrence',
            choices=['daily', 'weekly', 'monthly', 'yearly'],
            help='Recurrence interval'
        )

        # List command
        self.list_parser = self.subparsers.add_parser(
            'list',
            help='List all tasks'
        )

        # Update command
        self.update_parser = self.subparsers.add_parser(
            'update',
            help='Update a task'
        )
        self.update_parser.add_argument(
            'task_id',
            help='Task ID (can use short form: first 8 characters)'
        )
        self.update_parser.add_argument(
            '--title',
            nargs='+',
            help='New task title'
        )
        self.update_parser.add_argument(
            '--description', '-d',
            help='New task description'
        )
        self.update_parser.add_argument(
            '--priority', '-p',
            choices=['high', 'medium', 'low', 'none'],
            help='New task priority (use "none" to clear)'
        )

        # Delete command
        self.delete_parser = self.subparsers.add_parser(
            'delete',
            help='Delete a task'
        )
        self.delete_parser.add_argument(
            'task_id',
            help='Task ID (can use short form: first 8 characters)'
        )

        # Complete command
        self.complete_parser = self.subparsers.add_parser(
            'complete',
            help='Toggle task completion status'
        )
        self.complete_parser.add_argument(
            'task_id',
            help='Task ID (can use short form: first 8 characters)'
        )

        # Help command
        self.help_parser = self.subparsers.add_parser(
            'help',
            help='Show help message'
        )

        # Exit command
        self.exit_parser = self.subparsers.add_parser(
            'exit',
            help='Exit the application'
        )

        # Search command
        self.search_parser = self.subparsers.add_parser(
            'search',
            help='Search tasks'
        )
        self.search_parser.add_argument(
            'keyword',
            nargs='+',
            help='Search keyword'
        )

        # Filter command
        self.filter_parser = self.subparsers.add_parser(
            'filter',
            help='Filter tasks'
        )
        self.filter_parser.add_argument(
            'filter_by',
            choices=['status', 'priority', 'tag'],
            help='Filter by status, priority, or tag'
        )
        self.filter_parser.add_argument(
            'value',
            help='Filter value'
        )

        # Sort command
        self.sort_parser = self.subparsers.add_parser(
            'sort',
            help='Sort tasks'
        )
        self.sort_parser.add_argument(
            'sort_by',
            choices=['due_date', 'priority', 'title'],
            help='Sort by due_date, priority, or title'
        )

        # Tag command
        self.tag_parser = self.subparsers.add_parser(
            'tag',
            help='Add or remove tags from a task'
        )
        self.tag_parser.add_argument(
            'task_id',
            help='Task ID'
        )
        self.tag_parser.add_argument(
            'action',
            choices=['add', 'remove'],
            help='Action to perform'
        )
        self.tag_parser.add_argument(
            'tags',
            nargs='+',
            help='Tags to add or remove'
        )

        # Overdue command
        self.overdue_parser = self.subparsers.add_parser(
            'overdue',
            help='List overdue tasks'
        )

        # Upcoming command
        self.upcoming_parser = self.subparsers.add_parser(
            'upcoming',
            help='List upcoming tasks'
        )
        self.upcoming_parser.add_argument(
            'hours',
            type=int,
            nargs='?',
            default=24,
            help='Number of hours to check for upcoming tasks (default: 24)'
        )

    def parse(self, input_string: str) -> Optional[Dict[str, Any]]:
        """
        Parse user input string into command dictionary.

        Args:
            input_string: User input from console

        Returns:
            Dict with command details, or None if parsing fails

        Examples:
            >>> parser = CommandParser()
            >>> cmd = parser.parse("add Buy groceries --priority high")
            >>> cmd['command']
            'add'
            >>> cmd['title']
            'Buy groceries'
            >>> cmd['priority']
            'high'
        """
        if not input_string or not input_string.strip():
            return None

        try:
            # Split command respecting quotes
            args = shlex.split(input_string)

            # Parse arguments
            parsed = self.parser.parse_args(args)

            # Convert to dictionary
            result = vars(parsed)

            # Post-process specific fields
            if 'title' in result and isinstance(result['title'], list):
                result['title'] = ' '.join(result['title'])
            if 'keyword' in result and isinstance(result['keyword'], list):
                result['keyword'] = ' '.join(result['keyword'])

            # Handle priority "none" as None
            if result.get('priority') == 'none':
                result['priority'] = None

            return result

        except SystemExit:
            # argparse calls sys.exit on error, catch and return None
            return None
        except Exception:
            return None

    def get_help(self) -> str:
        """
        Get help message for all commands.

        Returns:
            str: Formatted help text
        """
        help_text = """
Available Commands:
==================

add <title> [options]
    Add a new task
    Options:
        --description, -d <text>     Task description
        --priority, -p <level>       Priority: high, medium, low
        --tags, -t <tag1> <tag2>     Tags (space-separated)
        --due-date <date>            Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)

    Examples:
        add Buy groceries
        add "Write report" --priority high --tags work urgent
        add "Team meeting" --due-date "2026-01-15 14:00"

list
    List all tasks

    Example:
        list

update <task_id> [options]
    Update an existing task
    Options:
        --title <text>               New title
        --description, -d <text>     New description
        --priority, -p <level>       New priority (use "none" to clear)

    Examples:
        update abc123 --title "New title"
        update abc123 --priority high

delete <task_id>
    Delete a task

    Example:
        delete abc123

complete <task_id>
    Toggle task completion status

    Example:
        complete abc123

help
    Show this help message

exit, quit, q
    Exit the application

Notes:
- Task IDs can be shortened to first 8 characters
- Use quotes for titles/descriptions with spaces
- Commands are case-insensitive
"""
        return help_text
