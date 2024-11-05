from pydantic import BaseModel

# Базовая схема для задач
class TaskBase(BaseModel):
    title: str
    description: str = None
    status: str

# Схема для создания задачи
class TaskCreate(TaskBase):
    pass

# Схема для возвращаемой задачи (с ID)
class Task(TaskBase):
    id: int

    class Config:
        orm_mode = True

# Схемы для пользователей и токенов аутентификации
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
