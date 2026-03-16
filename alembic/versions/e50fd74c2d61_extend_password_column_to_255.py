"""extend_password_column_to_255

Revision ID: e50fd74c2d61
Revises: 06e990cb07eb
Create Date: 2026-03-11 14:27:03.364682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e50fd74c2d61'
down_revision: Union[str, Sequence[str], None] = '06e990cb07eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'password',
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'password',
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True)
