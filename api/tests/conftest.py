import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from main import app
from models.db import Base, get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from settings import setting

import os

from sqlalchemy.pool import NullPool

TEST_DB_URL = os.getenv("TEST_DB_URL", setting.DB_URL.replace("host.docker.internal", "localhost"))

@pytest.fixture
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    mock_arq = AsyncMock()
    mock_arq.enqueue_job = AsyncMock()

    with patch("routers.v1.auth.get_arq_pool", return_value=mock_arq), \
         patch("routers.v1.auth.redis.set", new_callable=AsyncMock), \
         patch("routers.v1.auth.redis.get", new_callable=AsyncMock), \
         patch("routers.v1.auth.redis.delete", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
            yield ac

    app.dependency_overrides.clear()
