from pydantic import BaseModel, validator

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