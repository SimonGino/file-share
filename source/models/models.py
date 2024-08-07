import uuid
import datetime

from sqlalchemy import Column, Integer, String, DateTime

from source.storages.database import Base

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
    folder_id = Column(String(64))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    file_size = Column(Integer)  # 使用整数类型存储文件大小，以字节为单位
