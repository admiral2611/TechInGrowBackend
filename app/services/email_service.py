import os
import smtplib
import ssl

from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from dotenv import load_dotenv


load_dotenv()


SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
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

SMTP_USE_TLS = (
    os.getenv(
        "SMTP_USE_TLS",
        "true"
    )
    .strip()
    .lower()
    == "true"
)


def _validate_email_config() -> None:

    missing = []

    if not SMTP_HOST:
        missing.append(
            "SMTP_HOST"
        )

    if not SMTP_PORT:
        missing.append(
            "SMTP_PORT"
        )

    if not SMTP_USERNAME:
        missing.append(
            "SMTP_USERNAME"
        )

    if not SMTP_PASSWORD:
        missing.append(
            "SMTP_PASSWORD"
        )

    if not EMAIL_FROM_ADDRESS:
        missing.append(
            "EMAIL_FROM_ADDRESS"
        )

    if missing:

        raise RuntimeError(
            "Email konfiguratsiyasi to'liq emas: "
            + ", ".join(missing)
        )


def _send_email(
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str
) -> None:

    _validate_email_config()


    message = EmailMessage()


    message["Subject"] = subject

    message["From"] = (
        f"{EMAIL_FROM_NAME} "
        f"<{EMAIL_FROM_ADDRESS}>"
    )

    message["To"] = to_email

    message["Reply-To"] = (
        EMAIL_FROM_ADDRESS
    )

    message["Date"] = (
        formatdate(
            localtime=True
        )
    )

    message["Message-ID"] = (
        make_msgid()
    )


    message.set_content(
        text_content
    )


    message.add_alternative(
        html_content,
        subtype="html"
    )


    context = (
        ssl.create_default_context()
    )


    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=30
    ) as smtp:

        smtp.ehlo()


        if SMTP_USE_TLS:

            smtp.starttls(
                context=context
            )

            smtp.ehlo()


        smtp.login(
            SMTP_USERNAME,
            SMTP_PASSWORD
        )


        smtp.send_message(
            message
        )


def send_password_reset_email(
    to_email: str,
    code: str,
    expire_minutes: int
) -> None:

    subject = (
        "TechInGrow parolni tiklash kodi"
    )


    text_content = f"""
Salom,

TechInGrow akkauntingiz uchun parolni tiklash kodi:

{code}

Kod {expire_minutes} daqiqa davomida amal qiladi.

Agar siz parolni tiklashni so'ramagan bo'lsangiz,
ushbu xabarni e'tiborsiz qoldiring.

TechInGrow
""".strip()


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
        TechInGrow
    </title>

</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f5f6fa;
        font-family: Arial, Helvetica, sans-serif;
    "
>

    <div
        style="
            width: 100%;
            padding: 32px 16px;
            box-sizing: border-box;
        "
    >

        <div
            style="
                max-width: 520px;
                margin: 0 auto;
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                padding: 32px;
                box-sizing: border-box;
            "
        >

            <h1
                style="
                    margin: 0 0 24px;
                    color: #111827;
                    font-size: 24px;
                "
            >
                TechInGrow
            </h1>


            <p
                style="
                    margin: 0 0 16px;
                    color: #374151;
                    font-size: 15px;
                    line-height: 1.6;
                "
            >
                Salom,
            </p>


            <p
                style="
                    margin: 0 0 20px;
                    color: #374151;
                    font-size: 15px;
                    line-height: 1.6;
                "
            >
                Parolingizni tiklash uchun
                quyidagi tasdiqlash kodidan foydalaning.
            </p>


            <div
                style="
                    margin: 24px 0;
                    padding: 18px;
                    background-color: #f3f4f6;
                    border-radius: 10px;
                    text-align: center;
                    color: #111827;
                    font-size: 30px;
                    font-weight: 700;
                    letter-spacing: 6px;
                "
            >
                {code}
            </div>


            <p
                style="
                    margin: 0 0 16px;
                    color: #374151;
                    font-size: 14px;
                    line-height: 1.6;
                "
            >
                Ushbu kod
                <strong>
                    {expire_minutes} daqiqa
                </strong>
                davomida amal qiladi.
            </p>


            <p
                style="
                    margin: 24px 0 0;
                    color: #6b7280;
                    font-size: 13px;
                    line-height: 1.6;
                "
            >
                Agar siz parolni tiklashni
                so'ramagan bo'lsangiz,
                ushbu xabarni e'tiborsiz qoldiring.
            </p>

        </div>

    </div>

</body>

</html>
"""


    _send_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )


def send_email_verification_email(
    to_email: str,
    code: str,
    expire_minutes: int
) -> None:

    subject = (
        "TechInGrow email tasdiqlash kodi"
    )


    text_content = f"""
Salom,

TechInGrow akkauntingizni tasdiqlash kodi:

{code}

Kod {expire_minutes} daqiqa davomida amal qiladi.

Agar siz TechInGrow'da ro'yxatdan o'tmagan bo'lsangiz,
ushbu xabarni e'tiborsiz qoldiring.

TechInGrow
""".strip()


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
        TechInGrow
    </title>

</head>

<body
    style="
        margin: 0;
        padding: 0;
        background-color: #f5f6fa;
        font-family: Arial, Helvetica, sans-serif;
    "
>

    <div
        style="
            width: 100%;
            padding: 32px 16px;
            box-sizing: border-box;
        "
    >

        <div
            style="
                max-width: 520px;
                margin: 0 auto;
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
                padding: 32px;
                box-sizing: border-box;
            "
        >

            <h1
                style="
                    margin: 0 0 24px;
                    color: #111827;
                    font-size: 24px;
                "
            >
                TechInGrow
            </h1>


            <p
                style="
                    margin: 0 0 16px;
                    color: #374151;
                    font-size: 15px;
                    line-height: 1.6;
                "
            >
                Salom,
            </p>


            <p
                style="
                    margin: 0 0 20px;
                    color: #374151;
                    font-size: 15px;
                    line-height: 1.6;
                "
            >
                TechInGrow akkauntingizni
                tasdiqlash uchun quyidagi
                koddan foydalaning.
            </p>


            <div
                style="
                    margin: 24px 0;
                    padding: 18px;
                    background-color: #f3f4f6;
                    border-radius: 10px;
                    text-align: center;
                    color: #111827;
                    font-size: 30px;
                    font-weight: 700;
                    letter-spacing: 6px;
                "
            >
                {code}
            </div>


            <p
                style="
                    margin: 0 0 16px;
                    color: #374151;
                    font-size: 14px;
                    line-height: 1.6;
                "
            >
                Ushbu kod
                <strong>
                    {expire_minutes} daqiqa
                </strong>
                davomida amal qiladi.
            </p>


            <p
                style="
                    margin: 24px 0 0;
                    color: #6b7280;
                    font-size: 13px;
                    line-height: 1.6;
                "
            >
                Agar siz TechInGrow'da
                ro'yxatdan o'tmagan bo'lsangiz,
                ushbu xabarni e'tiborsiz qoldiring.
            </p>

        </div>

    </div>

</body>

</html>
"""


    _send_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )