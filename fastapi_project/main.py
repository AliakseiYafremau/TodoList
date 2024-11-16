from fastapi import FastAPI
from fastapi_project.routers import todo, task, users
from fastapi_project import database

app = FastAPI()

app.include_router(users.user_router, tags=["users"])
app.include_router(todo.todo_router, tags=["todos"])
app.include_router(task.task_router, tags=["tasks"])


if __name__ == "__main__":
    @app.on_event("startup")
    async def startup_event():
        await database.create_db_and_tables()