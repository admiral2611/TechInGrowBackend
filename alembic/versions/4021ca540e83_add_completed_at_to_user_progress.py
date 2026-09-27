"""add completed_at to user_progress

Revision ID: 4021ca540e83
Revises: 1e676109536f
Create Date: 2026-09-26

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4021ca540e83"

down_revision: Union[str, None] = "1e676109536f"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:
    with op.batch_alter_table(
        "user_progress"
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "completed_at",
                sa.DateTime(),
                nullable=True
            )
        )

    # Oldindan completed bo'lgan progresslar uchun
    # migration bajarilgan vaqtni completed_at sifatida yozamiz.
    op.execute(
        """
        UPDATE user_progress
        SET completed_at = CURRENT_TIMESTAMP
        WHERE completed = 1
          AND completed_at IS NULL
        """
    )


def downgrade() -> None:
    with op.batch_alter_table(
        "user_progress"
    ) as batch_op:

        batch_op.drop_column(
            "completed_at"
        )