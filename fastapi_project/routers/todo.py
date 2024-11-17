from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from fastapi_project.database import Task, TODOList, TODOListCreate, SessionDP
from .users import get_current_user


todo_router = APIRouter()


# Получение списка todo
@todo_router.get("/todo")
async def get_todolists(session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> List[TODOList]:
    todo = await session.execute(select(TODOList).where(TODOList.user==current_user))
    return todo.scalars().all()


# Получение конкретного todo
@todo_router.get("/todo/{todo_id}")
async def get_todolist(todo_id: int, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> TODOList:
    todo = await session.get(TODOList, todo_id)
    if not todo or todo.user != current_user:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


# Создание todo
@todo_router.post("/todo")
async def create_task(todo: TODOListCreate, current_user: Annotated[str, Depends(get_current_user)], session: SessionDP) -> TODOList:
    result = await session.execute(select(TODOList).where(TODOList.title==todo.title))
    existing_todo = result.scalars().first()
    if existing_todo:
        raise HTTPException(status_code=400, detail="Todo with this title already exists")
    todo = TODOList(user=current_user, title=todo.title)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


# Обновление todo
@todo_router.put("/todo/{todo_id}")
async def update_task(todo_id: int, new_todo: TODOListCreate, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> TODOList:
    old_todo: TODOList = await session.get(TODOList, todo_id)
    if not old_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_data = new_todo.model_dump(exclude_unset=True)
    old_todo.sqlmodel_update(todo_data)
    session.add(old_todo)
    await session.commit()
    await session.refresh(old_todo)
    return old_todo


# Удаление todo
@todo_router.delete("/todo/{todo_id}")
async def delete_todo(todo_id: int, session: SessionDP, current_user: Annotated[str, Depends(get_current_user)]) -> TODOList:
    todo: TODOList = await session.get(TODOList, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    await session.delete(todo)
    await session.commit()
    return {"msg": "Todo deleted successfully"}
