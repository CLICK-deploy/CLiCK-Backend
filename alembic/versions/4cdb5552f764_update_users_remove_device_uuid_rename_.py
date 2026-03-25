"""update_users_remove_device_uuid_rename_grade_to_plan

Revision ID: 4cdb5552f764
Revises: 1572899aab86
Create Date: 2026-03-25 15:07:17.121765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cdb5552f764'
down_revision: Union[str, Sequence[str], None] = '1572899aab86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('device_uuid')
        batch_op.alter_column('grade', new_column_name='plan')


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('plan', new_column_name='grade')
        batch_op.add_column(sa.Column('device_uuid', sa.String(length=36), nullable=True))
