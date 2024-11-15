from typing import Annotated

from sqlmodel import Field, SQLModel, create_engine, Session

from pathlib import Path
from sqlalchemy.engine import URL
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

from sqlalchemy.engine import URL
from os import getenv

# db_url = URL.create(
#     drivername="postgresql+psycopg2",  # Или "postgresql+psycopg" для psycopg3
#     username=getenv("DB_USER", "postgres"),
#     password=getenv("DB_PASSWORD", ""),
#     host=getenv("DB_HOST", "localhost"),
#     port=getenv("DB_PORT", "5432"),
#     database=getenv("DB_NAME", "mydatabase"),
# )

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="todo_user",
    password="todo_password",
    host="localhost",
    port=5432,
    database="todo_db",
)
print(db_url)

connect_args = {"check_same_thread": False, "options": "-c client_encoding=utf8"}
engine = create_engine(db_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
