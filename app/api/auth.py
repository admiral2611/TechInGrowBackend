from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from app.database.database import (
    get_db
)

from app.dependencies.auth import (
    get_current_user
)

from app.models.user import User

from app.schemas.auth import (
    LogoutRequest,
    LogoutResponse,
    RefreshTokenRequest,
    TokenResponse
)

from app.schemas.user import (
    UserRegister,
    UserResponse
)

from app.services.auth_service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_username
)

from app.services.token_service import (
    create_token_pair,
    revoke_refresh_token,
    rotate_refresh_token
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(
        get_db
    )
):

    existing_username = (
        get_user_by_username(
            db=db,
            username=user_data.username
        )
    )

    if existing_username is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    existing_email = (
        get_user_by_email(
            db=db,
            email=user_data.email
        )
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    return create_user(
        db=db,
        user_data=user_data
    )


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(
        get_db
    )
):

    user = authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Incorrect username or password"
            ),
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    token_pair = create_token_pair(
        db=db,
        user_id=user.id
    )

    return TokenResponse(
        **token_pair
    )


@router.post(
    "/refresh",
    response_model=TokenResponse
)
async def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(
        get_db
    )
):

    token_pair = rotate_refresh_token(
        db=db,
        token=request.refresh_token
    )

    if token_pair is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid or expired refresh token"
            )
        )

    return TokenResponse(
        **token_pair
    )


@router.post(
    "/logout",
    response_model=LogoutResponse
)
async def logout(
    request: LogoutRequest,
    db: Session = Depends(
        get_db
    )
):

    revoked = revoke_refresh_token(
        db=db,
        token=request.refresh_token
    )

    if not revoked:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid refresh token"
            )
        )

    return LogoutResponse(
        message="Logged out successfully"
    )


@router.get(
    "/me",
    response_model=UserResponse
)
async def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user