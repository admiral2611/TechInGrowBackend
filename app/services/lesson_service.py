import json

from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.lesson_errors import (
    LessonContentError
)

from app.models.progress import (
    UserProgress
)

from app.schemas.lesson import (
    Lesson,
    LessonSummary
)

from app.schemas.lesson_content import (
    LessonContent
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

LESSONS_DIR = (
    BASE_DIR
    / "data"
    / "lessons"
)


def load_lesson_file(
    file_path: Path
) -> LessonContent:

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            lesson_data = json.load(
                file
            )

    except json.JSONDecodeError as error:

        raise LessonContentError(
            file_name=file_path.name,
            message=(
                f"Invalid JSON: "
                f"{error.msg}"
            )
        )

    try:

        return LessonContent.model_validate(
            lesson_data
        )

    except ValidationError as error:

        raise LessonContentError(
            file_name=file_path.name,
            message=str(error)
        )


def get_lesson(
    day: int
) -> Lesson | None:

    file_path = (
        LESSONS_DIR
        / f"day_{day:02d}.json"
    )

    if not file_path.exists():
        return None

    lesson_content = load_lesson_file(
        file_path
    )

    return Lesson.model_validate(
        lesson_content.model_dump()
    )


def get_lesson_data_by_id(
    lesson_id: int
) -> dict | None:

    lesson_files = sorted(
        LESSONS_DIR.glob(
            "day_*.json"
        )
    )

    for file_path in lesson_files:

        lesson_content = load_lesson_file(
            file_path
        )

        if lesson_content.id == lesson_id:

            return lesson_content.model_dump()

    return None


def get_lesson_by_id(
    lesson_id: int
) -> Lesson | None:

    lesson_data = (
        get_lesson_data_by_id(
            lesson_id
        )
    )

    if lesson_data is None:
        return None

    return Lesson.model_validate(
        lesson_data
    )


def get_all_lessons(
    db: Session,
    user_id: int
) -> list[LessonSummary]:

    lesson_files = sorted(
        LESSONS_DIR.glob(
            "day_*.json"
        )
    )

    progress_records = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == user_id,
            UserProgress.completed == True
        )
        .all()
    )

    completed_lesson_ids = {
        progress.lesson_id
        for progress
        in progress_records
    }

    lessons: list[
        LessonSummary
    ] = []

    for file_path in lesson_files:

        lesson_data = load_lesson_file(
            file_path
        )

        lesson_id = (
            lesson_data.id
        )

        completed = (
            lesson_id
            in completed_lesson_ids
        )

        prerequisites_completed = all(
            prerequisite_id
            in completed_lesson_ids

            for prerequisite_id
            in lesson_data.prerequisites
        )

        locked = (
            not completed
            and not prerequisites_completed
        )

        lesson = LessonSummary(
            id=lesson_data.id,
            day=lesson_data.day,
            title=lesson_data.title,
            description=(
                lesson_data.description
            ),
            level=lesson_data.level,
            category=lesson_data.category,
            duration_minutes=(
                lesson_data.duration_minutes
            ),
            completed=completed,
            locked=locked
        )

        lessons.append(
            lesson
        )

    lessons.sort(
        key=lambda lesson: lesson.day
    )

    return lessons