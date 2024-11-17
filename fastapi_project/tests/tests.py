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
    response = await client.post("/register", params={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered successfully"}

    response = await client.post("/register", params={"username": "test_user", "password": "test_password"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}

    response = await client.post("/login", params={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200

    response = await client.post("/login", params={"username": "test_user", "password": "wrong_password"})
    assert response.status_code == 401

    response = await client.post("/login", params={"username": "wrong_user", "password": "test_password"})
    assert response.status_code == 401

async def test_get_todos(client: httpx.AsyncClient):
    response = await client.get("/todo")
    assert response.status_code == 200
    assert response.json() == []

    response = await client.get("/todo/1")
    assert response.status_code == 404

    response = await client.get("/todo/1/1")
    assert response.status_code == 404

    response = await client.get("/todo/2")
    assert response.status_code == 404


async def test_create_todo(client: httpx.AsyncClient):
    response = await client.post("/login", params={"username": "test_user", "password": "test_password"})
    token = response.json()["access_token"]

    response = await client.post("/todo", json={"title": "Test todo"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    response = await client.post("/todo", json={"title": "Test todo"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Todo with this title already exists"}

    response = await client.post("/todo", json={"title": "Test todo1"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

    response = await client.post("/todo", json={"title": "Test todo2"}, headers={"Authorization": f"Bearer wrong_token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}