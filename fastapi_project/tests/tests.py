import pytest
import pytest_asyncio
import httpx

from httpx import ASGITransport, AsyncClient
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from fastapi_project.database import get_session
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from fastapi_project.main import app

load_dotenv(dotenv_path=Path(__file__).parent / "../../.env", encoding="utf-8")

test_db_url = getenv("TEST_DB_URL")
engine = create_async_engine(test_db_url)


TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSession() as db:
        yield db

app.dependency_overrides[get_session] = override_get_db

@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup():
    # Create all the tables in the test database
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield  # This will ensure setup runs before tests and teardown runs after tests

    # Teardown: Drop all tables after tests are done
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.mark.asyncio
async def test_root(client: httpx.AsyncClient):
    response = await client.get("/todo")
    assert response.status_code == 200
    assert response.json() == []
