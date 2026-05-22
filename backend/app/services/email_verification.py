"""Token-based email verification (link logged to stdout in dev)."""

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import User, VerificationStatus

logger = logging.getLogger(__name__)

TOKEN_TTL_HOURS = 24


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def token_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)


def assign_verification_token(user: User) -> str:
    token = generate_verification_token()
    user.verification_token = token
    user.verification_token_expires_at = token_expires_at()
    return token


def verification_link(token: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/verify?token={token}"


def log_verification_link(email: str, token: str) -> None:
    link = verification_link(token)
    logger.info("[DEV] Verification link for %s: %s", email, link)


async def mark_user_verified(db: AsyncSession, user: User) -> User:
    user.is_verified = True
    user.verification_status = VerificationStatus.VERIFIED
    user.verification_token = None
    user.verification_token_expires_at = None
    await db.flush()
    return user


async def find_user_by_token(db: AsyncSession, token: str) -> User | None:
    result = await db.execute(
        select(User).where(User.verification_token == token)
    )
    return result.scalar_one_or_none()


def token_is_valid(user: User) -> bool:
    if not user.verification_token or not user.verification_token_expires_at:
        return False
    now = datetime.now(timezone.utc)
    expires = user.verification_token_expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    return now < expires
