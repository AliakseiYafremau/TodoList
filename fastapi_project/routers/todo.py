from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session, Task, TODOList, TODOListCreate


todo_router = APIRouter()
SessionDP = Annotated[Session, Depends(get_session)]


@todo_router.get("/todo")
async def get_todolists(session: SessionDP) -> List[TODOList]:
    todo = session.exec(select(TODOList)).all()
    return todo

@todo_router.get("/todo/{todo_id}")
async def get_todolist(todo_id: int, session: SessionDP) -> TODOList:
    todo = session.get(TODOList, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@todo_router.post("/todo")
async def create_task(todo: TODOListCreate, session: SessionDP) -> TODOList:
    todo = TODOList(title=todo.title)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@todo_router.put("/todo/{todo_id}")
async def update_task(todo_id: int, new_todo: TODOListCreate, session: SessionDP) -> TODOList:
    old_todo = session.get(TODOList, todo_id)
    if not old_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo_data = new_todo.model_dump(exclude_unset=True)
    old_todo.sqlmodel_update(todo_data)
    session.add(old_todo)
    session.commit()
    session.refresh(old_todo)
    return old_todo