import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from fastapi_project.config import settings
from fastapi_project.database import get_session
from fastapi_project.main import app


test_db_url = settings.TEST_DB_URL
engine = create_async_engine(test_db_url)

TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSession() as db:
        yield db

# Переписываем зависимость, через которую app обращается к базе
app.dependency_overrides[get_session] = override_get_db


# Настройка базы данных
@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup():
    # Create all the tables in the test database
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield  # This will ensure setup runs before tests and teardown runs after tests

    # Teardown: Drop all tables after tests are done
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


