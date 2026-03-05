"""
Task Resolver for Natural Language Task References.

Implements a 4-strategy hierarchical matching system:
1. Exact Title Match - User mentions exact task name
2. Fuzzy Title Match - Partial or similar titles using pg_trgm
3. Positional Reference - First, second, last, recent tasks
4. Recent Task Reference - The task just added

This enables natural language interactions like:
- "complete the buy groceries task"
- "delete the groceries task"
- "mark the first task as done"
- "complete the task I just added"
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from uuid import UUID

from sqlmodel import Session, select
from sqlalchemy import func, text

from ..models.task import Task

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TaskResolutionResult:
    """
    Result of task resolution operation.

    Attributes:
        task: The matched Task object (if single match found)
        matches: List of (Task, confidence_score) tuples (if ambiguous)
        strategy_used: Which matching strategy succeeded
        confidence: Float 0-1 indicating match confidence
        error: Error message if no match found
        disambiguation_message: Formatted message for ambiguous matches
    """
    task: Optional[Task]
    matches: List[Tuple[Task, float]]
    strategy_used: str
    confidence: float
    error: Optional[str]
    disambiguation_message: Optional[str]


# ============================================================================
# Positional Reference Mappings
# ============================================================================

ORDINAL_MAP = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
}

RECENT_KEYWORDS = ["last", "latest", "recent", "newest", "just added", "most recent"]

STOP_WORDS = [
    "the", "a", "an", "task", "about", "called", "named", "item",
    "one", "with", "for", "to", "of"
]


# ============================================================================
# Helper Functions
# ============================================================================

def normalize_reference(reference: str) -> str:
    """
    Normalize user reference for better matching.

    Removes common filler words and converts to lowercase.

    Examples:
        "buy groceries" → "buy groceries"
        "the groceries task" → "groceries"
        "task about food" → "food"
    """
    if not reference:
        return ""

    # Lowercase
    reference = reference.lower().strip()

    # Remove quotes
    reference = reference.strip('"').strip("'")

    # Remove stop words
    words = reference.split()
    filtered = [w for w in words if w not in STOP_WORDS]

    return " ".join(filtered).strip()


def extract_positional_reference(reference: str) -> Optional[int]:
    """
    Extract positional index from reference.

    Returns:
        - 1 for "first"
        - 2 for "second"
        - -1 for "last", "latest", "recent"
        - None if not a positional reference
    """
    normalized = normalize_reference(reference).lower()

    # Check for ordinal words
    for word, index in ORDINAL_MAP.items():
        if word in normalized:
            return index

    # Check for recent keywords
    for keyword in RECENT_KEYWORDS:
        if keyword in normalized:
            return -1  # -1 indicates most recent

    return None


def is_uuid(reference: str) -> bool:
    """
    Check if reference is a UUID (full or partial).
    """
    try:
        UUID(reference)
        return True
    except ValueError:
        # Try partial UUID (first 8 characters)
        if len(reference) >= 4 and len(reference) <= 8:
            try:
                UUID(reference.ljust(36, '0'))
                return True
            except ValueError:
                pass
        return False


# ============================================================================
# Main Resolution Function
# ============================================================================

async def resolve_task_reference(
    db: Session,
    user_id: UUID,
    reference: str,
    intent: str = "general"
) -> TaskResolutionResult:
    """
    Resolve a natural language reference to a task.

    Uses a 4-strategy hierarchical matching system:
    1. UUID fallback (backward compatibility)
    2. Positional reference (first, second, last, recent)
    3. Exact title match
    4. Fuzzy title match (using pg_trgm)

    Args:
        db: Database session
        user_id: User UUID
        reference: Natural language reference (e.g., "buy groceries", "first task")
        intent: Operation intent ("complete", "delete", "update", "general")

    Returns:
        TaskResolutionResult with matched task or disambiguation options
    """
    if not reference or not reference.strip():
        return TaskResolutionResult(
            task=None,
            matches=[],
            strategy_used="none",
            confidence=0.0,
            error="No task reference provided",
            disambiguation_message=None
        )

    normalized = normalize_reference(reference)

    logger.info(
        f"[TaskResolver] Resolving reference='{reference}' "
        f"(normalized='{normalized}') for user={user_id}, intent={intent}"
    )

    # ========================================================================
    # Strategy 1: UUID Fallback (Backward Compatibility)
    # ========================================================================
    if is_uuid(normalized):
        logger.info(f"[TaskResolver] Trying UUID strategy: {normalized}")
        try:
            # Try full UUID first
            task_uuid = UUID(normalized)
            task = db.get(Task, task_uuid)
            if task and task.user_id == user_id:
                logger.info(f"[TaskResolver] UUID match found: {task.id}")
                return TaskResolutionResult(
                    task=task,
                    matches=[],
                    strategy_used="uuid",
                    confidence=1.0,
                    error=None,
                    disambiguation_message=None
                )
        except ValueError:
            pass

        # Try partial UUID match
        tasks = db.exec(
            select(Task).where(
                Task.user_id == user_id,
                func.cast(Task.id, str).like(f"{normalized}%")
            )
        ).all()

        if len(tasks) == 1:
            logger.info(f"[TaskResolver] Partial UUID match found: {tasks[0].id}")
            return TaskResolutionResult(
                task=tasks[0],
                matches=[],
                strategy_used="uuid_partial",
                confidence=0.95,
                error=None,
                disambiguation_message=None
            )

    # ========================================================================
    # Strategy 2: Positional Reference (First, Second, Last, Recent)
    # ========================================================================
    position = extract_positional_reference(reference)
    if position is not None:
        logger.info(f"[TaskResolver] Trying positional strategy: position={position}")

        try:
            if position == -1:
                # Most recent task
                task = db.exec(
                    select(Task).where(
                        Task.user_id == user_id
                    ).order_by(Task.created_at.desc()).limit(1)
                ).first()
            else:
                # Nth task (1-based index)
                # Get all tasks ordered by created_at (newest first for display)
                tasks = db.exec(
                    select(Task).where(
                        Task.user_id == user_id
                    ).order_by(Task.created_at.desc())
                ).all()

                if position <= len(tasks):
                    task = tasks[position - 1]
                else:
                    task = None

            if task:
                logger.info(f"[TaskResolver] Positional match found: {task.title}")
                return TaskResolutionResult(
                    task=task,
                    matches=[],
                    strategy_used="positional",
                    confidence=0.9,
                    error=None,
                    disambiguation_message=None
                )
            else:
                return TaskResolutionResult(
                    task=None,
                    matches=[],
                    strategy_used="positional",
                    confidence=0.0,
                    error=f"No task found at position {position}. You have {len(db.exec(select(Task).where(Task.user_id == user_id)).all())} task(s).",
                    disambiguation_message=None
                )
        except Exception as e:
            logger.exception(f"[TaskResolver] Error in positional strategy: {e}")

    # ========================================================================
    # Strategy 3: Exact Title Match
    # ========================================================================
    logger.info(f"[TaskResolver] Trying exact title match: '{normalized}'")

    # Try exact case-insensitive match first
    exact_tasks = db.exec(
        select(Task).where(
            Task.user_id == user_id,
            func.lower(Task.title) == normalized
        )
    ).all()

    if len(exact_tasks) == 1:
        task = exact_tasks[0]
        logger.info(f"[TaskResolver] Exact title match found: {task.title}")
        return TaskResolutionResult(
            task=task,
            matches=[],
            strategy_used="exact_title",
            confidence=1.0,
            error=None,
            disambiguation_message=None
        )

    if len(exact_tasks) > 1:
        # Multiple exact matches (duplicate task names)
        logger.info(f"[TaskResolver] Multiple exact matches found: {len(exact_tasks)}")
        matches = [(t, 1.0) for t in exact_tasks]
        return TaskResolutionResult(
            task=None,
            matches=matches,
            strategy_used="exact_title",
            confidence=1.0,
            error=None,
            disambiguation_message=_format_disambiguation_message(matches, reference)
        )

    # ========================================================================
    # Strategy 4: Fuzzy Title Match (using pg_trgm)
    # ========================================================================
    logger.info(f"[TaskResolver] Trying fuzzy match: '{normalized}'")

    try:
        # Try pg_trgm similarity search first (most accurate)
        fuzzy_tasks = db.exec(
            select(Task).where(
                Task.user_id == user_id,
                text("title % :ref")
            ).bindparams(ref=normalized)
        ).all()

        # If pg_trgm not available, fall back to ILIKE
        if not fuzzy_tasks:
            fuzzy_tasks = db.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.title.ilike(f"%{normalized}%")
                )
            ).all()

        if fuzzy_tasks:
            # Calculate confidence scores
            matches_with_scores = []
            for t in fuzzy_tasks:
                # Simple confidence based on word overlap
                score = _calculate_confidence(normalized, t.title.lower())
                if score > 0.3:  # Minimum confidence threshold
                    matches_with_scores.append((t, score))

            # Sort by confidence
            matches_with_scores.sort(key=lambda x: x[1], reverse=True)

            if matches_with_scores:
                best_match, best_score = matches_with_scores[0]

                # If we have a single high-confidence match, use it
                if len(matches_with_scores) == 1 and best_score > 0.7:
                    logger.info(f"[TaskResolver] Single fuzzy match found: {best_match.title}")
                    return TaskResolutionResult(
                        task=best_match,
                        matches=[],
                        strategy_used="fuzzy_title",
                        confidence=best_score,
                        error=None,
                        disambiguation_message=None
                    )

                # If best match is significantly better than others, use it
                if len(matches_with_scores) > 1 and best_score > 0.8:
                    second_best_score = matches_with_scores[1][1]
                    if best_score - second_best_score > 0.3:
                        logger.info(f"[TaskResolver] Best fuzzy match: {best_match.title}")
                        return TaskResolutionResult(
                            task=best_match,
                            matches=[],
                            strategy_used="fuzzy_title",
                            confidence=best_score,
                            error=None,
                            disambiguation_message=None
                        )

                # Multiple matches - return for disambiguation
                logger.info(f"[TaskResolver] Multiple fuzzy matches: {len(matches_with_scores)}")
                return TaskResolutionResult(
                    task=None,
                    matches=matches_with_scores,
                    strategy_used="fuzzy_title",
                    confidence=best_score,
                    error=None,
                    disambiguation_message=_format_disambiguation_message(
                        matches_with_scores[:5],  # Limit to top 5
                        reference
                    )
                )

    except Exception as e:
        logger.exception(f"[TaskResolver] Error in fuzzy strategy: {e}")

    # ========================================================================
    # No Match Found
    # ========================================================================
    total_tasks = len(db.exec(select(Task).where(Task.user_id == user_id)).all())
    logger.warning(f"[TaskResolver] No match found for '{reference}'")

    return TaskResolutionResult(
        task=None,
        matches=[],
        strategy_used="none",
        confidence=0.0,
        error=f"I couldn't find a task matching '{reference}'. You have {total_tasks} task(s). Would you like me to list them?",
        disambiguation_message=None
    )


def _calculate_confidence(reference: str, title: str) -> float:
    """
    Calculate confidence score for a fuzzy match.

    Uses word overlap ratio.
    """
    ref_words = set(reference.split())
    title_words = set(title.split())

    if not ref_words:
        return 0.0

    # Exact match bonus
    if reference == title:
        return 1.0

    # Word overlap ratio
    overlap = len(ref_words & title_words)
    ratio = overlap / len(ref_words)

    # Bonus for containing reference as substring
    if reference in title:
        ratio += 0.2

    # Bonus for title being contained in reference
    if title in reference:
        ratio += 0.3

    return min(ratio, 1.0)


def _format_disambiguation_message(
    matches: List[Tuple[Task, float]],
    reference: str
) -> str:
    """
    Format a disambiguation message for multiple matching tasks.

    Example:
        I found multiple tasks matching 'groceries'. Which one do you mean?

        1. 'Buy Groceries' (created 2 hours ago) - [93% match]
        2. 'Groceries for Mom' (created yesterday) - [87% match]

        Please be more specific or use the task number.
    """
    from datetime import datetime, timezone

    lines = [
        f"I found multiple tasks matching '{reference}'. Which one do you mean?",
        ""
    ]

    now = datetime.now(timezone.utc)

    for i, (task, confidence) in enumerate(matches, 1):
        # Calculate time ago
        time_ago = _format_time_ago(now, task.created_at)

        # Format percentage
        percent = int(confidence * 100)

        lines.append(
            f"{i}. '{task.title}' ({time_ago}) - [{percent}% match]"
        )

    lines.append("")
    lines.append("Please be more specific or use the task number.")

    return "\n".join(lines)


def _format_time_ago(now: datetime, created_at: datetime) -> str:
    """Format a datetime as 'X time ago'."""
    diff = now - created_at

    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        return created_at.strftime("%B %d, %Y")
