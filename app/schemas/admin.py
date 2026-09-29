from datetime import datetime

from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    total_users: int
    active_today: int
    active_7_days: int
    active_30_days: int
    new_users_today: int
    new_users_7_days: int


class AdminUserItem(BaseModel):
    id: int
    username: str
    email: str

    created_at: datetime
    last_active_at: datetime | None

    completed_lessons: int
    total_lessons: int
    progress_percent: int

    course_completed: bool


class AdminUsersResponse(BaseModel):
    total: int
    users: list[AdminUserItem]


class AdminUserProgressItem(BaseModel):
    lesson_id: int
    day: int
    title: str

    completed: bool
    completed_at: datetime | None


class AdminUserAssessmentAttemptItem(BaseModel):
    id: int

    lesson_id: int
    day: int
    title: str

    attempt_number: int

    score: int
    correct_answers: int
    total_questions: int

    passed: bool

    created_at: datetime


class AdminUserAssessmentSummary(BaseModel):
    total_attempts: int

    passed_attempts: int
    failed_attempts: int

    average_score: float
    best_score: int


class AdminUserDetailResponse(BaseModel):
    id: int
    username: str
    email: str

    created_at: datetime
    last_active_at: datetime | None

    completed_lessons: int
    total_lessons: int

    progress_percent: int
    course_completed: bool

    progress: list[AdminUserProgressItem]

    assessment_summary: AdminUserAssessmentSummary

    recent_attempts: list[
        AdminUserAssessmentAttemptItem
    ]


class AdminCourseLessonStat(BaseModel):
    lesson_id: int
    day: int
    title: str

    completed_users: int
    completion_percent: float

    drop_from_previous: int


class AdminCourseDropStat(BaseModel):
    from_day: int
    to_day: int

    dropped_users: int
    drop_percent: float


class AdminCourseStatsResponse(BaseModel):
    total_users: int
    total_lessons: int

    started_users: int
    completed_course_users: int

    completion_rate: float

    average_completed_lessons: float
    average_progress_percent: float

    largest_drop: AdminCourseDropStat | None

    lessons: list[AdminCourseLessonStat]


class AdminAssessmentLessonStat(BaseModel):
    lesson_id: int
    day: int
    title: str

    total_attempts: int
    unique_users: int

    passed_attempts: int
    failed_attempts: int

    pass_rate: float
    average_score: float
    average_attempts_per_user: float


class AdminAssessmentStatsResponse(BaseModel):
    total_attempts: int
    unique_users: int

    passed_attempts: int
    failed_attempts: int

    pass_rate: float
    average_score: float
    average_attempts_per_user: float

    lessons: list[AdminAssessmentLessonStat]