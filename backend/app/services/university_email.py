"""Layered university email validation for signup."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

import dns.resolver
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    AllowedDomain,
    PendingDomain,
    PendingDomainConfidence,
    PendingDomainStatus,
)

logger = logging.getLogger(__name__)

DISPOSABLE_URL = (
    "https://raw.githubusercontent.com/disposable-email-domains/"
    "disposable-email-domains/master/disposable_email_blocklist.conf"
)

HIGH_CONFIDENCE_PATTERNS = [
    re.compile(r"\.edu$"),
    re.compile(r"\.edu\.[a-z]{2,3}$"),
    re.compile(r"\.ac\.[a-z]{2,3}$"),
    re.compile(r"^(stud|student|students)[.-]"),
    re.compile(r"\.(uni|hochschule|fh)-"),
    re.compile(r"-(university|universitaet|universite)\."),
]

ValidationStatus = Literal["allowed", "rejected", "pending"]

_disposable_domains: set[str] | None = None


@dataclass(frozen=True)
class EmailValidationResult:
    status: ValidationStatus
    reason: str


def extract_domain(email: str) -> str:
    return email.split("@", 1)[1].lower().strip()


async def load_disposable_domains() -> set[str]:
    global _disposable_domains
    if _disposable_domains is not None:
        return _disposable_domains

    async with httpx.AsyncClient() as client:
        resp = await client.get(DISPOSABLE_URL, timeout=60.0)
        resp.raise_for_status()

    domains = {
        line.strip().lower()
        for line in resp.text.splitlines()
        if line.strip() and not line.startswith("#")
    }
    _disposable_domains = domains
    logger.info("Loaded %d disposable email domains", len(domains))
    return domains


def get_disposable_domains() -> set[str]:
    if _disposable_domains is None:
        return set()
    return _disposable_domains


def domain_is_disposable(domain: str) -> bool:
    return domain.lower() in get_disposable_domains()


def domain_has_mx(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except Exception:
        return False


def domain_matches_high_confidence(domain: str) -> bool:
    return any(p.search(domain) for p in HIGH_CONFIDENCE_PATTERNS)


async def is_domain_allowed(db: AsyncSession, domain: str) -> bool:
    result = await db.execute(
        select(AllowedDomain.domain).where(AllowedDomain.domain == domain)
    )
    return result.scalar_one_or_none() is not None


async def _upsert_pending_domain(
    db: AsyncSession,
    *,
    domain: str,
    email: str,
    confidence: PendingDomainConfidence,
    country_hint: str | None,
) -> None:
    now = datetime.now(timezone.utc)
    result = await db.execute(select(PendingDomain).where(PendingDomain.domain == domain))
    row = result.scalar_one_or_none()
    if row is None:
        db.add(
            PendingDomain(
                domain=domain,
                first_seen_email=email,
                request_count=1,
                confidence=confidence,
                country_hint=country_hint,
                first_seen_at=now,
                last_seen_at=now,
                status=PendingDomainStatus.PENDING,
            )
        )
    elif row.status == PendingDomainStatus.PENDING:
        row.request_count += 1
        row.last_seen_at = now
    await db.flush()


async def validate_university_email(
    db: AsyncSession,
    email: str,
    *,
    country_hint: str | None = None,
    record_pending: bool = True,
) -> EmailValidationResult:
    email = email.lower().strip()
    domain = extract_domain(email)

    if await is_domain_allowed(db, domain):
        return EmailValidationResult("allowed", "Domain is on the university allowlist")

    if domain_is_disposable(domain):
        return EmailValidationResult("rejected", "Disposable email domains are not allowed")

    if not domain_has_mx(domain):
        return EmailValidationResult("rejected", "Domain has no valid MX records")

    if domain_matches_high_confidence(domain):
        if record_pending:
            await _upsert_pending_domain(
                db,
                domain=domain,
                email=email,
                confidence=PendingDomainConfidence.HIGH,
                country_hint=country_hint,
            )
        return EmailValidationResult(
            "pending",
            "Domain looks like a university but is not on our allowlist yet",
        )

    if record_pending:
        await _upsert_pending_domain(
            db,
            domain=domain,
            email=email,
            confidence=PendingDomainConfidence.LOW,
            country_hint=country_hint,
        )
    return EmailValidationResult(
        "pending",
        "Domain is not recognised; submitted for admin review",
    )
