from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False
    )

    lesson_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    correct_answers: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    passed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )