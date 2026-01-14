"""
Intent Classifier for Todo AI Chatbot
Classifies user intents for task management operations
"""

import re
from typing import Dict, List, Tuple
from enum import Enum


class TaskIntent(Enum):
    """
    Enumeration of possible task management intents
    """
    CREATE_TASK = "create_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    SEARCH_TASKS = "search_tasks"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Classifies user messages into specific task management intents
    """

    def __init__(self):
        # Define patterns for each intent with weights for confidence scoring
        self.intent_patterns = {
            TaskIntent.CREATE_TASK: [
                (r"create.*(?:a|an|the)?\s*(?:new|another)?\s*(?:task|todo|item).*?['\"](.+?)['\"]", 0.9),
                (r"add.*(?:a|an|the)?\s*(?:new|another)?\s*(?:task|todo|item).*?['\"](.+?)['\"]", 0.9),
                (r"make.*(?:a|an|the)?\s*(?:new|another)?\s*(?:task|todo|item).*?['\"](.+?)['\"]", 0.8),
                (r"new.*(?:task|todo|item).*?['\"](.+?)['\"]", 0.8),
                (r"please.*create.*['\"](.+?)['\"]", 0.7),
                (r"i\s+need.*to.*create.*['\"](.+?)['\"]", 0.8),
                (r"can.*you.*add.*['\"](.+?)['\"]", 0.7),
                (r"remind.*me.*to.*['\"](.+?)['\"]", 0.8),
                (r"schedule.*['\"](.+?)['\"]", 0.7),
                (r"set.*up.*['\"](.+?)['\"]", 0.7),
            ],

            TaskIntent.LIST_TASKS: [
                (r"show.*my.*(?:tasks|todos|items)", 0.9),
                (r"display.*my.*(?:tasks|todos|items)", 0.9),
                (r"list.*my.*(?:tasks|todos|items)", 0.9),
                (r"what.*tasks.*do.*i.*have", 0.9),
                (r"what.*is.*on.*my.*list", 0.8),
                (r"view.*my.*(?:tasks|todos|items)", 0.9),
                (r"see.*my.*(?:tasks|todos|items)", 0.8),
                (r"all.*(?:tasks|todos|items)", 0.7),
                (r"my.*(?:tasks|todos|items)", 0.7),
                (r"show.*(?:pending|incomplete|open).*tasks", 0.8),
                (r"show.*completed.*tasks", 0.8),
                (r"what.*did.*i.*finish", 0.7),
                (r"finished.*tasks", 0.7),
            ],

            TaskIntent.COMPLETE_TASK: [
                (r"complete.*['\"](.+?)['\"]", 0.9),
                (r"finish.*['\"](.+?)['\"]", 0.9),
                (r"done.*with.*['\"](.+?)['\"]", 0.9),
                (r"mark.*['\"](.+?)['\"].*as.*done", 0.9),
                (r"mark.*['\"](.+?)['\"].*as.*complete", 0.9),
                (r"check.*off.*['\"](.+?)['\"]", 0.8),
                (r"tick.*off.*['\"](.+?)['\"]", 0.8),
                (r"cross.*out.*['\"](.+?)['\"]", 0.8),
                (r"i.*completed.*['\"](.+?)['\"]", 0.8),
                (r"i.*finished.*['\"](.+?)['\"]", 0.8),
                (r"i.*did.*['\"](.+?)['\"]", 0.7),
                (r"i.*am.*done.*with.*['\"](.+?)['\"]", 0.8),
            ],

            TaskIntent.UPDATE_TASK: [
                (r"update.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.9),
                (r"change.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.9),
                (r"modify.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.8),
                (r"edit.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.8),
                (r"rename.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.8),
                (r"update.*title.*of.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.8),
                (r"change.*title.*of.*['\"](.+?)['\"].*to.*['\"](.+?)['\"]", 0.8),
            ],

            TaskIntent.DELETE_TASK: [
                (r"delete.*['\"](.+?)['\"]", 0.9),
                (r"remove.*['\"](.+?)['\"]", 0.9),
                (r"erase.*['\"](.+?)['\"]", 0.8),
                (r"get.*rid.*of.*['\"](.+?)['\"]", 0.8),
                (r"trash.*['\"](.+?)['\"]", 0.7),
                (r"dispose.*of.*['\"](.+?)['\"]", 0.7),
                (r"eliminate.*['\"](.+?)['\"]", 0.7),
                (r"cancel.*['\"](.+?)['\"]", 0.7),
            ],

            TaskIntent.SEARCH_TASKS: [
                (r"find.*(?:task|todo).*about.*(.+)", 0.8),
                (r"search.*for.*(?:task|todo).*['\"](.+?)['\"]", 0.8),
                (r"look.*for.*(?:task|todo).*['\"](.+?)['\"]", 0.8),
                (r"find.*tasks.*about.*(.+)", 0.8),
                (r"search.*my.*tasks.*for.*(.+)", 0.8),
                (r"got.*any.*tasks.*about.*(.+)", 0.7),
            ]
        }

    def classify_intent(self, message: str) -> Tuple[TaskIntent, Dict[str, any]]:
        """
        Classify the intent of a user message and extract parameters

        Args:
            message: The user's message

        Returns:
            Tuple of (intent, parameters dictionary)
        """
        message_lower = message.lower().strip()

        best_intent = TaskIntent.UNKNOWN
        best_confidence = 0.0
        best_match_params = {}

        for intent, patterns in self.intent_patterns.items():
            for pattern, weight in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    # Calculate confidence based on pattern weight
                    confidence = weight

                    # If this is a higher confidence match, update best
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent

                        # Extract parameters based on intent type
                        groups = match.groups()

                        if intent == TaskIntent.CREATE_TASK:
                            best_match_params = {'title': groups[0] if groups else self._extract_task_title(message)}
                        elif intent == TaskIntent.COMPLETE_TASK:
                            best_match_params = {'task_title': groups[0] if groups else self._extract_task_title(message)}
                        elif intent == TaskIntent.UPDATE_TASK:
                            if len(groups) >= 2:
                                best_match_params = {
                                    'task_title': groups[0],
                                    'new_title': groups[1]
                                }
                            else:
                                best_match_params = {'task_title': self._extract_task_title(message)}
                        elif intent == TaskIntent.DELETE_TASK:
                            best_match_params = {'task_title': groups[0] if groups else self._extract_task_title(message)}
                        elif intent == TaskIntent.SEARCH_TASKS:
                            best_match_params = {'query': groups[0] if groups else message.strip()}
                        else:
                            # For other intents, just store the raw groups
                            best_match_params = {'raw_groups': groups}

        # If confidence is too low, mark as unknown
        if best_confidence < 0.3:
            best_intent = TaskIntent.UNKNOWN
            best_match_params = {'raw_message': message}

        return best_intent, best_match_params

    def _extract_task_title(self, message: str) -> str:
        """
        Extract task title from message using heuristics
        """
        # First, try to find quoted text
        quote_match = re.search(r'["\']([^"\']+)["\']', message)
        if quote_match:
            return quote_match.group(1).strip()

        # If no quotes, try to extract the main content after action words
        action_words = ['create', 'add', 'make', 'new', 'task', 'todo', 'item', 'do', 'need', 'to']

        # Find the position after action words
        min_pos = float('inf')
        for word in action_words:
            pos = message.lower().find(word)
            if pos != -1:
                pos += len(word)
                min_pos = min(min_pos, pos)

        if min_pos != float('inf') and min_pos < len(message):
            # Get the remainder after action words
            remainder = message[min_pos:].strip()

            # Take the first sentence or phrase (before punctuation)
            parts = re.split(r'[.!?;,]', remainder)
            title = parts[0].strip()

            # Clean up the title
            title = re.sub(r'^["\']|["\']$', '', title)  # Remove leading/trailing quotes
            title = re.sub(r'^\s*the\s+|\s*the\s*$', ' ', title).strip()  # Remove 'the' if it's standalone

            if title:
                return title

        # If all else fails, return the original message trimmed
        return message.strip()[:100]  # Limit to 100 characters

    def get_intent_confidence(self, message: str) -> List[Tuple[TaskIntent, float]]:
        """
        Get all possible intents with their confidence scores for a message

        Args:
            message: The user's message

        Returns:
            List of tuples (intent, confidence) sorted by confidence
        """
        message_lower = message.lower().strip()
        intent_scores = []

        for intent, patterns in self.intent_patterns.items():
            max_score = 0.0
            for pattern, weight in patterns:
                if re.search(pattern, message_lower):
                    max_score = max(max_score, weight)

            if max_score > 0:
                intent_scores.append((intent, max_score))

        # Sort by confidence score descending
        intent_scores.sort(key=lambda x: x[1], reverse=True)
        return intent_scores


# Global instance
classifier = IntentClassifier()


def classify_intent(message: str) -> Tuple[TaskIntent, Dict[str, any]]:
    """
    Convenience function to classify intent of a message

    Args:
        message: The user's message

    Returns:
        Tuple of (intent, parameters dictionary)
    """
    return classifier.classify_intent(message)


def get_intent_confidence(message: str) -> List[Tuple[TaskIntent, float]]:
    """
    Get all possible intents with their confidence scores for a message

    Args:
        message: The user's message

    Returns:
        List of tuples (intent, confidence) sorted by confidence
    """
    return classifier.get_intent_confidence(message)