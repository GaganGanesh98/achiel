"""
Cursor generates the bulk of this file (Pydantic BaseSettings pulling DATABASE_URL,
REDIS_URL, JWT_*, SMTP_*, etc).

The non-obvious bit is `ALLOWED_EMAIL_DOMAINS` — it needs to be a dict, not a list,
because we want each domain to carry uni name + country metadata. Loaded from a JSON
env var or a YAML file shipped with the repo.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import json


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

    # Pass as a JSON string in env:
    # ALLOWED_EMAIL_DOMAINS='{"srh-hochschule-berlin.de": {"name": "SRH Berlin", "country": "DE", "city": "Berlin"}}'
    ALLOWED_EMAIL_DOMAINS_JSON: str = Field(default="{}", alias="ALLOWED_EMAIL_DOMAINS")

    @property
    def ALLOWED_EMAIL_DOMAINS(self) -> dict[str, dict]:
        try:
            return json.loads(self.ALLOWED_EMAIL_DOMAINS_JSON)
        except json.JSONDecodeError:
            return {}


settings = Settings()  # type: ignore[call-arg]
