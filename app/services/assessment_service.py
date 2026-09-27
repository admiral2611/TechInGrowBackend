from sqlalchemy.orm import Session

from app.models.assessment_attempt import AssessmentAttempt
from app.schemas.assessment import AssessmentSubmit
from app.services.lesson_service import get_lesson_data_by_id


def check_assessment(
    lesson_id: int,
    submission: AssessmentSubmit
) -> dict | None:

    lesson_data = get_lesson_data_by_id(
        lesson_id
    )

    if lesson_data is None:
        return None

    assessment = lesson_data.get(
        "assessment",
        {}
    )

    questions = assessment.get(
        "questions",
        []
    )

    passing_score = assessment.get(
        "passing_score",
        70
    )

    if not questions:
        return {
            "error": "no_questions"
        }

    question_ids = {
        question["id"]
        for question in questions
    }

    submitted_question_ids = [
        answer.question_id
        for answer in submission.answers
    ]

    if len(submitted_question_ids) != len(
        set(submitted_question_ids)
    ):
        return {
            "error": "duplicate_answers"
        }

    unknown_question_ids = (
        set(submitted_question_ids)
        - question_ids
    )

    if unknown_question_ids:
        return {
            "error": "invalid_question_id"
        }

    user_answers = {
        answer.question_id: answer.selected_answer
        for answer in submission.answers
    }

    correct_count = 0

    for question in questions:
        question_id = question["id"]
        correct_answer = question.get(
            "correct_answer"
        )

        user_answer = user_answers.get(
            question_id
        )

        if user_answer == correct_answer:
            correct_count += 1

    total_questions = len(questions)

    score = round(
        (correct_count / total_questions) * 100
    )

    passed = score >= passing_score

    return {
        "lesson_id": lesson_id,
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "score": score,
        "passing_score": passing_score,
        "passed": passed
    }


def save_assessment_attempt(
    db: Session,
    user_id: int,
    lesson_id: int,
    score: int,
    correct_answers: int,
    total_questions: int,
    passed: bool
) -> AssessmentAttempt:

    attempt_count = (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.lesson_id == lesson_id
        )
        .count()
    )

    attempt = AssessmentAttempt(
        user_id=user_id,
        lesson_id=lesson_id,
        attempt_number=attempt_count + 1,
        score=score,
        correct_answers=correct_answers,
        total_questions=total_questions,
        passed=passed
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


def get_assessment_attempts(
    db: Session,
    user_id: int,
    lesson_id: int
) -> list[AssessmentAttempt]:

    return (
        db.query(AssessmentAttempt)
        .filter(
            AssessmentAttempt.user_id == user_id,
            AssessmentAttempt.lesson_id == lesson_id
        )
        .order_by(
            AssessmentAttempt.attempt_number.asc()
        )
        .all()
    )


def get_assessment_summary(
    db: Session,
    user_id: int,
    lesson_id: int
) -> dict:

    attempts = get_assessment_attempts(
        db=db,
        user_id=user_id,
        lesson_id=lesson_id
    )

    if not attempts:
        return {
            "lesson_id": lesson_id,
            "attempt_count": 0,
            "last_score": None,
            "best_score": None,
            "passed": False
        }

    last_attempt = attempts[-1]

    best_score = max(
        attempt.score
        for attempt in attempts
    )

    passed = any(
        attempt.passed
        for attempt in attempts
    )

    return {
        "lesson_id": lesson_id,
        "attempt_count": len(attempts),
        "last_score": last_attempt.score,
        "best_score": best_score,
        "passed": passed
    }