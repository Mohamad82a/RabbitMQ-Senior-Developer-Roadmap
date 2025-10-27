from fastapi import FastAPI, BackgroundTasks
from producer import publish_task

app = FastAPI()

@app.post('/task')
def send_task(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_task, data)
    return {'status': 'Task sent', 'data': data}



@app.post('/async-task')
async def send_task2(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(publish_task, data)
    return {'status': 'Async task sent', 'data': data}
