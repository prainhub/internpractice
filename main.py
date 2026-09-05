
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
def get_tasks(db: Session = Depends(database.get_db)):
    return {"tasks": db.query(models.Task).all()}

@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": task}

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    updated_task: Task,
    db: Session = Depends(database.get_db),
):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    db.commit()
    db.refresh(task)
    return {"message": "Task updated", "task": task}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}