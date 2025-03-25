# tests/conftest.py

import os
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app
from app.core.database import get_session
from app.models.models import Base

os.environ["ENV"] = "test"
load_dotenv(".env.test")

DATABASE_URL = os.getenv("DATABASE_URL")

@pytest_asyncio.fixture(scope="function")
async def client():
    # ✅ Create a fresh engine per test
    engine = create_async_engine(DATABASE_URL, echo=False)
    TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    # ✅ Reset DB tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # ✅ New session override
    async def override_get_session():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # ✅ Client with isolated DB per test
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
