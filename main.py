from fastapi import FastAPI
from pydantic import BaseModel

class Task(BaseModel):
    title: str
    description: str | None = None
    completed : bool = False

app = FastAPI()


@app.post("/tasks")
def create_task(task: Task):
    return {"message": "Task created", "task": task}
