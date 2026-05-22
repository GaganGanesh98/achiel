import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import AllowedDomain, PendingDomain, User
from app.models.domain import AllowedDomainSource
from app.services import university_email as uni_email

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://campusvoice:campusvoice@localhost:5434/campusvoice",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture(autouse=True)
def disposable_domains() -> None:
    uni_email._disposable_domains = {"mailinator.com", "tempmail.com"}
    yield
    uni_email._disposable_domains = None


@pytest.fixture
async def clean_domain_tables(db: AsyncSession) -> AsyncIterator[None]:
    await db.execute(delete(User).where(User.email.like("%@newuni.education")))
    await db.execute(delete(User).where(User.email.like("admin-%@test.edu")))
    await db.execute(delete(PendingDomain))
    await db.execute(delete(AllowedDomain))
    await db.commit()
    yield
    await db.rollback()
    await db.execute(delete(User).where(User.email.like("%@newuni.education")))
    await db.execute(delete(User).where(User.email.like("admin-%@test.edu")))
    await db.execute(delete(PendingDomain))
    await db.execute(delete(AllowedDomain))
    await db.commit()


async def allow_domain(
    db: AsyncSession,
    domain: str,
    *,
    source: AllowedDomainSource = AllowedDomainSource.ADMIN,
) -> None:
    db.add(
        AllowedDomain(
            domain=domain,
            source=source,
            added_by="test",
        )
    )
    await db.flush()
