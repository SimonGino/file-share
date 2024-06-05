from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # Specify the length here
    email = Column(String(100), unique=True, index=True)  # Specify the length here
    hashed_password = Column(String(128))  # Specify the length here
    is_active = Column(Integer, default=1)

