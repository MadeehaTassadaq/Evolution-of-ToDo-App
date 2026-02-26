"""
Message Parser for Todo AI Chatbot
Handles natural language processing for task management commands
"""

import re
from typing import Dict, Optional, List
from datetime import datetime


class MessageParser:
    """
    Parses natural language messages to extract task management intents
    """

    def __init__(self):
        # Define patterns for different task operations
        self.patterns = {
            # Task creation patterns
            'create_task': [
                r"create.*task.*\"([^\"]+)\"",
                r"add.*task.*\"([^\"]+)\"",
                r"make.*task.*\"([^\"]+)\"",
                r"new.*task.*\"([^\"]+)\"",
                r"create.*\"([^\"]+)\"",
                r"add.*\"([^\"]+)\"",
            ],

            # Task listing patterns
            'list_tasks': [
                r"show.*my.*tasks?",
                r"list.*my.*tasks?",
                r"what.*tasks?",
                r"my.*tasks?",
                r"view.*tasks?",
                r"see.*tasks?",
                r"all.*tasks?",
                r"pending.*tasks?",
                r"incomplete.*tasks?",
                r"completed.*tasks?",
            ],

            # Task completion patterns
            'complete_task': [
                r"complete.*\"([^\"]+)\"",
                r"finish.*\"([^\"]+)\"",
                r"done.*\"([^\"]+)\"",
                r"mark.*\"([^\"]+)\".*complete",
                r"mark.*\"([^\"]+)\".*done",
                r"check.*off.*\"([^\"]+)\"",
            ],

            # Task update patterns
            'update_task': [
                r"update.*\"([^\"]+)\".*to.*\"([^\"]+)\"",
                r"change.*\"([^\"]+)\".*to.*\"([^\"]+)\"",
                r"edit.*\"([^\"]+)\".*to.*\"([^\"]+)\"",
            ],

            # Task deletion patterns
            'delete_task': [
                r"delete.*\"([^\"]+)\"",
                r"remove.*\"([^\"]+)\"",
                r"erase.*\"([^\"]+)\"",
                r"get rid of.*\"([^\"]+)\"",
            ]
        }

    def parse_message(self, message: str) -> Dict[str, any]:
        """
        Parse a message and extract intent and parameters

        Args:
            message: The user's natural language message

        Returns:
            Dictionary containing the intent and extracted parameters
        """
        message_lower = message.lower().strip()

        # Check for task creation
        for pattern in self.patterns['create_task']:
            match = re.search(pattern, message_lower)
            if match:
                task_title = match.group(1) if len(match.groups()) > 0 else self._extract_task_title(message)
                return {
                    'intent': 'create_task',
                    'parameters': {'title': task_title}
                }

        # Check for task listing
        for pattern in self.patterns['list_tasks']:
            if re.search(pattern, message_lower):
                status_filter = 'all'
                if 'pending' in message_lower or 'incomplete' in message_lower:
                    status_filter = 'pending'
                elif 'completed' in message_lower:
                    status_filter = 'completed'

                return {
                    'intent': 'list_tasks',
                    'parameters': {'status': status_filter}
                }

        # Check for task completion
        for pattern in self.patterns['complete_task']:
            match = re.search(pattern, message_lower)
            if match:
                task_identifier = match.group(1) if len(match.groups()) > 0 else self._extract_task_title(message)
                return {
                    'intent': 'complete_task',
                    'parameters': {'task_title': task_identifier}
                }

        # Check for task deletion
        for pattern in self.patterns['delete_task']:
            match = re.search(pattern, message_lower)
            if match:
                task_identifier = match.group(1) if len(match.groups()) > 0 else self._extract_task_title(message)
                return {
                    'intent': 'delete_task',
                    'parameters': {'task_title': task_identifier}
                }

        # Check for task update
        for pattern in self.patterns['update_task']:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) >= 2:
                    old_title = match.group(1)
                    new_title = match.group(2)
                    return {
                        'intent': 'update_task',
                        'parameters': {
                            'task_title': old_title,
                            'new_title': new_title
                        }
                    }

        # Check for task search
        search_patterns = [
            r"find.*(?:task|todo).*about.*(.+)",
            r"search.*for.*(?:task|todo).*['\"](.+?)['\"]",
            r"look.*for.*(?:task|todo).*['\"](.+?)['\"]",
            r"find.*tasks.*about.*(.+)",
            r"search.*my.*tasks.*for.*(.+)",
            r"got.*any.*tasks.*about.*(.+)",
            r"find.*['\"](.+?)['\"]",
            r"search.*['\"](.+?)['\"]"
        ]

        for pattern in search_patterns:
            match = re.search(pattern, message_lower)
            if match:
                query = match.group(1) if len(match.groups()) > 0 else message.strip()
                return {
                    'intent': 'search_tasks',
                    'parameters': {'query': query}
                }

        # If no specific pattern matched, treat as general query
        return {
            'intent': 'unknown',
            'parameters': {'raw_message': message}
        }

    def _extract_task_title(self, message: str) -> Optional[str]:
        """
        Extract task title from message using heuristics
        """
        # Look for quoted text
        quote_match = re.search(r'"([^"]*)"', message)
        if quote_match:
            return quote_match.group(1)

        # Look for text after certain keywords
        keywords = ['create', 'add', 'make', 'new', 'task']
        for keyword in keywords:
            idx = message.lower().find(keyword)
            if idx != -1:
                # Get the text after the keyword
                remainder = message[idx + len(keyword):].strip()
                # Take the first sentence or phrase
                parts = re.split(r'[.!?;,]', remainder)
                title = parts[0].strip()
                if len(title) > 0:
                    return title

        # If all else fails, return the entire message (trimmed)
        return message.strip()[:100]  # Limit length


# Singleton instance
message_parser = MessageParser()


def parse_message(message: str) -> Dict[str, any]:
    """
    Convenience function to parse a message

    Args:
        message: The user's natural language message

    Returns:
        Dictionary containing the intent and extracted parameters
    """
    return message_parser.parse_message(message)