from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.assessment_attempt import AssessmentAttempt
from app.models.progress import UserProgress
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.lesson_service import load_lesson_file


ROOT_DIR = Path(__file__).resolve().parents[2]

LESSONS_DIR = (
    ROOT_DIR
    / "data"
    / "lessons"
)


def _load_lessons() -> list[dict]:

    lessons = []

    lesson_files = sorted(
        LESSONS_DIR.glob(
            "day_*.json"
        )
    )

    for file_path in lesson_files:

        lesson = load_lesson_file(
            file_path
        )

        lessons.append(
            {
                "id": lesson.id,
                "day": lesson.day,
                "title": lesson.title
            }
        )

    lessons.sort(
        key=lambda item: item["day"]
    )

    return lessons


def get_user_detail_by_admin(
    db: Session,
    user_id: int
) -> dict:

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    lessons = _load_lessons()

    total_lessons = len(
        lessons
    )

    progress_rows = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id
            == user.id
        )
        .all()
    )

    progress_by_lesson = {
        progress.lesson_id:
            progress

        for progress
        in progress_rows
    }

    progress_items = []

    completed_lessons = 0

    for lesson in lessons:

        progress = (
            progress_by_lesson.get(
                lesson["id"]
            )
        )

        completed = bool(
            progress
            and
            progress.completed
        )

        completed_at = (
            progress.completed_at

            if (
                progress
                and
                progress.completed
            )

            else None
        )

        if completed:
            completed_lessons += 1

        progress_items.append(
            {
                "lesson_id":
                    lesson["id"],

                "day":
                    lesson["day"],

                "title":
                    lesson["title"],

                "completed":
                    completed,

                "completed_at":
                    completed_at
            }
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

    attempts = (
        db.query(
            AssessmentAttempt
        )
        .filter(
            AssessmentAttempt.user_id
            == user.id
        )
        .order_by(
            AssessmentAttempt
            .created_at
            .desc()
        )
        .all()
    )

    total_attempts = len(
        attempts
    )

    passed_attempts = sum(
        1

        for attempt
        in attempts

        if attempt.passed
    )

    failed_attempts = (
        total_attempts
        - passed_attempts
    )

    if total_attempts > 0:

        average_score = round(
            sum(
                attempt.score
                for attempt
                in attempts
            )
            / total_attempts,
            1
        )

        best_score = max(
            attempt.score
            for attempt
            in attempts
        )

    else:

        average_score = 0.0
        best_score = 0

    lesson_map = {
        lesson["id"]:
            lesson

        for lesson
        in lessons
    }

    recent_attempts = []

    for attempt in attempts[:20]:

        lesson = lesson_map.get(
            attempt.lesson_id
        )

        if lesson is None:

            day = attempt.lesson_id

            title = (
                f"Lesson {attempt.lesson_id}"
            )

        else:

            day = lesson["day"]
            title = lesson["title"]

        recent_attempts.append(
            {
                "id":
                    attempt.id,

                "lesson_id":
                    attempt.lesson_id,

                "day":
                    day,

                "title":
                    title,

                "attempt_number":
                    attempt.attempt_number,

                "score":
                    attempt.score,

                "correct_answers":
                    attempt.correct_answers,

                "total_questions":
                    attempt.total_questions,

                "passed":
                    attempt.passed,

                "created_at":
                    attempt.created_at
            }
        )

    return {
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
            course_completed,

        "progress":
            progress_items,

        "assessment_summary":
            {
                "total_attempts":
                    total_attempts,

                "passed_attempts":
                    passed_attempts,

                "failed_attempts":
                    failed_attempts,

                "average_score":
                    average_score,

                "best_score":
                    best_score
            },

        "recent_attempts":
            recent_attempts
    }


def delete_user_by_admin(
    db: Session,
    user_id: int
) -> dict:

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_admin:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user cannot be deleted"
        )

    username = user.username

    try:

        (
            db.query(RefreshToken)
            .filter(
                RefreshToken.user_id
                == user.id
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(AssessmentAttempt)
            .filter(
                AssessmentAttempt.user_id
                == user.id
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(UserProgress)
            .filter(
                UserProgress.user_id
                == user.id
            )
            .delete(
                synchronize_session=False
            )
        )

        db.delete(
            user
        )

        db.commit()

    except Exception:

        db.rollback()

        raise

    return {
        "message":
            "User deleted successfully",

        "user_id":
            user_id,

        "username":
            username
    }