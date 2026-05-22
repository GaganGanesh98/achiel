#!/usr/bin/env -S uv run python
"""One-shot seed: university domains + student subdomain variants (idempotent)."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.dialects.postgresql import insert

from app.core.db import AsyncSessionLocal
from app.models.domain import AllowedDomain, AllowedDomainSource

logger = logging.getLogger(__name__)

UNIVERSITIES_URL = (
    "https://raw.githubusercontent.com/Hipo/university-domains-list/master/"
    "world_universities_and_domains.json"
)

STUDENT_PREFIXES = ("stud.", "student.", "students.")


async def seed() -> None:
    logging.basicConfig(level=logging.INFO)
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
        "Collected %d seed domains and %d pattern variants",
        len(seed_domains),
        len(pattern_domains),
    )

    now = datetime.now(timezone.utc)
    batch_size = 500
    inserted = 0

    async with AsyncSessionLocal() as db:
        for source, domain_set in (
            (AllowedDomainSource.SEED, seed_domains),
            (AllowedDomainSource.PATTERN, pattern_domains),
        ):
            domain_list = sorted(domain_set)
            for i in range(0, len(domain_list), batch_size):
                chunk = domain_list[i : i + batch_size]
                rows = [
                    {
                        "domain": domain,
                        "source": source,
                        "added_at": now,
                        "added_by": None,
                    }
                    for domain in chunk
                ]
                stmt = insert(AllowedDomain).values(rows)
                stmt = stmt.on_conflict_do_nothing(index_elements=["domain"])
                result = await db.execute(stmt)
                inserted += result.rowcount or 0
        await db.commit()

    logger.info("Seed complete (%d rows reported inserted this run)", inserted)


if __name__ == "__main__":
    asyncio.run(seed())
