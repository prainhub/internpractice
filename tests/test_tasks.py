import os
import sys
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-for-pytest-32-characters")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app

client = TestClient(app)

def register_user():
    username = f"user_{uuid4().hex}"
    payload = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "correct-password",
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    return payload

def auth_headers():
    user = register_user()
    response = client.post(
        "/login",
        json={"username": user["username"], "password": user["password"]},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_registration_and_current_user():
    user = register_user()
    response = client.post(
        "/login",
        json={"username": user["username"], "password": user["password"]},
    )
    token = response.json()["access_token"]
    me_response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert me_response.status_code == 200
    assert me_response.json()["username"] == user["username"]
    assert "hashed_password" not in me_response.json()

def test_duplicate_user_is_rejected():
    user = register_user()

    response = client.post("/register", json=user)

    assert response.status_code == 400

def test_invalid_login_is_rejected():
    user = register_user()

    response = client.post(
        "/login",
        json={"username": user["username"], "password": "wrong-password"},
    )

    assert response.status_code == 401

def test_unauthenticated_access_is_rejected():
    assert client.get("/users/me").status_code == 401
    assert client.get("/tasks").status_code == 401
    assert client.post("/tasks", json={"title": "Unauthenticated"}).status_code == 401

def test_create_task_and_response_structure():
    headers = auth_headers()
    response = client.post(
        "/tasks",
        json={"title": "Write tests", "description": "Cover the API"},
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Task created"
    assert body["task"]["title"] == "Write tests"
    assert body["task"]["completed"] is False
    assert isinstance(body["task"]["task_id"], int)

def test_create_task_rejects_invalid_input():
    response = client.post("/tasks", json={"title": 123}, headers=auth_headers())

    assert response.status_code == 422

def test_create_task_requires_title():
    response = client.post(
        "/tasks",
        json={"description": "No title"},
        headers=auth_headers(),
    )

    assert response.status_code == 422

def test_list_and_get_task():
    headers = auth_headers()
    created = client.post(
        "/tasks", json={"title": "Read task"}, headers=headers
    ).json()["task"]

    list_response = client.get("/tasks", headers=headers)
    get_response = client.get(f"/tasks/{created['task_id']}", headers=headers)

    assert list_response.status_code == 200
    assert created in list_response.json()
    assert get_response.status_code == 200
    assert get_response.json() == created

def test_update_task():
    headers = auth_headers()
    created = client.post(
        "/tasks", json={"title": "Old title"}, headers=headers
    ).json()["task"]

    response = client.put(
        f"/tasks/{created['task_id']}",
        json={"title": "New title", "completed": True},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["completed"] is True

def test_update_rejects_invalid_input():
    headers = auth_headers()
    created = client.post(
        "/tasks", json={"title": "Update me"}, headers=headers
    ).json()["task"]

    response = client.put(
        f"/tasks/{created['task_id']}",
        json={"completed": "yes"},
        headers=headers,
    )

    assert response.status_code == 422

def test_missing_task_returns_404():
    headers = auth_headers()
    assert client.get("/tasks/999999", headers=headers).status_code == 404
    assert client.put(
        "/tasks/999999", json={"title": "Missing"}, headers=headers
    ).status_code == 404
    assert client.delete("/tasks/999999", headers=headers).status_code == 404

def test_delete_task():
    headers = auth_headers()
    created = client.post(
        "/tasks", json={"title": "Delete me"}, headers=headers
    ).json()["task"]

    response = client.delete(f"/tasks/{created['task_id']}", headers=headers)

    assert response.status_code == 200
    assert client.get(f"/tasks/{created['task_id']}", headers=headers).status_code == 404

def test_users_can_access_only_their_own_tasks():
    owner_headers = auth_headers()
    other_headers = auth_headers()
    created = client.post(
        "/tasks",
        json={"title": "Private task"},
        headers=owner_headers,
    ).json()["task"]

    assert client.get("/tasks", headers=other_headers).json() == []
    assert client.get(
        f"/tasks/{created['task_id']}", headers=other_headers
    ).status_code == 404
