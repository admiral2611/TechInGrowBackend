from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.progress import (
    ProgressResponse,
    ProgressSummary
)

from app.services.progress_service import (
    get_progress_summary,
    get_user_progress
)


router = APIRouter(
    prefix="/api/v1/progress",
    tags=["Progress"]
)


@router.get(
    "",
    response_model=list[ProgressResponse]
)
async def read_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return get_user_progress(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/summary",
    response_model=ProgressSummary
)
async def read_progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return get_progress_summary(
        db=db,
        user_id=current_user.id
    )