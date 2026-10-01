from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


class VerifyEmailRequest(BaseModel):

    email: EmailStr

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )


class VerifyEmailResponse(BaseModel):

    message: str


class ResendVerificationRequest(BaseModel):

    email: EmailStr


class ResendVerificationResponse(BaseModel):

    message: str