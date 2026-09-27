"""empty message

Revision ID: c1c391e1da9a
Revises: 4021ca540e83
Create Date: 2026-09-26 10:54:04.176825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1c391e1da9a'
down_revision: Union[str, Sequence[str], None] = '4021ca540e83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
