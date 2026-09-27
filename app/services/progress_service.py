import json

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.assessment_attempt import AssessmentAttempt
from app.models.progress import UserProgress

from app.services.lesson_service import (
    LESSONS_DIR,
    get_lesson_by_id
)


def get_user_progress(
    db: Session,
    user_id: int
) -> list[UserProgress]:

    return (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id
        )
        .order_by(
            UserProgress.lesson_id.asc()
        )
        .all()
    )


def get_completed_lesson_ids(
    db: Session,
    user_id: int
) -> set[int]:

    progress_records = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.completed == True
        )
        .all()
    )

    return {
        progress.lesson_id
        for progress in progress_records
    }


def can_access_lesson(
    db: Session,
    user_id: int,
    lesson_id: int
) -> bool:

    lesson = get_lesson_by_id(
        lesson_id
    )

    if lesson is None:
        return False

    completed_lesson_ids = (
        get_completed_lesson_ids(
            db=db,
            user_id=user_id
        )
    )

    if lesson_id in completed_lesson_ids:
        return True

    prerequisites = lesson.prerequisites

    return all(
        prerequisite_id in completed_lesson_ids
        for prerequisite_id in prerequisites
    )


def complete_lesson(
    db: Session,
    user_id: int,
    lesson_id: int
) -> UserProgress:

    progress = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id == lesson_id
        )
        .first()
    )

    if progress is None:

        progress = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.now(
                timezone.utc
            )
        )

        db.add(progress)

    else:

        if (
            not progress.completed
            or progress.completed_at is None
        ):
            progress.completed = True

            progress.completed_at = (
                datetime.now(
                    timezone.utc
                )
            )

    db.commit()
    db.refresh(progress)

    return progress


def get_progress_summary(
    db: Session,
    user_id: int
) -> dict:

    # =========================
    # LESSONLARNI O'QIYMIZ
    # =========================

    lesson_files = LESSONS_DIR.glob(
        "day_*.json"
    )

    lessons = []

    for file_path in lesson_files:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            lesson_data = json.load(
                file
            )

        lessons.append(
            lesson_data
        )

    lessons.sort(
        key=lambda lesson: lesson["day"]
    )

    total_lessons = len(
        lessons
    )

    lesson_by_id = {
        lesson["id"]: lesson
        for lesson in lessons
    }

    # =========================
    # COMPLETED LESSONS
    # =========================

    completed_lesson_ids = (
        get_completed_lesson_ids(
            db=db,
            user_id=user_id
        )
    )

    completed_lessons = sum(
        1
        for lesson in lessons
        if lesson["id"]
        in completed_lesson_ids
    )

    # =========================
    # PROGRESS %
    # =========================

    if total_lessons == 0:
        progress_percent = 0

    else:
        progress_percent = round(
            (
                completed_lessons
                / total_lessons
            ) * 100
        )

    # =========================
    # CURRENT LESSON
    # =========================

    current_day = None
    current_lesson_id = None
    current_lesson_title = None

    for lesson in lessons:

        lesson_id = lesson["id"]

        if lesson_id in completed_lesson_ids:
            continue

        prerequisites = lesson.get(
            "prerequisites",
            []
        )

        prerequisites_completed = all(
            prerequisite_id
            in completed_lesson_ids
            for prerequisite_id
            in prerequisites
        )

        if prerequisites_completed:

            current_day = lesson["day"]

            current_lesson_id = (
                lesson_id
            )

            current_lesson_title = (
                lesson["title"]
            )

            break

    # =========================
    # ASSESSMENT STATISTICS
    # =========================

    total_attempts = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id
            == user_id
        )
        .count()
    )

    best_score = (
        db.query(
            func.max(
                AssessmentAttempt.score
            )
        )
        .filter(
            AssessmentAttempt.user_id
            == user_id
        )
        .scalar()
    )

    # =========================
    # LAST COMPLETED LESSON
    # =========================

    last_progress = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.completed == True,
            UserProgress.completed_at.isnot(
                None
            )
        )
        .order_by(
            UserProgress.completed_at.desc()
        )
        .first()
    )

    last_completed_day = None
    last_completed_at = None

    if last_progress is not None:

        last_completed_at = (
            last_progress.completed_at
        )

        lesson_data = lesson_by_id.get(
            last_progress.lesson_id
        )

        if lesson_data is not None:
            last_completed_day = (
                lesson_data["day"]
            )

    # =========================
    # COURSE COMPLETED
    # =========================

    course_completed = (
        total_lessons > 0
        and completed_lessons
        == total_lessons
    )

    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percent": progress_percent,

        "current_day": current_day,
        "current_lesson_id": current_lesson_id,
        "current_lesson_title": current_lesson_title,

        "total_attempts": total_attempts,
        "best_score": best_score,

        "last_completed_day": last_completed_day,
        "last_completed_at": last_completed_at,

        "course_completed": course_completed
    }