from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base

BaseAuth = declarative_base()

class User(BaseAuth):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, unique=False, nullable=False)
    last_login_at = Column(DateTime, unique=False, nullable=True)
    is_active = Column(Boolean, default=True, unique=False, nullable=False)
