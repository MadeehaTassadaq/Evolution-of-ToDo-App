#!/usr/bin/env python3
"""
Phase I Console Todo Application - Main Entry Point

This is the entry point for the in-memory Python console todo application.
It provides an interactive menu-driven interface for task management.
"""

from src.models.task_list import TaskList
from src.services.task_service import TaskService
from src.services.search_service import SearchService
from src.services.recurrence_service import RecurrenceService
from src.cli.renderer import Renderer
from src.cli.interactive import InteractiveUI


def main():
    """
    Main entry point - Interactive menu-driven task management.

    Initializes the application components and runs the interactive UI.
    Features:
    - Visible menu showing all options
    - Numbered task selection (no memorizing IDs)
    - Guided prompts for all inputs
    - Self-explanatory interface (no help command needed)
    """
    # Initialize application components
    task_list = TaskList()
    recurrence_service = RecurrenceService()
    task_service = TaskService(task_list, recurrence_service)
    search_service = SearchService()
    renderer = Renderer()

    # Create and run interactive UI
    ui = InteractiveUI(task_service, search_service, renderer)
    ui.run()


if __name__ == "__main__":
    main()
