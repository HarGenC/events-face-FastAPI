from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.database import Base
from app.modules.events.models import Events, Place
from app.modules.sync.models import SyncLogs

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/test_db"


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"\n  Ошибка подключения к PostgreSQL: {e}")
        raise

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(session):
    await session.execute(delete(Events))
    await session.execute(delete(SyncLogs))
    await session.execute(delete(Place))
    await session.commit()

    yield

    await session.rollback()
