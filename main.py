from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException


class Task(BaseModel):
    task_id: int = 0
    title: str
    description: str | None = None
    completed: bool = False


app = FastAPI()
tasks = []


@app.post("/tasks")
def create_task(task: Task):
    task.task_id = max((t["task_id"] for t in tasks), default=0) + 1
    tasks.append(task.model_dump())
    return {"message": "Task created", "task": task}


@app.get("/tasks")
def get_tasks():
    return {"tasks": tasks}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": task}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task):
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.update(updated_task.model_dump())
    return {"message": "Task updated", "task": task}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task = next((t for t in tasks if t["task_id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks.remove(task)
    return {"message": "Task deleted"}