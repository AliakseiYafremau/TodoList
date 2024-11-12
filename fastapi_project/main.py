from fastapi import FastAPI
from .routers import todo, task, users
from . import database

app = FastAPI()

app.include_router(todo.todo_router, tags=["todos"])
app.include_router(task.task_router, tags=["tasks"])
app.include_router(users.user_router, tags=["users"])


@app.on_event("startup")
async def startup_event():
    database.create_db_and_tables()
