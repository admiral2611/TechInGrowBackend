from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.profile import (
    PasswordChange,
    PasswordChangeResponse,
    ProfileResponse,
    ProfileUpdate
)

from app.services.profile_service import (
    change_password,
    email_exists,
    get_profile,
    update_profile,
    username_exists
)


router = APIRouter(
    prefix="/api/v1/profile",
    tags=["Profile"]
)


@router.get(
    "",
    response_model=ProfileResponse
)
async def read_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return get_profile(
        db=db,
        user=current_user
    )


@router.patch(
    "",
    response_model=ProfileResponse
)
async def edit_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    if (
        profile_data.username is None
        and profile_data.email is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile fields provided"
        )

    if profile_data.username is not None:

        username = (
            profile_data.username
            .strip()
            .lower()
        )

        if username_exists(
            db=db,
            username=username,
            current_user_id=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

    if profile_data.email is not None:

        email = (
            str(profile_data.email)
            .strip()
            .lower()
        )

        if email_exists(
            db=db,
            email=email,
            current_user_id=current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

    update_profile(
        db=db,
        user=current_user,
        profile_data=profile_data
    )

    return get_profile(
        db=db,
        user=current_user
    )


@router.patch(
    "/password",
    response_model=PasswordChangeResponse
)
async def update_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    result = change_password(
        db=db,
        user=current_user,
        password_data=password_data
    )

    if result == "invalid_current_password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    if result == "same_password":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    return PasswordChangeResponse(
        message="Password changed successfully"
    )