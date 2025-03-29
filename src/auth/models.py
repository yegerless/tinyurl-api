from typing import List
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from base import Base
from links.models import Link



class User(Base):
    __tablename__ = 'user'
    
    id = mapped_column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, unique=False, nullable=False)
    last_login_at = Column(DateTime, unique=False, nullable=True)
    is_active = Column(Boolean, default=True, unique=False, nullable=False)

    link: Mapped[List["Link"]] = relationship(back_populates='user')
