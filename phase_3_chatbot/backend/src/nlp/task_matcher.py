"""
Task Matcher for Todo AI Chatbot
Matches natural language descriptions to existing tasks
"""

from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
import re
from uuid import UUID


class TaskMatcher:
    """
    Matches natural language descriptions to existing tasks using fuzzy matching
    """

    def __init__(self):
        self.similarity_threshold = 0.6  # Minimum similarity threshold

    def find_best_match(self,
                       query: str,
                       tasks: List[Dict],
                       user_id: str) -> Optional[Dict]:
        """
        Find the best matching task for a query among user's tasks

        Args:
            query: Natural language query to match against tasks
            tasks: List of task dictionaries to search through
            user_id: User ID to filter tasks

        Returns:
            Best matching task dictionary or None if no match found
        """
        if not query or not tasks:
            return None

        # Filter tasks for the specific user
        user_tasks = [task for task in tasks if str(task.get('user_id', '')) == user_id]

        best_match = None
        best_score = 0.0

        query_lower = query.lower().strip()

        for task in user_tasks:
            task_title = task.get('title', '').lower()
            task_description = task.get('description', '').lower() if task.get('description') else ''

            # Calculate similarity scores
            title_similarity = self._calculate_similarity(query_lower, task_title)
            desc_similarity = self._calculate_similarity(query_lower, task_description) if task_description else 0.0

            # Use the higher of the two similarities
            max_similarity = max(title_similarity, desc_similarity)

            # Check for keyword matches (boost score for exact matches)
            keyword_boost = self._calculate_keyword_boost(query_lower, task_title, task_description)

            # Final score is a combination of similarity and keyword matches
            final_score = max_similarity + keyword_boost

            if final_score > best_score and final_score >= self.similarity_threshold:
                best_score = final_score
                best_match = task

        return best_match

    def find_multiple_matches(self,
                           query: str,
                           tasks: List[Dict],
                           user_id: str,
                           limit: int = 5) -> List[Tuple[Dict, float]]:
        """
        Find multiple matching tasks for a query

        Args:
            query: Natural language query to match against tasks
            tasks: List of task dictionaries to search through
            user_id: User ID to filter tasks
            limit: Maximum number of matches to return

        Returns:
            List of tuples (task_dict, similarity_score) sorted by score
        """
        if not query or not tasks:
            return []

        # Filter tasks for the specific user
        user_tasks = [task for task in tasks if str(task.get('user_id', '')) == user_id]

        matches = []

        query_lower = query.lower().strip()

        for task in user_tasks:
            task_title = task.get('title', '').lower()
            task_description = task.get('description', '').lower() if task.get('description') else ''

            # Calculate similarity scores
            title_similarity = self._calculate_similarity(query_lower, task_title)
            desc_similarity = self._calculate_similarity(query_lower, task_description) if task_description else 0.0

            # Use the higher of the two similarities
            max_similarity = max(title_similarity, desc_similarity)

            # Check for keyword matches (boost score for exact matches)
            keyword_boost = self._calculate_keyword_boost(query_lower, task_title, task_description)

            # Final score is a combination of similarity and keyword matches
            final_score = max_similarity + keyword_boost

            if final_score >= self.similarity_threshold:
                matches.append((task, final_score))

        # Sort by score in descending order
        matches.sort(key=lambda x: x[1], reverse=True)

        # Return limited results
        return matches[:limit]

    def _calculate_similarity(self, query: str, text: str) -> float:
        """
        Calculate similarity between query and text using SequenceMatcher

        Args:
            query: Query string
            text: Text to compare against

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        if not text:
            return 0.0

        # Use SequenceMatcher for similarity calculation
        return SequenceMatcher(None, query, text).ratio()

    def _calculate_keyword_boost(self, query: str, title: str, description: str = "") -> float:
        """
        Calculate additional boost for keyword matches

        Args:
            query: Query string
            title: Task title
            description: Task description (optional)

        Returns:
            Boost value to add to similarity score
        """
        boost = 0.0

        # Split query into words
        query_words = set(re.findall(r'\b\w+\b', query.lower()))

        # Check for exact word matches in title
        title_words = set(re.findall(r'\b\w+\b', title.lower()))
        common_words = query_words.intersection(title_words)
        boost += len(common_words) * 0.1  # 0.1 boost per common word

        # Check for exact word matches in description if provided
        if description:
            desc_words = set(re.findall(r'\b\w+\b', description.lower()))
            common_desc_words = query_words.intersection(desc_words)
            boost += len(common_desc_words) * 0.05  # 0.05 boost per common word in description

        # Check for phrase matches (boost for longer matches)
        for word in query_words:
            if len(word) > 3:  # Only consider longer words
                if word in title:
                    boost += 0.05  # Additional boost for longer word matches
                if description and word in description:
                    boost += 0.02

        return min(boost, 0.3)  # Cap the boost at 0.3 to prevent overwhelming similarity score

    def normalize_task_identifier(self, identifier: str) -> str:
        """
        Normalize a task identifier for comparison

        Args:
            identifier: Raw task identifier (could be title, partial title, etc.)

        Returns:
            Normalized identifier string
        """
        # Remove common prefixes/suffixes
        normalized = identifier.lower().strip()

        # Remove common task-related words
        common_words = ['task', 'todo', 'item', 'the', 'a', 'an', 'to', 'be', 'do', 'please']
        for word in common_words:
            normalized = re.sub(r'\b' + word + r'\b', '', normalized)

        # Clean up extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def match_by_keywords(self, query: str, tasks: List[Dict], user_id: str) -> Optional[Dict]:
        """
        Match tasks based on keyword extraction and matching

        Args:
            query: Natural language query
            tasks: List of task dictionaries
            user_id: User ID to filter tasks

        Returns:
            Matching task or None
        """
        if not query or not tasks:
            return None

        # Filter tasks for the specific user
        user_tasks = [task for task in tasks if str(task.get('user_id', '')) == user_id]

        # Extract keywords from query
        query_keywords = set(re.findall(r'\b\w{3,}\b', query.lower()))  # Only words with 3+ chars

        best_match = None
        best_keyword_count = 0

        for task in user_tasks:
            task_title = task.get('title', '').lower()
            task_description = task.get('description', '').lower() if task.get('description') else ''

            # Count matching keywords
            title_words = set(re.findall(r'\b\w{3,}\b', task_title))
            desc_words = set(re.findall(r'\b\w{3,}\b', task_description)) if task_description else set()

            matching_keywords = query_keywords.intersection(title_words.union(desc_words))
            keyword_count = len(matching_keywords)

            if keyword_count > best_keyword_count:
                best_keyword_count = keyword_count
                best_match = task

        return best_match


# Global instance
task_matcher = TaskMatcher()


def find_best_match(query: str, tasks: List[Dict], user_id: str) -> Optional[Dict]:
    """
    Find the best matching task for a query

    Args:
        query: Natural language query to match against tasks
        tasks: List of task dictionaries to search through
        user_id: User ID to filter tasks

    Returns:
        Best matching task dictionary or None if no match found
    """
    return task_matcher.find_best_match(query, tasks, user_id)


def find_multiple_matches(query: str, tasks: List[Dict], user_id: str, limit: int = 5) -> List[Tuple[Dict, float]]:
    """
    Find multiple matching tasks for a query

    Args:
        query: Natural language query to match against tasks
        tasks: List of task dictionaries to search through
        user_id: User ID to filter tasks
        limit: Maximum number of matches to return

    Returns:
        List of tuples (task_dict, similarity_score) sorted by score
    """
    return task_matcher.find_multiple_matches(query, tasks, user_id, limit)


def match_by_keywords(query: str, tasks: List[Dict], user_id: str) -> Optional[Dict]:
    """
    Match tasks based on keyword extraction and matching

    Args:
        query: Natural language query
        tasks: List of task dictionaries
        user_id: User ID to filter tasks

    Returns:
        Matching task or None
    """
    return task_matcher.match_by_keywords(query, tasks, user_id)