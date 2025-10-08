import sys
import os
from pathlib import Path

# ДОБАВЬ ЭТО В САМОМ ВЕРХУ
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from .email_send import send_email
from contextlib import asynccontextmanager
from .schemas import *

# Импорты для RabbitMQ
from shared.rabbitmq import rabbit_manager
from .consumers.email_consumer import app as faststream_app
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Подключаем RabbitMQ при старте
    await rabbit_manager.connect()
    print("✅ RabbitMQ connected and infrastructure declared")
    
    # 2. Запускаем FastStream consumer в фоне
    consumer_task = asyncio.create_task(faststream_app.run())
    print("✅ RabbitMQ consumer started")
    
    yield
    
    # 3. При остановке отменяем задачу
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("RabbitMQ consumer stopped")

app = FastAPI(lifespan=lifespan)

@app.get("/notify")
async def get():
    return 'success'


@app.post("/notify")
async def notify(request: NotificationRequest):
    try:
        success = False
        success = await send_email(request.email, 
                                   request.message, 
                                   request.full_name, 
                                   request.subject)
        print('success', success)
        if success:
            return {"status": "success", "error": "no errors"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

#uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
