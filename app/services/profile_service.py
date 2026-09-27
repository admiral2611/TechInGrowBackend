from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password
)

from app.models.user import User

from app.schemas.profile import (
    PasswordChange,
    ProfileUpdate
)

from app.services.progress_service import (
    get_progress_summary
)

from app.services.token_service import (
    revoke_all_refresh_tokens
)


def get_profile(
    db: Session,
    user: User
) -> dict:

    progress = get_progress_summary(
        db=db,
        user_id=user.id
    )

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "progress": progress
    }


def username_exists(
    db: Session,
    username: str,
    current_user_id: int
) -> bool:

    user = (
        db.query(User)
        .filter(
            User.username
            == username.lower(),

            User.id
            != current_user_id
        )
        .first()
    )

    return user is not None


def email_exists(
    db: Session,
    email: str,
    current_user_id: int
) -> bool:

    user = (
        db.query(User)
        .filter(
            User.email
            == email.lower(),

            User.id
            != current_user_id
        )
        .first()
    )

    return user is not None


def update_profile(
    db: Session,
    user: User,
    profile_data: ProfileUpdate
) -> User:

    if profile_data.username is not None:

        user.username = (
            profile_data.username
            .strip()
            .lower()
        )

    if profile_data.email is not None:

        user.email = (
            str(
                profile_data.email
            )
            .strip()
            .lower()
        )

    db.commit()
    db.refresh(user)

    return user


def change_password(
    db: Session,
    user: User,
    password_data: PasswordChange
) -> str:

    current_password_is_correct = (
        verify_password(
            plain_password=(
                password_data.current_password
            ),
            hashed_password=(
                user.hashed_password
            )
        )
    )

    if not current_password_is_correct:
        return "invalid_current_password"

    same_password = verify_password(
        plain_password=(
            password_data.new_password
        ),
        hashed_password=(
            user.hashed_password
        )
    )

    if same_password:
        return "same_password"

    user.hashed_password = (
        hash_password(
            password_data.new_password
        )
    )

    db.commit()
    db.refresh(user)

    revoke_all_refresh_tokens(
        db=db,
        user_id=user.id
    )

    return "success"