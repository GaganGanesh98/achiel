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

import secrets
from datetime import timedelta

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import University, User, VerificationStatus


OTP_TTL_SECONDS = 15 * 60  # 15 min


class DomainNotAllowed(Exception):
    pass


class InvalidOTP(Exception):
    pass


def extract_domain(email: str) -> str:
    return email.split("@", 1)[1].lower().strip()


async def get_or_reject_university(db: AsyncSession, email: str) -> University:
    """Returns the University row for this email's domain, or raises."""
    domain = extract_domain(email)

    # settings.ALLOWED_EMAIL_DOMAINS is a dict[str, dict] loaded from env/JSON:
    #   {"srh-hochschule-berlin.de": {"name": "SRH Berlin", "country": "DE", "city": "Berlin"}, ...}
    meta = settings.ALLOWED_EMAIL_DOMAINS.get(domain)
    if not meta:
        raise DomainNotAllowed(
            f"'{domain}' is not a recognised university domain. "
            f"Contact support if your institution should be added."
        )

    # Upsert the university so the first user from a school populates it
    result = await db.execute(select(University).where(University.domain == domain))
    uni = result.scalar_one_or_none()
    if uni is None:
        uni = University(
            domain=domain,
            name=meta["name"],
            country=meta["country"],
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
    user.verification_status = VerificationStatus.VERIFIED
    await db.flush()
    return user


async def send_otp_email(to: str, code: str) -> None:
    """
    Stub. Wire this to your SMTP / SendGrid / Resend / Postmark of choice.
    In dev, just log the code so Cursor can test the flow without SMTP setup.
    """
    if settings.SMTP_HOST:
        # TODO: implement smtplib send. Keeping it stub'd so dev works out of the box.
        pass
    print(f"[DEV-OTP] verification code for {to}: {code}")
