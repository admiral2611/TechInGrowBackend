MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128


COMMON_PASSWORDS = {
    "123456",
    "1234567",
    "12345678",
    "123456789",
    "1234567890",
    "password",
    "password1",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "letmein",
    "welcome",
    "abcdef",
    "abc123",
}


def validate_password_strength(
    password: str
) -> str:

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least "
            f"{MIN_PASSWORD_LENGTH} characters long"
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must not exceed "
            f"{MAX_PASSWORD_LENGTH} characters"
        )

    if password.isspace():
        raise ValueError(
            "Password cannot contain only spaces"
        )

    normalized_password = (
        password
        .strip()
        .lower()
    )

    if normalized_password in COMMON_PASSWORDS:
        raise ValueError(
            "This password is too common"
        )

    return password