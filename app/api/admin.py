from fastapi import (
    APIRouter,
    Depends,
    Query
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.admin import get_current_admin
from app.models.user import User
from app.schemas.admin import (
    AdminAssessmentStatsResponse,
    AdminCourseStatsResponse,
    AdminDashboardResponse,
    AdminUserDetailResponse
)
from app.schemas.admin_users import (
    AdminUsersPaginatedResponse
)
from app.services.admin_service import (
    get_assessment_stats,
    get_course_stats,
    get_dashboard_stats
)
from app.services.admin_user_service import (
    delete_user_by_admin,
    get_user_detail_by_admin
)
from app.services.admin_users_service import (
    get_paginated_admin_users
)


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse
)
def get_admin_dashboard(
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    )
):
    return get_dashboard_stats(
        db
    )


@router.get(
    "/users",
    response_model=AdminUsersPaginatedResponse
)
def get_users(
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=20,
        ge=5,
        le=100
    ),
    search: str | None = Query(
        default=None,
        max_length=100
    ),
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    )
):
    return get_paginated_admin_users(
        db=db,
        page=page,
        page_size=page_size,
        search=search
    )


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetailResponse
)
def get_user_detail(
    user_id: int,
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    )
):
    return get_user_detail_by_admin(
        db=db,
        user_id=user_id
    )


@router.delete(
    "/users/{user_id}"
)
def delete_user(
    user_id: int,
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    )
):
    return delete_user_by_admin(
        db=db,
        user_id=user_id
    )


@router.get(
    "/course/stats",
    response_model=AdminCourseStatsResponse
)
def get_course_statistics(
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    )
):
    return get_course_stats(
        db
    )


@router.get(
    "/assessments/stats",
    response_model=AdminAssessmentStatsResponse
)
def get_assessment_statistics(
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    )
):
    return get_assessment_stats(
        db
    )