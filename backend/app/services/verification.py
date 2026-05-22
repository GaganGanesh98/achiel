"""
Email-domain verification:
1. On register, check the email domain is in the allowlist of university domains.
   If yes → create User(verification_status=PENDING), create University if missing.
   If no  → reject with 422.
2. Generate a 6-digit OTP, store in Redis with TTL, email it to the user.
3. POST /auth/verify with token → flip to VERIFIED, allow login & posting.

Why domain allowlist over a regex like r'@.+\\.edu$':
- .edu is US-specific; .ac.in, .ac.uk, tu-berlin.de, srh-hochschule-berlin.de don't match
- Spam domains can buy weird TLDs
- Allowlist is boring but correct
"""

import logging
import secrets
import smtplib
from email.message import EmailMessage

import httpx
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import University, User, VerificationStatus
from app.models.domain import AllowedDomain
from app.services.university_email import extract_domain as email_extract_domain

logger = logging.getLogger(__name__)

OTP_TTL_SECONDS = 15 * 60  # 15 min


class DomainNotAllowed(Exception):
    pass


class InvalidOTP(Exception):
    pass


def extract_domain(email: str) -> str:
    return email_extract_domain(email)


async def _domain_is_allowed(db: AsyncSession, domain: str) -> bool:
    result = await db.execute(
        select(AllowedDomain.domain).where(AllowedDomain.domain == domain)
    )
    if result.scalar_one_or_none() is not None:
        return True
    return domain in settings.ALLOWED_EMAIL_DOMAINS


async def get_or_reject_university(db: AsyncSession, email: str) -> University:
    """Returns the University row for this email's domain, or raises."""
    domain = extract_domain(email)

    if not await _domain_is_allowed(db, domain):
        raise DomainNotAllowed(
            f"'{domain}' is not a recognised university domain. "
            f"Contact support if your institution should be added."
        )

    meta = settings.ALLOWED_EMAIL_DOMAINS.get(domain, {})
    result = await db.execute(select(University).where(University.domain == domain))
    uni = result.scalar_one_or_none()
    if uni is None:
        uni = University(
            domain=domain,
            name=meta.get("name") or domain,
            country=meta.get("country") or "XX",
            city=meta.get("city"),
        )
        db.add(uni)
        await db.flush()
    return uni


def _otp_key(email: str) -> str:
    return f"otp:verify:{email.lower()}"


async def issue_otp(redis: Redis, email: str) -> str:
    code = f"{secrets.randbelow(1_000_000):06d}"
    await redis.set(_otp_key(email), code, ex=OTP_TTL_SECONDS)
    return code


async def consume_otp(redis: Redis, email: str, code: str) -> None:
    key = _otp_key(email)
    stored = await redis.get(key)
    if stored is None:
        raise InvalidOTP("OTP expired or never issued")
    stored_str = stored.decode() if isinstance(stored, bytes) else stored
    if stored_str != code:
        raise InvalidOTP("OTP does not match")
    await redis.delete(key)


async def mark_verified(db: AsyncSession, user: User) -> User:
    user.is_verified = True
    user.verification_status = VerificationStatus.VERIFIED
    user.verification_token = None
    user.verification_token_expires_at = None
    await db.flush()
    return user


def _otp_email_body(code: str) -> tuple[str, str]:
    subject = "Your CampusVoice verification code"
    text = (
        f"Your verification code is: {code}\n\n"
        f"It expires in {OTP_TTL_SECONDS // 60} minutes.\n"
    )
    html = (
        f"<p>Your verification code is: <strong>{code}</strong></p>"
        f"<p>It expires in {OTP_TTL_SECONDS // 60} minutes.</p>"
    )
    return subject, text, html  # type: ignore[return-value]


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


async def send_otp_email(to: str, code: str) -> None:
    subject = "Your CampusVoice verification code"
    text = (
        f"Your verification code is: {code}\n\n"
        f"It expires in {OTP_TTL_SECONDS // 60} minutes.\n"
    )
    html = (
        f"<p>Your verification code is: <strong>{code}</strong></p>"
        f"<p>It expires in {OTP_TTL_SECONDS // 60} minutes.</p>"
    )

    if settings.RESEND_API_KEY:
        await _send_via_resend(to, subject, text, html)
        return

    if settings.SMTP_HOST:
        import asyncio

        await asyncio.to_thread(_send_via_smtp, to, subject, text, html)
        return

    logger.warning("[DEV-OTP] verification code for %s: %s", to, code)
