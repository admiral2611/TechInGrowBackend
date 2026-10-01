from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password
)

from app.models.user import User

from app.schemas.user import (
    UserRegister
)

from app.services.email_verification_service import (
    create_and_send_verification_code
)


def get_user_by_username(
    db: Session,
    username: str
) -> User | None:

    normalized_username = (
        username
        .strip()
        .lower()
    )

    return (
        db.query(User)
        .filter(
            User.username
            == normalized_username
        )
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
) -> User | None:

    normalized_email = (
        email
        .strip()
        .lower()
    )

    return (
        db.query(User)
        .filter(
            User.email
            == normalized_email
        )
        .first()
    )


def create_user(
    db: Session,
    user_data: UserRegister
) -> User:

    user = User(
        username=(
            user_data.username
            .strip()
            .lower()
        ),

        email=(
            str(
                user_data.email
            )
            .strip()
            .lower()
        ),

        hashed_password=(
            hash_password(
                user_data.password
            )
        ),

        # SECURITY:
        # Har bir yangi account
        # email tasdiqlanmaguncha
        # verified bo'lmaydi.
        is_email_verified=False
    )

    db.add(
        user
    )

    db.commit()

    db.refresh(
        user
    )

    # Account yaratilgach verification
    # email avtomatik yuboriladi.
    #
    # Email yuborish muvaffaqiyatsiz bo'lsa
    # user DB'da qoladi va keyinchalik
    # resend-verification ishlata oladi.
    create_and_send_verification_code(
        db=db,
        user=user
    )

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

    password_is_valid = (
        verify_password(
            plain_password=password,
            hashed_password=
                user.hashed_password
        )
    )

    if not password_is_valid:
        return None

    return user