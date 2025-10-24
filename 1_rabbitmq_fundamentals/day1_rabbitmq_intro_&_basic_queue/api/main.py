from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import send_to_queue

app = FastAPI()


class Task(BaseModel):
    title: str
    body: str

@app.post('/send-task/')
def send_task(data: Task, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_to_queue, data.dict())
    return {"status": "Message queued successfully", "data": data}

