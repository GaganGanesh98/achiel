"""Transactional emails for domain review outcomes."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _send_via_resend(to: str, subject: str, text: str, html: str) -> None:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.resend_from,
                "to": [to],
                "subject": subject,
                "text": text,
                "html": html,
            },
            timeout=30.0,
        )
        resp.raise_for_status()


def _send_via_smtp(to: str, subject: str, text: str, html: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)


async def send_email(to: str, subject: str, text: str, html: str | None = None) -> None:
    html_body = html or f"<p>{text.replace(chr(10), '<br>')}</p>"

    if settings.RESEND_API_KEY:
        await _send_via_resend(to, subject, text, html_body)
        return

    if settings.SMTP_HOST:
        import asyncio

        await asyncio.to_thread(_send_via_smtp, to, subject, text, html_body)
        return

    logger.info("[DEV] Email to %s — %s: %s", to, subject, text)


async def notify_domain_approved(email: str, domain: str) -> None:
    subject = "Your CampusVoice account is active"
    text = (
        f"Good news — {domain} has been approved.\n\n"
        "You can log in and start posting on CampusVoice."
    )
    await send_email(email, subject, text)


async def notify_domain_rejected(email: str, domain: str, reason: str) -> None:
    subject = "CampusVoice registration update"
    text = (
        f"We could not approve the email domain {domain} for CampusVoice.\n\n"
        f"Reason: {reason}\n\n"
        "If you believe this is a mistake, contact support."
    )
    await send_email(email, subject, text)
