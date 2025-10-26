from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import publish_level

app = FastAPI()


@app.post("/log")
def broadcast_message(data: dict, background_tasks: BackgroundTasks):
    level = data.get('level', 'info')
    message = data.get('message', '')
    background_tasks.add_task(publish_level, level, message)

    return {"status": "Message sent", "level": level, "message": message}
