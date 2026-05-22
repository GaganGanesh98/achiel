from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import VerificationStatus


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=60)
    country: str = Field(min_length=2, max_length=2)
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
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UniversityOut(BaseModel):
    id: UUID
    name: str
    domain: str
    country: str
    city: str | None

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


class UniversityLookupResponse(BaseModel):
    university: str | None
