import pytest
import pytest_asyncio
import httpx

from httpx import ASGITransport, AsyncClient
from fastapi_project.config import settings
from fastapi_project.tests.conftest import app, override_get_db
from fastapi_project.database import User, TODOList, Task


# Создаем клиента
@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# Тесты
async def test_create_user(client: httpx.AsyncClient):
    """Авторизация и регистрация пользователей"""

    # Регистрируем двух пользователей
    response = await client.post("/register", params={"username": "test_user1", "password": "test_password1"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}

    response = await client.post("/register", params={"username": "test_user2", "password": "test_password2"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}

    # Пытаемся зарегистрировать одного пользователя дважды
    response = await client.post("/register", params={"username": "test_user1", "password": "test_password1"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}

    # Проверяем авторизацию
    response = await client.post("/login", params={"username": "test_user1", "password": "test_password1"})
    assert response.status_code == 200
    assert "access_token" in response.json().keys()

    response = await client.post("/login", params={"username": "test_user1", "password": "wrong_password1"})
    assert response.status_code == 401

    response = await client.post("/login", params={"username": "wrong_user", "password": "test_password"})
    assert response.status_code == 401

async def test_get_todos(client: httpx.AsyncClient):
    """Получение списка задач"""
    response = await client.post("/login", params={"username": "test_user1", "password": "test_password1"})
    token = response.json()["access_token"]

    # Получаем список задач неавторизованным пользователем
    response = await client.get("/todo")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = await client.get("/todo/1")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = await client.get("/todo/1/1")
    assert response.status_code == 404

    response = await client.get("/todo/2")
    assert response.status_code == 401

    # Получаем список задач авторизованным пользователем
    response = await client.get("/todo", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []

    response = await client.get("/todo/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

    response = await client.get("/todo/1/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

    response = await client.get("/todo/2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


async def test_create_todo(client: httpx.AsyncClient):
    """Создание задачи"""

    # Регистрируем пользователя
    response = await client.post("/login", params={"username": "test_user1", "password": "test_password1"})
    token = response.json()["access_token"]

    # Создаем задачи
    response = await client.post("/todo", json={"title": "Test todo"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = await client.post("/todo", json={"title": "Test todo"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Todo with this title already exists"}

    # Пытаемся создать задачу неавторизованным пользователем
    response = await client.post("/todo", json={"title": "Test todo1"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Пытаемся создать задачу с невалидным токеном
    response = await client.post("/todo", json={"title": "Test todo2"}, headers={"Authorization": f"Bearer wrong_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


async def test_update_todo(client: httpx.AsyncClient):
    """Обновление задачи"""

    # Регистрируем пользователя
    response = await client.post("/login", params={"username": "test_user1", "password": "test_password1"})
    token = response.json()["access_token"]

    # Создаем задачу
    response = await client.post("/todo", json={"title": "Test todo. Not updated"}, headers={"Authorization": f"Bearer {token}"})
    todo_id = response.json()["id"]

    # Обновляем задачу
    response = await client.put(f"/todo/{todo_id}", json={"title": "Test todo. Updated"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert ("title", "Test todo. Updated") in response.json().items()

    # Проверяем, что задача обновилась
    responde = await client.get(f"/todo/{todo_id}", headers={"Authorization": f"Bearer {token}"})
    assert responde.status_code == 200
    assert ("id", todo_id) in responde.json().items() and ("title", "Test todo. Updated") in responde.json().items()

    # Пытаемся обновить задачу неавторизованным пользователем
    response = await client.put(f"/todo/{todo_id}", json={"title": "Test todo. Updated"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Пытаемся обновить задачу с невалидным токеном
    response = await client.put(f"/todo/{todo_id}", json={"title": "Test todo. Updated"}, headers={"Authorization": f"Bearer wrong_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


async def test_delete_todo(client: httpx.AsyncClient):
    """Удаление задачи"""

    # Регистрируем пользователей
    response = await client.post("/login", params={"username": "test_user1", "password": "test_password1"})
    token = response.json()["access_token"]

    response = await client.post("/login", params={"username": "test_user2", "password": "test_password2"})
    token_not_owner = response.json()["access_token"]

    # Создаем задачи
    response = await client.post("/todo", json={"title": "Test todo for delete1"}, headers={"Authorization": f"Bearer {token}"})
    todo_id1 = response.json()["id"]

    response = await client.post("/todo", json={"title": "Test todo for delete2"}, headers={"Authorization": f"Bearer {token}"})
    todo_id2 = response.json()["id"]

    # Пытаемся удалить задачу неавторизованным пользователем
    response = await client.delete(f"/todo/{todo_id1}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Пытаемся удалить задачу с невалидным токеном
    response = await client.delete(f"/todo/{todo_id1}", headers={"Authorization": f"Bearer wrong_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

    # Пытаемся удалить задачу пользователем, который не является владельцем
    response = await client.delete(f"/todo/{todo_id1}", headers={"Authorization": f"Bearer {token_not_owner}"})
    assert response.status_code == 404

    response = await client.get(f"/todo/{todo_id2}", headers={"Authorization": f"Bearer {token_not_owner}"})
    assert response.status_code == 404

    # Пытаемся удалить задачи пользователем, который является владельцем
    response = await client.delete(f"/todo/{todo_id1}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = await client.delete(f"/todo/{todo_id2}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Пытаемся получить удаленные задачи
    response = await client.get(f"/todo/{todo_id1}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

    response = await client.get(f"/todo/{todo_id2}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

    # Пытаемся удалить задачи неавторизованным пользователем
    response = await client.delete(f"/todo/{todo_id1}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = await client.delete(f"/todo/{todo_id2}")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    # Пытаемся удалить задачи с невалидным токеном
    response = await client.delete(f"/todo/{todo_id1}", headers={"Authorization": f"Bearer wrong_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

    response = await client.delete(f"/todo/{todo_id2}", headers={"Authorization": f"Bearer wrong_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


async def test_owner_todo(client: httpx.AsyncClient):
    """Проверка владельца задачи"""

    # Регистрируем пользователей
    response = await client.post("/login", params={"username": "test_user1", "password": "test_password1"})
    token = response.json()["access_token"]

    response = await client.post("/login", params={"username": "test_user2", "password": "test_password2"})
    token_not_owner = response.json()["access_token"]

    # Создаем задачи
    response = await client.post("/todo", json={"title": "Test todo for owner"}, headers={"Authorization": f"Bearer {token}"})
    todo_id = response.json()["id"]

    response = await client.get("/todo", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert ("id", todo_id) in response.json()[-1].items()

    # Пытаемся получить владельца задачи неавторизованным пользователем
    response = await client.get(f"/todo/{todo_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

    # Пытаемся изменить задачу пользователем, который не является владельцем
    response = await client.put(f"/todo/{todo_id}", json={"title": "Test todo for owner"}, headers={"Authorization": f"Bearer {token_not_owner}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

    # Пытаемся удалить задачу пользователем, который не является владельцем
    response = await client.delete(f"/todo/{todo_id}", headers={"Authorization": f"Bearer {token_not_owner}"})
    