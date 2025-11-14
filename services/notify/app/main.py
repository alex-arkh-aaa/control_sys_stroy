from faststream import FastStream
from faststream.rabbit import RabbitBroker
from .email_send import send_email
from .schemas import *

# Брокер
broker = RabbitBroker()
app = FastStream(broker)

# Consumer для очереди defects_queue
@broker.subscriber("main")
async def notify(data: dict):
    print(data)
    try:
        success = False

        success = await send_email(data.get('email'), 
                                   data.get('message'), 
                                   data.get('full_name'), 
                                   data.get('subject'))
        print('success', success)
        if success:
            return {"status": "success", "error": "no errors"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}
    

from fastapi import FastAPI

fastapi_app = FastAPI()

@fastapi_app.get("/notify")
async def get():
    return 'success'

@fastapi_app.post("/notify")
async def notify(request: NotificationRequest):
    try:
        success = await send_email(
            request.email, 
            request.message, 
            request.full_name, 
            request.subject
        )
        
        if success:
            return {"status": "success", "error": "no errors"}
        else:
            return {"status": "failed", "error": "Email sending failed"}

    except Exception as e:
        return {"status": "failed", "error": str(e)}

#faststream run app.main:app --reload