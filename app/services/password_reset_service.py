import logging
import secrets

from datetime import (
    datetime,
    timedelta,
    timezone
)

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password
)

from app.models.password_reset_code import (
    PasswordResetCode
)

from app.models.refresh_token import (
    RefreshToken
)

from app.models.user import User

from app.services.email_service import (
    send_password_reset_email
)


logger = logging.getLogger(
    __name__
)


RESET_CODE_EXPIRE_MINUTES = 10

MAX_RESET_ATTEMPTS = 5

RESET_REQUEST_COOLDOWN_SECONDS = 60

MAX_RESET_REQUESTS_PER_HOUR = 5


def _now_utc() -> datetime:

    return datetime.now(
        timezone.utc
    ).replace(
        tzinfo=None
    )


def _generate_reset_code() -> str:

    return str(
        secrets.randbelow(
            900000
        )
        + 100000
    )


def request_password_reset(
    db: Session,
    email: str
) -> dict:

    normalized_email = (
        email
        .strip()
        .lower()
    )

    generic_response = {
        "message":
            "Agar bu email bilan account mavjud bo'lsa, password reset kodi yuboriladi."
    }

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

    # User mavjudligini API orqali
    # oshkor qilmaymiz.
    if user is None:
        return generic_response

    now = _now_utc()

    latest_request = (
        db.query(
            PasswordResetCode
        )
        .filter(
            PasswordResetCode.user_id
            == user.id
        )
        .order_by(
            PasswordResetCode
            .created_at
            .desc()
        )
        .first()
    )

    # 60 sekund ichida qayta email
    # yuborilishining oldini olamiz.
    if latest_request:

        created_at = (
            latest_request.created_at
        )

        if created_at:

            cooldown_until = (
                created_at
                + timedelta(
                    seconds=
                        RESET_REQUEST_COOLDOWN_SECONDS
                )
            )

            if now < cooldown_until:
                return generic_response

    one_hour_ago = (
        now
        - timedelta(
            hours=1
        )
    )

    requests_last_hour = (
        db.query(
            PasswordResetCode
        )
        .filter(
            PasswordResetCode.user_id
            == user.id,
            PasswordResetCode.created_at
            >= one_hour_ago
        )
        .count()
    )

    # Bir userga bir soatda maksimal
    # 5 ta reset email.
    if (
        requests_last_hour
        >= MAX_RESET_REQUESTS_PER_HOUR
    ):
        return generic_response

    # Eski ishlatilmagan reset kodlarini
    # bekor qilamiz.
    (
        db.query(
            PasswordResetCode
        )
        .filter(
            PasswordResetCode.user_id
            == user.id,
            PasswordResetCode.used.is_(
                False
            )
        )
        .update(
            {
                PasswordResetCode.used:
                    True
            },
            synchronize_session=False
        )
    )

    reset_code = (
        _generate_reset_code()
    )

    code_hash = (
        hash_password(
            reset_code
        )
    )

    expires_at = (
        now
        + timedelta(
            minutes=
                RESET_CODE_EXPIRE_MINUTES
        )
    )

    reset_record = (
        PasswordResetCode(
            user_id=user.id,
            code_hash=code_hash,
            expires_at=expires_at,
            used=False,
            attempts=0
        )
    )

    db.add(
        reset_record
    )

    db.commit()

    db.refresh(
        reset_record
    )

    try:

        send_password_reset_email(
            to_email=user.email,
            reset_code=reset_code,
            expires_minutes=
                RESET_CODE_EXPIRE_MINUTES
        )

        logger.info(
            "Password reset email sent "
            "for user_id=%s",
            user.id
        )

    except Exception:

        logger.exception(
            "Password reset email "
            "could not be sent "
            "for user_id=%s",
            user.id
        )

        # Email yuborilmagan kod
        # ishlatilmasligi kerak.
        reset_record.used = True

        db.add(
            reset_record
        )

        db.commit()

    return generic_response


def reset_password(
    db: Session,
    email: str,
    code: str,
    new_password: str
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

    if user is None:

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Reset code noto'g'ri yoki muddati tugagan"
        )

    reset_record = (
        db.query(
            PasswordResetCode
        )
        .filter(
            PasswordResetCode.user_id
            == user.id,
            PasswordResetCode.used.is_(
                False
            )
        )
        .order_by(
            PasswordResetCode
            .created_at
            .desc()
        )
        .first()
    )

    if reset_record is None:

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Reset code noto'g'ri yoki muddati tugagan"
        )

    now = _now_utc()

    if (
        reset_record.expires_at
        <= now
    ):

        reset_record.used = True

        db.commit()

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Reset code noto'g'ri yoki muddati tugagan"
        )

    if (
        reset_record.attempts
        >= MAX_RESET_ATTEMPTS
    ):

        reset_record.used = True

        db.commit()

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Reset code noto'g'ri yoki muddati tugagan"
        )

    code_is_valid = (
        verify_password(
            code,
            reset_record.code_hash
        )
    )

    if not code_is_valid:

        reset_record.attempts += 1

        if (
            reset_record.attempts
            >= MAX_RESET_ATTEMPTS
        ):
            reset_record.used = True

        db.commit()

        raise HTTPException(
            status_code=
                status.HTTP_400_BAD_REQUEST,
            detail=
                "Reset code noto'g'ri yoki muddati tugagan"
        )

    user.hashed_password = (
        hash_password(
            new_password
        )
    )

    reset_record.used = True

    # Boshqa reset kodlarini ham
    # bekor qilamiz.
    (
        db.query(
            PasswordResetCode
        )
        .filter(
            PasswordResetCode.user_id
            == user.id,
            PasswordResetCode.id
            != reset_record.id,
            PasswordResetCode.used.is_(
                False
            )
        )
        .update(
            {
                PasswordResetCode.used:
                    True
            },
            synchronize_session=False
        )
    )

    # Userning oldingi login
    # sessionlarini bekor qilamiz.
    (
        db.query(
            RefreshToken
        )
        .filter(
            RefreshToken.user_id
            == user.id
        )
        .delete(
            synchronize_session=False
        )
    )

    db.add(
        user
    )

    db.add(
        reset_record
    )

    db.commit()

    return {
        "message":
            "Password muvaffaqiyatli yangilandi"
    }