"""University display-name lookup from email domain."""

from __future__ import annotations

from app.services.german_catalogue import lookup_name_from_catalogue


def extract_domain(email: str) -> str:
    return email.split("@", 1)[1].lower().strip()


def lookup_university(email: str) -> str | None:
    """Return mapped university name for the email domain, or None."""
    return lookup_name_from_catalogue(email)
