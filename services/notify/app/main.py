from fastapi import FastAPI
from .email_send import send_email
from .schemas import *

app = FastAPI()

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
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

#uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
