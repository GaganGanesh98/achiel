import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    get_current_user_required,
    hash_password,
    verify_password,
)
from app.models import User, VerificationStatus
from app.schemas.auth import (
    MessageResponse,
    RegisterResponse,
    ResendVerificationRequest,
    Token,
    UserLogin,
    UserOut,
    UserRegister,
    UserUpdate,
    VerifyTokenRequest,
)
from app.services import email_verification as email_verif
from app.services import verification as verif
from app.services.universities import lookup_university

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _domain_not_allowed() -> HTTPException:
    return HTTPException(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Email domain not allowed. We only accept verified university emails.",
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    if not payload.privacy_consent:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "You must accept the privacy policy to register",
        )

    email = payload.email.lower()
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    domain = verif.extract_domain(email)
    if domain not in settings.ALLOWED_EMAIL_DOMAINS:
        raise _domain_not_allowed()

    university_name = lookup_university(email)
    university_id = None
    try:
        uni = await verif.get_or_reject_university(db, email)
        university_id = uni.id
        if not university_name:
            university_name = uni.name
    except verif.DomainNotAllowed:
        raise _domain_not_allowed()

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name,
        country=payload.country.upper(),
        university=university_name,
        program=payload.program,
        year_of_study=payload.year_of_study,
        university_id=university_id,
        verification_status=VerificationStatus.PENDING,
        is_verified=False,
    )

    if settings.DEV_AUTO_VERIFY:
        user.is_verified = True
        user.verification_status = VerificationStatus.VERIFIED
        logger.info("[DEV] Auto-verified user %s", email)
    else:
        token = email_verif.assign_verification_token(user)
        email_verif.log_verification_link(email, token)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token: str | None = None
    next_path = "/verify-pending"
    if user.is_verified:
        access_token = create_access_token(subject=str(user.id))
        next_path = "/dashboard"

    return RegisterResponse(
        id=user.id,
        email=user.email,
        is_verified=user.is_verified,
        next=next_path,
        access_token=access_token,
    )


@router.post("/verify", response_model=UserOut)
async def verify_email(
    payload: VerifyTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await email_verif.find_user_by_token(db, payload.token)
    if not user or not email_verif.token_is_valid(user):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Invalid or expired verification link. Request a new one.",
        )

    await email_verif.mark_user_verified(db, user)
    await db.commit()
    await db.refresh(user, ["university_link"])
    return user


@router.post("/resend-verification", response_model=MessageResponse)
@limiter.limit("3/minute")
async def resend_verification(
    request: Request,
    payload: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    email = payload.email.lower()
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user and not user.is_verified:
        token = email_verif.assign_verification_token(user)
        email_verif.log_verification_link(email, token)
        await db.commit()

    return MessageResponse(
        message="If an account exists for that email, a new verification link has been sent.",
    )


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")
    if not user.is_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Your email isn't verified yet. Check your inbox or resend the verification link.",
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    """Client clears JWT cookie; server acknowledges."""
    return None


@router.get("/me", response_model=UserOut)
async def me(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_required),
) -> User:
    await db.refresh(user, ["university_link"])
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
        user.country = payload.country.upper() if payload.country else user.country
    if payload.program is not None:
        user.program = payload.program
    if payload.year_of_study is not None:
        user.year_of_study = payload.year_of_study
    await db.commit()
    await db.refresh(user, ["university_link"])
    return user
