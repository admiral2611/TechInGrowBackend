from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password
)

from app.models.user import User

from app.schemas.user import (
    UserRegister
)


def get_user_by_username(
    db: Session,
    username: str
) -> User | None:

    return (
        db.query(User)
        .filter(
            User.username == username.lower()
        )
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
) -> User | None:

    return (
        db.query(User)
        .filter(
            User.email == email.lower()
        )
        .first()
    )


def create_user(
    db: Session,
    user_data: UserRegister
) -> User:

    user = User(
        username=user_data.username.lower(),
        email=user_data.email.lower(),
        hashed_password=hash_password(
            user_data.password
        )
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> User | None:

    user = get_user_by_username(
        db=db,
        username=username
    )

    if user is None:
        return None

    if not verify_password(
        plain_password=password,
        hashed_password=user.hashed_password
    ):
        return None

    return user