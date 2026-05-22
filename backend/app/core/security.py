"""
Security primitives: password hashing, JWT, and auth dependencies.

- `get_current_user` — optional JWT; returns None for public reads.
- `get_current_user_required` — JWT required (e.g. /auth/me).
- `require_verified` — JWT required and email verification must be complete.
"""

from fastapi import Depends, HTTPException, status

from app.core._security_base import (
    create_access_token,
    decode_token,
    get_current_user_optional,
    get_current_user_strict,
    hash_password,
    verify_password,
)
from app.models import User, VerificationStatus

get_current_user_required = get_current_user_strict


async def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User | None:
    return user


async def require_verified(user: User = Depends(get_current_user_strict)) -> User:
    if not user.is_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Please verify your email before posting",
        )
    if user.verification_status != VerificationStatus.VERIFIED:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Your university domain is under review. We'll email you when you can post.",
        )
    return user


async def require_admin(user: User = Depends(get_current_user_strict)) -> User:
    if not user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "get_current_user_required",
    "require_verified",
    "require_admin",
]
