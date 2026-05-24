from __future__ import annotations

import hashlib
import secrets
from uuid import UUID

from app.core.redis_client import get_redis_pool

PWRESET_PREFIX = "pwreset:"
EMAILVERIFY_PREFIX = "emailverify:"
PWRESET_TTL_SECONDS = 900
EMAILVERIFY_TTL_SECONDS = 86400


def generate_token() -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, token_hash


async def store_token(
    prefix: str, token_hash: str, user_id: UUID, ttl_seconds: int
) -> None:
    redis = get_redis_pool()
    key = f"{prefix}{token_hash}"
    await redis.set(key, str(user_id).encode(), ex=ttl_seconds)


async def consume_token(prefix: str, raw_token: str) -> UUID | None:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    redis = get_redis_pool()
    key = f"{prefix}{token_hash}"
    user_id_raw = await redis.getdel(key)
    if user_id_raw is None:
        return None
    return UUID(user_id_raw.decode())
