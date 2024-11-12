from typing import Annotated

from sqlmodel import Field, SQLModel, create_engine, Session


# Таблицы
class TODOList(SQLModel, table=True):
    id: int = Field(default=..., primary_key=True)
    title: str

class Task(SQLModel, table=True):
    id: int = Field(default=..., primary_key=True)
    todo_list: int = Field(default=..., foreign_key="todolist.id")
    note: str


# Модели
class TODOListCreate(SQLModel):
    title: str


class TaskCreate(SQLModel):
    todo_list: int = Field(default=..., foreign_key="todolist.id")
    note: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
