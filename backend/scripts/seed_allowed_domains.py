#!/usr/bin/env -S uv run python
"""One-shot seed: university domains + student subdomain variants (idempotent)."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.models.domain import AllowedDomain, AllowedDomainSource
from app.seed.german_private_unis import german_private_domains_with_variants

logger = logging.getLogger(__name__)

UNIVERSITIES_URL = (
    "https://raw.githubusercontent.com/Hipo/university-domains-list/master/"
    "world_universities_and_domains.json"
)

STUDENT_PREFIXES = ("stud.", "student.", "students.")


async def _bulk_insert_domains(
    db: AsyncSession,
    *,
    domains: set[str],
    source: AllowedDomainSource,
    added_at: datetime,
) -> int:
    if not domains:
        return 0

    batch_size = 500
    inserted = 0
    domain_list = sorted(domains)
    for i in range(0, len(domain_list), batch_size):
        chunk = domain_list[i : i + batch_size]
        rows = [
            {
                "domain": domain,
                "source": source,
                "added_at": added_at,
                "added_by": None,
            }
            for domain in chunk
        ]
        stmt = insert(AllowedDomain).values(rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=["domain"])
        result = await db.execute(stmt)
        inserted += result.rowcount or 0
    return inserted


async def seed_hipo(db: AsyncSession, *, added_at: datetime) -> int:
    async with httpx.AsyncClient() as client:
        resp = await client.get(UNIVERSITIES_URL, timeout=120.0)
        resp.raise_for_status()
        entries = resp.json()

    seed_domains: set[str] = set()
    pattern_domains: set[str] = set()
    for entry in entries:
        raw = entry.get("domains") or []
        if not raw and entry.get("domain"):
            raw = [entry["domain"]]
        for d in raw:
            if not d or not isinstance(d, str):
                continue
            base = d.lower().strip()
            if base:
                seed_domains.add(base)
                for prefix in STUDENT_PREFIXES:
                    pattern_domains.add(f"{prefix}{base}")

    logger.info(
        "Hipo: %d seed domains, %d pattern variants",
        len(seed_domains),
        len(pattern_domains),
    )

    inserted = 0
    inserted += await _bulk_insert_domains(
        db, domains=seed_domains, source=AllowedDomainSource.SEED, added_at=added_at
    )
    inserted += await _bulk_insert_domains(
        db, domains=pattern_domains, source=AllowedDomainSource.PATTERN, added_at=added_at
    )
    return inserted


async def seed_german_private_unis(db: AsyncSession, *, added_at: datetime) -> int:
    domains = german_private_domains_with_variants()
    logger.info("German private unis: %d domains (incl. student variants)", len(domains))
    return await _bulk_insert_domains(
        db, domains=domains, source=AllowedDomainSource.MANUAL, added_at=added_at
    )


async def seed() -> None:
    logging.basicConfig(level=logging.INFO)
    now = datetime.now(timezone.utc)
    inserted = 0

    async with AsyncSessionLocal() as db:
        inserted += await seed_hipo(db, added_at=now)
        inserted += await seed_german_private_unis(db, added_at=now)
        await db.commit()

    logger.info("Seed complete (%d rows reported inserted this run)", inserted)


if __name__ == "__main__":
    asyncio.run(seed())
