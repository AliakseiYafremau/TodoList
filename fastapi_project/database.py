from typing import Annotated

from sqlmodel import Field, SQLModel

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from pathlib import Path
from dotenv import load_dotenv
from os import getenv

load_dotenv(dotenv_path=Path(__file__).parent / "../.env", encoding="utf-8")


# Таблицы
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str


class TODOList(SQLModel, table=True):
    id: int = Field(default=..., primary_key=True)
    user: int = Field(default=..., foreign_key="user.id")
    title: str

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    todo_list: int = Field(default=..., foreign_key="todolist.id")
    note: str | None = Field(default=None)


# Модели
class TODOListCreate(SQLModel):
    title: str


class TaskCreate(SQLModel):
    todo_list: int = Field(default=..., foreign_key="todolist.id")
    note: str

class TaskUpdate(SQLModel):
    note: str


db_url = getenv("DB_URL")
# print(db_url)

engine = create_async_engine(db_url)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

SessionDP = Annotated[AsyncSession, Depends(get_session)]