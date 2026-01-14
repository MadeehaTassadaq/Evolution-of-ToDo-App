"""Create user table

Revision ID: 004_create_user_table
Revises: 003_create_todo_table
Create Date: 2026-01-10 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from datetime import datetime

# revision identifiers
revision = '004_create_user_table'
down_revision = '003_create_todo_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create the user table
    op.create_table('user',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_user_username', 'user', ['username'], unique=True)
    op.create_index('ix_user_email', 'user', ['email'], unique=True)
    op.create_index('ix_user_is_active', 'user', ['is_active'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_user_is_active', table_name='user')
    op.drop_index('ix_user_email', table_name='user')
    op.drop_index('ix_user_username', table_name='user')

    # Drop the user table
    op.drop_table('user')