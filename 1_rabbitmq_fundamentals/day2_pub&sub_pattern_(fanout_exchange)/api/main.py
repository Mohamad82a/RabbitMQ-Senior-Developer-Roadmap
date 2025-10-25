from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import publish_event

app = FastAPI()

class Event(BaseModel):
    title: str
    body: str

@app.post("/broadcast/")
def broadcast_message(data: Event, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_event, data.dict())
    return {"status": "broadcast sent", "data": data}
