from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    tags=["Admin Web"]
)


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

ADMIN_WEB_DIR = (
    ROOT_DIR
    / "admin_web"
)


def admin_file(
    file_name: str
) -> FileResponse:

    return FileResponse(
        ADMIN_WEB_DIR
        / file_name
    )


@router.get(
    "/admin",
    include_in_schema=False
)
def admin_login_page():

    return admin_file(
        "login.html"
    )


@router.get(
    "/admin/dashboard",
    include_in_schema=False
)
def admin_dashboard_page():

    return admin_file(
        "dashboard.html"
    )


@router.get(
    "/admin/users",
    include_in_schema=False
)
def admin_users_page():

    return admin_file(
        "users.html"
    )


@router.get(
    "/admin/users/{user_id}",
    include_in_schema=False
)
def admin_user_detail_page(
    user_id: int
):

    return admin_file(
        "user_detail.html"
    )


@router.get(
    "/admin/admins",
    include_in_schema=False
)
def admin_accounts_page():

    return admin_file(
        "admins.html"
    )


@router.get(
    "/admin/course",
    include_in_schema=False
)
def admin_course_page():

    return admin_file(
        "course.html"
    )


@router.get(
    "/admin/assessments",
    include_in_schema=False
)
def admin_assessments_page():

    return admin_file(
        "assessments.html"
    )