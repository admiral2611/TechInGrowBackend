from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProgressResponse(BaseModel):
    lesson_id: int
    completed: bool
    completed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )


class ProgressSummary(BaseModel):
    total_lessons: int
    completed_lessons: int

    progress_percent: int

    current_day: int | None
    current_lesson_id: int | None
    current_lesson_title: str | None

    total_attempts: int
    best_score: int | None

    last_completed_day: int | None
    last_completed_at: datetime | None

    course_completed: bool