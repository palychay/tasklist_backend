from pydantic import BaseModel, EmailStr


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class Task(TaskCreate):
    id: int
    priority: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"