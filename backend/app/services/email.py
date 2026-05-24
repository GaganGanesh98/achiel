from __future__ import annotations

import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def _log_only(self) -> bool:
        if not (settings.SMTP_HOST or "").strip():
            return True
        return settings.ENV.lower() in ("dev", "development")

    async def send_email(self, to: str, subject: str, html: str, text: str) -> None:
        if self._log_only():
            print(
                f"\n--- Email (not sent; SMTP_HOST empty or ENV=dev) ---\n"
                f"To: {to}\n"
                f"Subject: {subject}\n"
                f"{text}\n"
                f"---\n",
                flush=True,
            )
            return

        message = EmailMessage()
        message["From"] = settings.SMTP_FROM
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text)
        message.add_alternative(html, subtype="html")

        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=settings.SMTP_TLS,
        )
        logger.info("Sent email to %s: %s", to, subject)


email_service = EmailService()
