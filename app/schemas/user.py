# app/schemas/user.py
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: int

    class Config:
        from_attributes = True  # 使用 Pydantic v2 的新配置键
        # orm_mode = True