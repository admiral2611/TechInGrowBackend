"""empty message

Revision ID: 080cd425df2b
Revises: c1c391e1da9a
Create Date: 2026-09-26 10:57:57.251429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '080cd425df2b'
down_revision: Union[str, Sequence[str], None] = 'c1c391e1da9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
