"""
Pytest configuration and fixtures for async SQLAlchemy testing.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from app.db.connection import Base, get_db

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a fresh test database for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession):
    """Create an async test client with database override."""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """Get authentication headers for a new test user."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def demo_user_headers(client: AsyncClient):
    """Register a demo user and get auth headers."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "demo_player",
            "email": "demo@example.com",
            "password": "demo1234"
        }
    )
    assert response.status_code == 201
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}
