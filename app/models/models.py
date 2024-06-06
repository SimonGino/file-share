import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # Specify the length here
    email = Column(String(100), unique=True, index=True)  # Specify the length here
    hashed_password = Column(String(128))  # Specify the length here
    is_active = Column(Integer, default=1)

class Folder(Base):
    __tablename__ = "folders"

    id = Column(String(64), primary_key=True, default=str(uuid.uuid4), index=True)
    name = Column(String(255), index=True)
    parent_id = Column(String(64), nullable=True)  # 不再定义外键关系

class FuFile(Base):
    __tablename__ = "files"

    id = Column(String(64), primary_key=True, default=str(uuid.uuid4), index=True)
    name = Column(String(255), index=True)
    path = Column(String(255))
    folder_id = Column(String(64))  # 不再定义外键关系
