from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session, Task, TaskCreate


task_router = APIRouter()
SessionDP = Annotated[Session, Depends(get_session)]


@task_router.get("/task")
async def get_tasks(session: SessionDP) -> List[Task]:
    task = session.exec(select(Task)).all()
    return task

@task_router.get("/task/{task_id}")
async def get_task(task_id: int, session: SessionDP) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@task_router.post("/task")
async def create_task(task: TaskCreate, session: SessionDP) -> Task:
    task = Task(todo_list=task.todo_list, note=task.note)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@task_router.put("/task/{task_id}")
async def update_task(task_id: int, new_task: TaskCreate, session: SessionDP) -> Task:
    old_task = session.get(Task, task_id)
    if not old_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = new_task.model_dump(exclude_unset=True)
    old_task.sqlmodel_update(task_data)
    session.add(old_task)
    session.commit()
    session.refresh(old_task)
    return old_task