from fastapi.testclient import TestClient 
from main import app

client = TestClient(app) 

def test_create_task():
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 200  

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200  
    assert "tasks" in response.json()   

def test_get_task():
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["task"]["task_id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200  
    assert response.json()["task"]["task_id"] == task_id

def test_update_task():
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["task"]["task_id"]

    updated_task_data = {
        "title": "Updated Task",
        "description": "This is an updated test task",
        "completed": True
    }
    response = client.put(f"/tasks/{task_id}", json=updated_task_data)
    assert response.status_code == 200  
    assert response.json()["task"]["title"] == updated_task_data["title"]
    assert response.json()["task"]["completed"] == updated_task_data["completed"]

def test_delete_task():
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False
    }
    create_response = client.post("/tasks", json=task_data)
    task_id = create_response.json()["task"]["task_id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200  
    assert response.json()["message"] == "Task deleted" 
    response = client.delete("/tasks/1")

    assert response.status_code == 200


def test_get_nonexistent_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404
