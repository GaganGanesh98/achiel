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

    FRONTEND_URL: str = "http://localhost:3000"
    APP_BASE_URL: str = "http://localhost:3000"
    ENV: str = "development"
    DEV_AUTO_VERIFY: bool = False
    EMAIL_SENDER: str | None = None

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 2525
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str = "noreply@campusvoice.app"
    SMTP_TLS: bool = False

    RESEND_API_KEY: str | None = None
    RESEND_FROM: str | None = None

    CORS_ORIGINS: str = "http://localhost:3000"

    SEVERE_TERMS_PATH: str | None = None
    SEVERE_TERMS_JSON: str = "[]"
    SEVERE_TERMS_DE_PATH: str | None = None
    SEVERE_TERMS_DE_JSON: str = "[]"

    OPENAI_API_KEY: str | None = None

    ALLOWED_EMAIL_DOMAINS_JSON: str = Field(default="{}", alias="ALLOWED_EMAIL_DOMAINS")
    ALLOWED_EMAIL_DOMAINS_FILE: str | None = None

    @property
    def ALLOWED_EMAIL_DOMAINS(self) -> dict[str, dict]:
        # 1) Inline env JSON wins if non-empty (back-compat).
        try:
            inline = json.loads(self.ALLOWED_EMAIL_DOMAINS_JSON)
        except json.JSONDecodeError:
            inline = {}
        # Strip internal keys (e.g. "_comment") that aren't real domains.
        inline = {k: v for k, v in inline.items() if not k.startswith("_")}
        if inline:
            return inline

        # 2) Otherwise load from JSON file (default: backend/allowed_domains.json).
        candidate = (
            Path(self.ALLOWED_EMAIL_DOMAINS_FILE)
            if self.ALLOWED_EMAIL_DOMAINS_FILE
            else _BACKEND_ROOT / "allowed_domains.json"
        )
        if candidate.exists():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                return {k: v for k, v in data.items() if not k.startswith("_")}
            except json.JSONDecodeError:
                return {}
        return {}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def resend_from(self) -> str:
        return self.RESEND_FROM or self.SMTP_FROM or self.EMAIL_SENDER or self.SMTP_FROM

    @property
    def severe_terms_path(self) -> Path:
        if self.SEVERE_TERMS_PATH:
            return Path(self.SEVERE_TERMS_PATH)
        return _BACKEND_ROOT / "severe_terms.txt"

    @property
    def severe_terms_de_path(self) -> Path:
        if self.SEVERE_TERMS_DE_PATH:
            return Path(self.SEVERE_TERMS_DE_PATH)
        return _BACKEND_ROOT / "severe_terms_de.txt"


settings = Settings()  # type: ignore[call-arg]
