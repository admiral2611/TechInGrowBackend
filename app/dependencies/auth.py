from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.database.database import get_db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if user is None:
            raise credentials_exception

    except (InvalidTokenError, ValueError):
        raise credentials_exception

    now_utc = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    activity_update_interval = timedelta(
        minutes=5
    )

    should_update_activity = (
        user.last_active_at is None
        or
        user.last_active_at
        < now_utc - activity_update_interval
    )

    if should_update_activity:
        user.last_active_at = now_utc

        db.add(user)
        db.commit()
        db.refresh(user)

    return user