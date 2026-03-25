"""rename events table to analyze_history

Revision ID: c1d2e3f4a5b6
Revises: e50fd74c2d61
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'e50fd74c2d61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('events', 'analyze_history')


def downgrade() -> None:
    op.rename_table('analyze_history', 'events')
