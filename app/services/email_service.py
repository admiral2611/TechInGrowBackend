import os
import smtplib
import ssl

from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp-relay.brevo.com"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USERNAME = os.getenv(
    "SMTP_USERNAME"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)

EMAIL_FROM_ADDRESS = os.getenv(
    "EMAIL_FROM_ADDRESS"
)

EMAIL_FROM_NAME = os.getenv(
    "EMAIL_FROM_NAME",
    "TechInGrow"
)


def _validate_email_config() -> None:

    if not SMTP_USERNAME:
        raise RuntimeError(
            "SMTP_USERNAME .env ichida topilmadi"
        )

    if not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP_PASSWORD .env ichida topilmadi"
        )

    if not EMAIL_FROM_ADDRESS:
        raise RuntimeError(
            "EMAIL_FROM_ADDRESS .env ichida topilmadi"
        )


def send_password_reset_email(
    to_email: str,
    reset_code: str,
    expires_minutes: int
) -> None:

    _validate_email_config()

    message = EmailMessage()

    message["Subject"] = (
        "TechInGrow - Parolni tiklash kodi"
    )

    message["From"] = (
        f"{EMAIL_FROM_NAME} "
        f"<{EMAIL_FROM_ADDRESS}>"
    )

    message["To"] = to_email

    text_content = f"""
TechInGrow

Parolni tiklash uchun tasdiqlash kodingiz:

{reset_code}

Kod {expires_minutes} daqiqa davomida amal qiladi.

Agar parolni tiklashni siz so'ramagan bo'lsangiz,
ushbu xabarni e'tiborsiz qoldiring.

TechInGrow
""".strip()

    message.set_content(
        text_content
    )

    html_content = f"""
<!DOCTYPE html>
<html lang="uz">

<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        TechInGrow Password Reset
    </title>
</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f4f6fa;
        font-family: Arial, Helvetica, sans-serif;
    "
>

    <div
        style="
            width: 100%;
            padding: 40px 16px;
            box-sizing: border-box;
        "
    >

        <div
            style="
                max-width: 520px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                padding: 32px;
                box-sizing: border-box;
            "
        >

            <h1
                style="
                    margin: 0 0 24px 0;
                    font-size: 28px;
                    line-height: 1.2;
                "
            >
                TechInGrow
            </h1>

            <h2
                style="
                    font-size: 20px;
                    margin-bottom: 16px;
                "
            >
                Parolni tiklash
            </h2>

            <p
                style="
                    font-size: 16px;
                    line-height: 1.6;
                "
            >
                Parolni tiklash uchun
                quyidagi tasdiqlash kodidan
                foydalaning:
            </p>

            <div
                style="
                    margin: 28px 0;
                    padding: 20px;
                    background-color: #f4f6fa;
                    border-radius: 12px;
                    text-align: center;
                    font-size: 34px;
                    font-weight: bold;
                    letter-spacing: 8px;
                "
            >
                {reset_code}
            </div>

            <p
                style="
                    font-size: 16px;
                    line-height: 1.6;
                "
            >
                Ushbu kod
                <strong>
                    {expires_minutes} daqiqa
                </strong>
                davomida amal qiladi.
            </p>

            <p
                style="
                    margin-top: 32px;
                    font-size: 14px;
                    color: #666666;
                    line-height: 1.6;
                "
            >
                Agar parolni tiklashni siz
                so'ramagan bo'lsangiz,
                ushbu xabarni e'tiborsiz
                qoldirishingiz mumkin.
            </p>

            <hr
                style="
                    border: none;
                    border-top: 1px solid #eeeeee;
                    margin: 32px 0 20px;
                "
            >

            <p
                style="
                    font-size: 13px;
                    color: #999999;
                "
            >
                © TechInGrow
            </p>

        </div>

    </div>

</body>

</html>
"""

    message.add_alternative(
        html_content,
        subtype="html"
    )

    ssl_context = (
        ssl.create_default_context()
    )

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=30
    ) as smtp:

        smtp.ehlo()

        smtp.starttls(
            context=ssl_context
        )

        smtp.ehlo()

        smtp.login(
            SMTP_USERNAME,
            SMTP_PASSWORD
        )

        smtp.send_message(
            message
        )