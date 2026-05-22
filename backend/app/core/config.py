from pathlib import Path

import json

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "noreply@campusvoice.app"

    RESEND_API_KEY: str | None = None
    RESEND_FROM: str | None = None  # defaults to SMTP_FROM when unset

    CORS_ORIGINS: str = "http://localhost:3000"

    SEVERE_TERMS_PATH: str | None = None
    SEVERE_TERMS_JSON: str = "[]"

    # Pass as a JSON string in env:
    # ALLOWED_EMAIL_DOMAINS='{"srh-hochschule-berlin.de": {"name": "SRH Berlin", "country": "DE", "city": "Berlin"}}'
    ALLOWED_EMAIL_DOMAINS_JSON: str = Field(default="{}", alias="ALLOWED_EMAIL_DOMAINS")

    @property
    def ALLOWED_EMAIL_DOMAINS(self) -> dict[str, dict]:
        try:
            return json.loads(self.ALLOWED_EMAIL_DOMAINS_JSON)
        except json.JSONDecodeError:
            return {}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def resend_from(self) -> str:
        return self.RESEND_FROM or self.SMTP_FROM

    @property
    def severe_terms_path(self) -> Path:
        if self.SEVERE_TERMS_PATH:
            return Path(self.SEVERE_TERMS_PATH)
        return _BACKEND_ROOT / "severe_terms.txt"


settings = Settings()  # type: ignore[call-arg]
