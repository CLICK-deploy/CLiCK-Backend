"""add rating to users

Revision ID: f3a1b2c4d5e6
Revises: 4cdb5552f764
Create Date: 2026-03-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a1b2c4d5e6'
down_revision: Union[str, Sequence[str], None] = '4cdb5552f764'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('rating', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'rating')
