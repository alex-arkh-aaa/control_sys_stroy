from pydantic import BaseModel
from typing import Optional, List


class NotificationRequest(BaseModel):
    email: str
    message: str
    full_name: str
    subject: str
