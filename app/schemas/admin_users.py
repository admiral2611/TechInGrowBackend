from datetime import datetime

from pydantic import BaseModel


class AdminUserListItem(BaseModel):
    id: int

    username: str
    email: str

    is_email_verified: bool

    created_at: datetime
    last_active_at: datetime | None

    completed_lessons: int
    total_lessons: int

    progress_percent: float
    course_completed: bool


class AdminUsersPaginatedResponse(BaseModel):
    page: int
    page_size: int

    total: int
    total_pages: int

    users: list[AdminUserListItem]