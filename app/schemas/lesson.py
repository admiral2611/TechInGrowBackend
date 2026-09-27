from typing import Literal

from pydantic import (
    BaseModel,
    Field
)


class Section(BaseModel):
    id: int
    title: str
    content: str


class Practice(BaseModel):
    id: int

    question: str

    type: Literal[
        "text",
        "multiple_choice",
        "code"
    ]

    options: list[str] | None = None

    hints: list[str] = Field(
        default_factory=list
    )


class Challenge(BaseModel):
    title: str
    description: str

    hints: list[str] = Field(
        default_factory=list
    )


class AssessmentQuestion(BaseModel):
    id: int
    question: str

    type: Literal[
        "multiple_choice"
    ]

    options: list[str]


class Assessment(BaseModel):
    passing_score: int

    questions: list[
        AssessmentQuestion
    ]


class LessonSummary(BaseModel):
    id: int
    day: int

    title: str
    description: str

    level: str
    category: str

    duration_minutes: int

    completed: bool = False
    locked: bool = False


class Lesson(BaseModel):
    id: int
    day: int

    title: str
    description: str

    level: str
    category: str

    duration_minutes: int

    objectives: list[str]

    prerequisites: list[int]

    sections: list[
        Section
    ]

    practice: list[
        Practice
    ]

    challenge: Challenge

    assessment: Assessment