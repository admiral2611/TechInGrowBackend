import math
from pathlib import Path

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.progress import UserProgress
from app.models.user import User


ROOT_DIR = Path(
    __file__
).resolve().parents[2]

LESSONS_DIR = (
    ROOT_DIR
    / "data"
    / "lessons"
)


def _get_total_lessons() -> int:

    if not LESSONS_DIR.exists():
        return 0

    return len(
        list(
            LESSONS_DIR.glob(
                "day_*.json"
            )
        )
    )


def get_paginated_admin_users(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None
) -> dict:

    total_lessons = (
        _get_total_lessons()
    )

    completed_subquery = (
        db.query(
            UserProgress.user_id.label(
                "user_id"
            ),
            func.count(
                func.distinct(
                    UserProgress.lesson_id
                )
            ).label(
                "completed_lessons"
            )
        )
        .filter(
            UserProgress.completed.is_(
                True
            )
        )
        .group_by(
            UserProgress.user_id
        )
        .subquery()
    )

    base_query = (
        db.query(
            User,
            func.coalesce(
                completed_subquery
                .c
                .completed_lessons,
                0
            ).label(
                "completed_lessons"
            )
        )
        .outerjoin(
            completed_subquery,
            completed_subquery
            .c
            .user_id
            == User.id
        )
        .filter(
            User.is_admin.is_(
                False
            )
        )
    )

    if search:

        clean_search = (
            search
            .strip()
        )

        if clean_search:

            search_pattern = (
                f"%{clean_search}%"
            )

            base_query = (
                base_query.filter(
                    or_(
                        User.username.ilike(
                            search_pattern
                        ),
                        User.email.ilike(
                            search_pattern
                        )
                    )
                )
            )

    total = (
        base_query.count()
    )

    total_pages = (
        math.ceil(
            total
            / page_size
        )
        if total > 0
        else 0
    )

    offset = (
        page - 1
    ) * page_size

    rows = (
        base_query
        .order_by(
            User.created_at.desc()
        )
        .offset(
            offset
        )
        .limit(
            page_size
        )
        .all()
    )

    users = []

    for user, completed_lessons in rows:

        completed_lessons = int(
            completed_lessons
            or 0
        )

        if total_lessons > 0:

            progress_percent = round(
                (
                    completed_lessons
                    / total_lessons
                )
                * 100
            )

        else:

            progress_percent = 0

        course_completed = (
            total_lessons > 0
            and
            completed_lessons
            >= total_lessons
        )

        users.append(
            {
                "id":
                    user.id,

                "username":
                    user.username,

                "email":
                    user.email,

                "created_at":
                    user.created_at,

                "last_active_at":
                    user.last_active_at,

                "completed_lessons":
                    completed_lessons,

                "total_lessons":
                    total_lessons,

                "progress_percent":
                    progress_percent,

                "course_completed":
                    course_completed
            }
        )

    return {
        "page":
            page,

        "page_size":
            page_size,

        "total":
            total,

        "total_pages":
            total_pages,

        "users":
            users
    }