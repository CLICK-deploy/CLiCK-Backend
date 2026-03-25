"""rename_histories_to_input_history

Revision ID: 8352c1d5ef3c
Revises: 56b9dbde4ed4
Create Date: 2026-03-25 14:42:19.015147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8352c1d5ef3c'
down_revision: Union[str, Sequence[str], None] = '56b9dbde4ed4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('histories', 'input_history')
    op.drop_index('idx_hist_user_room_created', table_name='input_history')
    op.create_index('idx_input_hist_user_room_created', 'input_history', ['user_id', 'room_id', sa.literal_column('created_at DESC')], unique=False)


def downgrade() -> None:
    op.drop_index('idx_input_hist_user_room_created', table_name='input_history')
    op.create_index('idx_hist_user_room_created', 'input_history', ['user_id', 'room_id', sa.literal_column('created_at DESC')], unique=False)
    op.rename_table('input_history', 'histories')
