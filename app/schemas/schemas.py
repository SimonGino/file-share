# app/schemas/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: int

class FolderBase(BaseModel):
    name: str
    parent_id: Optional[UUID] = None

class FolderCreate(FolderBase):
    pass

class Folder(FolderBase):
    id: UUID
    children: List['Folder'] = []
    files: List['File'] = []

class FileBase(BaseModel):
    name: str
    path: str
    folder_id: UUID

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: UUID

    class Config:
        from_attributes = True  # 使用 Pydantic v2 的新配置键
        # orm_mode = True