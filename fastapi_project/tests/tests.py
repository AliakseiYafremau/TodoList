import pytest
import pytest_asyncio
import httpx

from httpx import ASGITransport, AsyncClient
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from fastapi_project.database import get_session
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from fastapi_project.main import app

load_dotenv(dotenv_path=Path(__file__).parent / "../../.env", encoding="utf-8")

test_db_url = getenv("TEST_DB_URL")
engine = create_async_engine(test_db_url)

TestSession = async_sessionmaker(engine, expire_on_commit=False)

async def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_session] = override_get_db

@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root(client: httpx.AsyncClient):
    response = await client.get("/todo")
    assert response.status_code == 200

async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def teardown():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)