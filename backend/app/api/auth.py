from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.limiter import limiter
from app.core.redis_client import get_redis
from app.core.security import (
    create_access_token,
    get_current_user_required,
    hash_password,
    verify_password,
)
from app.models import User, VerificationStatus
from app.schemas.auth import (
    Token,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
    VerifyEmailRequest,
)
from app.services import verification as verif


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    # Email already taken?
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    # Domain allowed?
    try:
        uni = await verif.get_or_reject_university(db, payload.email)
    except verif.DomainNotAllowed as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name,
        country=payload.country,
        university_id=uni.id,
        verification_status=VerificationStatus.PENDING,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user, ["university"])

    code = await verif.issue_otp(redis, user.email)
    await verif.send_otp_email(user.email, code)
    return user


@router.post("/verify", response_model=UserOut)
async def verify(
    payload: VerifyEmailRequest,
    email: str = Query(..., description="Email address being verified"),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    try:
        await verif.consume_otp(redis, email, payload.token)
    except verif.InvalidOTP as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))

    await verif.mark_verified(db, user)
    await db.commit()
    await db.refresh(user, ["university"])
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
) -> User:
    await db.refresh(user, ["university"])
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
) -> User:
    if payload.display_name is not None:
        user.display_name = payload.display_name
    if payload.country is not None:
        user.country = payload.country.upper() if payload.country else None
    await db.commit()
    await db.refresh(user, ["university"])
    return user
