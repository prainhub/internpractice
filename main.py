
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import database
import models


class Task(BaseModel):
    task_id: int = 0
    title: str
    description: str | None = None
    completed: bool = False


app = FastAPI()
tasks = []
database.Base.metadata.create_all(bind=database.engine)

@app.post("/tasks")
def create_task(task: Task, db: Session = Depends(database.get_db)):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "message": "Task created",
        "task": {
            "task_id": new_task.task_id,
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.completed
        }
    }


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