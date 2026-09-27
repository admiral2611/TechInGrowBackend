from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

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

    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )