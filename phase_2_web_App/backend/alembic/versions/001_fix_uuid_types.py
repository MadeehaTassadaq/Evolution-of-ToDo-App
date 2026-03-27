"""Fix UUID types for conversation and message tables

Revision ID: fix_uuid_types
Revises:
Create Date: 2025-03-05

This migration documents the manual UUID type conversion that was performed
to fix the "operator does not exist: character varying = uuid" error.

The conversation and message tables were created with VARCHAR columns
instead of UUID, which caused type mismatch errors when ChatKit tried to
load threads.

Changes:
- conversation.id: VARCHAR -> UUID
- conversation.user_id: VARCHAR -> UUID
- message.id: VARCHAR -> UUID
- message.conversation_id: VARCHAR -> UUID
- Recreated foreign key constraints with proper UUID types

Also cleaned up test data with invalid user_id values ("test-user-id", "test_user_123").
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'fix_uuid_types'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    This migration documents changes already applied manually.

    The UUID conversion was performed using:

    ```sql
    -- These commands were already executed:
    ALTER TABLE conversation ALTER COLUMN id TYPE UUID USING id::UUID;
    ALTER TABLE conversation ALTER COLUMN user_id TYPE UUID USING user_id::UUID;
    ALTER TABLE message ALTER COLUMN id TYPE UUID USING id::UUID;
    ALTER TABLE message ALTER COLUMN conversation_id TYPE UUID USING conversation_id::UUID;

    -- Foreign key constraints were recreated:
    ALTER TABLE message ADD CONSTRAINT message_conversation_id_fkey
        FOREIGN KEY (conversation_id) REFERENCES conversation(id);
    ```

    No action needed - this documents the manual fix.
    """
    pass


def downgrade():
    """
    Revert the UUID types back to VARCHAR (not recommended).

    Only use this if you need to rollback to the broken state.
    """
    # Drop foreign key constraint
    op.drop_constraint('message', 'message_conversation_id_fkey', type_='foreignkey')

    # Convert columns back to VARCHAR
    op.alter_column('conversation', 'id',
                   existing_type=postgresql.UUID(),
                   type_=sa.VARCHAR(),
                   existing_nullable=False)

    op.alter_column('conversation', 'user_id',
                   existing_type=postgresql.UUID(),
                   type_=sa.VARCHAR(),
                   existing_nullable=False)

    op.alter_column('message', 'id',
                   existing_type=postgresql.UUID(),
                   type_=sa.VARCHAR(),
                   existing_nullable=False)

    op.alter_column('message', 'conversation_id',
                   existing_type=postgresql.UUID(),
                   type_=sa.VARCHAR(),
                   existing_nullable=False)

    # Recreate foreign key with VARCHAR
    op.create_foreign_key(
        'message_conversation_id_fkey', 'message', 'conversation',
        ['conversation_id'], ['id']
    )
