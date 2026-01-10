"""Create conversation table

Revision ID: 001
Revises:
Create Date: 2026-01-10 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

# revision identifiers
revision = '001_create_conversation_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create conversation table
    op.create_table(
        'conversation',
        sa.Column('id', sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column('user_id', sa.String(255), nullable=False, index=True),
        sa.Column('title', sa.String(200), default="New Conversation"),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('status', sa.String(20), default="active"),
    )


def downgrade():
    op.drop_table('conversation')