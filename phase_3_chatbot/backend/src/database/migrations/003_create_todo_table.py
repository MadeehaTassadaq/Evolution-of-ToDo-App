"""Create todo table

Revision ID: 003
Revises: 002
Create Date: 2026-01-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from datetime import datetime

# revision identifiers
revision = '003_create_todo_table'
down_revision = '002_create_message_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create the todo table
    op.create_table('todo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('due_date', sa.String(length=20), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index for user_id for better query performance
    op.create_index('ix_todo_user_id', 'todo', ['user_id'])

    # Create index for status for filtering
    op.create_index('ix_todo_status', 'todo', ['status'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_todo_status', table_name='todo')
    op.drop_index('ix_todo_user_id', table_name='todo')

    # Drop the todo table
    op.drop_table('todo')