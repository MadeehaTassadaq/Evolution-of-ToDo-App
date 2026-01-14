"""
Update Parameter Extractor for Todo AI Chatbot
Extracts update parameters from natural language requests
"""

import re
from typing import Dict, Optional, Tuple
from datetime import datetime


class UpdateExtractor:
    """
    Extracts update parameters from natural language update requests
    """

    def __init__(self):
        # Patterns for extracting different types of updates
        self.update_patterns = {
            'title_change': [
                r"change.*(?:title|name|heading).*['\"](.+?)['\"].*to.*['\"](.+?)['\"]",
                r"update.*(?:title|name|heading).*['\"](.+?)['\"].*to.*['\"](.+?)['\"]",
                r"rename.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]",
                r"modify.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]",
            ],

            'due_date_change': [
                r"change.*due.*date.*['\"](.+?)['\"].*to.*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})",
                r"update.*due.*date.*['\"](.+?)['\"].*to.*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})",
                r"set.*due.*date.*for.*['\"](.+?)['\"].*to.*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})",
                r"move.*['\"](.+?)['\"].*to.*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})",
            ],

            'status_change': [
                r"mark.*['\"](.+?)['\"].*(?:as|to).*completed",
                r"mark.*['\"](.+?)['\"].*(?:as|to).*done",
                r"complete.*['\"](.+?)['\"]",
                r"finish.*['\"](.+?)['\"]",
                r"reopen.*['\"](.+?)['\"]",
                r"mark.*['\"](.+?)['\"].*(?:as|to).*pending",
                r"uncomplete.*['\"](.+?)['\"]",
            ],

            'description_change': [
                r"update.*description.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]",
                r"change.*description.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]",
                r"add.*description.*['\"](.+?)['\"].*['\"](.+?)['\"]",
            ]
        }

    def extract_update_params(self, message: str) -> Dict[str, any]:
        """
        Extract update parameters from a natural language message

        Args:
            message: Natural language update request

        Returns:
            Dictionary containing the original task identifier and update parameters
        """
        message_lower = message.lower().strip()

        # Try to identify the type of update
        for update_type, patterns in self.update_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    groups = match.groups()

                    if update_type == 'title_change':
                        if len(groups) >= 2:
                            return {
                                'task_title': groups[0],
                                'new_title': groups[1]
                            }
                    elif update_type == 'due_date_change':
                        if len(groups) >= 2:
                            # Parse the date
                            date_str = groups[1]
                            parsed_date = self._parse_date(date_str)

                            return {
                                'task_title': groups[0],
                                'new_due_date': parsed_date.isoformat() if parsed_date else None
                            }
                    elif update_type == 'status_change':
                        if len(groups) >= 1:
                            task_title = groups[0]

                            # Determine the new status based on the message
                            if 'completed' in message_lower or 'done' in message_lower or 'finish' in message_lower or 'complete' in message_lower:
                                new_status = 'completed'
                            elif 'reopen' in message_lower or 'pending' in message_lower or 'uncomplete' in message_lower:
                                new_status = 'pending'
                            else:
                                # Try to infer from the message
                                new_status = 'completed'  # Default to completed for completion verbs

                            return {
                                'task_title': task_title,
                                'new_status': new_status
                            }
                    elif update_type == 'description_change':
                        if len(groups) >= 2:
                            return {
                                'task_title': groups[0],
                                'new_description': groups[1]
                            }

        # If no specific pattern matched, try a more general approach
        return self._extract_general_update(message)

    def _extract_general_update(self, message: str) -> Dict[str, any]:
        """
        Extract update parameters using a more general approach

        Args:
            message: Natural language update request

        Returns:
            Dictionary containing extracted parameters
        """
        message_lower = message.lower().strip()

        # Try to extract quoted strings (likely task title and new value)
        quotes = re.findall(r"['\"](.+?)['\"]", message)

        # Extract date if present
        date_match = re.search(r"([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4}|[0-9]{4}-[0-9]{2}-[0-9]{2})", message)
        date_str = date_match.group(1) if date_match else None
        parsed_date = self._parse_date(date_str) if date_str else None

        # Determine intent based on keywords
        if 'completed' in message_lower or 'done' in message_lower or 'finish' in message_lower or 'complete' in message_lower:
            # Likely a status change
            if len(quotes) >= 1:
                return {
                    'task_title': quotes[0],
                    'new_status': 'completed'
                }
        elif 'pending' in message_lower or 'reopen' in message_lower or 'uncomplete' in message_lower:
            # Likely changing status to pending
            if len(quotes) >= 1:
                return {
                    'task_title': quotes[0],
                    'new_status': 'pending'
                }
        elif len(quotes) >= 2:
            # Likely a title change
            return {
                'task_title': quotes[0],
                'new_title': quotes[1]
            }
        elif len(quotes) == 1 and parsed_date:
            # Likely setting a due date for a task
            return {
                'task_title': quotes[0],
                'new_due_date': parsed_date.isoformat()
            }

        # If we can't determine the update clearly, return the first quoted string as task identifier
        if quotes:
            return {
                'task_title': quotes[0]
            }

        # If no quotes, try to extract the task title from the message
        return {
            'task_title': self._extract_task_title_from_message(message)
        }

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse various date formats into a datetime object

        Args:
            date_str: Date string in various formats

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_str:
            return None

        # List of possible date formats to try
        formats = [
            "%Y-%m-%d",      # 2023-12-25
            "%m/%d/%Y",      # 12/25/2023
            "%m-%d-%Y",      # 12-25-2023
            "%d/%m/%Y",      # 25/12/2023
            "%d-%m-%Y",      # 25-12-2023
            "%m/%d/%y",      # 12/25/23
            "%m-%d-%y",      # 12-25-23
            "%d/%m/%y",      # 25/12/23
            "%d-%m-%y",      # 25-12-23
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # If none of the formats worked, return None
        return None

    def _extract_task_title_from_message(self, message: str) -> str:
        """
        Extract task title from message when no quotes are available

        Args:
            message: The original message

        Returns:
            Extracted task title
        """
        # Look for text after common action words
        action_words = ['update', 'change', 'modify', 'edit', 'adjust', 'alter', 'revise']

        for word in action_words:
            idx = message.lower().find(word)
            if idx != -1:
                # Get everything after the action word
                remainder = message[idx + len(word):].strip()

                # Stop at common prepositions or punctuation
                remainder = re.split(r'[.,;:!?]| for | to | the | that ', remainder)[0].strip()

                if len(remainder) > 0:
                    return remainder

        # If all else fails, return the whole message (trimmed)
        return message.strip()[:100]


# Global instance
extractor = UpdateExtractor()


def extract_update_params(message: str) -> Dict[str, any]:
    """
    Extract update parameters from a natural language message

    Args:
        message: Natural language update request

    Returns:
        Dictionary containing the original task identifier and update parameters
    """
    return extractor.extract_update_params(message)