import math

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.progress import UserProgress
from app.models.user import User


TOTAL_LESSONS = 30


def get_paginated_admin_users(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None
) -> dict:

    completed_progress_subquery = (
        db.query(
            UserProgress.user_id.label(
                "user_id"
            ),

            func.count(
                UserProgress.id
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


    query = (
        db.query(
            User,

            func.coalesce(
                completed_progress_subquery
                .c
                .completed_lessons,
                0
            ).label(
                "completed_lessons"
            )
        )
        .outerjoin(
            completed_progress_subquery,

            completed_progress_subquery
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

            pattern = (
                f"%{clean_search}%"
            )

            query = (
                query.filter(
                    or_(
                        User.username.ilike(
                            pattern
                        ),

                        User.email.ilike(
                            pattern
                        )
                    )
                )
            )


    total = (
        query.count()
    )


    total_pages = (
        math.ceil(
            total / page_size
        )
        if total > 0
        else 0
    )


    offset = (
        page - 1
    ) * page_size


    rows = (
        query
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


    for (
        user,
        completed_lessons
    ) in rows:

        completed_lessons = int(
            completed_lessons or 0
        )


        progress_percent = round(
            (
                completed_lessons
                / TOTAL_LESSONS
            )
            * 100,
            1
        )


        course_completed = (
            completed_lessons
            >= TOTAL_LESSONS
        )


        users.append(
            {
                "id":
                    user.id,

                "username":
                    user.username,

                "email":
                    user.email,

                "is_email_verified":
                    user.is_email_verified,

                "created_at":
                    user.created_at,

                "last_active_at":
                    user.last_active_at,

                "completed_lessons":
                    completed_lessons,

                "total_lessons":
                    TOTAL_LESSONS,

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