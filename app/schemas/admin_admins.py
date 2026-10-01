from datetime import datetime

from pydantic import BaseModel


class AdminAccountListItem(BaseModel):
    id: int
    username: str
    email: str

    is_email_verified: bool
    is_current_admin: bool

    created_at: datetime
    last_active_at: datetime | None


class AdminAccountsPaginatedResponse(BaseModel):
    page: int
    page_size: int

    total: int
    total_pages: int

    admins: list[AdminAccountListItem]


class AdminAccountDetailResponse(BaseModel):
    id: int
    username: str
    email: str

    is_admin: bool
    is_email_verified: bool
    is_current_admin: bool

    created_at: datetime
    last_active_at: datetime | None


class DeleteAdminResponse(BaseModel):
    message: str

    admin_id: int
    username: str
