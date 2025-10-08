from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
import uuid

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"

class UserRegisteredEvent(BaseEvent):
    event_type: Literal["user.registered"] = "user.registered"
    user_id: int
    email: str
    name: str

class UserDeletedEvent(BaseEvent):
    event_type: Literal["user.deleted"] = "user.deleted"
    user_id: int
    email: str
    name: str

# Для будущих событий
class DefectCreatedEvent(BaseEvent):
    event_type: Literal["defect.created"] = "defect.created"
    defect_id: int
    title: str
    assigned_to: int  # user_id