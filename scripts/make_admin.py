import sys

from app.database.database import SessionLocal
from app.models.user import User


def make_admin(
    username: str
) -> None:

    username = username.strip().lower()

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == username)
            .first()
        )

        if user is None:
            print(
                f"User topilmadi: {username}"
            )
            return

        if user.is_admin:
            print(
                f"{username} allaqachon admin."
            )
            return

        user.is_admin = True

        db.add(user)
        db.commit()
        db.refresh(user)

        print(
            f"{username} admin qilindi."
        )

    finally:
        db.close()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Usage:"
        )
        print(
            "python -m scripts.make_admin <username>"
        )
        sys.exit(1)

    make_admin(
        sys.argv[1]
    )