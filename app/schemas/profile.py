from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)

from app.core.password_policy import (
    validate_password_strength
)

from app.schemas.progress import (
    ProgressSummary
)


class ProfileUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50
    )

    email: EmailStr | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(
        cls,
        value: str
    ) -> str:

        return validate_password_strength(
            value
        )


class PasswordChangeResponse(BaseModel):
    message: str


class ProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    progress: ProgressSummary