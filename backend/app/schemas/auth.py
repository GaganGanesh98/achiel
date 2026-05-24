from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core._security_base import truncate_password_for_bcrypt
from app.models.user import VerificationStatus


def _truncate_password(v: str) -> str:
    return truncate_password_for_bcrypt(v)


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=60)

    @field_validator("password", mode="before")
    @classmethod
    def truncate_password(cls, v: object) -> object:
        if isinstance(v, str):
            return _truncate_password(v)
        return v
    country: str = Field(default="DE", min_length=2, max_length=2)
    program: str | None = Field(default=None, max_length=255)
    year_of_study: str | None = Field(default=None, max_length=20)
    privacy_consent: bool

    @field_validator("display_name")
    @classmethod
    def no_obvious_handles(cls, v: str) -> str:
        if v.strip().lower() in {"admin", "moderator", "root", "system"}:
            raise ValueError("Reserved display name")
        return v.strip()

    @field_validator("country")
    @classmethod
    def country_upper(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("privacy_consent")
    @classmethod
    def must_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("You must accept the privacy policy to register")
        return v


class RegisterResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool
    next: str = "/verify-pending"
    access_token: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("password", mode="before")
    @classmethod
    def truncate_password(cls, v: object) -> object:
        if isinstance(v, str):
            return _truncate_password(v)
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UniversityOut(BaseModel):
    id: UUID
    name: str
    domain: str
    city: str | None
    short_name: str | None = None
    state: str | None = None
    type: str | None = None
    website: str | None = None
    verified_student_count: int = 0

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    country: str
    university: str | None
    program: str | None
    year_of_study: str | None
    is_verified: bool
    email_confirmed_at: datetime | None = None
    is_admin: bool = False
    verification_status: VerificationStatus
    university_link: UniversityOut | None = Field(
        default=None, validation_alias="university_link"
    )
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=60)
    country: str | None = Field(default=None, min_length=2, max_length=2)
    program: str | None = Field(default=None, max_length=255)
    year_of_study: str | None = Field(default=None, max_length=20)

    @field_validator("display_name")
    @classmethod
    def no_obvious_handles(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v.strip().lower() in {"admin", "moderator", "root", "system"}:
            raise ValueError("Reserved display name")
        return v.strip()


class VerifyTokenRequest(BaseModel):
    token: str = Field(min_length=16, max_length=255)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=16, max_length=255)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password", mode="before")
    @classmethod
    def truncate_new_password(cls, v: object) -> object:
        if isinstance(v, str):
            return _truncate_password(v)
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("current_password", "new_password", mode="before")
    @classmethod
    def truncate_passwords(cls, v: object) -> object:
        if isinstance(v, str):
            return _truncate_password(v)
        return v


class ConfirmEmailRequest(BaseModel):
    token: str = Field(min_length=16, max_length=255)


class UniversityLookupResponse(BaseModel):
    university: str | None
