from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    name: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
