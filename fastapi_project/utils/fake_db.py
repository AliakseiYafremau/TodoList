import asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_project.database import User, TODOList, Task, SessionDP, engine
from sqlalchemy import select

fake = Faker()

# Асинхронная функция для заполнения базы данных
async def populate_database(session: AsyncSession, num_users: int = 1000, num_todolists_per_user: int = 5, num_tasks_per_list: int = 10):
    # Создаем пользователей
    users = []
    for _ in range(num_users):
        user = User(username=fake.unique.user_name(), password=fake.password())
        session.add(user)
        users.append(user)
    await session.commit()

    # Подгружаем созданных пользователей
    result = await session.execute(select(User))
    users = result.scalars().all()

    # Создаем TODO-листы для каждого пользователя
    for user in users:
        for _ in range(num_todolists_per_user):
            todo_list = TODOList(user=user.id, title=fake.sentence(nb_words=3))
            session.add(todo_list)
            await session.commit()  # Коммит, чтобы получить ID TODO-листа

            # Подгружаем созданный TODO-лист
            result = await session.execute(select(TODOList).where(TODOList.user == user.id))
            todo_list = result.scalars().first()

            # Создаем задачи для TODO-листа
            for _ in range(num_tasks_per_list):
                task = Task(todo_list=todo_list.id, note=fake.sentence(nb_words=5))
                session.add(task)
    await session.commit()

# Асинхронный контекстный менеджер
async def main(engine):
    async with SessionDP(engine) as session:
        await populate_database(session=session)

if __name__ == "__main__":
    # Вызов функции main()
    asyncio.run(main(engine))
