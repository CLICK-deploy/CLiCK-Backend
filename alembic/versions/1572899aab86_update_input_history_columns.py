"""update_input_history_columns

Revision ID: 1572899aab86
Revises: 8352c1d5ef3c
Create Date: 2026-03-25 15:02:04.218735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1572899aab86'
down_revision: Union[str, Sequence[str], None] = '8352c1d5ef3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('input_history') as batch_op:
        batch_op.drop_column('role')
        batch_op.drop_column('fixed_content')
        batch_op.drop_column('reason')
        batch_op.alter_column('topic', new_column_name='input')


def downgrade() -> None:
    with op.batch_alter_table('input_history') as batch_op:
        batch_op.alter_column('input', new_column_name='topic')
        batch_op.add_column(sa.Column('reason', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('fixed_content', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('role', sa.String(length=10), nullable=False, server_default='user'))
