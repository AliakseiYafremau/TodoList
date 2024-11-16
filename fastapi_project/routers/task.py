from typing import Annotated, List

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from ..database import Task, TaskCreate, TaskUpdate, SessionDP


task_router = APIRouter()


# Получение списка задач
@task_router.get("/task")
async def get_tasks(session: SessionDP) -> List[Task]:
    task = await session.execute(select(Task))
    return task.scalars().all()


# Получение конкретной задачи
@task_router.get("/task/{task_id}")
async def get_task(task_id: int, session: SessionDP) -> Task:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Создание задачи
@task_router.post("/task")
async def create_task(task: TaskCreate, session: SessionDP) -> Task:
    task = Task(todo_list=task.todo_list, note=task.note)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


# Обновление задачи
@task_router.put("/task/{task_id}")
async def update_task(task_id: int, new_task: TaskUpdate, session: SessionDP) -> Task:
    old_task: Task = await session.get(Task, task_id)
    if not old_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = new_task.model_dump(exclude_unset=True)
    old_task.sqlmodel_update(task_data)
    session.add(old_task)
    await session.commit()
    await session.refresh(old_task)
    return old_task


# Удаление задачи
@task_router.delete("/task/{task_id}")
async def delete_task(task_id: int, session: SessionDP) -> Task:
    task: Task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"msg": "Task deleted successfully"}
