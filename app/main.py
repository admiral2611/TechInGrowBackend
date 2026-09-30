from pathlib import Path

from fastapi import (
    FastAPI,
    Request
)
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.admin_web import router as admin_web_router
from app.api.assessment import router as assessment_router
from app.api.auth import router as auth_router
from app.api.lessons import router as lessons_router
from app.api.password_reset import router as password_reset_router
from app.api.profile import router as profile_router
from app.api.progress import router as progress_router
from app.core.lesson_errors import LessonContentError


ROOT_DIR = Path(
    __file__
).resolve().parents[1]

ADMIN_STATIC_DIR = (
    ROOT_DIR
    / "admin_web"
    / "static"
)


app = FastAPI(
    title="TechInGrow API",
    description=
        "TechInGrow learning platform backend API",
    version="1.0.0"
)


app.mount(
    "/admin/static",
    StaticFiles(
        directory=
            ADMIN_STATIC_DIR
    ),
    name="admin-static"
)


@app.exception_handler(
    LessonContentError
)
async def lesson_content_error_handler(
    request: Request,
    exc: LessonContentError
):
    return JSONResponse(
        status_code=500,
        content={
            "detail":
                "Lesson content is invalid",

            "file":
                exc.file_name,

            "error":
                exc.message
        }
    )


app.include_router(
    auth_router
)

app.include_router(
    password_reset_router
)

app.include_router(
    profile_router
)

app.include_router(
    lessons_router
)

app.include_router(
    progress_router
)

app.include_router(
    assessment_router
)

app.include_router(
    admin_router
)

app.include_router(
    admin_web_router
)