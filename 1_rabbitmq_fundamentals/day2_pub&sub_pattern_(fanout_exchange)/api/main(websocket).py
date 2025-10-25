from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from producer import publish_event

app = FastAPI(title="FastAPI + RabbitMQ Pub/Sub + WebSocket")


class Event(BaseModel):
    title: str
    body: str


# Keep active connections
clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)


@app.post("/broadcast/")
async def broadcast_message(data: Event, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_event, data.dict())
    for client in clients:
        await client.send_json(data)
    return {"status": "broadcast sent", "data": data}
