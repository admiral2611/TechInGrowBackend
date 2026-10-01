import math

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.assessment_attempt import (
    AssessmentAttempt
)

from app.models.email_verification_code import (
    EmailVerificationCode
)

from app.models.password_reset_code import (
    PasswordResetCode
)

from app.models.progress import (
    UserProgress
)

from app.models.refresh_token import (
    RefreshToken
)

from app.models.user import User


def get_paginated_admin_accounts(
    db: Session,
    current_admin_id: int,
    page: int,
    page_size: int,
    search: str | None = None
) -> dict:

    query = (
        db.query(User)
        .filter(
            User.is_admin.is_(
                True
            )
        )
    )

    if search:

        clean_search = (
            search
            .strip()
        )

        if clean_search:

            pattern = (
                f"%{clean_search}%"
            )

            query = (
                query.filter(
                    or_(
                        User.username.ilike(
                            pattern
                        ),
                        User.email.ilike(
                            pattern
                        )
                    )
                )
            )

    total = query.count()

    total_pages = (
        math.ceil(
            total / page_size
        )
        if total > 0
        else 0
    )

    offset = (
        page - 1
    ) * page_size

    admins = (
        query
        .order_by(
            User.created_at.desc()
        )
        .offset(
            offset
        )
        .limit(
            page_size
        )
        .all()
    )

    items = []

    for admin in admins:

        items.append(
            {
                "id":
                    admin.id,

                "username":
                    admin.username,

                "email":
                    admin.email,

                "is_email_verified":
                    admin.is_email_verified,

                "is_current_admin":
                    admin.id
                    == current_admin_id,

                "created_at":
                    admin.created_at,

                "last_active_at":
                    admin.last_active_at
            }
        )

    return {
        "page":
            page,

        "page_size":
            page_size,

        "total":
            total,

        "total_pages":
            total_pages,

        "admins":
            items
    }


def get_admin_account_detail(
    db: Session,
    admin_id: int,
    current_admin_id: int
) -> dict:

    admin = (
        db.query(User)
        .filter(
            User.id == admin_id,
            User.is_admin.is_(
                True
            )
        )
        .first()
    )

    if admin is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Admin not found"
        )

    return {
        "id":
            admin.id,

        "username":
            admin.username,

        "email":
            admin.email,

        "is_admin":
            admin.is_admin,

        "is_email_verified":
            admin.is_email_verified,

        "is_current_admin":
            admin.id
            == current_admin_id,

        "created_at":
            admin.created_at,

        "last_active_at":
            admin.last_active_at
    }


def delete_admin_account(
    db: Session,
    admin_id: int,
    current_admin_id: int
) -> dict:

    admin = (
        db.query(User)
        .filter(
            User.id == admin_id,
            User.is_admin.is_(
                True
            )
        )
        .first()
    )

    if admin is None:

        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,

            detail=
                "Admin not found"
        )

    # SECURITY:
    # Admin o'z accountini admin paneldan
    # o'chira olmaydi.
    if admin.id == current_admin_id:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,

            detail=
                "You cannot delete your own admin account"
        )

    admin_count = (
        db.query(User)
        .filter(
            User.is_admin.is_(
                True
            )
        )
        .count()
    )

    # SECURITY:
    # Sistemada kamida bitta admin
    # doim qolishi kerak.
    if admin_count <= 1:

        raise HTTPException(
            status_code=
                status.HTTP_409_CONFLICT,

            detail=
                "The last admin account cannot be deleted"
        )

    username = admin.username

    try:

        (
            db.query(
                RefreshToken
            )
            .filter(
                RefreshToken.user_id
                == admin.id
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(
                PasswordResetCode
            )
            .filter(
                PasswordResetCode.user_id
                == admin.id
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(
                EmailVerificationCode
            )
            .filter(
                EmailVerificationCode.user_id
                == admin.id
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(
                AssessmentAttempt
            )
            .filter(
                AssessmentAttempt.user_id
                == admin.id
            )
            .delete(
                synchronize_session=False
            )
        )

        (
            db.query(
                UserProgress
            )
            .filter(
                UserProgress.user_id
                == admin.id
            )
            .delete(
                synchronize_session=False
            )
        )

        db.delete(
            admin
        )

        db.commit()

    except Exception:

        db.rollback()

        raise

    return {
        "message":
            "Admin deleted successfully",

        "admin_id":
            admin_id,

        "username":
            username
    }