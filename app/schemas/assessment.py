from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AssessmentAnswer(BaseModel):
    question_id: int
    selected_answer: int = Field(ge=0)


class AssessmentSubmit(BaseModel):
    answers: list[AssessmentAnswer]


class AssessmentResult(BaseModel):
    lesson_id: int
    attempt_number: int

    total_questions: int
    correct_answers: int

    score: int
    passing_score: int

    passed: bool
    completed: bool


class AssessmentAttemptResponse(BaseModel):
    id: int
    lesson_id: int
    attempt_number: int

    score: int
    correct_answers: int
    total_questions: int

    passed: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class AssessmentSummary(BaseModel):
    lesson_id: int

    attempt_count: int
    last_score: int | None
    best_score: int | None

    passed: bool