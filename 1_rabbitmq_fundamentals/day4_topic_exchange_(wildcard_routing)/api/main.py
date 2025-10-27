from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from producer import publish_event

app = FastAPI()


@app.post("/publish")
def broadcast_message(data: dict, background_tasks: BackgroundTasks):
    routing_key = data.get('routing_key', 'info.default')
    message = data.get('message', {})
    background_tasks.add_task(publish_event, routing_key, message)

    return {"status": "Message published", "routing_key": routing_key,}
