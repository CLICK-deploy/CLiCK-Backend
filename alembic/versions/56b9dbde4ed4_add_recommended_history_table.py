"""add_recommended_history_table

Revision ID: 56b9dbde4ed4
Revises: c1d2e3f4a5b6
Create Date: 2026-03-25 13:50:03.797419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '56b9dbde4ed4'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('recommended_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.String(length=200), nullable=True),
    sa.Column('title', sa.String(length=30), nullable=False),
    sa.Column('content', sa.String(length=1000), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name=op.f('fk_recommended_history_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recommended_history'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('recommended_history')
