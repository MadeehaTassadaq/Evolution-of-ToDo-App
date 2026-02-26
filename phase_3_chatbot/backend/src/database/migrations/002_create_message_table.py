"""Create message table

Revision ID: 002
Revises: 001
Create Date: 2026-01-10 14:16:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

# revision identifiers
revision = '002_create_message_table'
down_revision = '001_create_conversation_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create message table
    op.create_table(
        'message',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('conversation_id', sa.String(36), nullable=False, index=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.utcnow),
        sa.Column('metadata', sa.JSON, nullable=True),
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_message_conversation_id',
        'message',
        'conversation',
        ['conversation_id'],
        ['id']
    )


def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_message_conversation_id', 'message', type_='foreignkey')
    # Then drop the table
    op.drop_table('message')