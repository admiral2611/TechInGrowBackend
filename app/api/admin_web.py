from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    tags=["Admin Web"]
)


ROOT_DIR = Path(
    __file__
).resolve().parents[2]

ADMIN_WEB_DIR = (
    ROOT_DIR
    / "admin_web"
)


@router.get(
    "/admin",
    include_in_schema=False
)
def admin_login_page():

    return FileResponse(
        ADMIN_WEB_DIR
        / "login.html"
    )


@router.get(
    "/admin/dashboard",
    include_in_schema=False
)
def admin_dashboard_page():

    return FileResponse(
        ADMIN_WEB_DIR
        / "dashboard.html"
    )


@router.get(
    "/admin/users",
    include_in_schema=False
)
def admin_users_page():

    return FileResponse(
        ADMIN_WEB_DIR
        / "users.html"
    )


@router.get(
    "/admin/users/{user_id}",
    include_in_schema=False
)
def admin_user_detail_page(
    user_id: int
):

    return FileResponse(
        ADMIN_WEB_DIR
        / "user_detail.html"
    )


@router.get(
    "/admin/course",
    include_in_schema=False
)
def admin_course_page():

    return FileResponse(
        ADMIN_WEB_DIR
        / "course.html"
    )


@router.get(
    "/admin/assessments",
    include_in_schema=False
)
def admin_assessments_page():

    return FileResponse(
        ADMIN_WEB_DIR
        / "assessments.html"
    )