from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import VerificationStatus


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=60)
    country: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("display_name")
    @classmethod
    def no_obvious_handles(cls, v: str) -> str:
        if v.strip().lower() in {"admin", "moderator", "root", "system"}:
            raise ValueError("Reserved display name")
        return v.strip()


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
    country: str | None
    verification_status: VerificationStatus
    university: UniversityOut | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VerifyEmailRequest(BaseModel):
    token: str
