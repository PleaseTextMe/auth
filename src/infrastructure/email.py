import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from src.core.config import settings
from src.domain.exceptions import VerificationDeliveryUnavailable


async def send_verification_email(email: str, code: int) -> None:
    config = settings.email
    if not config.host or not config.sender:
        raise VerificationDeliveryUnavailable()

    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = email
    message["Subject"] = "PleaseTextMe verification code"
    message.set_content(f"Your verification code is {code:06d}. It expires in 5 minutes.")

    def send() -> None:
        with smtplib.SMTP(config.host, config.port, timeout=10) as client:
            if config.starttls:
                client.starttls(context=ssl.create_default_context())
            if config.username:
                client.login(config.username, config.password.get_secret_value())
            if client.send_message(message):
                raise smtplib.SMTPException("Verification recipient refused")

    try:
        await asyncio.to_thread(send)
    except (OSError, smtplib.SMTPException) as exc:
        raise VerificationDeliveryUnavailable() from exc
