from pathlib import Path

from app.core.lesson_errors import (
    LessonContentError
)

from app.schemas.lesson_content import (
    LessonContent
)

from app.services.lesson_service import (
    LESSONS_DIR,
    load_lesson_file
)


EXPECTED_TOTAL_DAYS = 30


def check_duplicate_ids(
    lessons: list[LessonContent]
) -> list[str]:

    errors: list[str] = []

    seen: dict[int, LessonContent] = {}

    for lesson in lessons:

        if lesson.id in seen:

            previous = seen[lesson.id]

            errors.append(
                (
                    f"Duplicate lesson id: "
                    f"{lesson.id} "
                    f"(Day {previous.day} "
                    f"and Day {lesson.day})"
                )
            )

        else:
            seen[lesson.id] = lesson

    return errors


def check_duplicate_days(
    lessons: list[LessonContent]
) -> list[str]:

    errors: list[str] = []

    seen: dict[int, LessonContent] = {}

    for lesson in lessons:

        if lesson.day in seen:

            previous = seen[lesson.day]

            errors.append(
                (
                    f"Duplicate day: "
                    f"{lesson.day} "
                    f"(lesson id {previous.id} "
                    f"and lesson id {lesson.id})"
                )
            )

        else:
            seen[lesson.day] = lesson

    return errors


def check_filename_day(
    lesson: LessonContent,
    file_path: Path
) -> list[str]:

    errors: list[str] = []

    expected_file_name = (
        f"day_{lesson.day:02d}.json"
    )

    if file_path.name != expected_file_name:

        errors.append(
            (
                f"{file_path.name}: "
                f"lesson day is {lesson.day}, "
                f"but expected filename is "
                f"{expected_file_name}"
            )
        )

    return errors


def check_day_sequence(
    lessons: list[LessonContent]
) -> list[str]:

    errors: list[str] = []

    if not lessons:
        return errors

    existing_days = {
        lesson.day
        for lesson in lessons
    }

    max_day = max(existing_days)

    for day in range(
        1,
        max_day + 1
    ):

        if day not in existing_days:

            errors.append(
                (
                    f"Missing lesson day: "
                    f"Day {day}"
                )
            )

    return errors


def check_day_range(
    lessons: list[LessonContent]
) -> list[str]:

    errors: list[str] = []

    for lesson in lessons:

        if lesson.day > EXPECTED_TOTAL_DAYS:

            errors.append(
                (
                    f"Lesson id {lesson.id} "
                    f"has Day {lesson.day}, "
                    f"but course maximum is "
                    f"{EXPECTED_TOTAL_DAYS}"
                )
            )

    return errors


def check_prerequisites(
    lessons: list[LessonContent]
) -> list[str]:

    errors: list[str] = []

    lessons_by_id = {
        lesson.id: lesson
        for lesson in lessons
    }

    for lesson in lessons:

        for prerequisite_id in (
            lesson.prerequisites
        ):

            prerequisite = (
                lessons_by_id.get(
                    prerequisite_id
                )
            )

            if prerequisite is None:

                errors.append(
                    (
                        f"Day {lesson.day}: "
                        f"prerequisite lesson id "
                        f"{prerequisite_id} "
                        f"does not exist"
                    )
                )

                continue

            if prerequisite.day >= lesson.day:

                errors.append(
                    (
                        f"Day {lesson.day}: "
                        f"prerequisite lesson "
                        f"{prerequisite_id} "
                        f"is Day "
                        f"{prerequisite.day}. "
                        f"A prerequisite must "
                        f"come before the lesson."
                    )
                )

    return errors


def check_prerequisite_cycles(
    lessons: list[LessonContent]
) -> list[str]:

    errors: list[str] = []

    lessons_by_id = {
        lesson.id: lesson
        for lesson in lessons
    }

    visited: set[int] = set()

    visiting: set[int] = set()

    def visit(
        lesson_id: int,
        path: list[int]
    ) -> None:

        if lesson_id in visiting:

            cycle_start = (
                path.index(lesson_id)
                if lesson_id in path
                else 0
            )

            cycle = (
                path[cycle_start:]
                + [lesson_id]
            )

            cycle_text = " -> ".join(
                str(item)
                for item in cycle
            )

            message = (
                f"Prerequisite cycle "
                f"detected: "
                f"{cycle_text}"
            )

            if message not in errors:
                errors.append(message)

            return

        if lesson_id in visited:
            return

        lesson = lessons_by_id.get(
            lesson_id
        )

        if lesson is None:
            return

        visiting.add(
            lesson_id
        )

        path.append(
            lesson_id
        )

        for prerequisite_id in (
            lesson.prerequisites
        ):

            visit(
                prerequisite_id,
                path
            )

        path.pop()

        visiting.remove(
            lesson_id
        )

        visited.add(
            lesson_id
        )

    for lesson in lessons:

        visit(
            lesson.id,
            []
        )

    return errors


def validate_all_lessons() -> None:

    lesson_files = sorted(
        LESSONS_DIR.glob(
            "day_*.json"
        )
    )

    print()
    print(
        "TechInGrow Course Validator"
    )

    print(
        "=" * 50
    )

    if not lesson_files:

        print(
            "[ERROR] No lesson files found."
        )

        return

    lessons: list[LessonContent] = []

    file_by_lesson_id: dict[
        int,
        Path
    ] = {}

    file_errors = 0

    for file_path in lesson_files:

        try:

            lesson = load_lesson_file(
                file_path
            )

            lessons.append(
                lesson
            )

            file_by_lesson_id[
                lesson.id
            ] = file_path

            print(
                (
                    f"[OK] "
                    f"{file_path.name} "
                    f"- Day {lesson.day}: "
                    f"{lesson.title}"
                )
            )

        except LessonContentError as error:

            file_errors += 1

            print()
            print(
                f"[ERROR] "
                f"{error.file_name}"
            )

            print(
                error.message
            )

    print()
    print(
        "-" * 50
    )

    course_errors: list[str] = []

    course_errors.extend(
        check_duplicate_ids(
            lessons
        )
    )

    course_errors.extend(
        check_duplicate_days(
            lessons
        )
    )

    course_errors.extend(
        check_day_sequence(
            lessons
        )
    )

    course_errors.extend(
        check_day_range(
            lessons
        )
    )

    course_errors.extend(
        check_prerequisites(
            lessons
        )
    )

    course_errors.extend(
        check_prerequisite_cycles(
            lessons
        )
    )

    for lesson in lessons:

        file_path = (
            file_by_lesson_id.get(
                lesson.id
            )
        )

        if file_path:

            course_errors.extend(
                check_filename_day(
                    lesson=lesson,
                    file_path=file_path
                )
            )

    if course_errors:

        print(
            "Course errors:"
        )

        print()

        for error in course_errors:

            print(
                f"[ERROR] {error}"
            )

    else:

        print(
            "[OK] Course structure "
            "is valid."
        )

    print()
    print(
        "=" * 50
    )

    total_valid_files = len(
        lessons
    )

    total_errors = (
        file_errors
        + len(course_errors)
    )

    print(
        f"Lesson files: "
        f"{len(lesson_files)}"
    )

    print(
        f"Valid files: "
        f"{total_valid_files}"
    )

    print(
        f"File errors: "
        f"{file_errors}"
    )

    print(
        f"Course errors: "
        f"{len(course_errors)}"
    )

    print(
        f"Total errors: "
        f"{total_errors}"
    )

    print()

    progress_percent = round(
        (
            total_valid_files
            / EXPECTED_TOTAL_DAYS
        )
        * 100
    )

    remaining = max(
        EXPECTED_TOTAL_DAYS
        - total_valid_files,
        0
    )

    print(
        (
            f"Course progress: "
            f"{total_valid_files}/"
            f"{EXPECTED_TOTAL_DAYS} "
            f"({progress_percent}%)"
        )
    )

    print(
        (
            f"Remaining lessons: "
            f"{remaining}"
        )
    )

    print()

    if total_errors == 0:

        print(
            "[SUCCESS] "
            "All existing lessons "
            "are valid."
        )

    else:

        print(
            "[FAILED] "
            "Fix the errors above."
        )


if __name__ == "__main__":

    validate_all_lessons()