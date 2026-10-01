from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.email_verification import (
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyEmailRequest,
    VerifyEmailResponse
)

from app.services.email_verification_service import (
    resend_verification_code,
    verify_email
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/verify-email",
    response_model=VerifyEmailResponse
)
def verify_user_email(
    data: VerifyEmailRequest,
    db: Session = Depends(
        get_db
    )
):
    return verify_email(
        db=db,
        email=str(
            data.email
        ),
        code=data.code
    )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse
)
def resend_user_verification(
    data: ResendVerificationRequest,
    db: Session = Depends(
        get_db
    )
):
    return resend_verification_code(
        db=db,
        email=str(
            data.email
        )
    )