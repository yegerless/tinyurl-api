from typing import List
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column

from base import Base



class Link(Base):
    __tablename__ = 'link'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    alias = Column(String, unique=True, nullable=False)
    source_url = Column(String, unique=False, nullable=False)
    created_at = Column(DateTime, unique=False, nullable=False)
    expires_at = Column(DateTime, unique=False, nullable=True)
    last_used_at = Column(DateTime, unique=False, nullable=True)
    transitions_quantity = Column(Integer, default=0, unique=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates='link')