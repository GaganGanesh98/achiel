"""German university domain catalogue helpers."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import University
from app.seed.german_universities import (
    NON_DE_TLD_ALLOWLIST,
    all_catalogue_domains,
    domain_to_university,
)

NON_GERMAN_DOMAIN_KEY = "auth.signup.non_german_domain"


@lru_cache
def catalogue_domain_set() -> frozenset[str]:
    return frozenset(all_catalogue_domains())


def _domain_variants(domain: str) -> list[str]:
    parts = domain.split(".")
    return [".".join(parts[i:]) for i in range(len(parts) - 1)]


def matches_catalogue_domain(domain: str) -> bool:
    domain = domain.lower().strip()
    allowed = catalogue_domain_set()
    return any(v in allowed for v in _domain_variants(domain))


def is_allowlisted_non_de_domain(domain: str) -> bool:
    for variant in _domain_variants(domain):
        if variant in NON_DE_TLD_ALLOWLIST:
            return True
        for allowed in NON_DE_TLD_ALLOWLIST:
            if variant == allowed or variant.endswith(f".{allowed}"):
                return True
    return False


def is_german_scoped_domain(domain: str) -> bool:
    """`.de` TLD or explicit non-.de German university allowlist."""
    domain = domain.lower()
    if domain.endswith(".de"):
        return True
    return is_allowlisted_non_de_domain(domain)


async def find_university_by_email_domain(
    db: AsyncSession, email: str
) -> University | None:
    from app.services.university_email import extract_domain

    domain = extract_domain(email)
    for candidate in _domain_variants(domain):
        result = await db.execute(
            select(University).where(
                University.domain == candidate,
                University.deleted_at.is_(None),
            )
        )
        uni = result.scalar_one_or_none()
        if uni is not None:
            return uni
    return None


def lookup_name_from_catalogue(email: str) -> str | None:
    from app.services.university_email import extract_domain

    domain = extract_domain(email)
    mapping = domain_to_university()
    for candidate in _domain_variants(domain):
        uni = mapping.get(candidate)
        if uni is not None:
            return uni.name
    return None
