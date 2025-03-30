import asyncio
from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, Boolean, select
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from base import Base
from links.models import Link
from database import get_session



class User(Base):
    __tablename__ = 'user'
    
    id = mapped_column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    created_at = Column(DateTime, unique=False, nullable=False)
    last_login_at = Column(DateTime, unique=False, nullable=True)
    is_active = Column(Boolean, default=True, unique=False, nullable=False)

    link: Mapped[List["Link"]] = relationship(back_populates='user')


def create_anonimous_user():
    '''
        Функция create_anonimous_user проверяет, есть ли в базе данных запись о
            пользователе с id 1 и email default@default.default. Если такой
            записи нет, то создает ее и сохраняет в БД.
        Это лютый костыль, чтобы ссылки, которые создают неавторизованные пользователи
            числились за этим (типо анонимным) пользователем.
    '''

    session = get_session()
    query = select(User).filter((User.id == 1) & (User.email == 'default@default.default'))
    result = session.execute(query)
    result = result.scalar()

    if not result:
        new_user = User(email='default@default.default', hashed_password=None, created_at=datetime.now(),
                    last_login_at=None, is_active=True)
        session.add(new_user)
        session.commit()

    return None
