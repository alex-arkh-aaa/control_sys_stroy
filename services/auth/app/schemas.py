from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class User(BaseModel):
    name: str
    email: str
    age: int
    password: str
    job_title: str  # ← Просто str!

    @validator('job_title')
    def validate_job_title(cls, v):
        allowed = ['engineer', 'manager', 'seo']
        if v not in allowed:
            raise ValueError(f'job_title must be one of: {allowed}')
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    job_title: str  # ← Тоже str!

    class Config:
        from_attributes = True

class UserCreds(BaseModel):
    email: str
    password: str



class DefectStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress" 
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class DefectPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProjectCreate(BaseModel):
    name: str
    address: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    address: str
    description: Optional[str]
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class DefectCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None

    @validator('priority')
    def validate_priority(cls, v):
        allowed = ['low', 'medium', 'high', 'critical']
        if v not in allowed:
            raise ValueError(f'priority must be one of: {allowed}')
        return v

class DefectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DefectStatus] = None
    priority: Optional[DefectPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class DefectResponse(BaseModel):
    id: int
    title: str
    description: str
    status: DefectStatus
    priority: DefectPriority
    project_id: int
    author_id: int
    assignee_id: Optional[int]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: int
    text: str
    defect_id: int
    author_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class ProjectHistoryResponse(BaseModel):
    id: int
    project_id: int
    defect_id: int
    changed_by: int
    change_type: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    change_date: datetime
    defect: Optional[DefectResponse] = None
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True

        