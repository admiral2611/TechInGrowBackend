import logging
import secrets

from datetime import (
    datetime,
    timedelta
)

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.email_verification_code import (
    EmailVerificationCode
)
from app.models.user import User

from app.services.auth_service import (
    hash_password,
    verify_password
)

from app.services.email_service import (
    send_email_verification_email
)


logger = logging.getLogger(
    __name__
)


VERIFICATION_CODE_EXPIRE_MINUTES = 10

MAX_VERIFICATION_ATTEMPTS = 5

RESEND_COOLDOWN_SECONDS = 60

MAX_VERIFICATION_REQUESTS_PER_HOUR = 5


GENERIC_RESEND_MESSAGE = (
    "Agar email mavjud bo'lsa, "
    "tasdiqlash kodi yuborildi"
)


INVALID_CODE_MESSAGE = (
    "Tasdiqlash kodi noto'g'ri "
    "yoki muddati tugagan"
)


def _now_utc() -> datetime:

    return datetime.utcnow()


def _generate_verification_code() -> str:

    number = (
        secrets.randbelow(
            900000
        )
        + 100000
    )

    return str(
        number
    )


def _invalidate_existing_codes(
    db: Session,
    user_id: int
) -> None:

    (
        db.query(
            EmailVerificationCode
        )
        .filter(
            EmailVerificationCode.user_id
            == user_id,

            EmailVerificationCode.used.is_(
                False
            )
        )
        .update(
            {
                EmailVerificationCode.used:
                    True
            },

            synchronize_session=False
        )
    )


def _get_latest_unused_code(
    db: Session,
    user_id: int
) -> EmailVerificationCode | None:

    return (
        db.query(
            EmailVerificationCode
        )
        .filter(
            EmailVerificationCode.user_id
            == user_id,

            EmailVerificationCode.used.is_(
                False
            )
        )
        .order_by(
            EmailVerificationCode.created_at.desc(),
            EmailVerificationCode.id.desc()
        )
        .first()
    )


def _verification_requests_last_hour(
    db: Session,
    user_id: int
) -> int:

    one_hour_ago = (
        _now_utc()
        - timedelta(
            hours=1
        )
    )


    return (
        db.query(
            EmailVerificationCode
        )
        .filter(
            EmailVerificationCode.user_id
            == user_id,

            EmailVerificationCode.created_at
            >= one_hour_ago
        )
        .count()
    )


def create_and_send_verification_code(
    db: Session,
    user: User
) -> bool:

    if user.is_email_verified:

        return True


    code = (
        _generate_verification_code()
    )


    expires_at = (
        _now_utc()
        + timedelta(
            minutes=
                VERIFICATION_CODE_EXPIRE_MINUTES
        )
    )


    _invalidate_existing_codes(
        db=db,
        user_id=user.id
    )


    verification_record = (
        EmailVerificationCode(
            user_id=user.id,

            code_hash=hash_password(
                code
            ),

            expires_at=expires_at,

            used=False,

            attempts=0
        )
    )


    db.add(
        verification_record
    )


    db.commit()


    try:

        send_email_verification_email(
            to_email=user.email,
            code=code,
            expire_minutes=(
                VERIFICATION_CODE_EXPIRE_MINUTES
            )
        )


        return True


    except Exception:

        logger.exception(
            "Email verification email "
            "could not be sent for user_id=%s",
            user.id
        )


        verification_record.used = True


        db.commit()


        return False


def resend_verification_code(
    db: Session,
    email: str
) -> dict:

    normalized_email = (
        email
        .strip()
        .lower()
    )


    user = (
        db.query(
            User
        )
        .filter(
            User.email
            == normalized_email
        )
        .first()
    )


    if not user:

        return {
            "message":
                GENERIC_RESEND_MESSAGE
        }


    if user.is_email_verified:

        return {
            "message":
                GENERIC_RESEND_MESSAGE
        }


    latest_code = (
        db.query(
            EmailVerificationCode
        )
        .filter(
            EmailVerificationCode.user_id
            == user.id
        )
        .order_by(
            EmailVerificationCode.created_at.desc(),
            EmailVerificationCode.id.desc()
        )
        .first()
    )


    if latest_code:

        cooldown_limit = (
            latest_code.created_at
            + timedelta(
                seconds=
                    RESEND_COOLDOWN_SECONDS
            )
        )


        if (
            _now_utc()
            < cooldown_limit
        ):

            return {
                "message":
                    GENERIC_RESEND_MESSAGE
            }


    request_count = (
        _verification_requests_last_hour(
            db=db,
            user_id=user.id
        )
    )


    if (
        request_count
        >= MAX_VERIFICATION_REQUESTS_PER_HOUR
    ):

        return {
            "message":
                GENERIC_RESEND_MESSAGE
        }


    create_and_send_verification_code(
        db=db,
        user=user
    )


    return {
        "message":
            GENERIC_RESEND_MESSAGE
    }


def verify_email(
    db: Session,
    email: str,
    code: str
) -> dict:

    normalized_email = (
        email
        .strip()
        .lower()
    )


    user = (
        db.query(
            User
        )
        .filter(
            User.email
            == normalized_email
        )
        .first()
    )


    if not user:

        raise HTTPException(
            status_code=400,
            detail=INVALID_CODE_MESSAGE
        )


    if user.is_email_verified:

        return {
            "message":
                "Email muvaffaqiyatli "
                "tasdiqlandi"
        }


    verification_record = (
        _get_latest_unused_code(
            db=db,
            user_id=user.id
        )
    )


    if not verification_record:

        raise HTTPException(
            status_code=400,
            detail=INVALID_CODE_MESSAGE
        )


    if (
        verification_record.expires_at
        < _now_utc()
    ):

        verification_record.used = True

        db.commit()


        raise HTTPException(
            status_code=400,
            detail=INVALID_CODE_MESSAGE
        )


    if (
        verification_record.attempts
        >= MAX_VERIFICATION_ATTEMPTS
    ):

        verification_record.used = True

        db.commit()


        raise HTTPException(
            status_code=400,
            detail=INVALID_CODE_MESSAGE
        )


    if not verify_password(
        code,
        verification_record.code_hash
    ):

        verification_record.attempts += 1


        if (
            verification_record.attempts
            >= MAX_VERIFICATION_ATTEMPTS
        ):

            verification_record.used = True


        db.commit()


        raise HTTPException(
            status_code=400,
            detail=INVALID_CODE_MESSAGE
        )


    user.is_email_verified = True

    verification_record.used = True


    _invalidate_existing_codes(
        db=db,
        user_id=user.id
    )


    db.commit()


    return {
        "message":
            "Email muvaffaqiyatli "
            "tasdiqlandi"
    }