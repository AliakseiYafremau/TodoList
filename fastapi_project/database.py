from typing import Annotated

from sqlmodel import Field, SQLModel, Relationship

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from pathlib import Path
from fastapi_project.config import settings


# Таблицы
class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    todo_list: int = Field(default=..., foreign_key="todolist.id")
    note: str | None = Field(default=None)
    
    # Добавление отношения к TODOList
    todo_list_rel: "TODOList" = Relationship(back_populates="tasks")


class TODOList(SQLModel, table=True):
    id: int = Field(default=..., primary_key=True)
    user: int = Field(default=..., foreign_key="user.id")
    title: str

    # Добавление отношения к User
    user_rel: "User" = Relationship(back_populates="todo_lists")

    # Добавление отношения к Task
    tasks: list[Task] = Relationship(back_populates="todo_list_rel", cascade_delete=True)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str

    # Добавление отношения к TODOList
    todo_lists: list[TODOList] = Relationship(back_populates="user_rel", cascade_delete=True)



# Модели
class TODOListCreate(SQLModel):
    title: str

class TaskCreate(SQLModel):
    todo_list: int = Field(default=..., foreign_key="todolist.id")
    note: str

class TaskUpdate(SQLModel):
    note: str

class UserRegister(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    username: str

    class Config:
        orm_mode = True


engine = create_async_engine(settings.DB_URL)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session

SessionDP = Annotated[AsyncSession, Depends(get_session)]