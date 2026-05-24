import uuid
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core._security_base import hash_password, verify_password
from app.core.db import get_db
from app.models import User, VerificationStatus
from app.services import tokens as token_store
from main import app


@pytest.fixture
async def api_client(db: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


async def _create_user(
    db,
    *,
    email: str | None = None,
    password: str = "oldpassword12",
) -> tuple[User, str]:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        email=email or f"authflow-{suffix}@mit.edu",
        hashed_password=hash_password(password),
        display_name="Auth Flow User",
        country="US",
        is_verified=True,
        verification_status=VerificationStatus.VERIFIED,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user, password


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _login_token(api_client: AsyncClient, email: str, password: str) -> str:
    res = await api_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


@patch("app.api.auth.email_service.send_email", new_callable=AsyncMock)
async def test_forgot_password_unknown_email_returns_200(
    mock_send: AsyncMock, api_client: AsyncClient
) -> None:
    res = await api_client.post(
        "/auth/forgot-password",
        json={"email": "nobody@mit.edu"},
    )
    assert res.status_code == 200
    assert "account exists" in res.json()["message"].lower()
    mock_send.assert_not_called()


@patch("app.api.auth.email_service.send_email", new_callable=AsyncMock)
async def test_reset_password_with_valid_token_updates_password(
    mock_send: AsyncMock, api_client: AsyncClient, db
) -> None:
    user, old_password = await _create_user(db)
    raw_token, token_hash = token_store.generate_token()
    await token_store.store_token(
        token_store.PWRESET_PREFIX,
        token_hash,
        user.id,
        token_store.PWRESET_TTL_SECONDS,
    )

    res = await api_client.post(
        "/auth/reset-password",
        json={"token": raw_token, "new_password": "newpassword99"},
    )
    assert res.status_code == 200

    await db.refresh(user)
    assert verify_password("newpassword99", user.hashed_password)
    assert not verify_password(old_password, user.hashed_password)


async def test_reset_password_with_expired_token_returns_400(
    api_client: AsyncClient,
) -> None:
    with patch(
        "app.api.auth.token_store.consume_token",
        new_callable=AsyncMock,
        return_value=None,
    ):
        res = await api_client.post(
            "/auth/reset-password",
            json={
                "token": "expired-token-value-32chars!!",
                "new_password": "newpassword99",
            },
        )
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


async def test_change_password_wrong_current_returns_400(
    api_client: AsyncClient, db
) -> None:
    user, password = await _create_user(db)
    token = await _login_token(api_client, user.email, password)

    res = await api_client.post(
        "/auth/change-password",
        json={"current_password": "wrongpassword", "new_password": "newpassword99"},
        headers=_auth_header(token),
    )
    assert res.status_code == 400
    assert "incorrect" in res.json()["detail"].lower()


async def test_change_password_correct_updates_hash(
    api_client: AsyncClient, db
) -> None:
    user, password = await _create_user(db)
    token = await _login_token(api_client, user.email, password)

    res = await api_client.post(
        "/auth/change-password",
        json={"current_password": password, "new_password": "brandnewpass1"},
        headers=_auth_header(token),
    )
    assert res.status_code == 200

    await db.refresh(user)
    assert verify_password("brandnewpass1", user.hashed_password)


@patch("app.api.auth.email_service.send_email", new_callable=AsyncMock)
async def test_verify_email_sets_email_confirmed_at(
    mock_send: AsyncMock, api_client: AsyncClient, db
) -> None:
    user, _ = await _create_user(db)
    assert user.email_confirmed_at is None

    with patch(
        "app.api.auth.token_store.consume_token",
        new_callable=AsyncMock,
        return_value=user.id,
    ):
        res = await api_client.post(
            "/auth/verify-email",
            json={"token": "valid-email-confirm-token"},
        )
    assert res.status_code == 200

    await db.refresh(user)
    assert user.email_confirmed_at is not None
