from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.password_policy import validate_password_strength


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )

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


class ResetPasswordResponse(BaseModel):
    message: str