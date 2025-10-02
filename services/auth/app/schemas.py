from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str
    age: int
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int

    class Config:
        from_attributes = True

class UserCreds(BaseModel):
    email: str
    password: str