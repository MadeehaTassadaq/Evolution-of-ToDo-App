"""
Fuzzy Matcher for Todo AI Chatbot
Provides fuzzy string matching for task search functionality
"""

from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher, get_close_matches
import re


class FuzzyMatcher:
    """
    Implements fuzzy matching algorithms for task search functionality
    """

    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold

    def fuzzy_search_tasks(self,
                          query: str,
                          tasks: List[Dict],
                          user_id: str,
                          limit: int = 10) -> List[Tuple[Dict, float]]:
        """
        Perform fuzzy search on tasks based on a query

        Args:
            query: Search query string
            tasks: List of task dictionaries to search through
            user_id: User ID to filter tasks
            limit: Maximum number of results to return

        Returns:
            List of tuples (task_dict, similarity_score) sorted by score
        """
        if not query or not tasks:
            return []

        # Filter tasks for the specific user
        user_tasks = [task for task in tasks if str(task.get('user_id', '')) == user_id]

        results = []

        query_lower = query.lower().strip()

        for task in user_tasks:
            task_title = task.get('title', '').lower()
            task_description = task.get('description', '').lower() if task.get('description') else ''

            # Calculate similarity for title and description separately
            title_score = self._calculate_similarity(query_lower, task_title)
            desc_score = self._calculate_similarity(query_lower, task_description) if task_description else 0.0

            # Use weighted average (title is more important than description)
            combined_score = (title_score * 0.7) + (desc_score * 0.3)

            # Boost score if query words appear as substrings
            substring_boost = self._substring_boost(query_lower, task_title, task_description)
            final_score = min(combined_score + substring_boost, 1.0)  # Cap at 1.0

            if final_score >= self.threshold:
                results.append((task, final_score))

        # Sort by score in descending order
        results.sort(key=lambda x: x[1], reverse=True)

        # Return limited results
        return results[:limit]

    def _calculate_similarity(self, query: str, text: str) -> float:
        """
        Calculate similarity between query and text using SequenceMatcher

        Args:
            query: Query string
            text: Text to compare against

        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        if not text or not query:
            return 0.0

        # Use SequenceMatcher for similarity calculation
        return SequenceMatcher(None, query, text).ratio()

    def _substring_boost(self, query: str, title: str, description: str = "") -> float:
        """
        Calculate boost for substring matches

        Args:
            query: Query string
            title: Task title
            description: Task description (optional)

        Returns:
            Boost value to add to similarity score
        """
        boost = 0.0

        # Check if query is a substring of title or description
        if query in title:
            boost += 0.2  # Significant boost for title substring match

        if description and query in description:
            boost += 0.1  # Moderate boost for description substring match

        # Check for individual word matches
        query_words = query.split()
        if len(query_words) == 1:
            # For single word queries, check if it appears in title
            if query in title:
                boost += 0.15

        return min(boost, 0.5)  # Cap the boost at 0.5

    def find_best_match(self,
                       query: str,
                       tasks: List[Dict],
                       user_id: str) -> Optional[Tuple[Dict, float]]:
        """
        Find the single best matching task for a query

        Args:
            query: Search query string
            tasks: List of task dictionaries to search through
            user_id: User ID to filter tasks

        Returns:
            Tuple of (task_dict, similarity_score) for the best match, or None
        """
        matches = self.fuzzy_search_tasks(query, tasks, user_id, limit=1)
        return matches[0] if matches else None

    def keyword_search(self,
                      query: str,
                      tasks: List[Dict],
                      user_id: str,
                      limit: int = 10) -> List[Tuple[Dict, float]]:
        """
        Perform keyword-based search on tasks

        Args:
            query: Search query string
            tasks: List of task dictionaries to search through
            user_id: User ID to filter tasks
            limit: Maximum number of results to return

        Returns:
            List of tuples (task_dict, relevance_score) sorted by score
        """
        if not query or not tasks:
            return []

        # Filter tasks for the specific user
        user_tasks = [task for task in tasks if str(task.get('user_id', '')) == user_id]

        results = []

        # Extract keywords from query (words of 3+ characters)
        query_keywords = set(re.findall(r'\b\w{3,}\b', query.lower()))

        for task in user_tasks:
            task_title = task.get('title', '').lower()
            task_description = task.get('description', '').lower() if task.get('description') else ''

            # Count keyword matches in title and description
            title_words = set(re.findall(r'\b\w{3,}\b', task_title))
            desc_words = set(re.findall(r'\b\w{3,}\b', task_description)) if task_description else set()

            title_matches = len(query_keywords.intersection(title_words))
            desc_matches = len(query_keywords.intersection(desc_words))

            # Calculate relevance score
            # Title matches are worth more than description matches
            relevance_score = (title_matches * 0.7) + (desc_matches * 0.3)

            # Boost if all query keywords are found
            if query_keywords.issubset(title_words.union(desc_words)):
                relevance_score += 0.3  # Extra boost for complete matches

            # Normalize score to 0-1 range based on number of query keywords
            if query_keywords:
                max_possible_matches = len(query_keywords)
                if max_possible_matches > 0:
                    relevance_score = relevance_score / max_possible_matches
                    relevance_score = min(relevance_score, 1.0)  # Cap at 1.0

            if relevance_score > 0:
                results.append((task, relevance_score))

        # Sort by relevance score in descending order
        results.sort(key=lambda x: x[1], reverse=True)

        # Return limited results
        return results[:limit]

    def phonetic_search(self,
                       query: str,
                       tasks: List[Dict],
                       user_id: str,
                       limit: int = 10) -> List[Tuple[Dict, float]]:
        """
        Perform phonetic search using Soundex or similar algorithm concept

        Args:
            query: Search query string
            tasks: List of task dictionaries to search through
            user_id: User ID to filter tasks
            limit: Maximum number of results to return

        Returns:
            List of tuples (task_dict, similarity_score) sorted by score
        """
        # For simplicity, we'll use difflib's get_close_matches as a proxy for phonetic matching
        # In a real implementation, we'd use Soundex, Metaphone, or Double Metaphone algorithms

        if not query or not tasks:
            return []

        # Filter tasks for the specific user
        user_tasks = [task for task in tasks if str(task.get('user_id', '')) == user_id]

        # Extract all possible titles to match against
        all_titles = [task.get('title', '') for task in user_tasks if task.get('title')]

        # Find close matches for the query among all titles
        close_matches = get_close_matches(query, all_titles, n=len(all_titles), cutoff=self.threshold)

        results = []
        for match_title in close_matches:
            # Find the corresponding task
            matching_task = next((task for task in user_tasks if task.get('title', '') == match_title), None)
            if matching_task:
                # Calculate similarity for the match
                similarity = self._calculate_similarity(query.lower(), match_title.lower())
                results.append((matching_task, similarity))

        # Sort by similarity score in descending order
        results.sort(key=lambda x: x[1], reverse=True)

        # Return limited results
        return results[:limit]


# Global instance
fuzzy_matcher = FuzzyMatcher()


def fuzzy_search_tasks(query: str, tasks: List[Dict], user_id: str, limit: int = 10) -> List[Tuple[Dict, float]]:
    """
    Perform fuzzy search on tasks based on a query

    Args:
        query: Search query string
        tasks: List of task dictionaries to search through
        user_id: User ID to filter tasks
        limit: Maximum number of results to return

    Returns:
        List of tuples (task_dict, similarity_score) sorted by score
    """
    return fuzzy_matcher.fuzzy_search_tasks(query, tasks, user_id, limit)


def find_best_match(query: str, tasks: List[Dict], user_id: str) -> Optional[Tuple[Dict, float]]:
    """
    Find the single best matching task for a query

    Args:
        query: Search query string
        tasks: List of task dictionaries to search through
        user_id: User ID to filter tasks

    Returns:
        Tuple of (task_dict, similarity_score) for the best match, or None
    """
    return fuzzy_matcher.find_best_match(query, tasks, user_id)


def keyword_search(query: str, tasks: List[Dict], user_id: str, limit: int = 10) -> List[Tuple[Dict, float]]:
    """
    Perform keyword-based search on tasks

    Args:
        query: Search query string
        tasks: List of task dictionaries to search through
        user_id: User ID to filter tasks
        limit: Maximum number of results to return

    Returns:
        List of tuples (task_dict, relevance_score) sorted by score
    """
    return fuzzy_matcher.keyword_search(query, tasks, user_id, limit)


def phonetic_search(query: str, tasks: List[Dict], user_id: str, limit: int = 10) -> List[Tuple[Dict, float]]:
    """
    Perform phonetic search using Soundex or similar algorithm concept

    Args:
        query: Search query string
        tasks: List of task dictionaries to search through
        user_id: User ID to filter tasks
        limit: Maximum number of results to return

    Returns:
        List of tuples (task_dict, similarity_score) sorted by score
    """
    return fuzzy_matcher.phonetic_search(query, tasks, user_id, limit)