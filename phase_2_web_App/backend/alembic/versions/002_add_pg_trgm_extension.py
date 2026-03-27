"""Add pg_trgm extension and GIN index for fuzzy task title matching

Revision ID: 002_add_pg_trgm
Revises: 59103f8c7b95
Create Date: 2025-03-05 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = '002_add_pg_trgm'
down_revision = '59103f8c7b95'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add pg_trgm extension and create GIN index on task.title.

    The pg_trgm extension provides:
    - Similarity operator (%) for fuzzy matching
    - similarity() function for calculating string similarity
    - GIN index support for fast similarity searches

    This enables natural language task references like:
    - "complete the groceries task" → matches "Buy Groceries"
    - "delete the food task" → matches "Buy Food Items"
    """
    # Enable pg_trgm extension (required for fuzzy matching)
    # This adds the % operator and similarity() function
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    # Create GIN index on task.title for fast similarity searches
    # Uses gin_trgm_ops for trigram-based indexing
    # This makes queries like "title % 'groceries'" very fast
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_task_title_trgm '
        'ON task USING gin(title gin_trgm_ops)'
    )

    # Also add a standard B-tree index for exact matches if not exists
    # This helps with case-insensitive exact title searches
    op.execute(
        'CREATE INDEX IF NOT EXISTS idx_task_title_lower '
        'ON task (LOWER(title))'
    )


def downgrade() -> None:
    """Remove pg_trgm extension and indexes."""
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS idx_task_title_trgm')
    op.execute('DROP INDEX IF EXISTS idx_task_title_lower')

    # Drop extension (CASCADE to drop dependent objects)
    op.execute('DROP EXTENSION IF EXISTS pg_trgm CASCADE')
