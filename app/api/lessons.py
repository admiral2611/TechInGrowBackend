from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.lesson import (
    Lesson,
    LessonSummary
)

from app.services.lesson_service import (
    get_all_lessons,
    get_lesson
)

from app.services.progress_service import (
    can_access_lesson
)


router = APIRouter(
    prefix="/api/v1/lessons",
    tags=["Lessons"]
)


@router.get(
    "",
    response_model=list[LessonSummary]
)
async def read_lessons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_all_lessons(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/{day}",
    response_model=Lesson
)
async def read_lesson(
    day: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    lesson = get_lesson(
        day
    )

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    if not can_access_lesson(
        db=db,
        user_id=current_user.id,
        lesson_id=lesson.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Lesson is locked"
        )

    return lesson