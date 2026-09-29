from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.models.assessment_attempt import AssessmentAttempt
from app.models.progress import UserProgress
from app.models.user import User
from app.services.lesson_service import load_lesson_file


TASHKENT_TZ = ZoneInfo(
    "Asia/Tashkent"
)

ROOT_DIR = Path(
    __file__
).resolve().parents[2]

LESSONS_DIR = (
    ROOT_DIR
    / "data"
    / "lessons"
)


def _count_users(
    db: Session,
    *conditions
) -> int:

    query = (
        db.query(
            func.count(
                User.id
            )
        )
        .filter(
            User.is_admin.is_(
                False
            )
        )
    )

    if conditions:
        query = query.filter(
            *conditions
        )

    return int(
        query.scalar()
        or 0
    )


def _load_course_lessons() -> list[dict]:

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


def _get_total_lessons() -> int:

    return len(
        _load_course_lessons()
    )


def get_dashboard_stats(
    db: Session
) -> dict:

    now_utc = datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )

    now_tashkent = datetime.now(
        TASHKENT_TZ
    )

    today_start_tashkent = (
        now_tashkent
        .replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
    )

    today_start_utc = (
        today_start_tashkent
        .astimezone(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )

    seven_days_ago = (
        now_utc
        - timedelta(
            days=7
        )
    )

    thirty_days_ago = (
        now_utc
        - timedelta(
            days=30
        )
    )

    total_users = _count_users(
        db
    )

    active_today = _count_users(
        db,
        User.last_active_at.is_not(
            None
        ),
        User.last_active_at
        >= today_start_utc
    )

    active_7_days = _count_users(
        db,
        User.last_active_at.is_not(
            None
        ),
        User.last_active_at
        >= seven_days_ago
    )

    active_30_days = _count_users(
        db,
        User.last_active_at.is_not(
            None
        ),
        User.last_active_at
        >= thirty_days_ago
    )

    new_users_today = _count_users(
        db,
        User.created_at
        >= today_start_utc
    )

    new_users_7_days = _count_users(
        db,
        User.created_at
        >= seven_days_ago
    )

    return {
        "total_users":
            total_users,

        "active_today":
            active_today,

        "active_7_days":
            active_7_days,

        "active_30_days":
            active_30_days,

        "new_users_today":
            new_users_today,

        "new_users_7_days":
            new_users_7_days
    }


def get_admin_users(
    db: Session
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

    rows = (
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
        .order_by(
            User.created_at.desc()
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
        "total":
            len(
                users
            ),

        "users":
            users
    }


def get_course_stats(
    db: Session
) -> dict:

    lessons = (
        _load_course_lessons()
    )

    total_lessons = len(
        lessons
    )

    total_users = _count_users(
        db
    )

    completion_rows = (
        db.query(
            UserProgress.lesson_id,

            func.count(
                func.distinct(
                    UserProgress.user_id
                )
            ).label(
                "completed_users"
            )
        )
        .join(
            User,
            User.id
            == UserProgress.user_id
        )
        .filter(
            User.is_admin.is_(
                False
            ),
            UserProgress.completed.is_(
                True
            )
        )
        .group_by(
            UserProgress.lesson_id
        )
        .all()
    )

    completed_by_lesson = {
        int(lesson_id):
            int(completed_users)

        for (
            lesson_id,
            completed_users
        )
        in completion_rows
    }

    user_progress_rows = (
        db.query(
            User.id,

            func.count(
                func.distinct(
                    UserProgress.lesson_id
                )
            ).label(
                "completed_lessons"
            )
        )
        .outerjoin(
            UserProgress,
            and_(
                UserProgress.user_id
                == User.id,

                UserProgress.completed.is_(
                    True
                )
            )
        )
        .filter(
            User.is_admin.is_(
                False
            )
        )
        .group_by(
            User.id
        )
        .all()
    )

    progress_counts = [
        int(
            completed_lessons
            or 0
        )

        for (
            _,
            completed_lessons
        )
        in user_progress_rows
    ]

    started_users = sum(
        1

        for completed_lessons
        in progress_counts

        if completed_lessons > 0
    )

    if total_lessons > 0:

        completed_course_users = sum(
            1

            for completed_lessons
            in progress_counts

            if completed_lessons
            >= total_lessons
        )

    else:

        completed_course_users = 0

    if total_users > 0:

        completion_rate = round(
            (
                completed_course_users
                / total_users
            )
            * 100,
            1
        )

        average_completed_lessons = round(
            sum(
                progress_counts
            )
            / total_users,
            2
        )

    else:

        completion_rate = 0.0

        average_completed_lessons = 0.0

    if total_lessons > 0:

        average_progress_percent = round(
            (
                average_completed_lessons
                / total_lessons
            )
            * 100,
            1
        )

    else:

        average_progress_percent = 0.0

    lesson_stats = []

    previous_completed = None

    largest_drop = None

    largest_drop_count = 0

    for lesson in lessons:

        completed_users = (
            completed_by_lesson.get(
                lesson["id"],
                0
            )
        )

        if total_users > 0:

            completion_percent = round(
                (
                    completed_users
                    / total_users
                )
                * 100,
                1
            )

        else:

            completion_percent = 0.0

        if previous_completed is None:

            drop_from_previous = 0

        else:

            drop_from_previous = max(
                0,
                previous_completed
                - completed_users
            )

            if (
                drop_from_previous
                > largest_drop_count
            ):

                previous_day = (
                    lesson["day"]
                    - 1
                )

                if previous_completed > 0:

                    drop_percent = round(
                        (
                            drop_from_previous
                            / previous_completed
                        )
                        * 100,
                        1
                    )

                else:

                    drop_percent = 0.0

                largest_drop = {
                    "from_day":
                        previous_day,

                    "to_day":
                        lesson["day"],

                    "dropped_users":
                        drop_from_previous,

                    "drop_percent":
                        drop_percent
                }

                largest_drop_count = (
                    drop_from_previous
                )

        lesson_stats.append(
            {
                "lesson_id":
                    lesson["id"],

                "day":
                    lesson["day"],

                "title":
                    lesson["title"],

                "completed_users":
                    completed_users,

                "completion_percent":
                    completion_percent,

                "drop_from_previous":
                    drop_from_previous
            }
        )

        previous_completed = (
            completed_users
        )

    return {
        "total_users":
            total_users,

        "total_lessons":
            total_lessons,

        "started_users":
            started_users,

        "completed_course_users":
            completed_course_users,

        "completion_rate":
            completion_rate,

        "average_completed_lessons":
            average_completed_lessons,

        "average_progress_percent":
            average_progress_percent,

        "largest_drop":
            largest_drop,

        "lessons":
            lesson_stats
    }


def get_assessment_stats(
    db: Session
) -> dict:

    lessons = (
        _load_course_lessons()
    )

    lesson_rows = (
        db.query(
            AssessmentAttempt.lesson_id,

            func.count(
                AssessmentAttempt.id
            ).label(
                "total_attempts"
            ),

            func.count(
                func.distinct(
                    AssessmentAttempt.user_id
                )
            ).label(
                "unique_users"
            ),

            func.sum(
                case(
                    (
                        AssessmentAttempt.passed.is_(
                            True
                        ),
                        1
                    ),
                    else_=0
                )
            ).label(
                "passed_attempts"
            ),

            func.avg(
                AssessmentAttempt.score
            ).label(
                "average_score"
            )
        )
        .join(
            User,
            User.id
            == AssessmentAttempt.user_id
        )
        .filter(
            User.is_admin.is_(
                False
            )
        )
        .group_by(
            AssessmentAttempt.lesson_id
        )
        .all()
    )

    lesson_aggregates = {}

    for row in lesson_rows:

        total_attempts = int(
            row.total_attempts
            or 0
        )

        unique_users = int(
            row.unique_users
            or 0
        )

        passed_attempts = int(
            row.passed_attempts
            or 0
        )

        failed_attempts = max(
            0,
            total_attempts
            - passed_attempts
        )

        if total_attempts > 0:

            pass_rate = round(
                (
                    passed_attempts
                    / total_attempts
                )
                * 100,
                1
            )

        else:

            pass_rate = 0.0

        average_score = round(
            float(
                row.average_score
                or 0
            ),
            1
        )

        if unique_users > 0:

            average_attempts_per_user = round(
                total_attempts
                / unique_users,
                2
            )

        else:

            average_attempts_per_user = 0.0

        lesson_aggregates[
            int(
                row.lesson_id
            )
        ] = {
            "total_attempts":
                total_attempts,

            "unique_users":
                unique_users,

            "passed_attempts":
                passed_attempts,

            "failed_attempts":
                failed_attempts,

            "pass_rate":
                pass_rate,

            "average_score":
                average_score,

            "average_attempts_per_user":
                average_attempts_per_user
        }

    overall_row = (
        db.query(
            func.count(
                AssessmentAttempt.id
            ).label(
                "total_attempts"
            ),

            func.sum(
                case(
                    (
                        AssessmentAttempt.passed.is_(
                            True
                        ),
                        1
                    ),
                    else_=0
                )
            ).label(
                "passed_attempts"
            ),

            func.avg(
                AssessmentAttempt.score
            ).label(
                "average_score"
            )
        )
        .join(
            User,
            User.id
            == AssessmentAttempt.user_id
        )
        .filter(
            User.is_admin.is_(
                False
            )
        )
        .first()
    )

    total_attempts = int(
        overall_row.total_attempts
        or 0
    )

    passed_attempts = int(
        overall_row.passed_attempts
        or 0
    )

    failed_attempts = max(
        0,
        total_attempts
        - passed_attempts
    )

    unique_users = int(
        (
            db.query(
                func.count(
                    func.distinct(
                        AssessmentAttempt.user_id
                    )
                )
            )
            .join(
                User,
                User.id
                == AssessmentAttempt.user_id
            )
            .filter(
                User.is_admin.is_(
                    False
                )
            )
            .scalar()
        )
        or 0
    )

    if total_attempts > 0:

        pass_rate = round(
            (
                passed_attempts
                / total_attempts
            )
            * 100,
            1
        )

    else:

        pass_rate = 0.0

    average_score = round(
        float(
            overall_row.average_score
            or 0
        ),
        1
    )

    if unique_users > 0:

        average_attempts_per_user = round(
            total_attempts
            / unique_users,
            2
        )

    else:

        average_attempts_per_user = 0.0

    lesson_stats = []

    for lesson in lessons:

        aggregate = (
            lesson_aggregates.get(
                lesson["id"]
            )
        )

        if aggregate is None:

            aggregate = {
                "total_attempts": 0,
                "unique_users": 0,
                "passed_attempts": 0,
                "failed_attempts": 0,
                "pass_rate": 0.0,
                "average_score": 0.0,
                "average_attempts_per_user": 0.0
            }

        lesson_stats.append(
            {
                "lesson_id":
                    lesson["id"],

                "day":
                    lesson["day"],

                "title":
                    lesson["title"],

                **aggregate
            }
        )

    return {
        "total_attempts":
            total_attempts,

        "unique_users":
            unique_users,

        "passed_attempts":
            passed_attempts,

        "failed_attempts":
            failed_attempts,

        "pass_rate":
            pass_rate,

        "average_score":
            average_score,

        "average_attempts_per_user":
            average_attempts_per_user,

        "lessons":
            lesson_stats
    }