import os

from datetime import (
    datetime,
    timedelta,
    timezone
)

from pathlib import Path

import jwt

from dotenv import load_dotenv
from pwdlib import PasswordHash


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

ENV_FILE = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_FILE
)


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30


if not JWT_SECRET_KEY:
    raise RuntimeError(
        f"JWT_SECRET_KEY is not configured. "
        f"Expected .env file: {ENV_FILE}"
    )


password_hash = PasswordHash.recommended()


def hash_password(
    password: str
) -> str:

    return password_hash.hash(
        password
    )


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    user_id: int
) -> str:

    now = datetime.now(
        timezone.utc
    )

    expire = (
        now
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def create_refresh_token(
    user_id: int,
    jti: str
) -> str:

    now = datetime.now(
        timezone.utc
    )

    expire = (
        now
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "iat": now,
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def decode_token(
    token: str
) -> dict:

    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[
            JWT_ALGORITHM
        ],
        options={
            "require": [
                "sub",
                "type",
                "exp"
            ]
        }
    )