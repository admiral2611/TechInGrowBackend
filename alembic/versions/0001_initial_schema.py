"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-26

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"

down_revision: Union[str, None] = None

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

    # =========================
    # USERS
    # =========================

    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "username",
            sa.String(length=50),
            nullable=False
        ),

        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text(
                "(CURRENT_TIMESTAMP)"
            ),
            nullable=False
        ),

        sa.PrimaryKeyConstraint(
            "id"
        )
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_users_username",
        "users",
        ["username"],
        unique=True
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True
    )

    # =========================
    # USER PROGRESS
    # =========================

    op.create_table(
        "user_progress",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "lesson_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "completed",
            sa.Boolean(),
            nullable=False
        ),

        sa.PrimaryKeyConstraint(
            "id"
        )
    )

    op.create_index(
        "ix_user_progress_id",
        "user_progress",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_user_progress_user_id",
        "user_progress",
        ["user_id"],
        unique=False
    )

    op.create_index(
        "ix_user_progress_lesson_id",
        "user_progress",
        ["lesson_id"],
        unique=False
    )

    # =========================
    # ASSESSMENT ATTEMPTS
    # =========================

    op.create_table(
        "assessment_attempts",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "lesson_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "attempt_number",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "score",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "correct_answers",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "total_questions",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "passed",
            sa.Boolean(),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text(
                "(CURRENT_TIMESTAMP)"
            ),
            nullable=False
        ),

        sa.PrimaryKeyConstraint(
            "id"
        )
    )

    op.create_index(
        "ix_assessment_attempts_id",
        "assessment_attempts",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_assessment_attempts_user_id",
        "assessment_attempts",
        ["user_id"],
        unique=False
    )

    op.create_index(
        "ix_assessment_attempts_lesson_id",
        "assessment_attempts",
        ["lesson_id"],
        unique=False
    )


def downgrade() -> None:

    op.drop_index(
        "ix_assessment_attempts_lesson_id",
        table_name="assessment_attempts"
    )

    op.drop_index(
        "ix_assessment_attempts_user_id",
        table_name="assessment_attempts"
    )

    op.drop_index(
        "ix_assessment_attempts_id",
        table_name="assessment_attempts"
    )

    op.drop_table(
        "assessment_attempts"
    )

    op.drop_index(
        "ix_user_progress_lesson_id",
        table_name="user_progress"
    )

    op.drop_index(
        "ix_user_progress_user_id",
        table_name="user_progress"
    )

    op.drop_index(
        "ix_user_progress_id",
        table_name="user_progress"
    )

    op.drop_table(
        "user_progress"
    )

    op.drop_index(
        "ix_users_email",
        table_name="users"
    )

    op.drop_index(
        "ix_users_username",
        table_name="users"
    )

    op.drop_index(
        "ix_users_id",
        table_name="users"
    )

    op.drop_table(
        "users"
    )