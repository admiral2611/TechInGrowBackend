from datetime import (
    datetime,
    timedelta,
    timezone
)

from secrets import token_urlsafe

from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    decode_token
)

from app.models.refresh_token import (
    RefreshToken
)


def utc_now_naive() -> datetime:

    return (
        datetime.now(
            timezone.utc
        )
        .replace(
            tzinfo=None
        )
    )


def create_token_pair(
    db: Session,
    user_id: int
) -> dict:

    jti = token_urlsafe(
        32
    )

    expires_at = (
        utc_now_naive()
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    refresh_record = RefreshToken(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at
    )

    db.add(
        refresh_record
    )

    db.commit()

    access_token = (
        create_access_token(
            user_id=user_id
        )
    )

    refresh_token = (
        create_refresh_token(
            user_id=user_id,
            jti=jti
        )
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": (
            ACCESS_TOKEN_EXPIRE_MINUTES
            * 60
        )
    }


def rotate_refresh_token(
    db: Session,
    token: str
) -> dict | None:

    try:
        payload = decode_token(
            token
        )

    except InvalidTokenError:
        return None

    if payload.get("type") != "refresh":
        return None

    user_id = payload.get(
        "sub"
    )

    jti = payload.get(
        "jti"
    )

    if (
        user_id is None
        or jti is None
    ):
        return None

    try:
        user_id = int(
            user_id
        )

    except ValueError:
        return None

    refresh_record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == user_id,

            RefreshToken.jti
            == jti
        )
        .first()
    )

    if refresh_record is None:
        return None

    if refresh_record.revoked_at is not None:
        return None

    if (
        refresh_record.expires_at
        <= utc_now_naive()
    ):
        return None

    refresh_record.revoked_at = (
        utc_now_naive()
    )

    db.commit()

    return create_token_pair(
        db=db,
        user_id=user_id
    )


def revoke_refresh_token(
    db: Session,
    token: str
) -> bool:

    try:
        payload = decode_token(
            token
        )

    except InvalidTokenError:
        return False

    if payload.get("type") != "refresh":
        return False

    user_id = payload.get(
        "sub"
    )

    jti = payload.get(
        "jti"
    )

    if (
        user_id is None
        or jti is None
    ):
        return False

    try:
        user_id = int(
            user_id
        )

    except ValueError:
        return False

    refresh_record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == user_id,

            RefreshToken.jti
            == jti
        )
        .first()
    )

    if refresh_record is None:
        return False

    if refresh_record.revoked_at is None:

        refresh_record.revoked_at = (
            utc_now_naive()
        )

        db.commit()

    return True


def revoke_all_refresh_tokens(
    db: Session,
    user_id: int
) -> None:

    tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == user_id,

            RefreshToken.revoked_at.is_(
                None
            )
        )
        .all()
    )

    now = utc_now_naive()

    for token in tokens:
        token.revoked_at = now

    db.commit()