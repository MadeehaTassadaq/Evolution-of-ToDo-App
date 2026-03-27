"""add_extra_data_to_message

Revision ID: 59103f8c7b95
Revises: fix_uuid_types
Create Date: 2026-03-05 15:27:06.319685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59103f8c7b95'
down_revision: Union[str, Sequence[str], None] = 'fix_uuid_types'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add extra_data column to message table
    op.add_column('message', sa.Column('extra_data', sa.JSON, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove extra_data column from message table
    op.drop_column('message', 'extra_data')
