import pytest
from httpx import AsyncClient
from app.main import app
from app.database import SessionLocal
from app.models import User


@pytest.fixture(scope="module")
def test_app():
    # Настройка тестового приложения
    yield app


@pytest.fixture(scope="module")
async def test_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
async def setup_database():
    # Создаем тестовую базу данных и пользователя
    async with SessionLocal() as session:
        # Создание пользователя для тестов
        user = User(username="testuser", password_hash="hashedpassword")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user  # Возвращаем пользователя для использования в тестах
        await session.delete(user)  # Очистка после тестов


# Проверяет успешную регистрацию нового пользователя
@pytest.mark.asyncio
async def test_register(test_client):
    response = await test_client.post("/auth/register", json={"username": "newuser", "password": "password"})
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


# Проверяет успешную аутентификацию существующего пользователя
@pytest.mark.asyncio
async def test_login(test_client, setup_database):
    response = await test_client.post("/auth/login", data={"username": "testuser", "password": "hashedpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()


# Проверяет создание новой задачи
@pytest.mark.asyncio
async def test_create_task(test_client, setup_database):
    token_response = await test_client.post("/auth/login", data={"username": "testuser", "password": "hashedpassword"})
    access_token = token_response.json()["access_token"]

    response = await test_client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Test Task", "description": "Test Description", "status": "pending"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


# Проверяет получение списка задач
@pytest.mark.asyncio
async def test_get_tasks(test_client, setup_database):
    token_response = await test_client.post("/auth/login", data={"username": "testuser", "password": "hashedpassword"})
    access_token = token_response.json()["access_token"]

    response = await test_client.get("/tasks", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Проверяет обновление существующей задачи
@pytest.mark.asyncio
async def test_update_task(test_client, setup_database):
    token_response = await test_client.post("/auth/login", data={"username": "testuser", "password": "hashedpassword"})
    access_token = token_response.json()["access_token"]

    create_response = await test_client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Task to Update", "description": "Update me", "status": "pending"}
    )

    task_id = create_response.json()["id"]

    update_response = await test_client.put(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Updated Task", "description": "Updated Description", "status": "completed"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"


# Проверяет удаление задачи
@pytest.mark.asyncio
async def test_delete_task(test_client, setup_database):
    token_response = await test_client.post("/auth/login", data={"username": "testuser", "password": "hashedpassword"})
    access_token = token_response.json()["access_token"]

    create_response = await test_client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"title": "Task to Delete", "description": "Delete me", "status": "pending"}
    )

    task_id = create_response.json()["id"]

    delete_response = await test_client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {access_token}"})

    assert delete_response.status_code == 200
    assert delete_response.json() == {"detail": "Task deleted"}
