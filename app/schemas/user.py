from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)

from app.core.password_policy import (
    validate_password_strength
)


class UserRegister(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str
    ) -> str:

        return validate_password_strength(
            value
        )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )