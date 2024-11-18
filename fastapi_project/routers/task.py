from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from fastapi_project.database import Task, TODOList, TaskCreate, TaskUpdate, SessionDP
from fastapi_project.routers.users import get_current_user

task_router = APIRouter()


# Получение списка задач
@task_router.get("/task")
async def get_tasks(session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> List[Task]:
    todo_list = await session.execute(select(TODOList).where(TODOList.user==current_user))
    tasks = []
    for todo in todo_list.scalars().all():
        task = await session.execute(select(Task).where(Task.todo_list==todo.id))
        tasks.extend(task.scalars().all())
    return tasks


# Получение конкретной задачи
@task_router.get("/task/{task_id}")
async def get_task(task_id: int, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> Task:
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    todo_id = await session.get(TODOList, task.todo_list)
    if not task or todo_id.user != current_user or not todo_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# Создание задачи
@task_router.post("/task")
async def create_task(task: TaskCreate, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> Task:
    todo_id = await session.get(TODOList, task.todo_list)
    if not todo_id or todo_id.user != current_user:
        raise HTTPException(status_code=400, detail="Unknown todo list")
    task = Task(todo_list=task.todo_list, note=task.note)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


# Обновление задачи
@task_router.put("/task/{task_id}")
async def update_task(task_id: int, new_task: TaskUpdate, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> Task:
    old_task: Task = await session.get(Task, task_id)
    if not old_task:
        raise HTTPException(status_code=404, detail="Task not found")
    todo_id = await session.get(TODOList, old_task.todo_list)
    if not old_task or todo_id.user != current_user:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = new_task.model_dump(exclude_unset=True)
    old_task.sqlmodel_update(task_data)
    session.add(old_task)
    await session.commit()
    await session.refresh(old_task)
    return old_task


# Удаление задачи
@task_router.delete("/task/{task_id}")
async def delete_task(task_id: int, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> Task:
    task: Task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    todo_id = await session.get(TODOList, task.todo_list)
    if not task or todo_id.user != current_user:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()
    return {"msg": "Task deleted successfully"}
