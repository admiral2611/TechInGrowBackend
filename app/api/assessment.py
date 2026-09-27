from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.assessment import (
    AssessmentAttemptResponse,
    AssessmentResult,
    AssessmentSubmit,
    AssessmentSummary
)

from app.services.assessment_service import (
    check_assessment,
    get_assessment_attempts,
    get_assessment_summary,
    save_assessment_attempt
)

from app.services.lesson_service import (
    get_lesson_by_id
)

from app.services.progress_service import (
    can_access_lesson,
    complete_lesson
)


router = APIRouter(
    prefix="/api/v1/assessments",
    tags=["Assessments"]
)


@router.post(
    "/{lesson_id}/submit",
    response_model=AssessmentResult
)
async def submit_assessment(
    lesson_id: int,
    submission: AssessmentSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    lesson = get_lesson_by_id(
        lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    if not can_access_lesson(
        db=db,
        user_id=current_user.id,
        lesson_id=lesson_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Lesson is locked"
        )

    result = check_assessment(
        lesson_id=lesson_id,
        submission=submission
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    error = result.get(
        "error"
    )

    if error == "no_questions":
        raise HTTPException(
            status_code=400,
            detail="Assessment has no questions"
        )

    if error == "duplicate_answers":
        raise HTTPException(
            status_code=400,
            detail="Duplicate answers are not allowed"
        )

    if error == "invalid_question_id":
        raise HTTPException(
            status_code=400,
            detail="Invalid question id"
        )

    attempt = save_assessment_attempt(
        db=db,
        user_id=current_user.id,
        lesson_id=lesson_id,
        score=result["score"],
        correct_answers=result["correct_answers"],
        total_questions=result["total_questions"],
        passed=result["passed"]
    )

    completed = False

    if result["passed"]:
        complete_lesson(
            db=db,
            user_id=current_user.id,
            lesson_id=lesson_id
        )

        completed = True

    return AssessmentResult(
        lesson_id=lesson_id,
        attempt_number=attempt.attempt_number,
        total_questions=result["total_questions"],
        correct_answers=result["correct_answers"],
        score=result["score"],
        passing_score=result["passing_score"],
        passed=result["passed"],
        completed=completed
    )


@router.get(
    "/{lesson_id}/attempts",
    response_model=list[AssessmentAttemptResponse]
)
async def read_assessment_attempts(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    lesson = get_lesson_by_id(
        lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    return get_assessment_attempts(
        db=db,
        user_id=current_user.id,
        lesson_id=lesson_id
    )


@router.get(
    "/{lesson_id}/summary",
    response_model=AssessmentSummary
)
async def read_assessment_summary(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    lesson = get_lesson_by_id(
        lesson_id
    )

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    return get_assessment_summary(
        db=db,
        user_id=current_user.id,
        lesson_id=lesson_id
    )