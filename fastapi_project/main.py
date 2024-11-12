from fastapi import FastAPI
from .routers import todo, task
from . import database

app = FastAPI()

app.include_router(todo.todo_router)
app.include_router(task.task_router)


@app.on_event("startup")
async def startup_event():
    database.create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}
