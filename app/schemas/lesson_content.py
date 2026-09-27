from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


class SectionContent(BaseModel):
    id: int = Field(gt=0)

    title: str = Field(
        min_length=1,
        max_length=150
    )

    content: str = Field(
        min_length=1
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class PracticeContent(BaseModel):
    id: int = Field(gt=0)

    question: str = Field(
        min_length=1
    )

    type: Literal[
        "text",
        "multiple_choice",
        "code"
    ]

    options: list[str] | None = None

    hints: list[str] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class ChallengeContent(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=150
    )

    description: str = Field(
        min_length=1
    )

    hints: list[str] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )


class AssessmentQuestionContent(BaseModel):
    id: int = Field(gt=0)

    question: str = Field(
        min_length=1
    )

    type: Literal[
        "multiple_choice"
    ]

    options: list[str] = Field(
        min_length=2
    )

    correct_answer: int = Field(
        ge=0
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    @model_validator(mode="after")
    def validate_correct_answer(
        self
    ):
        if self.correct_answer >= len(
            self.options
        ):
            raise ValueError(
                "correct_answer must be a valid "
                "option index"
            )

        return self


class AssessmentContent(BaseModel):
    passing_score: int = Field(
        ge=0,
        le=100
    )

    questions: list[
        AssessmentQuestionContent
    ]

    model_config = ConfigDict(
        extra="forbid"
    )

    @model_validator(mode="after")
    def validate_question_ids(
        self
    ):
        question_ids = [
            question.id
            for question in self.questions
        ]

        if len(question_ids) != len(
            set(question_ids)
        ):
            raise ValueError(
                "Assessment question IDs "
                "must be unique"
            )

        return self


class LessonContent(BaseModel):
    id: int = Field(gt=0)

    day: int = Field(gt=0)

    title: str = Field(
        min_length=1,
        max_length=150
    )

    description: str = Field(
        min_length=1
    )

    level: Literal[
        "beginner",
        "intermediate",
        "advanced"
    ]

    category: str = Field(
        min_length=1,
        max_length=100
    )

    duration_minutes: int = Field(
        ge=5,
        le=180
    )

    objectives: list[str]

    prerequisites: list[int]

    sections: list[
        SectionContent
    ]

    practice: list[
        PracticeContent
    ]

    challenge: ChallengeContent

    assessment: AssessmentContent

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    @model_validator(mode="after")
    def validate_lesson(
        self
    ):
        if self.id in self.prerequisites:
            raise ValueError(
                "Lesson cannot require itself"
            )

        if len(self.prerequisites) != len(
            set(self.prerequisites)
        ):
            raise ValueError(
                "Prerequisites must be unique"
            )

        section_ids = [
            section.id
            for section in self.sections
        ]

        if len(section_ids) != len(
            set(section_ids)
        ):
            raise ValueError(
                "Section IDs must be unique"
            )

        practice_ids = [
            practice.id
            for practice in self.practice
        ]

        if len(practice_ids) != len(
            set(practice_ids)
        ):
            raise ValueError(
                "Practice IDs must be unique"
            )

        return self