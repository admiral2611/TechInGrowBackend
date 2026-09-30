from fastapi import (
    APIRouter,
    Depends
)
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse
)
from app.services.password_reset_service import (
    request_password_reset,
    reset_password
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(
        get_db
    )
):
    return request_password_reset(
        db=db,
        email=str(
            data.email
        )
    )


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse
)
def change_forgotten_password(
    data: ResetPasswordRequest,
    db: Session = Depends(
        get_db
    )
):
    return reset_password(
        db=db,
        email=str(
            data.email
        ),
        code=data.code,
        new_password=
            data.new_password
    )