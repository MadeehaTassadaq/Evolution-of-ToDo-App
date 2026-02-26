#!/usr/bin/env python3
"""
Demo script to showcase the interactive UI features.

Run this to see the interactive interface in action.
"""

from src.models.task_list import TaskList
from src.services.task_service import TaskService
from src.services.search_service import SearchService
from src.services.recurrence_service import RecurrenceService
from src.cli.renderer import Renderer
from src.cli.interactive import InteractiveUI


def main():
    """Run the interactive todo application."""
    print("🚀 Starting Interactive Console Todo Application...")
    print("=" * 80)
    print()
    print("KEY FEATURES:")
    print("  ✓ Visible menu - all options shown on screen")
    print("  ✓ Numbered tasks - select by number (1, 2, 3...), no IDs to remember")
    print("  ✓ Guided prompts - step-by-step instructions for every action")
    print("  ✓ Self-explanatory - no help command needed")
    print("  ✓ Confirmation prompts - safe delete operations")
    print("  ✓ Visual feedback - clear success/error messages with emojis")
    print()
    print("=" * 80)
    input("\nPress Enter to launch the app...")

    # Initialize components
    task_list = TaskList()
    recurrence_service = RecurrenceService()
    task_service = TaskService(task_list, recurrence_service)
    search_service = SearchService()
    renderer = Renderer()

    # Launch interactive UI
    ui = InteractiveUI(task_service, search_service, renderer)
    ui.run()


if __name__ == "__main__":
    main()
